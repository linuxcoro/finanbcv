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
| `tasas.json` | Últimas tasas USD/EUR generadas por `bcv_scraper.py`. La app las descarga desde GitHub. |
| `tasas.html` | Ejemplo generado: página estática con las tasas del día. |
| `.github/workflows/actualizar-tasas.yml` | Workflow de GitHub Actions que regenera `tasas.json` cada hora y lo commitea. |

`index.html` (la app FinanBCV) muestra las tasas de USD y EUR desde el
`tasas.json` publicado en GitHub y tiene un botón **Actualizar**; ver la
última sección.

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
python3 bcv_scraper.py > tasas.json 2>/dev/null   # copia local (la app usa GitHub)
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

## Actualización automática (GitHub Actions)

El repositorio incluye `.github/workflows/actualizar-tasas.yml`, que **cada
hora** ejecuta el scraper y actualiza `tasas.json` dentro del mismo
repositorio:

1. Corre con `schedule` (`cron: '5 * * * *'`, UTC) y también a mano desde
   **Actions → Actualizar tasas BCV → Run workflow**.
2. Instala `requirements-tasas.txt`, ejecuta
   `python3 bcv_scraper.py > tasas.json` y valida el JSON.
3. Hace commit y push como `github-actions[bot]` solo si el archivo cambió
   (mensaje `chore: actualizar tasas BCV`).
4. Si el BCV falla, la ejecución queda en rojo y **no** se commitea: se
   conserva la última tasa buena.

Requiere **Settings → Actions → General → Workflow permissions → “Read and
write permissions”**. Los commits de `tasas.json` no recompilan el APK (su
workflow los ignora con `paths-ignore`).

En local el flujo sigue siendo manual (`python3 bcv_scraper.py > tasas.json`);
la automatización solo actúa cuando el proyecto está en GitHub.

## 2. Servidor con HTML + API

```bash
python3 bcv_server.py
# o bien:
# uvicorn bcv_server:app --host 0.0.0.0 --port 8000
```

Abre <http://127.0.0.1:8000> para ver la página con ambas tasas; se
actualiza sola cada 60 segundos consultando la API. La app FinanBCV está en
<http://127.0.0.1:8000/app> y su botón **Actualizar** descarga las tasas de
GitHub (el servidor ya no las regenera para la app).

### Endpoints

| Ruta | Descripción |
|------|-------------|
| `GET /` | Página HTML con las tasas (dólar y euro). |
| `GET /app` | App FinanBCV (`index.html`) servida desde el mismo origen. |
| `GET /tasas.json` | Archivo `tasas.json` regenerado por el scraper (sin caché). |
| `GET /api/tasas` | JSON con USD, EUR, fecha valor y metadatos. |
| `GET /api/tasas?refresh=true` | Igual, ignorando la caché. |
| `POST /api/actualizar` | Ejecuta `bcv_scraper.py`, regenera `tasas.json` y devuelve el JSON (la app ya no lo usa). |
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

La app muestra dos tarjetas, **dólar (USD)** y **euro (EUR)**, y un botón
**Actualizar**. Al cargar y al pulsar el botón:

1. Descarga `tasas.json` desde GitHub:
   <https://raw.githubusercontent.com/linuxcoro/finanbcv/main/tasas.json>
   (con `?t=…` para evitar la caché).
2. Si no hay red o la descarga falla, usa las últimas tasas guardadas en
   `localStorage` (`finanbcv_tasas`).

El workflow horario mantiene ese archivo al día, así que la app no necesita
servidor local ni que se regenere `tasas.json` a mano para actualizarse.

La tasa del dólar se coloca automáticamente en el campo **Tasa BCV (Bs/$)** de
la calculadora (sin pisar una tasa escrita a mano); las tarjetas del **dólar** y
del **euro** permiten aplicar su tasa exacta con un toque. Al elegir el euro, el
campo pasa a mostrarse como **Tasa BCV (Bs/€)**, el badge de la calculadora
indica `Tasa BCV · EUR` y todo el formulario cambia a euros: el monto se muestra
como **Monto Total (€ EUR)**, el prefijo de los campos y los cálculos en vivo
usan `€`, y el crédito registrado queda asociado a esa moneda. En **Créditos
Activos**, el historial de pagos y el comprobante de Pago Móvil cada crédito
conserva el símbolo con el que se registró (`$` o `€`). Una actualización
posterior de tasas conserva la moneda elegida (guardada en
`localStorage` como `finanbcv_moneda`).

### Servir la app con el servidor

Opcional, para desarrollo local:

```bash
python3 bcv_server.py
```

Abre <http://127.0.0.1:8000/app>. Para el modo estático:

```bash
python3 -m http.server 8000
# luego abre http://127.0.0.1:8000/index.html
```

> En el APK de Capacitor la app también descarga las tasas de GitHub; el
> `www/tasas.json` que copia el workflow es una foto de la compilación y ya no
> se usa para actualizar. El servidor habilita CORS para cualquier origen, así
> que también se puede consultar `GET /api/tasas` desde otra página.
