# 📱 FinanBCV - Gestor de Ventas Financiadas a Tasa BCV

**FinanBCV** es una aplicación web progresiva y liviana (Single-Page Application) diseñada para comerciantes que venden productos en dólares y permiten financiamiento por cuotas calculadas a la tasa oficial del Banco Central de Venezuela (BCV). 

La aplicación permite llevar el control de abonos de clientes, calcular el monto de las cuotas en tiempo real, y generar comprobantes de Pago Móvil listos para compartir por WhatsApp o cualquier app de mensajería nativa.

---

## 🚀 Características Principales

* **Cálculo Automático a Tasa BCV:** Convierte el monto (en dólares o en euros, según la tasa elegida) a bolívares según la tasa ingresada y divide el monto exacto en las cuotas acordadas.
* **Tasas BCV Integradas (USD y EUR):** la pantalla principal muestra la tasa oficial del dólar y del euro con su fecha valor y hora de actualización. El botón **Actualizar** descarga `tasas.json` por la API de GitHub (repo privado + PAT de solo lectura) y coloca por defecto la tasa del dólar en la calculadora sin pisar una tasa personalizada. Las tarjetas **USD** y **EUR** son seleccionables: al tocar cualquiera se aplica su tasa exacta al campo **Tasa BCV**, que ajusta su etiqueta a `Bs/$` o `Bs/€`.
* **Moneda activa en toda la app:** al elegir la tasa del dólar o la del euro, la calculadora cambia el símbolo de los montos (`$` o `€`), la etiqueta a **Monto Total ($ USD)** o **Monto Total (€ EUR)**, el resumen en vivo y el badge del formulario (`Tasa BCV · EUR`). Cada crédito guarda la moneda con la que se registró, así que **Créditos Activos**, el historial de pagos y el comprobante de Pago Móvil muestran el símbolo correcto aunque luego se cambie la tasa. La moneda elegida se recuerda en `localStorage` (`finanbcv_moneda`) y una actualización de tasas la conserva.
* **Integración Nativa de Pago Móvil:** Configura tus datos bancarios una sola vez (Banco, Cédula/RIF y Teléfono) y genera plantillas de cobro personalizadas con 1 clic, indicando la parte que corresponde pagar (por ejemplo, "Parte 2 de 3").
* **Comprobante al Instante:** al presionar **"Abonar Cuota"** se descuenta la parte pendiente, la tarjeta actualiza su progreso y se abre automáticamente el comprobante de Pago Móvil con la siguiente parte a pagar.
* **Historial de Pagos por Crédito:** cada tarjeta muestra directamente todos los abonos de cuota del crédito, con fecha, número de parte y montos en dólares y bolívares, además del total abonado en cuotas.
* **Compartir Directo (selector nativo de apps):** el botón **Pago Móvil** abre el menú de compartir del dispositivo (WhatsApp, Telegram, Instagram, SMS, correo o cualquier red social instalada). En el APK usa el plugin `@capacitor/share` y en el navegador la Web Share API; si no hay selector disponible, muestra el texto para copiarlo.
* **Anuncios AdMob (solo en el APK):** banner adaptativo en la parte inferior y anuncios interstitial en cortes naturales (al registrar un crédito o al cerrar el comprobante de abono), con consentimiento UMP y anuncios de prueba por defecto. En el navegador la monetización queda desactivada.
* **Modo Oscuro / Claro:** Alternador de interfaz de usuario con almacenamiento persistente en el navegador para ahorrar batería en pantallas OLED.
* **Persistencia Local (`localStorage`):** Guarda la lista de clientes, abonos y configuraciones directamente en el almacenamiento del dispositivo, sin requerir internet ni bases de datos externas.
* **Respaldo y restauración:** desde **Ajustes → Respaldo y restauración** se genera un texto JSON con los créditos, los datos de Pago Móvil y el tema; se puede copiar, compartir por WhatsApp/correo y restaurar en el mismo u otro teléfono (útil antes de cambiar de versión o de dispositivo).
* **Diseño Responsive / Mobile-First:** Interfaz moderna adaptada para teléfonos celulares y computadoras con Tailwind CSS.

---

## 🛠️ Arquitectura y Tecnologías Utilizadas

La aplicación está construida sobre una arquitectura limpia de **un solo archivo (Single-File App)** —`index.html`— para garantizar rapidez de carga y facilidad de empaquetado en APK:

* **HTML5:** Estructura semántica de la aplicación y modales interactivos.
* **Tailwind CSS (CDN):** Framework de utilidades CSS para el diseño responsive, soporte de modo oscuro por clases (`dark:`) y componentes visuales elegantes.
* **JavaScript (Vanilla ES6+):** 
  * Manejo del Estado (Clientes, Pagos, Ajustes).
  * `localStorage` para almacenamiento persistente.
  * `fetch` para descargar las tasas (`tasas.json`) desde GitHub y para la actualización manual.
  * API de compartir: plugin `@capacitor/share` en el APK, `navigator.share` en navegadores compatibles y `document.execCommand('copy')` como respaldo.
  * Manipulación dinámica del DOM y lógica de cálculo financiero.
* **Lucide Icons (CDN):** Iconografía liviana vectorial.
* **Capacitor 8:** Empaquetado del contenido web como aplicación Android y acceso a funciones nativas: `@capacitor/share` para el selector nativo de compartir y `@capacitor-community/admob` para los anuncios (ambos usados por el workflow de CI para generar el APK).

---

## 🗂️ Estructura del Repositorio

| Archivo | Descripción |
|---------|-------------|
| `index.html` | Aplicación completa (SPA de un solo archivo). |
| `tasas.json` | Ya no se versiona en este repositorio: la app las descarga de [`linuxcoro/bcv_scraper`](https://github.com/linuxcoro/bcv_scraper) por la API de GitHub con un PAT de solo lectura. |
| `bcv_server.py` | Servidor local opcional: sirve la app y actualiza las tasas con `POST /api/actualizar`. |
| `templates/tasas.html` | Página de tasas del servidor (modo servidor y estático). |
| `README_tasas.md` | Guía del scraper, del servidor y de la integración con la app. |
| `documentaci_n_de_la_aplicaci_n.md` | Esta documentación. |
| `plan_de_mejoras.md` | Roadmap y bitácora de mejoras del proyecto. |
| `capacitor.config.json` | Configuración e identidad de la app para Capacitor. |
| `ads.config.json` | IDs de AdMob (App ID + unidades de banner e interstitial) y modo prueba/real. |
| `scripts/admob-build-config.mjs` | Script del CI: genera `www/ads-config.js` y parchea el proyecto Android generado (`AndroidManifest.xml` y `strings.xml`) con el App ID de AdMob. |
| `scripts/patch-android-version.mjs` | Script del CI: ajusta `versionCode` y `versionName` del proyecto Android generado (obligatorio para subir AAB a Play). |
| `scripts/inject-rates-token.mjs` | Script del CI: inyecta el PAT de solo lectura (`BCV_TASAS_PAT`) en `www/index.html`; el repo conserva el marcador `__RATES_PAT__`. |
| `.github/workflows/build-apk.yml` | Workflow de GitHub Actions que compila el **APK debug** con anuncios de prueba. |
| `.github/workflows/build-release.yml` | Workflow manual que compila el **AAB firmado** para Google Play y un **APK release** firmado con la clave de carga. |

---

## 📋 Estructura de Datos (JSON Schema Interno)

### Objeto Crédito (`credits`)
```json
{
  "id": 1700000000000,
  "clientName": "Juan Pérez (0412-1112233)",
  "totalUsd": 100.00,
  "bcvRate": 40.10,
  "currency": "eur",
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
      "amountBs": 2005.00,
      "rate": 40.10
    }
  ]
}
```

> Nota: `currency` (`"usd"` o `"eur"`) indica la moneda de la tasa y de los montos del crédito; los nombres `totalUsd` e `installmentUsd` se conservan por compatibilidad, pero guardan el monto en esa moneda. Los créditos guardados por versiones anteriores no tienen `currency`: la app los asume en dólares (`usd`) y no altera sus montos. Los abonos heredan la moneda de su crédito.

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
   * Pulsa **Actualizar** para descargar las tasas por la API de GitHub (repo `linuxcoro/bcv_scraper` + PAT de solo lectura); si no hay conexión se usan las últimas guardadas.
   * La tasa del dólar se coloca sola en la calculadora; toca la tarjeta **USD** o **EUR** para aplicar esa tasa exacta. El campo **Tasa BCV** cambia su etiqueta y el formulario completo cambia de moneda: el monto pasa a **Monto Total ($ USD)** o **Monto Total (€ EUR)**, el prefijo del campo y los cálculos en vivo usan `$` o `€`, y el badge muestra `Tasa BCV · EUR` cuando corresponde. Una tasa escrita a mano no se sobrescribe al actualizar y conserva la moneda elegida.
2. **Configuración Inicial:**
   * Haz clic en el icono del código QR / Ajustes en la barra superior.
   * Ingresa tu Banco, Cédula/RIF y número de teléfono de Pago Móvil.
3. **Registrar Venta:**
   * Introduce el nombre y teléfono del cliente.
   * Ingresa el monto en la moneda elegida (`$ USD` o `€ EUR`) y la tasa BCV del día (se rellena con la del dólar o con la del euro si tocaste su tarjeta).
   * Define el número de partes.
   * Presiona **"Registrar Crédito"**: el crédito queda asociado a la moneda de la tasa usada y su tarjeta muestra los montos con ese símbolo (`$` o `€`).
4. **Abonar y Compartir:**
   * Cuando el cliente realice un pago, presiona **"Abonar Cuota"** en su tarjeta.
   * El sistema descontará una parte restante, actualizará la tarjeta (total y cuota) y abrirá el comprobante con la siguiente parte a pagar (por ejemplo, "Parte 2 de 3").
   * El **historial de pagos** aparece directamente al final de cada tarjeta: cada abono con fecha, número de parte y montos en la moneda del crédito (`$` o `€`) y en bolívares, además del total abonado. Se actualiza solo al abonar.
   * Presiona **"Pago Móvil"** para abrir el selector de apps y compartir el comprobante por WhatsApp, Telegram o cualquier red social. Si el selector no está disponible, se abre una ventana con el texto, los botones **"Copiar Texto"** y **"Compartir en redes"**.

### Actualizar `tasas.json` a mano

```bash
python3 bcv_scraper.py > tasas.json 2>/dev/null
```

Este comando solo actualiza la copia local (útil para el servidor o para
commitear). La app **no** lee ese archivo local: al pulsar **Actualizar**
descarga el `tasas.json` por la API de GitHub (con el PAT inyectado en el
APK), que el workflow horario regenera. Guía completa en
[`README_tasas.md`](README_tasas.md).

> El APK necesita el secreto `BCV_TASAS_PAT` (PAT fine-grained con Contents:
> Read-only sobre `linuxcoro/bcv_scraper`). Sin él,
> `scripts/inject-rates-token.mjs` falla y el build se detiene.

> No se usa `GITHUB_TOKEN`: GitHub reserva el prefijo `GITHUB_` y el token
> automático no accede a `bcv_scraper` ni sobrevive al job.

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
  * `scripts/admob-build-config.mjs` (configuración de AdMob para el APK).
  * `scripts/patch-android-version.mjs` (versionCode/versionName del AAB).
  * `.github/workflows/build-apk.yml` (workflow del APK debug).
  * `.github/workflows/build-release.yml` (workflow del AAB/APK release firmado).

### Subir el proyecto a GitHub

```bash
git remote add origin https://github.com/<usuario>/finanbcv.git
git push -u origin main
```

### Generar el APK

1. El workflow **Build APK** se dispara automáticamente con cada *push* a la rama `main` (también se puede lanzar manualmente desde **Actions → Build APK → Run workflow**).
2. El workflow configura Node 22, Java 21 (Temurin) y Capacitor 8 con los plugins `@capacitor/share` y `@capacitor-community/admob`, verifica el SDK de Android 36 (`android-36` y `build-tools/36.0.0`) preinstalado en el runner, copia `index.html` a `www/`, genera `www/ads-config.js`, añade la plataforma Android, configura AdMob en el manifest y ejecuta `./gradlew assembleDebug`.
3. Antes de subir el artifact, el workflow verifica dentro del APK que existan el meta-data de AdMob, el plugin en `capacitor.plugins.json` y `ads-config.js`.
4. Al terminar, abre la ejecución del workflow en la pestaña **Actions** y descarga el *artifact* **`FinanBCV-apk`**, que contiene `app-debug.apk`.

### Instalar el APK

1. Descarga y descomprime el *artifact* (contiene `app-debug.apk`) y cópialo al teléfono, o descárgalo directamente desde el navegador del teléfono.
2. Habilita la instalación desde **fuentes desconocidas** para el explorador de archivos o el navegador: *Ajustes → Seguridad → Instalar apps desconocidas*.
3. Toca `app-debug.apk` y confirma la instalación.
   * Alternativa por cable USB con [Android Debug Bridge](https://developer.android.com/tools/adb): `adb install -r app-debug.apk`.

> ⚠️ Es un APK **debug**: sirve para probar la aplicación, no está firmado para producción ni publicado en Play Store. Además, **Google Play Protect puede bloquearlo** por venir de fuera de Play (no es un fallo de la app): desactiva temporalmente *Play Store → perfil → Play Protect → ⚙️ → Analizar apps con Play Protect*, instala y vuelve a activarlo; o instálalo por `adb install -r app-debug.apk`. Para una distribución estable usa el APK/AAB firmado con la clave de carga (ver **Firma release, AAB y prueba interna en Play**).

### Limitaciones

* **Requiere internet:** Tailwind CSS y Lucide Icons se cargan por CDN y las tasas se descargan de GitHub; sin conexión no hay estilos ni iconos y se muestran las últimas tasas guardadas en `localStorage`.
* **Las tasas vienen de GitHub:** `index.html` consulta la API de contenidos de `linuxcoro/bcv_scraper` con un PAT de solo lectura (inyectado al compilar el APK). No necesita servidor local; sin token (por ejemplo, abierta desde `file://` o desde el repo público) usa las últimas tasas guardadas en `localStorage` (`finanbcv_tasas`).
* En el APK las tasas se descargan de la API al abrir la app y al pulsar **Actualizar**; el `www/tasas.json` que copia el workflow ya no se usa para actualizar.
* El PAT va dentro del APK y se puede extraer. No publiques la app en Play Store con ese token: antes de publicarla, deja el JSON público o usa un intermediario que guarde el token en el servidor.
* Los datos (`finanbcv_credits`, `finanbcv_settings`, `finanbcv_theme`) se guardan en el `localStorage` del WebView del teléfono; no hay sincronización entre dispositivos. La moneda elegida en la calculadora se guarda aparte en `finanbcv_moneda` (`usd` o `eur`).
* Los respaldos incluyen el campo `currency` de cada crédito; al restaurar un respaldo antiguo (sin ese campo) los créditos se completan como `usd`.
* El historial de pagos se guarda dentro de `finanbcv_credits` (campo `payments`) y se muestra directamente en cada tarjeta. Los créditos creados antes de esta versión no tienen detalle de pagos: su historial muestra un resumen "pagos anteriores sin detalle".
* **Anuncios:** el banner y los interstitial necesitan internet y Google Play Services; si faltan, la app funciona igual, sin anuncios. Un APK instalado a mano **no genera ingresos**: AdMob solo sirve anuncios reales cuando la app está publicada en Google Play y verificada (ver la sección de monetización).
* El workflow copia `index.html` a `www/` y genera `www/ads-config.js`; la carpeta generada no se versiona ni se edita a mano.

### Plan B si falla el build de Capacitor

Si el build de Android fallara en CI, el workflow puede sustituirse por uno que publique como *artifact* un `.zip` con `index.html`; la app sigue funcionando como web (o se puede empaquetar manualmente con Capacitor).

---

## 🔐 Firma release, AAB y prueba interna en Play

El workflow manual **Build release (AAB + APK firmado)** compila con una clave de carga propia: así las actualizaciones del APK ya no fallan por firmas distintas (cada build debug usa una clave nueva) y el AAB se puede subir a Google Play.

### 1. Configurar los secrets de firma

Genera una clave de carga (una sola vez) y guárdala fuera del repositorio:

```bash
keytool -genkeypair -v -keystore finanbcv-upload.jks -alias finanbcv \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=FinanBCV, O=FinanBCV, C=VE"
base64 -w0 finanbcv-upload.jks > finanbcv-upload.jks.b64
```

En **GitHub → Settings → Secrets and variables → Actions → New repository secret** crea:

| Secret | Valor |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | Contenido de `finanbcv-upload.jks.b64` (una sola línea) |
| `ANDROID_KEYSTORE_PASSWORD` | Contraseña del keystore |
| `ANDROID_KEY_ALIAS` | `finanbcv` |
| `ANDROID_KEY_PASSWORD` | Contraseña de la clave (puede ser la misma) |

> ⚠️ El `.jks` y sus contraseñas **nunca** se suben al repositorio (`.gitignore` excluye `.release/`, `*.jks` y `key.properties`). Guarda una copia de seguridad: si pierdes la clave de carga, hay que pedir su restablecimiento en Play Console.

### 2. Generar el AAB y el APK release

1. **Actions → Build release (AAB + APK firmado) → Run workflow**.
2. El workflow calcula el **versionCode** solo (`run_number * 100 + intento`, siempre creciente), compila `bundleRelease` y `assembleRelease`, firma el AAB con `jarsigner` (clave de carga) y el APK con `zipalign` + `apksigner` usando la misma clave.
3. Descarga el artifact **`FinanBCV-release`**:
   * `app-release.aab` → para subir a Google Play.
   * `app-release.apk` → para instalar/actualizar directamente en el teléfono (misma firma en cada build).

### 3. Publicar en prueba interna de Play

1. En [Play Console](https://play.google.com/console), crea la app (`com.finanbcv.app`) y completa *App content*: política de privacidad, **Data safety**, declaración de anuncios, clasificación de contenido y público objetivo.
2. Ve a **Prueba → Prueba interna → Crear nueva versión** y sube `app-release.aab` (Play App Signing se activa en la primera subida).
3. Añade tu cuenta de Google como tester, publica la versión y abre el enlace de prueba: la app se instala **desde Play Store**, sin el bloqueo de Play Protect.
4. Cuando quieras monetizar de verdad, sube las mismas versiones a Producción (la cuenta personal exige antes 12 testers durante 14 días) y verifica la app en AdMob.

## 💾 Respaldo y restauración de datos

Los créditos viven en el `localStorage` del WebView, así que **se pierden al desinstalar o cambiar de teléfono**. Para evitarlo:

1. **Ajustes → Respaldo y restauración**.
2. **Generar y copiar**: crea un texto JSON con todos los créditos, los datos de Pago Móvil y el tema, y lo copia al portapapeles.
3. **Compartir**: abre el selector nativo (WhatsApp, Telegram, correo, Notas…) para guardar el respaldo fuera del teléfono.
4. **Restaurar desde el texto**: pega un respaldo, confirma y la app reemplaza los datos actuales (créditos, ajustes y tema) y refresca la interfaz.

> Consejo: genera un respaldo antes de cada cambio de versión o de teléfono. El respaldo no incluye las tasas del BCV (se descargan de nuevo).

---

## 💰 Monetización con AdMob

La app integra AdMob con el plugin comunitario `@capacitor-community/admob` (Google Mobile Ads SDK). La lógica vive en `index.html` (módulo `window.Ads`) y solo se activa cuando la página corre dentro del APK; en el navegador no hace nada.

### Formatos y ubicación

* **Banner adaptativo** (`ADAPTIVE_BANNER`) anclado abajo, visible solo en la pantalla principal. Se oculta mientras hay un modal abierto (Ajustes, Respaldo o Compartir) para no tapar botones, y se reanuda al cerrarlo. El alto real que informa AdMob se reserva con la variable CSS `--admob-banner-h`, así no tapa la última tarjeta ni el toast.
* **Interstitial** en dos cortes naturales: al registrar un crédito y al cerrar el comprobante después de abonar una cuota. Nunca aparece encima de un modal ni al abrir la app; hay un límite de **1 cada 3 minutos** y se precarga para no hacer esperar.
* **Consentimiento (UMP):** al iniciar se consulta el estado de consentimiento; si es obligatorio se muestra el formulario de Google y, si la persona no autoriza anuncios, no se solicita ninguno. Cuando UMP exige un punto de acceso de privacidad, aparece el botón **Privacidad y anuncios** en Ajustes.
* **Sin anuncios en el comprobante:** el banner se oculta antes de abrir el modal de Pago Móvil y el interstitial se difiere hasta que se cierra, para evitar clics accidentales.

### Anuncios de prueba vs. anuncios reales

* Por defecto el build usa los **IDs de prueba de Google** (`ca-app-pub-3940256099942544~...`), que nunca generan tráfico inválido ni ingresos. Sirven para verificar que todo funciona.
* **Forma recomendada (versionada):** edita `ads.config.json` en la raíz con tus IDs reales y `"testMode": false`, haz commit y el siguiente build (debug o release) usará anuncios reales:

```json
{
    "testMode": false,
    "appId": "ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX",
    "bannerId": "ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX",
    "interstitialId": "ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX"
}
```

* **Alternativa sin tocar el repo:** define en **Settings → Secrets and variables → Actions → Variables** `ADMOB_APP_ID`, `ADMOB_BANNER_ID`, `ADMOB_INTERSTITIAL_ID` y `ADMOB_TEST_MODE=false`. Las variables de Actions tienen prioridad sobre `ads.config.json`.
* Con anuncios reales los tres IDs son obligatorios; `scripts/admob-build-config.mjs` falla el build si falta alguno o tiene formato inválido, para no publicar IDs de prueba mezclados.
* Para probar sin generar tráfico inválido usa los IDs de prueba o registra tu teléfono como dispositivo de prueba (el ID aparece en `adb logcat`).

### Obtener los IDs en AdMob

1. Entra a [AdMob](https://apps.admob.com) → **Apps → Agregar app** → Android. Si la app todavía no está en Play, indica que aún no está listada (se puede vincular después).
2. En **Configuración de la app** copia el **App ID** (`ca-app-pub-...~...`).
3. En **Unidades de anuncio → Agregar unidad**: crea una de **Banner** y una de **Interstitial**; copia cada ID (`ca-app-pub-.../...`).
4. Si vas a mostrar anuncios en el EEE/Reino Unido, crea el mensaje de consentimiento en **Privacidad y mensajería → GDPR** (la app ya integra el formulario UMP).
5. Pega los 3 IDs en `ads.config.json`, pon `"testMode": false` y haz commit.

> Recuerda: AdMob solo sirve anuncios reales de forma plena cuando la app está publicada en Play y verificada; mientras tanto puede entregar pocos anuncios o ninguno.

### Para que AdMob pague (checklist de publicación)

AdMob no monetiza un APK instalado a mano: exige que la app esté **publicada en Google Play (o App Store)** y verificada. Pasos:

1. **Google Play Console:** ficha de la app (`com.finanbcv.app`), política de privacidad pública, formulario de **Data safety** (AdMob recoge identificadores del dispositivo para publicidad), declaración **"contiene anuncios"**, clasificación de contenido y prueba cerrada con **12 testers durante 14 días** (cuentas personales creadas después del 13-11-2023).
2. **APK/AAB de producción:** firmar con un *keystore* propio (guardar el keystore y `key.properties` fuera del repo), subir el AAB con Play App Signing y compilar con los IDs reales.
3. **app-ads.txt:** publicar el archivo en la raíz del dominio de la web del desarrollador que figure en la ficha de Play (por ejemplo, un repo `linuxcoro.github.io` con `app-ads.txt` en la raíz), con la línea `google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0`, y verificarlo desde AdMob.
4. **AdMob:** crear la app, crear las unidades de banner e interstitial, vincular la ficha de Play, pedir la verificación con `app-ads.txt` y esperar la revisión de *app readiness*.
5. **Cobro:** completar dirección y PIN de verificación, datos fiscales (W-8BEN para no residentes en EE. UU.) y método de pago; AdMob paga a partir de un umbral de 100 USD.

> Mientras la app no esté publicada y verificada, AdMob puede no servir anuncios reales aunque el código esté listo. El APK debug con IDs de prueba sirve para validar la integración.

### Requisitos que ya cubre el repo para publicar

* `targetSdk 36` (exigido por Play a las apps nuevas desde el 31-08-2026) vía Capacitor 8.
* `INTERNET` en el manifest (Capacitor lo incluye) y meta-data `com.google.android.gms.ads.APPLICATION_ID`.
* La firma de producción, el AAB y el `app-ads.txt` quedan pendientes para la fase de publicación.

---

## 🗺️ Hoja de Ruta

El roadmap y la bitácora de mejoras del proyecto se mantienen en [`plan_de_mejoras.md`](plan_de_mejoras.md).
