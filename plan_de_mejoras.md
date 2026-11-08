# Plan de mejoras — FinanBCV

**Fecha:** 2026-11-08 · **Estado global:** ✅ 5 de 5 pasos ejecutados en local · ✅ repositorio en GitHub (`linuxcoro/finanbcv`, público) con `main` subido · ✅ automatización horaria de tasas activa y con primer run verde · 🟡 pendiente: generar el APK (Fase C) · Historial de pagos: ✅ añadido como mejora posterior · Pago inicial: ✅ eliminado
**Archivo de la app:** `index.html` (602 líneas, SPA de un solo archivo)
**Documentación:** `documentaci_n_de_la_aplicaci_n.md`

> Este documento es el plan de trabajo **por pasos**. Los pasos 1–5 están ejecutados en local (ver Bitácora); el repositorio ya está en GitHub con `main` subido (Fase A) y la automatización horaria de las tasas está activa y verificada con un primer run verde (Fase B). Falta solo la Fase C (generar el APK). El **workflow de GitHub** fue deliberadamente el último, por pedido del usuario. Al cerrar cada paso se marca el estado (`✅ hecho`), se actualiza la tabla y se añade una línea a la Bitácora.

---

## 1. Objetivo y criterios de éxito

Corregir las inconsistencias detectadas en la aplicación y dejarla lista para compilarse como APK, ejecutando el trabajo por pasos.

Se considera terminado cuando:

1. El archivo de la app se llama `index.html` (requisito de la documentación para GitHub/APK) y el proyecto es un repositorio git con un commit por paso.
2. La tarjeta de crédito muestra la **inicial pagada**, no solo el total y la cuota.
3. El mensaje de Pago Móvil indica la **parte/cuota correcta** ("Parte 2 de 3"; "Parte a pagar: 1 de N" si aún no hay abonos) y ya no queda la variable muerta `currentInstallmentNum`.
4. La documentación refleja la realidad: nombre del archivo, funcionalidad y workflow existente.
5. Existe `.github/workflows/build-apk.yml` que produce un **APK debug** descargable como artifact, validado sintácticamente en local.
6. El repositorio `finanbcv` existe en GitHub y `main` está subido; el workflow **Actualizar tasas BCV** refresca `tasas.json` **cada hora** sin disparar builds del APK, y el workflow **Build APK** deja el artifact `FinanBCV-apk` descargable.

## 2. Hechos verificados (base del plan — estado previo a la ejecución)

- El proyecto **no era un repositorio git** y no tenía carpeta `.github/` (el repositorio se creó en el Paso 1; `.github/` se añade en el Paso 5).
- La app **no referencia recursos locales**: Tailwind, Lucide y las fuentes se cargan por CDN, así que renombrar el archivo HTML no rompe ninguna ruta.
- `registerPayment()` descuenta `remainingInstallments` y abre automáticamente el modal de compartir; el mensaje ya distingue un crédito liquidado.
- `initialPercent` **sí se guardaba** en `localStorage.finanbcv_credits`, pero **no se mostraba** en la tarjeta del crédito (se muestra desde el Paso 2).
- Herramientas disponibles: node v24.22.2, Python 3.10 con PyYAML 6.0.3, git 2.34.1 con identidad configurada. **No** hay `gh` ni `actionlint`/`yamllint`.

## 3. Tabla de pasos

| # | Paso | Estado |
|---|------|--------|
| 1 | Repositorio git y renombrar a `index.html` | ✅ hecho |
| 2 | Mostrar la inicial pagada en la tarjeta del crédito | ✅ hecho |
| 3 | Número de parte correcto en el mensaje de Pago Móvil | ✅ hecho |
| 4 | Actualizar `documentaci_n_de_la_aplicaci_n.md` | ✅ hecho |
| 5 | **Último:** crear el repositorio, automatizar las tasas y generar el APK | 🟡 Fases A y B ✅ (repo subido + automatización activa) · falta Fase C (APK) |

---

## Paso 1 — Repositorio git y renombrar a `index.html`

**Objetivo:** coincidir con la documentación (que pide subir el archivo como `index.html`) sin perder el nombre descriptivo actual.

1. `git init -b main` y commit inicial con los archivos actuales (red de seguridad para el rename).
2. `git mv gestor_de_ventas_financiadas_bcv.html index.html`.
3. Commit: `chore: renombrar a index.html para despliegue y APK`.

**Aceptación:** `index.html` es el único HTML de la raíz, `git log --oneline` muestra ambos commits y la app sigue abriendo igual (no hay rutas relativas, ya verificado).

## Paso 2 — Mostrar la inicial pagada en la tarjeta del crédito

**Archivo:** `index.html`, función `renderCredits()` — bloque "Desglose Financiero" (líneas 442–451 de la versión original).

- Calcular al renderizar:

  ```js
  const initialPercent = credit.initialPercent ?? 0;   // compatibilidad con créditos antiguos
  const initialUsd = credit.totalUsd * (initialPercent / 100);
  const initialBs = initialUsd * credit.bcvRate;
  ```

- Añadir una celda **"Inicial (X%)"** con formato `$X (Bs Y)` junto a "Total Venta".
- Mover "Monto por Cuota" a una fila `col-span-2` para que no se vea apretado en móvil.
- Formatear los bolívares con `toLocaleString('es-VE', {minimumFractionDigits: 2, maximumFractionDigits: 2})`, igual que el resto de la app.
- **No** se toca el cálculo de cuotas ni el esquema de `localStorage` (solo datos derivados en pantalla).
- Commit: `feat: mostrar inicial pagada en la tarjeta del crédito`.

**Casos borde:** créditos viejos sin `initialPercent` → se asume 0 % (`$0.00`) sin romper; inicial de 0 % es válida.

**Aceptación:** un crédito de $100 al 30 % muestra `$30.00 (Bs …)`; uno al 0 % muestra `$0.00`.

## Paso 3 — Número de parte correcto en el mensaje de Pago Móvil

**Archivo:** `index.html`, función `prepareShareMessage()` (líneas 498–532 originales).

- Eliminar la variable muerta `currentInstallmentNum` (línea 509), que se calcula y nunca se usa, y sustituirla por algo que sí se muestre:

  ```js
  const paidParts = credit.totalInstallments - credit.remainingInstallments;
  ```

- Si `credit.remainingInstallments === 0`: mantener el mensaje de felicitación refiriéndose a `Parte ${paidParts} de ${credit.totalInstallments}`.
- Si quedan partes: insertar la línea `🧾 *Parte a pagar:* ${paidParts + 1} de ${credit.totalInstallments}` antes del aviso de partes restantes.
- Commit: `fix: indicar la parte correcta en el mensaje de Pago Móvil`.

**Casos borde:**
- Crédito recién registrado y compartido sin abonos → "Parte a pagar: 1 de N".
- Último abono → "Parte N de N" (liquidado).
- Sin datos de Pago Móvil configurados → se mantiene el comportamiento actual (toast + modal de ajustes).

**Aceptación:** con 3 partes y 1 abono el mensaje dice "Parte a pagar: 2 de 3" y "Te restan 2 parte(s)"; al llegar a 0 partes dice "Parte 3 de 3" y no ofrece parte siguiente.

## Paso 4 — Actualizar `documentaci_n_de_la_aplicaci_n.md`

- Corregir el nombre del archivo a `index.html` en todas las referencias (la guía de compilación pide `index.html` pero el archivo real tiene otro nombre).
- Añadir en características: la tarjeta muestra la **inicial pagada** y "Abonar Cuota" abre el comprobante.
- Reescribir la sección "Instrucciones para Compilar como APK": el workflow ya vive en `.github/workflows/build-apk.yml`, se dispara con push a `main` o manualmente, el APK queda como *artifact* en la pestaña **Actions**, e incluir cómo instalarlo (permitir fuentes desconocidas o `adb install`).
- Añadir una nota de limitación: Tailwind y Lucide se cargan por CDN, por lo que el primer arranque requiere internet.
- Referenciar este `plan_de_mejoras.md` como roadmap.
- Commit: `docs: actualizar documentación a index.html y workflow APK`.

**Aceptación:** ninguna referencia al nombre viejo; la guía coincide con los archivos reales del repositorio.

## Paso 5 — ÚLTIMO: crear el repositorio, automatizar las tasas y generar el APK

**Archivos implicados:** `.github/workflows/actualizar-tasas.yml` (nuevo), `.github/workflows/build-apk.yml` (ajuste del disparador) y `capacitor.config.json` (ya creado, identidad de la app versionada). El orden es **A → B → C**: sin repositorio en GitHub no hay dónde ejecutar los workflows.

**Estado actual (2026-11-08):** Fases **A** y **B** ejecutadas. El repositorio público `linuxcoro/finanbcv` existe, `origin` apunta a `git@github.com:linuxcoro/finanbcv.git` y `main` sigue su upstream con todo el historial. El workflow **Actualizar tasas BCV** quedó registrado y activo; su primer run (`workflow_dispatch`) terminó en verde y commiteó `tasas.json` como `github-actions[bot]` sin disparar el APK. Falta la Fase **C** (build del APK).

`capacitor.config.json`:

```json
{
  "appId": "com.finanbcv.app",
  "appName": "FinanBCV",
  "webDir": "www",
  "server": { "androidScheme": "https" }
}
```

### Fase A — Crear el repositorio en GitHub y subir `main`

Prerrequisitos: cuenta de GitHub y autenticación. No hay `gh` instalado; la ruta principal es la web.

1. Abrir `https://github.com/new` con:
   - **Owner:** `<usuario>` · **Repository name:** `finanbcv`.
   - **Visibilidad:** **Public** (minutos de Actions gratis); un repo privado también funciona, con la cuota mensual de minutos.
   - **Sin** README, `.gitignore` ni licencia: el repositorio local ya tiene el historial y así se evita un commit inicial que estorbe.
2. Enlazar y subir `main` (autenticación HTTPS con un PAT clásico con scopes `repo` + `workflow`, o por SSH):

   ```bash
   git remote add origin https://github.com/<usuario>/finanbcv.git
   git push -u origin main
   ```

   El scope `workflow` es necesario porque el push incluye `.github/workflows/*`.
3. Ruta alternativa con `gh` (si se instala): `gh auth login` y
   `gh repo create finanbcv --public --source=. --remote=origin --push`.
4. Verificar: `git remote -v`, `git status -sb`, `git branch -vv` (`main` con upstream).
5. **Settings → Actions → General → Workflow permissions → “Read and write permissions”** y guardar. Es imprescindible para que la Fase B pueda hacer commit y push con `GITHUB_TOKEN`.

> Si el repo se creó con README: `git pull --rebase origin main` y reintentar `git push -u origin main`. Si el remote ya existe con otra URL: `git remote set-url origin …`.

### Fase B — La Automatización

**Archivo nuevo:** `.github/workflows/actualizar-tasas.yml`.

- Disparadores: `schedule` con `cron: '5 * * * *'` (cada hora, minuto 5, **UTC**) y `workflow_dispatch` para ejecutarlo a mano desde **Actions → Actualizar tasas BCV → Run workflow**.
- `permissions: contents: write` y `concurrency` (`actualizar-tasas`) para que dos ejecuciones no se pisen. Sin secretos: usa el `GITHUB_TOKEN` del repositorio.
- Pasos:
  1. `actions/checkout@v4`.
  2. `actions/setup-python@v5` con Python 3.10 y caché de pip sobre `requirements-tasas.txt`.
  3. `pip install -r requirements-tasas.txt`.
  4. **`python3 bcv_scraper.py > tasas.json`** (el scraper imprime el JSON por stdout y los avisos por stderr) seguido de `python3 -m json.tool tasas.json > /dev/null` para no aceptar una salida vacía o corrupta.
  5. Commit y push como `github-actions[bot]`: solo si `tasas.json` cambió; mensaje `chore: actualizar tasas BCV`.
- Si el BCV falla o cambia el HTML, el scraping devuelve código 1 y el step se marca en rojo **sin** commitear: se conserva la última tasa buena y el error queda visible en Actions.
- El workflow debe estar en `main` para que el `schedule` se active; el primer run puede forzarse con **Run workflow**.
- Con los campos `obtenido_en`/`actualizado_texto` el archivo cambia en cada ejecución, así que se hace **un commit por hora** (≈8.760/año), que es lo pedido: `tasas.json` siempre refleja la última consulta. Si se prefiere no llenar el historial, basta comparar solo `usd`/`eur`/`fecha_valor` y omitir el commit cuando la tasa no cambie.
- Los commits del bot **no** recompilan el APK: la Fase C ignora `tasas.json` y `**.md`.
- Aviso: GitHub puede retrasar el cron; el horario es UTC (irrelevante al ser cada hora).

### Fase C — Generar el APK con GitHub Actions

**Archivo:** `.github/workflows/build-apk.yml`.

- Disparadores: `push` a `main` (ignorando `tasas.json` y `**.md`) y `workflow_dispatch`.
- Runner `ubuntu-latest`: checkout, Node 20, Java 17 (temurin), Android SDK, Capacitor 6 fijado, copia de `index.html` y `tasas.json` a `www/`, `npx cap add android && npx cap sync android`, `./gradlew assembleDebug --no-daemon`.
- El APK queda como artifact **`FinanBCV-apk`** (`app-debug.apk`) en la pestaña **Actions**, dentro de la ejecución del workflow.
- Seguimiento y descarga:

  ```bash
  gh run list --workflow=build-apk.yml
  gh run watch
  gh run download --name FinanBCV-apk
  ```

  Desde la web: **Actions → Build APK → última ejecución → Artifacts → FinanBCV-apk**.
- Instalación: descomprimir el artifact, copiar `app-debug.apk` al teléfono y permitir **fuentes desconocidas**, o `adb install -r app-debug.apk`. Es un APK **debug** (sin firma de producción).
- El APK lleva la foto de `tasas.json` del momento del build; para refrescarla, relanzar el workflow a mano.

**Plan B:** si el build de Capacitor fallara en CI, publicar como artifact un `.zip` con `index.html`; no bloquea las fases A/B.

**Aceptación:** el repositorio existe con `main` subido y permisos de escritura para workflows; el workflow “Actualizar tasas BCV” corre cada hora (o a mano), commitea un `tasas.json` válido y no dispara el APK; el workflow “Build APK” termina en verde y deja el artifact `FinanBCV-apk` descargable.

---

## 4. Verificación (pasos 2–5)

- **Sintaxis del JavaScript inline** (el script está embebido en el HTML, no hay archivo .js aparte):

  ```bash
  awk '/Lógica en JavaScript/{f=1;next} f && /^[[:space:]]*<\/script>/{exit} f && /^[[:space:]]*<script>/{next} f' index.html > /tmp/app.js && node --check /tmp/app.js
  ```

- **Smoke manual en el navegador:** abrir `index.html`, revisar que la consola no tenga errores y recorrer el flujo completo:
  1. Guardar datos de Pago Móvil.
  2. Registrar un crédito de $100 a tasa 36,50 con 30 % de inicial y 2 partes.
  3. "Abonar Cuota" → comprobar que el mensaje dice "Parte a pagar: 2 de 2" (la siguiente parte) y probar "Copiar Texto".
  4. Segundo abono → "Parte 2 de 2" y estado "Pagado Total".
  5. Recargar la página y confirmar la persistencia de `finanbcv_credits`, `finanbcv_settings` y `finanbcv_theme`.
- **Datos heredados:** probar con un crédito antiguo sin `initialPercent` en `localStorage` para validar el fallback.
- **Validación de los workflows** (no se pueden ejecutar en local): parsear ambos YAML con PyYAML y comprobar su estructura:

  ```bash
  python3 - <<'PY'
  import yaml

  for archivo in ['.github/workflows/build-apk.yml', '.github/workflows/actualizar-tasas.yml']:
      datos = yaml.safe_load(open(archivo))
      print(archivo, 'OK', list(datos))
  PY
  ```

  Además, revisar que `build-apk.yml` tenga `paths-ignore` para `tasas.json` y `**.md`, y que `actualizar-tasas.yml` tenga `contents: write`, el `cron: '5 * * * *'` y el comando `python3 bcv_scraper.py > tasas.json`.
- **Grep de control:** `grep -rn "gestor_de_ventas_financiadas_bcv\|currentInstallmentNum" .` no debe devolver resultados en código/documentación (solo pueden quedar referencias históricas en este mismo plan).

## 5. Riesgos y reversión

- El rename se hace con `git mv` después del commit inicial, por lo que es recuperable con `git checkout`.
- Los cambios no alteran el esquema de `localStorage`: no hay migración ni pérdida de datos de créditos.
- El APK depende de CDNs (sin internet no hay estilos ni iconos) y de versiones fijadas de Capacitor; se documenta como limitación y su fallo afecta solo a ese archivo.
- No se modifica ni se elimina ningún crédito del usuario.
- La creación del repositorio, la autenticación y el push requieren credenciales del usuario: el agente deja todo listo en local y documenta los comandos; no se ejecuta sin autorización.
- El workflow horario depende del BCV: si la página falla o cambia su HTML, la ejecución queda en rojo y **no** commitea, conservando la última tasa buena.
- GitHub puede retrasar u omitir ejecuciones del `schedule` y las desactiva tras 60 días sin actividad; los commits del bot mantienen el repo activo y el workflow se puede relanzar a mano.
- En un repo privado los minutos de Actions son limitados; el APK solo se compila con cambios de código o a mano (la Fase C ignora `tasas.json` y `**.md` para no recompilar cada hora).
- Los commits horarios generan mucho historial (≈8.760/año); se puede reducir comparando solo `usd`/`eur`/`fecha_valor` antes de commitear.
- Reversión de la automatización: borrar `.github/workflows/actualizar-tasas.yml` (o desactivarla en Actions) y hacer push.

## 6. Bitácora

| Fecha | Paso | Resultado |
|-------|------|-----------|
| 2026-11-08 | — | Plan creado. Ningún paso ejecutado todavía; el repositorio sigue con `gestor_de_ventas_financiadas_bcv.html` y `documentaci_n_de_la_aplicaci_n.md`. |
| 2026-11-08 | 1 | Repositorio git creado en rama `main` con commit inicial de los 3 archivos; rename con `git mv` de `gestor_de_ventas_financiadas_bcv.html` a `index.html`. Único HTML de la raíz y app sin rutas relativas. |
| 2026-11-08 | 2 | `renderCredits()` muestra la celda "Inicial (X%)" con `$X (Bs Y)` junto a "Total Venta" (fallback 0 % para créditos heredados) y "Monto por Cuota" pasa a fila `col-span-2`. Verificado con arnés Node sobre el JS inline: $100 al 30 % → `$30.00 (Bs 1.095,00)`; sin `initialPercent` → `$0.00 (Bs 0,00)`. |
| 2026-11-08 | 3 | `prepareShareMessage()` elimina la variable muerta `currentInstallmentNum` y calcula `paidParts`; el mensaje muestra `🧾 *Parte a pagar:* paidParts+1 de N` o `Parte N de N` al liquidar. Verificado: 3 partes con 1 abono → "Parte a pagar: 2 de 3" y "Te restan 2 parte(s)"; sin abonos → "1 de N"; liquidado → "Parte 3 de 3". Se corrigieron también el comando de extracción JS del §4 y el smoke para que coincidan con la numeración "Parte a pagar". |
| 2026-11-08 | 4 | `documentaci_n_de_la_aplicaci_n.md` actualizada: nombre `index.html`, características de la inicial en la tarjeta y del comprobante automático al abonar, estructura del repositorio, guía APK reescrita (workflow, disparadores, artifact en Actions, instalación por fuentes desconocidas o `adb`), limitación de CDN y referencia al plan como roadmap. Verificado: sin referencias al nombre viejo. |
| 2026-11-08 | 5 | `capacitor.config.json` y `.github/workflows/build-apk.yml` creados: disparadores `push` a `main` + `workflow_dispatch`, `permissions: contents: read`, Ubuntu + Node 20 + Java 17 (temurin) + Android SDK, Capacitor 6 con versiones fijadas, copia de `index.html` a `www/`, `assembleDebug` y artifact `FinanBCV-apk`. Validado en local con PyYAML y comprobación de estructura (24/24 PASS, sin secretos). **Pendiente** crear el repositorio en GitHub y el push (`git remote add origin …` + `git push -u origin main`); ver Paso 5 reformulado. |
| 2026-11-08 | Post-plan | **Historial de pagos por crédito:** campo aditivo `payments` en `finanbcv_credits`, botón "Historial de pagos (N)" en cada tarjeta y modal con la inicial + abonos (fecha, parte, $ y Bs), compatible con créditos heredados (resumen "pagos anteriores sin detalle"). Documentación actualizada. Commit `feat: mostrar historial de pagos por crédito`. |
| 2026-11-08 | Post-plan | Se quitó la inicial del historial de pagos: ahora solo lista abonos de cuota y el total mostrado es el de cuotas. En ese momento la tarjeta aún mostraba la inicial. Documentación actualizada. Commit `fix: excluir la inicial del historial de pagos`. |
| 2026-11-08 | Post-plan | Se eliminó el **% de pago inicial**: sin campo en el formulario, sin "Monto Inicial" en el resumen y sin celda "Inicial (X%)" en la tarjeta; el cálculo ahora financia el monto total (`cuota = totalUsd / partes`) y los créditos nuevos no guardan `initialPercent` (los antiguos se leen igual). Documentación actualizada. Commit `refactor: eliminar el % de pago inicial`. |
| 2026-11-08 | Post-plan | **Tasas USD/EUR en la app:** `index.html` lee `tasas.json` y muestra tarjetas del dólar y del euro con botón **Actualizar** (usa `POST /api/actualizar` de `bcv_server.py` si está disponible; si no, relee el archivo; fallback a `localStorage`). La tasa del dólar se aplica a la calculadora sin pisar tasas personalizadas. `bcv_server.py` gana `/app`, `/tasas.json` y `POST /api/actualizar`; el workflow del APK copia `tasas.json` si existe. Documentación y `README_tasas.md` actualizados. |
| 2026-11-08 | Paso 5 (reformulación) | Paso 5 reorganizado en tres fases: **A** crear el repositorio en GitHub y subir `main`; **B — La Automatización** con `.github/workflows/actualizar-tasas.yml` (cron horario, `python3 bcv_scraper.py > tasas.json`, validación JSON, commit del bot, `contents: write`); **C** generar el APK. `build-apk.yml` ignora `tasas.json` y `**.md` para no recompilar cada hora. `README_tasas.md` y `documentaci_n_de_la_aplicaci_n.md` actualizados. Pendiente: crear el repo y el push. |
| 2026-11-08 | Paso 5 · Fase A | Repositorio público `linuxcoro/finanbcv` creado en la web (sin README, `.gitignore` ni licencia) y `main` subido por SSH, porque no hay `gh` ni token en la máquina. `origin` = `git@github.com:linuxcoro/finanbcv.git`, `main` con upstream (`## main...origin/main`) y los 14 commits en el remoto; ambos workflows registrados y en estado `active`. Nota: el push inicial no generó evento de Actions (repo creado segundos antes), por eso el primer run de la Fase B se forzó a mano. |
| 2026-11-08 | Paso 5 · Fase B | Automatización verificada de punta a punta: `actualizar-tasas.yml` ejecutado con `workflow_dispatch` desde Actions → run en verde que commiteó `tasas.json` como `github-actions[bot]` (`chore: actualizar tasas BCV`, commit `c67d705`) con JSON válido (`usd 897.5383`, `eur 1001.18602288`, fecha valor 2026-11-09) y **sin** disparar el build del APK. Los mismos pasos se probaron en local con el scraper real. Queda activo el cron `5 * * * *` (cada hora, minuto 5 UTC). |

## 7. Mejora posterior — Historial de pagos por crédito

**Estado:** ✅ hecho (mejora posterior a los pasos 1–5; no reabre el plan original).

- Nuevo campo **aditivo** `payments` en cada crédito de `localStorage.finanbcv_credits`; los créditos antiguos se leen sin migración y muestran un resumen "pagos anteriores sin detalle".
- Botón **"Historial de pagos (N)"** en cada tarjeta → modal con cada abono de cuota, con fecha, número de parte y montos en `$` y `Bs`, además del total abonado en cuotas.
- El flujo de **"Abonar Cuota" no cambia**: sigue registrando el abono y abriendo el comprobante de Pago Móvil; el historial se actualiza solo.
- Documentación actualizada en `documentaci_n_de_la_aplicaci_n.md`.
- Commit: `feat: mostrar historial de pagos por crédito`.

## 8. Mejora posterior — Eliminación del % de pago inicial

**Estado:** ✅ hecho (mejora posterior a los pasos 1–5; reemplaza para créditos nuevos lo añadido en el Paso 2).

- Se eliminó el campo **"% Pago Inicial"** del formulario, la fila "Monto Inicial" del resumen en vivo y la celda "Inicial (X%)" de la tarjeta de crédito.
- El cálculo ahora financia el **monto total**: `cuota = totalUsd / partes` (sin descontar inicial). El resumen en vivo muestra "Total a Financiar".
- Los créditos nuevos ya no guardan `initialPercent`; los créditos antiguos que lo tengan siguen usando y mostrando su monto por cuota ya calculado (el campo se ignora).
- El historial de pagos (solo abonos de cuota) no cambia.
- Documentación actualizada en `documentaci_n_de_la_aplicaci_n.md`.
- Commit: `refactor: eliminar el % de pago inicial`.

## 9. Mejora posterior — Tasas USD/EUR en la app con botón Actualizar

**Estado:** ✅ hecho (mejora posterior a los pasos 1–5).

- `index.html` muestra las tasas oficiales **USD** y **EUR** del BCV con fecha valor y hora de actualización, y un botón **Actualizar**.
- Al cargar y al pulsar el botón lee `tasas.json` (con caché evitada); si la app se sirve con `bcv_server.py`, el botón hace `POST /api/actualizar`: el servidor ejecuta `bcv_scraper.py`, regenera `tasas.json` de forma atómica y devuelve el JSON. Sin endpoint (servidor estático) el botón relee el archivo; como último recurso usa las tasas guardadas en `localStorage.finanbcv_tasas`.
- La tasa del dólar se rellena automáticamente en el campo **Tasa BCV (Bs/$)** sin pisar una tasa personalizada; la tarjeta USD permite reaplicarla y la del euro se muestra como referencia.
- `bcv_server.py` incorpora las rutas `GET /app`, `GET /tasas.json` y `POST /api/actualizar` (además de las existentes).
- El workflow del APK copia `tasas.json` a `www/` si existe, para que el APK muestre la última foto de las tasas.
- Documentación actualizada en `README_tasas.md` y `documentaci_n_de_la_aplicaci_n.md`.
