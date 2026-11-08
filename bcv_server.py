#!/usr/bin/env python3
"""Servidor de tasas BCV: página HTML + API JSON.

Ejecución::

    python bcv_server.py                 # http://127.0.0.1:8000
    BCV_PORT=8080 python bcv_server.py   # otro puerto
    uvicorn bcv_server:app --host 0.0.0.0 --port 8000

Rutas:
    GET /               -> página HTML con las tasas (se actualiza sola cada 60 s)
    GET /app            -> aplicación FinanBCV (index.html) desde el mismo origen
    GET /tasas.json     -> archivo tasas.json generado por el scraper (sin caché)
    GET /api/tasas      -> JSON con USD, EUR y metadatos de la consulta
    POST /api/actualizar -> ejecuta python3 bcv_scraper.py > tasas.json y devuelve el JSON
    GET /health         -> estado del servicio y de la caché
    GET /docs           -> documentación interactiva (Swagger UI)

Variables de entorno:
    BCV_CACHE_TTL  segundos que se reutiliza una consulta al BCV (mín. 30, def. 300)
    BCV_HOST       host de escucha (def. 127.0.0.1; usa 0.0.0.0 para red local)
    BCV_PORT       puerto (def. 8000)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import bcv_scraper

BASE_DIR = Path(__file__).resolve().parent
TASAS_JSON = BASE_DIR / "tasas.json"
TASAS_JSON_TMP = BASE_DIR / ".tasas.json.tmp"
ACTUALIZAR_TIMEOUT = 120  # segundos máximos para regenerar tasas.json
CACHE_TTL = max(30, int(os.getenv("BCV_CACHE_TTL", "300")))
HOST = os.getenv("BCV_HOST", "127.0.0.1")
PORT = int(os.getenv("BCV_PORT", "8000"))

app = FastAPI(
    title="Tasas BCV",
    description=(
        "Tasas oficiales del dólar (USD) y del euro (EUR) publicadas por el "
        "Banco Central de Venezuela, extraídas de bcv.org.ve."
    ),
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

_lock = threading.Lock()
_actualizar_lock = threading.Lock()
_cache: dict = {"tasas": None, "ts": 0.0}


def tasas_actuales(forzar: bool = False):
    """Devuelve las tasas usando una caché corta.

    Retorna ``(tasas, desde_cache, stale)``. ``stale`` es True cuando el BCV
    falló y se está sirviendo la última consulta guardada.
    """
    ahora = time.monotonic()
    with _lock:
        en_cache = _cache["tasas"]
        if not forzar and en_cache is not None and (ahora - _cache["ts"]) < CACHE_TTL:
            return en_cache, True, False

        try:
            tasas = bcv_scraper.obtener_tasas()
        except bcv_scraper.ScrapingError:
            if en_cache is not None:
                return en_cache, True, True
            raise

        _cache["tasas"] = tasas
        _cache["ts"] = ahora
        return tasas, False, False


def regenerar_tasas_json() -> dict:
    """Ejecuta el scraper y regenera ``tasas.json`` de forma atómica.

    Equivale a ``python3 bcv_scraper.py > tasas.json 2>/dev/null``, pero
    escribiendo primero a un temporal: si el scraper falla se conserva el
    JSON anterior en lugar de dejarlo vacío.
    """
    try:
        resultado = subprocess.run(
            [sys.executable, str(BASE_DIR / "bcv_scraper.py")],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=ACTUALIZAR_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"El scraper tardó más de {ACTUALIZAR_TIMEOUT} segundos."
        ) from exc
    except OSError as exc:
        raise RuntimeError(f"No se pudo ejecutar el scraper: {exc}") from exc

    if resultado.returncode != 0:
        raise RuntimeError(f"El scraper terminó con código {resultado.returncode}.")
    if not resultado.stdout.strip():
        raise RuntimeError("El scraper no devolvió datos.")

    try:
        datos = json.loads(resultado.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("El scraper devolvió una salida no válida.") from exc

    for clave in ("usd", "eur"):
        valor = datos.get(clave)
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise RuntimeError(f"El scraper devolvió un valor inválido para {clave}.")

    TASAS_JSON_TMP.write_bytes(resultado.stdout)
    os.replace(TASAS_JSON_TMP, TASAS_JSON)

    with _lock:
        try:
            _cache["tasas"] = bcv_scraper.Tasas(
                usd=float(datos["usd"]),
                eur=float(datos["eur"]),
                fecha_valor=datos.get("fecha_valor"),
                fecha_valor_texto=datos.get("fecha_valor_texto"),
                fuente=datos.get("fuente", bcv_scraper.URL),
                obtenido_en=datos.get("obtenido_en", ""),
            )
            _cache["ts"] = time.monotonic()
        except (KeyError, TypeError, ValueError):
            _cache["ts"] = 0.0

    return datos


@app.get("/", response_class=HTMLResponse)
def portada(request: Request):
    """Página HTML con las tasas del día."""
    error = None
    stale = False
    tasas = None
    try:
        tasas, _, stale = tasas_actuales()
    except bcv_scraper.ScrapingError as exc:
        error = str(exc)

    contexto = bcv_scraper.contexto_html(
        tasas, stale=stale, error=error, en_servidor=True
    )
    return templates.TemplateResponse(request, "tasas.html", contexto)


@app.get("/app", response_class=HTMLResponse)
@app.get("/app/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def aplicacion():
    """Aplicación FinanBCV (``index.html``) servida desde el mismo origen."""
    return FileResponse(BASE_DIR / "index.html", media_type="text/html")


@app.get("/tasas.json")
def archivo_tasas():
    """Devuelve ``tasas.json`` recién generado, sin caché."""
    if not TASAS_JSON.exists():
        return JSONResponse(
            status_code=404,
            content={
                "ok": False,
                "error": "tasas.json no existe; usa POST /api/actualizar.",
            },
        )
    return FileResponse(
        TASAS_JSON,
        media_type="application/json",
        headers={"Cache-Control": "no-store"},
    )


@app.post("/api/actualizar")
def api_actualizar():
    """Ejecuta ``bcv_scraper.py``, regenera tasas.json y devuelve las tasas."""
    if not _actualizar_lock.acquire(blocking=False):
        return JSONResponse(
            status_code=409,
            content={"ok": False, "error": "Ya hay una actualización en curso."},
        )
    try:
        return {"ok": True, **regenerar_tasas_json()}
    except RuntimeError as exc:
        return JSONResponse(
            status_code=502,
            content={"ok": False, "error": str(exc)},
        )
    finally:
        _actualizar_lock.release()


@app.get("/api/tasas")
def api_tasas(refresh: bool = Query(False, description="Ignorar la caché y consultar el BCV.")):
    """Tasas oficiales del dólar y del euro en bolívares."""
    try:
        tasas, desde_cache, stale = tasas_actuales(forzar=refresh)
    except bcv_scraper.ScrapingError as exc:
        return JSONResponse(
            status_code=502,
            content={
                "ok": False,
                "error": f"No se pudieron obtener las tasas del BCV: {exc}",
            },
        )

    return {
        "ok": True,
        **tasas.a_dict(),
        "cache": {
            "ttl_segundos": CACHE_TTL,
            "desde_cache": desde_cache,
            "stale": stale,
        },
    }


@app.get("/health")
def health():
    """Estado del servicio (no consulta el BCV)."""
    return {
        "ok": True,
        "tasas_en_cache": _cache["tasas"] is not None,
        "ttl_segundos": CACHE_TTL,
    }


def main() -> None:
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
