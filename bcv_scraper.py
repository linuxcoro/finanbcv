#!/usr/bin/env python3
"""Scraper de las tasas oficiales del BCV (USD y EUR).

Fuente: https://www.bcv.org.ve/glosario/cambio-oficial

Extrae el dólar y el euro desde los bloques ``<div id="dolar">`` y
``<div id="euro">`` de la página de cambio oficial del Banco Central de
Venezuela, junto con la "Fecha Valor" publicada.

Uso por consola::

    python bcv_scraper.py                          # imprime JSON
    python bcv_scraper.py --html tasas.html        # crea un HTML autónomo
    python bcv_scraper.py --url https://...        # otra URL equivalente

El sitio del BCV suele presentar una cadena TLS incompleta, por lo que el
scraper intenta primero con validación de certificado y, si falla, repite
la petición sin validar (la conexión sigue cifrada). Esto se avisa por log.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape
from requests.adapters import HTTPAdapter
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util.retry import Retry

URL = "https://www.bcv.org.ve/glosario/cambio-oficial"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
TIMEOUT = 25
BASE_DIR = Path(__file__).resolve().parent
MONEDAS = (("dolar", "USD"), ("euro", "EUR"))

# Zona horaria de Venezuela con respaldo fijo (UTC-4, sin horario de verano).
def _zona_local():
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo("America/Caracas")
    except Exception:  # pragma: no cover - solo si faltan los tzdata
        return timezone(timedelta(hours=-4))


LOGGER = logging.getLogger("bcv_scraper")
_VERIFICACION_TLS: Optional[bool] = None  # se fija tras la primera descarga


class ScrapingError(RuntimeError):
    """Error controlado al descargar o interpretar la página del BCV."""


@dataclass(frozen=True)
class Tasas:
    """Tasas oficiales del BCV expresadas en bolívares."""

    usd: float
    eur: float
    fecha_valor: Optional[str] = None
    fecha_valor_texto: Optional[str] = None
    fuente: str = URL
    obtenido_en: str = ""

    def a_dict(self) -> dict:
        """Representación JSON lista para la API o la consola."""
        return {
            "usd": self.usd,
            "eur": self.eur,
            "usd_bs": formatear_es(self.usd),
            "eur_bs": formatear_es(self.eur),
            "usd_exacta": formatear_es(self.usd, 8),
            "eur_exacta": formatear_es(self.eur, 8),
            "fecha_valor": self.fecha_valor,
            "fecha_valor_texto": self.fecha_valor_texto,
            "fuente": self.fuente,
            "obtenido_en": self.obtenido_en,
            "actualizado_texto": _formatear_fecha(self.obtenido_en),
        }


# ---------------------------------------------------------------------------
# Utilidades de formato / números
# ---------------------------------------------------------------------------


def formatear_es(valor: float, decimales: int = 2) -> str:
    """Formatea un número al estilo venezolano: 1.001,18602288."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def parsear_numero_ve(texto: str) -> float:
    """Convierte un número en formato venezolano (1.001,18) a float.

    Acepta tanto ``1.001,18602288`` como ``897,5383`` o ``897.5383``.
    La heurística para un único punto asume miles (formato del BCV, que
    usa coma como separador decimal).
    """
    limpio = re.sub(r"[^\d.,-]", "", texto or "")
    if not limpio:
        raise ValueError(f"Texto sin número: {texto!r}")

    negativo = limpio.startswith("-")
    limpio = limpio.lstrip("-")

    if "," in limpio:
        # Formato venezolano: el punto separa miles y la coma los decimales.
        limpio = limpio.replace(".", "").replace(",", ".")
    else:
        partes = limpio.split(".")
        if len(partes) > 2 or (
            len(partes) == 2 and len(partes[1]) == 3 and len(partes[0]) <= 3
        ):
            # "1.234.567" o "1.001" -> puntos de miles.
            limpio = "".join(partes)
        # Cualquier otro caso es punto decimal: "897.5383".

    try:
        valor = float(Decimal(limpio))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Número inválido: {texto!r}") from exc

    return -valor if negativo else valor


def _formatear_fecha(iso: str) -> str:
    if not iso:
        return ""
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y %H:%M:%S")
    except ValueError:
        return iso


# ---------------------------------------------------------------------------
# Descarga de la página
# ---------------------------------------------------------------------------


def _crear_sesion(reintentar: bool = True) -> requests.Session:
    sesion = requests.Session()
    sesion.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-VE,es;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
        }
    )
    if reintentar:
        reintentos = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=0.7,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )
        adaptador = HTTPAdapter(max_retries=reintentos)
        sesion.mount("https://", adaptador)
        sesion.mount("http://", adaptador)
    return sesion


def descargar_html(url: str = URL, timeout: int = TIMEOUT) -> str:
    """Descarga la página del BCV y devuelve su HTML.

    Intenta validar el certificado TLS y, si el BCV devuelve una cadena
    incompleta (caso habitual), reintenta sin validarlo. La verificación que
    funcione se recuerda para las siguientes llamadas.
    """
    global _VERIFICACION_TLS
    verificaciones = [_VERIFICACION_TLS] if _VERIFICACION_TLS is not None else [True, False]
    ultimo_error: Optional[Exception] = None

    for verificar in verificaciones:
        # La primera prueba de TLS va sin reintentos: un certificado inválido
        # no se arregla reintentando y solo añadiría espera.
        sesion = _crear_sesion(reintentar=not (verificar and _VERIFICACION_TLS is None))
        if not verificar:
            # Se conoce el problema de cadena TLS del BCV: no llenar stderr.
            import warnings

            warnings.simplefilter("ignore", InsecureRequestWarning)
        try:
            respuesta = sesion.get(url, timeout=timeout, verify=verificar)
            if respuesta.status_code >= 400:
                raise ScrapingError(
                    f"El BCV respondió con HTTP {respuesta.status_code}."
                )
            html = respuesta.text or ""
            if len(html) < 500:
                raise ScrapingError("La página del BCV llegó vacía o incompleta.")
            if not verificar and _VERIFICACION_TLS is None:
                LOGGER.warning(
                    "El certificado TLS del BCV no valida; se continúa sin "
                    "verificar la cadena (conexión cifrada)."
                )
            _VERIFICACION_TLS = verificar
            return html
        except requests.exceptions.SSLError as exc:
            ultimo_error = exc
            continue
        except requests.RequestException as exc:
            raise ScrapingError(f"No se pudo conectar con el BCV: {exc}") from exc

    raise ScrapingError(
        "No se pudo validar el certificado TLS del BCV. Revisa la conexión "
        "o usa verify=False de forma explícita."
    ) from ultimo_error


# ---------------------------------------------------------------------------
# Interpretación del HTML
# ---------------------------------------------------------------------------


def _texto_strong(soup: BeautifulSoup, html: str, div_id: str) -> Optional[str]:
    """Busca el valor dentro de ``div#<id>`` con respaldo por regex."""
    div = soup.find(id=div_id)
    if div is not None:
        strong = div.find("strong")
        if strong is not None:
            texto = strong.get_text(" ", strip=True)
            if re.search(r"\d", texto):
                return texto

    patron = re.compile(
        r'id=["\']' + re.escape(div_id) + r'["\'][\s\S]{0,2000}?<strong[^>]*>\s*([^<]+?)\s*</strong>',
        re.IGNORECASE,
    )
    coincidencia = patron.search(html)
    return coincidencia.group(1) if coincidencia else None


def _extraer_moneda(soup: BeautifulSoup, html: str, div_id: str, codigo: str) -> float:
    texto = _texto_strong(soup, html, div_id)
    if texto is None:
        raise ScrapingError(
            f"No se encontró el bloque de {codigo} (div id='{div_id}'). "
            "¿Cambió la estructura de la página del BCV?"
        )
    try:
        valor = parsear_numero_ve(texto)
    except ValueError as exc:
        raise ScrapingError(
            f"No se pudo interpretar el valor de {codigo}: {texto!r}"
        ) from exc
    if not 0 < valor < 1_000_000_000:
        raise ScrapingError(f"Valor fuera de rango para {codigo}: {valor!r}")
    return valor


def _extraer_fecha(soup: BeautifulSoup, html: str) -> tuple[Optional[str], Optional[str]]:
    """Devuelve (fecha ISO, texto visible) de la "Fecha Valor" del BCV."""
    span = soup.find(attrs={"property": "dc:date"})
    if span is None:
        span = soup.find(class_="date-display-single")

    fecha_iso: Optional[str] = None
    fecha_texto: Optional[str] = None

    if span is not None:
        contenido = str(span.get("content") or "")
        coincidencia = re.search(r"(\d{4}-\d{2}-\d{2})", contenido)
        if coincidencia:
            fecha_iso = coincidencia.group(1)
        texto = re.sub(r"\s+", " ", span.get_text(" ", strip=True)).strip()
        if texto:
            fecha_texto = texto

    if fecha_iso is None:
        coincidencia = re.search(
            r'Fecha Valor:[\s\S]{0,500}?content=["\'](\d{4}-\d{2}-\d{2})',
            html,
            re.IGNORECASE,
        )
        if coincidencia:
            fecha_iso = coincidencia.group(1)

    return fecha_iso, fecha_texto


def extraer_tasas(html: str, url: str = URL) -> Tasas:
    """Interpreta el HTML del BCV y devuelve las tasas de USD y EUR."""
    soup = BeautifulSoup(html, "html.parser")

    valores = {}
    for div_id, codigo in MONEDAS:
        valores[codigo] = _extraer_moneda(soup, html, div_id, codigo)

    fecha_iso, fecha_texto = _extraer_fecha(soup, html)
    obtenido_en = datetime.now(_zona_local()).isoformat(timespec="seconds")

    return Tasas(
        usd=valores["USD"],
        eur=valores["EUR"],
        fecha_valor=fecha_iso,
        fecha_valor_texto=fecha_texto,
        fuente=url,
        obtenido_en=obtenido_en,
    )


def obtener_tasas(url: str = URL, timeout: int = TIMEOUT) -> Tasas:
    """Descarga e interpreta las tasas oficiales del BCV."""
    html = descargar_html(url=url, timeout=timeout)
    return extraer_tasas(html, url=url)


# ---------------------------------------------------------------------------
# Render del HTML (compartido por el CLI y el servidor)
# ---------------------------------------------------------------------------


def contexto_html(
    tasas: Optional[Tasas] = None,
    *,
    stale: bool = False,
    error: Optional[str] = None,
    en_servidor: bool = True,
) -> dict:
    """Contexto de plantilla para ``templates/tasas.html``."""
    if tasas is None:
        return {
            "en_servidor": en_servidor,
            "stale": stale,
            "error": error or "No se pudieron obtener las tasas del BCV.",
            "usd_bs": "—",
            "eur_bs": "—",
            "usd_exacta": "—",
            "eur_exacta": "—",
            "fecha_valor": "",
            "fecha_valor_texto": "No disponible",
            "fuente": URL,
            "actualizado_texto": "",
        }
    return {
        **tasas.a_dict(),
        "en_servidor": en_servidor,
        "stale": stale,
        "error": error,
    }


def renderizar_html(
    tasas: Optional[Tasas],
    *,
    stale: bool = False,
    error: Optional[str] = None,
    en_servidor: bool = False,
) -> str:
    """Genera el HTML completo de la página de tasas."""
    entorno = Environment(
        loader=FileSystemLoader(str(BASE_DIR / "templates")),
        autoescape=select_autoescape(["html", "xml"]),
    )
    plantilla = entorno.get_template("tasas.html")
    contexto = contexto_html(
        tasas, stale=stale, error=error, en_servidor=en_servidor
    )
    return plantilla.render(**contexto)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scraper de las tasas oficiales USD/EUR del BCV."
    )
    parser.add_argument(
        "--html",
        metavar="RUTA",
        help="Guarda las tasas en un HTML autónomo (sin servidor).",
    )
    parser.add_argument("--url", default=URL, help=f"URL a consultar (por defecto {URL}).")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    try:
        tasas = obtener_tasas(url=args.url)
    except ScrapingError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.html:
        ruta = Path(args.html)
        ruta.write_text(renderizar_html(tasas), encoding="utf-8")
        print(f"HTML generado en {ruta}")
        print(json.dumps(tasas.a_dict(), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(tasas.a_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
