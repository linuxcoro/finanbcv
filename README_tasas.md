# Tasas BCV · Scraper + página HTML + API

Código nuevo para consultar las tasas oficiales del **dólar (USD)** y del
**euro (EUR)** publicadas por el Banco Central de Venezuela en
<https://www.bcv.org.ve/glosario/cambio-oficial>, mostrarlas en una página
HTML y exponerlas como API JSON.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `bcv_scraper.py` | Descarga e interpreta la página del BCV. También genera un HTML autónomo. |
| `bcv_server.py` | Servidor FastAPI: página HTML (`/`), app FinanBCV (`/app`), `tasas.json` y API JSON. |
| `templates/tasas.html` | Plantilla de la página de tasas (modo servidor y modo estático). |
| `requirements-tasas.txt` | Dependencias de Python. |
| `test_bcv_scraper.py` | Pruebas sin red del parser y del formato de números. |
| `tasas.json` | Últimas tasas USD/EUR generadas por `bcv_scraper.py`. Lo consume `index.html`. |
| `tasas.html` | Ejemplo generado: página estática con las tasas del día. |

`index.html` (la app FinanBCV) muestra las tasas de USD y EUR desde
`tasas.json` y tiene un botón **Actualizar**; ver la última sección.

## Instalación

```bash
cd /home/linuxoro/programas/finanbcv
pip install -r requirements-tasas.txt
```

(En el sistema ya están instaladas `requests`, `beautifulsoup4`, `fastapi`,
`uvicorn` y `jinja2`.)

## 1. Scraper por consola

```bash
python3 bcv_scraper.py                 # imprime el JSON con USD y EUR
python3 bcv_scraper.py --html tasas.html
python3 bcv_scraper.py > tasas.json 2>/dev/null   # archivo que consume index.html
```

Salida:

```json
{
  "usd": 897.5383,
  "eur": 1001.18602288,
  "usd_bs": "897,54",
  "eur_bs": "1.001,19",
  "usd_exacta": "897,53830000",
  "eur_exacta": "1.001,18602288",
  "fecha_valor": "2026-11-09",
  "fecha_valor_texto": "Lunes, 09 Noviembre 2026",
  "fuente": "https://www.bcv.org.ve/glosario/cambio-oficial",
  "obtenido_en": "2026-11-08T14:55:47-04:00",
  "actualizado_texto": "08/11/2026 14:55:47"
}
```

El HTML generado con `--html` es autónomo: se abre directamente en el
navegador sin necesidad de servidor.

## 2. Servidor con HTML + API

```bash
python3 bcv_server.py
# o bien:
# uvicorn bcv_server:app --host 0.0.0.0 --port 8000
```

Abre <http://127.0.0.1:8000> para ver la página con ambas tasas; se
actualiza sola cada 60 segundos consultando la API. La app FinanBCV está en
<http://127.0.0.1:8000/app> y su botón **Actualizar** regenera `tasas.json`.

### Endpoints

| Ruta | Descripción |
|------|-------------|
| `GET /` | Página HTML con las tasas (dólar y euro). |
| `GET /app` | App FinanBCV (`index.html`) servida desde el mismo origen. |
| `GET /tasas.json` | Archivo `tasas.json` regenerado por el scraper (sin caché). |
| `GET /api/tasas` | JSON con USD, EUR, fecha valor y metadatos. |
| `GET /api/tasas?refresh=true` | Igual, ignorando la caché. |
| `POST /api/actualizar` | Ejecuta `bcv_scraper.py`, regenera `tasas.json` y devuelve el JSON. |
| `GET /health` | Estado del servicio (no consulta el BCV). |
| `GET /docs` | Documentación interactiva (Swagger UI). |

Ejemplo:

```bash
curl http://127.0.0.1:8000/api/tasas
```

```json
{
  "ok": true,
  "usd": 897.5383,
  "eur": 1001.18602288,
  "usd_bs": "897,54",
  "eur_bs": "1.001,19",
  "fecha_valor": "2026-11-09",
  "fuente": "https://www.bcv.org.ve/glosario/cambio-oficial",
  "cache": { "ttl_segundos": 300, "desde_cache": false, "stale": false }
}
```

### Variables de entorno

| Variable | Defecto | Uso |
|----------|---------|-----|
| `BCV_CACHE_TTL` | `300` | Segundos que se reutiliza una consulta (mínimo 30). |
| `BCV_HOST` | `127.0.0.1` | Host de escucha (`0.0.0.0` para red local). |
| `BCV_PORT` | `8000` | Puerto del servidor. |

## Cómo funciona el scraping

- Descarga `div#dolar` y `div#euro`, toma el `<strong class="strong-tb">`
  y convierte el formato venezolano (`1.001,18602288` → `1001.18602288`).
- Lee la **Fecha Valor** del atributo `content` (`dc:date`) y su texto visible.
- Si el HTML cambia, hay un respaldo por expresión regular; si aun así no
  encuentra un valor, lanza `ScrapingError` con un mensaje claro.
- El certificado TLS de `bcv.org.ve` suele estar incompleto: se intenta
  validar y, si falla, se repite la petición sin validar la cadena
  (conexión cifrada). Se avisa por log.
- El servidor guarda la última consulta: si el BCV falla, sirve la tasa
  anterior con `"stale": true` en lugar de devolver un error.

## Pruebas

```bash
python3 -m unittest test_bcv_scraper -v
```

Las pruebas no usan red: validan parseo de números, formato venezolano,
extracción de USD/EUR, fecha valor y el contexto de la plantilla.

## Tasas en la app (`index.html`)

La app muestra una tarjeta con el **dólar (USD)** y el **euro (EUR)** y un
botón **Actualizar**. Al cargar y al pulsar el botón:

1. Si la app se sirve con `bcv_server.py`, el botón hace `POST /api/actualizar`:
   el servidor ejecuta el scraper, regenera `tasas.json` y devuelve las tasas.
2. Si se sirve con un servidor estático (`python3 -m http.server`), el botón
   relee `tasas.json` (con `?t=…` para evitar la caché). Para regenerarlo:

   ```bash
   python3 bcv_scraper.py > tasas.json 2>/dev/null
   ```

3. Si no hay red o `tasas.json` no está disponible, se usan las últimas tasas
   guardadas en `localStorage` (`finanbcv_tasas`).

La tasa del dólar se coloca automáticamente en el campo **Tasa BCV (Bs/$)** de
la calculadora (sin pisar una tasa escrita a mano); la tarjeta del dólar también
permite aplicarla con un toque. La del euro se muestra como referencia.

### Servir la app con el servidor

```bash
python3 bcv_server.py
```

Abre <http://127.0.0.1:8000/app>. Para el modo estático:

```bash
python3 -m http.server 8000
# luego abre http://127.0.0.1:8000/index.html
```

> En el APK de Capacitor el JSON se lee del paquete (`www/tasas.json`), por lo
> que las tasas son una foto del momento de la compilación; el botón
> **Actualizar** solo puede releer ese archivo. El servidor habilita CORS para
> cualquier origen, así que también se puede consultar `GET /api/tasas` desde
> otra página.
