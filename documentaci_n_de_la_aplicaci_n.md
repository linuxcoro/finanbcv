# 📱 FinanBCV - Gestor de Ventas Financiadas a Tasa BCV

**FinanBCV** es una aplicación web progresiva y liviana (Single-Page Application) diseñada para comerciantes que venden productos en dólares y permiten financiamiento por cuotas calculadas a la tasa oficial del Banco Central de Venezuela (BCV). 

La aplicación permite llevar el control de abonos de clientes, calcular el monto de las cuotas en tiempo real, y generar comprobantes de Pago Móvil listos para compartir por WhatsApp o cualquier app de mensajería nativa.

---

## 🚀 Características Principales

* **Cálculo Automático a Tasa BCV:** Convierte el monto en dólares a bolívares según la tasa ingresada y divide el monto exacto en las cuotas acordadas.
* **Tasas BCV Integradas (USD y EUR):** la pantalla principal muestra la tasa oficial del dólar y del euro con su fecha valor y hora de actualización. El botón **Actualizar** relee `tasas.json` (o ejecuta el scraper si la app se sirve con `bcv_server.py`) y coloca la tasa del dólar en la calculadora sin pisar una tasa personalizada.
* **Integración Nativa de Pago Móvil:** Configura tus datos bancarios una sola vez (Banco, Cédula/RIF y Teléfono) y genera plantillas de cobro personalizadas con 1 clic, indicando la parte que corresponde pagar (por ejemplo, "Parte 2 de 3").
* **Comprobante al Instante:** al presionar **"Abonar Cuota"** se descuenta la parte pendiente, la tarjeta actualiza su progreso y se abre automáticamente el comprobante de Pago Móvil con la siguiente parte a pagar.
* **Historial de Pagos por Crédito:** cada tarjeta abre una ventana con todos los abonos de cuota del crédito, con fecha, número de parte y montos en dólares y bolívares, además del total abonado en cuotas.
* **Compartir Directo (Web Share API):** Envía la salida del Pago Móvil con el desglose de partes restantes directamente a WhatsApp, Telegram o SMS usando el menú nativo del dispositivo.
* **Modo Oscuro / Claro:** Alternador de interfaz de usuario con almacenamiento persistente en el navegador para ahorrar batería en pantallas OLED.
* **Persistencia Local (`localStorage`):** Guarda la lista de clientes, abonos y configuraciones directamente en el almacenamiento del dispositivo, sin requerir internet ni bases de datos externas.
* **Diseño Responsive / Mobile-First:** Interfaz moderna adaptada para teléfonos celulares y computadoras con Tailwind CSS.

---

## 🛠️ Arquitectura y Tecnologías Utilizadas

La aplicación está construida sobre una arquitectura limpia de **un solo archivo (Single-File App)** —`index.html`— para garantizar rapidez de carga y facilidad de empaquetado en APK:

* **HTML5:** Estructura semántica de la aplicación y modales interactivos.
* **Tailwind CSS (CDN):** Framework de utilidades CSS para el diseño responsive, soporte de modo oscuro por clases (`dark:`) y componentes visuales elegantes.
* **JavaScript (Vanilla ES6+):** 
  * Manejo del Estado (Clientes, Pagos, Ajustes).
  * `localStorage` para almacenamiento persistente.
  * `fetch` para leer `tasas.json` y para pedir la actualización al servidor BCV.
  * API Nativa `navigator.share` y `document.execCommand('copy')` para salida de mensajes.
  * Manipulación dinámica del DOM y lógica de cálculo financiero.
* **Lucide Icons (CDN):** Iconografía liviana vectorial.
* **Capacitor 6:** Empaquetado del contenido web como aplicación Android (usado por el workflow de CI para generar el APK).

---

## 🗂️ Estructura del Repositorio

| Archivo | Descripción |
|---------|-------------|
| `index.html` | Aplicación completa (SPA de un solo archivo). |
| `tasas.json` | Tasas oficiales USD/EUR que muestra la app (lo genera `bcv_scraper.py`). |
| `bcv_scraper.py` | Scraper de las tasas del BCV; escribe `tasas.json`. |
| `bcv_server.py` | Servidor local opcional: sirve la app y actualiza las tasas con `POST /api/actualizar`. |
| `templates/tasas.html` | Página de tasas del servidor (modo servidor y estático). |
| `README_tasas.md` | Guía del scraper, del servidor y de la integración con la app. |
| `documentaci_n_de_la_aplicaci_n.md` | Esta documentación. |
| `plan_de_mejoras.md` | Roadmap y bitácora de mejoras del proyecto. |
| `capacitor.config.json` | Configuración e identidad de la app para Capacitor. |
| `.github/workflows/build-apk.yml` | Workflow de GitHub Actions que compila el APK debug. |
| `.github/workflows/actualizar-tasas.yml` | Workflow de GitHub Actions que regenera `tasas.json` cada hora y lo commitea. |

---

## 📋 Estructura de Datos (JSON Schema Interno)

### Objeto Crédito (`credits`)
```json
{
  "id": 1700000000000,
  "clientName": "Juan Pérez (0412-1112233)",
  "totalUsd": 100.00,
  "bcvRate": 36.50,
  "totalInstallments": 2,
  "remainingInstallments": 1,
  "installmentUsd": 50.00,
  "createdAt": "8/11/2026",
  "payments": [
    {
      "id": 1700000001000,
      "paidAt": "2026-11-08T13:30:00.000Z",
      "part": 1,
      "totalParts": 2,
      "amountUsd": 50.00,
      "amountBs": 1825.00,
      "rate": 36.50
    }
  ]
}
```

> Nota: los créditos guardados por versiones anteriores pueden conservar `initialPercent`; la app ya no lo usa ni lo muestra (mantiene el monto por cuota que se calculó al registrarlos).

### Objeto Ajustes Pago Móvil (`settings`)
```json
{
  "bank": "Banesco (0134)",
  "id": "V-12345678",
  "phone": "0414-1234567"
}
```

---

## ⚙️ Guía de Uso del Sistema

1. **Tasas del BCV:**
   * La sección **Tasas del BCV** muestra el dólar (USD) y el euro (EUR) con la fecha valor y la hora de actualización.
   * Pulsa **Actualizar** para releer `tasas.json`; si la app se sirve con `bcv_server.py`, el botón además ejecuta el scraper y regenera el archivo.
   * La tasa del dólar se coloca sola en la calculadora; toca la tarjeta **USD** para reaplicarla si escribiste una tasa a mano.
2. **Configuración Inicial:**
   * Haz clic en el icono del código QR / Ajustes en la barra superior.
   * Ingresa tu Banco, Cédula/RIF y número de teléfono de Pago Móvil.
3. **Registrar Venta:**
   * Introduce el nombre y teléfono del cliente.
   * Ingresa el total en USD y la tasa BCV del día (se rellena con la del dólar).
   * Define el número de partes.
   * Presiona **"Registrar Crédito"**.
4. **Abonar y Compartir:**
   * Cuando el cliente realice un pago, presiona **"Abonar Cuota"** en su tarjeta.
   * El sistema descontará una parte restante, actualizará la tarjeta (total y cuota) y abrirá el comprobante con la siguiente parte a pagar (por ejemplo, "Parte 2 de 3").
   * Para consultar el detalle, pulsa **"Historial de pagos (N)"** en la tarjeta: verás cada abono con fecha, número de parte y montos en $ y Bs.
   * Presiona **"Copiar Texto"** o **"Compartir App"** para enviarlo por WhatsApp u otra aplicación.

### Actualizar `tasas.json` a mano

```bash
python3 bcv_scraper.py > tasas.json 2>/dev/null
```

La app vuelve a leerlo al pulsar **Actualizar**. Si la sirves con
`python3 bcv_server.py` (en <http://127.0.0.1:8000/app>), el botón ejecuta el
scraper directamente. Guía completa en [`README_tasas.md`](README_tasas.md).

> En GitHub, el workflow **Actualizar tasas BCV**
> (`.github/workflows/actualizar-tasas.yml`) ejecuta ese mismo comando **cada
> hora**, valida el JSON y hace commit de `tasas.json` como
> `github-actions[bot]`; si el BCV falla, se conserva la última tasa buena. En
> local el comando sigue siendo manual.

---

## 📦 Compilar como Aplicación Móvil (APK)

El repositorio ya incluye el workflow de **GitHub Actions** y la configuración de **Capacitor** necesarios para generar un APK de depuración (*debug*) sin instalar Android Studio ni el SDK de Android en tu computadora.

### Requisitos

* Una cuenta de GitHub (gratuita).
* El proyecto subido al repositorio `finanbcv` con estos archivos, ya incluidos en el repositorio:
  * `index.html` (la aplicación).
  * `capacitor.config.json` (identidad de la app).
  * `.github/workflows/build-apk.yml` (workflow de compilación).

### Subir el proyecto a GitHub

```bash
git remote add origin https://github.com/<usuario>/finanbcv.git
git push -u origin main
```

### Generar el APK

1. El workflow **Build APK** se dispara automáticamente con cada *push* a la rama `main` (también se puede lanzar manualmente desde **Actions → Build APK → Run workflow**).
2. El workflow instala Node 20, Java 17 (Temurin), el SDK de Android y Capacitor 6; copia `index.html` a `www/`, añade la plataforma Android y ejecuta `./gradlew assembleDebug`.
3. Al terminar, abre la ejecución del workflow en la pestaña **Actions** y descarga el *artifact* **`FinanBCV-apk`**, que contiene `app-debug.apk`.

### Instalar el APK

1. Descarga y descomprime el *artifact* (contiene `app-debug.apk`) y cópialo al teléfono, o descárgalo directamente desde el navegador del teléfono.
2. Habilita la instalación desde **fuentes desconocidas** para el explorador de archivos o el navegador: *Ajustes → Seguridad → Instalar apps desconocidas*.
3. Toca `app-debug.apk` y confirma la instalación.
   * Alternativa por cable USB con [Android Debug Bridge](https://developer.android.com/tools/adb): `adb install -r app-debug.apk`.

> ⚠️ Es un APK **debug**: sirve para probar la aplicación, no está firmado para producción ni publicado en Play Store. Para distribuirlo formalmente hay que firmarlo con un *keystore* propio.

### Limitaciones

* **Requiere internet en el primer arranque:** Tailwind CSS y Lucide Icons se cargan por CDN; sin conexión no hay estilos ni iconos.
* **La app necesita un servidor para leer las tasas:** `index.html` obtiene USD/EUR de `tasas.json` con `fetch`, así que debe abrirse por HTTP (`python3 bcv_server.py` en `/app` o `python3 -m http.server`) o dentro del APK. Abierta con doble clic (`file://`) muestra el aviso y hay que escribir la tasa a mano; las últimas tasas también quedan en `localStorage` (`finanbcv_tasas`).
* En el APK las tasas son la copia de `tasas.json` incluida al compilar (`www/tasas.json`); el botón **Actualizar** relee esa copia, no consulta el BCV.
* Los datos (`finanbcv_credits`, `finanbcv_settings`, `finanbcv_theme`) se guardan en el `localStorage` del WebView del teléfono; no hay sincronización entre dispositivos.
* El historial de pagos se guarda dentro de `finanbcv_credits` (campo `payments`). Los créditos creados antes de esta versión no tienen detalle de pagos: su historial muestra un resumen "pagos anteriores sin detalle".
* El workflow copia `index.html` y `tasas.json` a `www/`; la carpeta generada no se versiona ni se edita a mano.

### Plan B si falla el build de Capacitor

Si el build de Android fallara en CI, el workflow puede sustituirse por uno que publique como *artifact* un `.zip` con `index.html`; la app sigue funcionando como web (o se puede empaquetar manualmente con Capacitor).

---

## 🗺️ Hoja de Ruta

El roadmap y la bitácora de mejoras del proyecto se mantienen en [`plan_de_mejoras.md`](plan_de_mejoras.md).
