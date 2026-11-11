# Plan de mejoras — FinanBCV

**Fecha:** 2026-11-08 · **Estado global:** ✅ plan cerrado · ✅ 5 de 5 pasos ejecutados · ✅ repositorio en GitHub (`linuxcoro/finanbcv`, público) con `main` subido · ✅ automatización horaria de tasas activa · ✅ Fase C: APK generado en Actions (artifact `FinanBCV-apk`, run [#42521051694](https://github.com/linuxcoro/finanbcv/actions/runs/42521051694)) · ✅ APK actualizado con compartir nativo (run [#42523675049](https://github.com/linuxcoro/finanbcv/actions/runs/42523675049)) · Historial de pagos: ✅ añadido como mejora posterior · Pago inicial: ✅ eliminado · ✅ Monetización AdMob integrada y validada en CI (run [#42529926855](https://github.com/linuxcoro/finanbcv/actions/runs/42529926855)) · ✅ Firma release (AAB Play) y respaldo de datos validados en CI (run [#42536731536](https://github.com/linuxcoro/finanbcv/actions/runs/42536731536)) · ✅ IDs reales de AdMob configurados y compilados en CI (run [#42543483026](https://github.com/linuxcoro/finanbcv/actions/runs/42543483026))
**Archivo de la app:** `index.html` (SPA de un solo archivo)
**Documentación:** `documentaci_n_de_la_aplicaci_n.md`

> Este documento es el plan de trabajo **por pasos**. Los pasos 1–5 están ejecutados (ver Bitácora); el repositorio está en GitHub con `main` subido (Fase A), la automatización horaria de las tasas está activa y verificada (Fase B) y la Fase C ya generó el APK en GitHub Actions, por lo que el plan queda cerrado. El **workflow de GitHub** fue deliberadamente el último, por pedido del usuario. Al cerrar cada paso se marca el estado (`✅ hecho`), se actualiza la tabla y se añade una línea a la Bitácora.

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
| 5 | **Último:** crear el repositorio, automatizar las tasas y generar el APK | ✅ hecho (Fases A, B y C; APK `FinanBCV-apk` en Actions) |

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

**Estado actual (2026-11-08):** Fases **A**, **B** y **C** ejecutadas. El repositorio público `linuxcoro/finanbcv` existe, `origin` apunta a `git@github.com:linuxcoro/finanbcv.git` y `main` sigue su upstream con todo el historial. El workflow **Actualizar tasas BCV** quedó registrado y activo; su primer run (`workflow_dispatch`) terminó en verde y commiteó `tasas.json` como `github-actions[bot]` sin disparar el APK. El workflow **Build APK** terminó en verde en su segundo intento (run #42521051694) y dejó el artifact `FinanBCV-apk` con `app-debug.apk` disponible en **Actions**.

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

**Resultado (2026-11-08):** el workflow se disparó con el push a `main` y terminó en verde (run [#42521051694](https://github.com/linuxcoro/finanbcv/actions/runs/42521051694)): los 10 pasos del job completaron en `success` y quedó el artifact `FinanBCV-apk` (3.379.141 bytes, sin expirar). El primer intento (run [#42520918036](https://github.com/linuxcoro/finanbcv/actions/runs/42520918036)) falló en `android-actions/setup-android@v3`; se sustituyó por una verificación del SDK preinstalado en los runners `ubuntu-latest` (commit `e041a1a`).

**Plan B:** si el build de Capacitor fallara en CI, publicar como artifact un `.zip` con `index.html`; no bloquea las fases A/B.

**Aceptación:** el repositorio existe con `main` subido y permisos de escritura para workflows; el workflow “Actualizar tasas BCV” corre cada hora (o a mano), commitea un `tasas.json` válido y no dispara el APK; el workflow “Build APK” termina en verde y deja el artifact `FinanBCV-apk` descargable. **✅ Cumplida el 2026-11-08.**

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
- **Tasas remotas:** comprobar que al cargar o pulsar **Actualizar** las tasas se pintan sin dejar un mensaje fijo de éxito (el estado queda oculto), que el botón conserva los valores y que las tarjetas USD/EUR aplican su tasa; sin red debe avisar y recurrir a las tasas de `localStorage`. Verificado en Chrome headless tanto por HTTP como con `file://`.
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
- El APK depende de CDNs (sin internet no hay estilos ni iconos) y de la URL de GitHub para las tasas; si falla la descarga, la app usa las tasas guardadas en `localStorage`. También depende de versiones fijadas de Capacitor; se documenta como limitación y su fallo afecta solo a ese archivo.
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
| 2026-11-08 | Post-plan | **Tasas USD/EUR en la app:** `index.html` lee `tasas.json` y muestra tarjetas del dólar y del euro con botón **Actualizar** (usa `POST /api/actualizar` de `bcv_server.py` si está disponible; si no, relee el archivo; fallback a `localStorage`). La tasa del dólar se aplica a la calculadora sin pisar tasas personalizadas. `bcv_server.py` gana `/app`, `/tasas.json` y `POST /api/actualizar`; el workflow del APK copia `tasas.json` si existe. Documentación y `README_tasas.md` actualizados. Posteriormente la fuente se cambió a GitHub (ver más abajo). |
| 2026-11-08 | Paso 5 (reformulación) | Paso 5 reorganizado en tres fases: **A** crear el repositorio en GitHub y subir `main`; **B — La Automatización** con `.github/workflows/actualizar-tasas.yml` (cron horario, `python3 bcv_scraper.py > tasas.json`, validación JSON, commit del bot, `contents: write`); **C** generar el APK. `build-apk.yml` ignora `tasas.json` y `**.md` para no recompilar cada hora. `README_tasas.md` y `documentaci_n_de_la_aplicaci_n.md` actualizados. Pendiente: crear el repo y el push. |
| 2026-11-08 | Paso 5 · Fase A | Repositorio público `linuxcoro/finanbcv` creado en la web (sin README, `.gitignore` ni licencia) y `main` subido por SSH, porque no hay `gh` ni token en la máquina. `origin` = `git@github.com:linuxcoro/finanbcv.git`, `main` con upstream (`## main...origin/main`) y los 14 commits en el remoto; ambos workflows registrados y en estado `active`. Nota: el push inicial no generó evento de Actions (repo creado segundos antes), por eso el primer run de la Fase B se forzó a mano. |
| 2026-11-08 | Paso 5 · Fase B | Automatización verificada de punta a punta: `actualizar-tasas.yml` ejecutado con `workflow_dispatch` desde Actions → run en verde que commiteó `tasas.json` como `github-actions[bot]` (`chore: actualizar tasas BCV`, commit `c67d705`) con JSON válido (`usd 897.5383`, `eur 1001.18602288`, fecha valor 2026-11-09) y **sin** disparar el build del APK. Los mismos pasos se probaron en local con el scraper real. Queda activo el cron `5 * * * *` (cada hora, minuto 5 UTC). |
| 2026-11-08 | Post-plan | **Tasas desde GitHub:** `index.html` descarga `tasas.json` de `https://raw.githubusercontent.com/linuxcoro/finanbcv/main/tasas.json` (con cache busting) y elimina el flujo `POST /api/actualizar`; el fallback son las tasas guardadas en `localStorage`. Se corrigió el campo **Tasa BCV** a `step="any"` para aceptar la tasa exacta autocompletada sin bloquear el registro del crédito. Documentación y plan actualizados. Commit `3c4beec`. |
| 2026-11-08 | Paso 5 · Fase C | APK generado en GitHub Actions: el primer run ([#42520918036](https://github.com/linuxcoro/finanbcv/actions/runs/42520918036)) falló en `android-actions/setup-android@v3`; se reemplazó por una verificación del SDK preinstalado (commit `e041a1a`). El segundo run ([#42521051694](https://github.com/linuxcoro/finanbcv/actions/runs/42521051694)) terminó en verde (10/10 pasos) y dejó el artifact `FinanBCV-apk` (3.379.141 bytes, `app-debug.apk`) disponible en Actions. Verificado además el flujo completo en Chrome headless (ajustes, alta de crédito, dos abonos, historial y persistencia) y la sintaxis JS con el comando del §4. |
| 2026-11-08 | Post-plan | **Compartir en cualquier red social:** el botón **Pago Móvil** abre el selector nativo de apps con el texto del comprobante; en el APK mediante `@capacitor/share` y en navegadores con Web Share API, con el modal de copia como respaldo. El workflow instala `@capacitor/share@6` (verificado en `capacitor.plugins.json` antes de compilar). APK regenerado en el run [#42523675049](https://github.com/linuxcoro/finanbcv/actions/runs/42523675049): 10/10 pasos en verde y artifact `FinanBCV-apk` (3.383.095 bytes). Commit `97c10ea`. |
| 2026-11-08 | Post-plan | **Monetización con AdMob:** integración del plugin `@capacitor-community/admob@8.3.0` (banner adaptativo, interstitial con límite de 3 minutos, consentimiento UMP y botón de privacidad), script `scripts/admob-build-config.mjs` (config web + parche del manifest/strings en CI), Capacitor 8 (Node 22, Java 21, `targetSdk 36`) e IDs de prueba por defecto. El workflow verifica el APK antes del artifact. Run [#42529926855](https://github.com/linuxcoro/finanbcv/actions/runs/42529926855) en verde (13/13 pasos) con artifact `FinanBCV-apk` de 8,01 MB. Pendiente: publicar en Play y `app-ads.txt` para que AdMob pague. Commit `0efe4b3`. |
| 2026-11-08 | Post-plan | **Firma release estable y respaldo de datos:** nuevo workflow manual `build-release.yml` (AAB firmado con `jarsigner` + APK release con `zipalign`/`apksigner`), `scripts/patch-android-version.mjs` (versionCode/versionName automáticos por ejecución), secrets `ANDROID_KEYSTORE_*` y modal **Respaldo y restauración** en la app (exportar/copiar/compartir/restaurar JSON, validado en Chrome headless). Run del APK debug [#42536731536](https://github.com/linuxcoro/finanbcv/actions/runs/42536731536) en verde con artifact de 8,01 MB. Pendiente: configurar los 4 secrets y ejecutar el workflow de release / subir el AAB a Play. Commit `e7e2d7b`. |
| 2026-11-08 | Post-plan | **IDs reales de AdMob:** `ads.config.json` con `testMode: false`, App ID `ca-app-pub-4783563714223320~9577805134`, banner `/3316308259` e interstitial `/6158094012`. Build debug run [#42543483026](https://github.com/linuxcoro/finanbcv/actions/runs/42543483026) en verde (artifact 8,01 MB). AdMob mantiene el servicio limitado hasta vincular la tienda en Play y aprobar la app. Commit `fe88463`. |

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

**Estado:** ✅ hecho (mejora posterior a los pasos 1–5; fuente actualizada a GitHub).

- `index.html` muestra las tasas oficiales **USD** y **EUR** del BCV con fecha valor y hora de actualización, y un botón **Actualizar**.
- Al cargar y al pulsar el botón descarga `tasas.json` desde `https://raw.githubusercontent.com/linuxcoro/finanbcv/main/tasas.json` (con `?t=…` para evitar la caché); si no hay red usa las últimas tasas guardadas en `localStorage.finanbcv_tasas`.
- La tasa del dólar se rellena automáticamente en el campo **Tasa BCV (Bs/$)** sin pisar una tasa personalizada; la tarjeta USD permite reaplicarla y la del euro se muestra como referencia.
- `bcv_server.py` conserva `GET /app`, `GET /tasas.json` y `POST /api/actualizar`, aunque la app ya no usa ese endpoint para actualizarse.
- El workflow del APK copia `index.html` y `tasas.json` a `www/`; la app empaquetada descarga las tasas de GitHub en tiempo de ejecución.
- Documentación actualizada en `README_tasas.md` y `documentaci_n_de_la_aplicaci_n.md`.

## 10. Mejora posterior — Compartir el Pago Móvil por cualquier red social

**Estado:** ✅ hecho (mejora posterior; APK regenerado en CI).

- El botón **Pago Móvil** abre directamente el selector nativo de apps (WhatsApp, Telegram, Instagram, SMS, correo, etc.) en vez de mostrar siempre el modal con el texto.
- En el APK se usa el plugin oficial `@capacitor/share` (Android `Intent.ACTION_SEND`); en navegadores compatibles se usa la Web Share API.
- Si no hay selector disponible (por ejemplo, un navegador de escritorio sin Web Share), se mantiene el modal con **Copiar Texto** y **Compartir en redes**.
- El workflow **Build APK** instala `@capacitor/share@6`, por lo que el plugin aparece en `capacitor.plugins.json` y queda disponible en el APK.
- APK regenerado: run [#42523675049](https://github.com/linuxcoro/finanbcv/actions/runs/42523675049), artifact `FinanBCV-apk` (3.383.095 bytes).
- Documentación actualizada en `documentaci_n_de_la_aplicaci_n.md`. Commit: `feat: compartir Pago Móvil por cualquier app o red social`.

## 11. Mejora posterior — Monetización con AdMob (integración)

**Estado:** ✅ integrada y validada en CI (run [#42529926855](https://github.com/linuxcoro/finanbcv/actions/runs/42529926855), 13/13 pasos en verde); pendiente publicar en Play y verificar la app en AdMob para que sirva anuncios reales.

- La app integra el plugin nativo `@capacitor-community/admob` (Google Mobile Ads SDK 25.x + UMP) mediante el módulo `window.Ads` de `index.html`: banner adaptativo abajo, interstitial en cortes naturales (registrar crédito y cerrar el comprobante de un abono), consentimiento UMP y botón **Privacidad y anuncios** en Ajustes.
- Por defecto el APK usa los **IDs de prueba de Google**. Los IDs reales se configuran en `ads.config.json` (versionado, con `"testMode": false`) o, alternativamente, con las variables de Actions `ADMOB_APP_ID`, `ADMOB_BANNER_ID`, `ADMOB_INTERSTITIAL_ID` y `ADMOB_TEST_MODE=false` (las variables tienen prioridad).
- Nuevo script `scripts/admob-build-config.mjs` (idempotente): genera `www/ads-config.js` y parchea `AndroidManifest.xml` / `strings.xml` del proyecto Android que se genera en CI.
- El workflow **Build APK** sube a Capacitor 8 (Node 22, Java 21, `android-36`/`build-tools 36.0.0`, `targetSdk 36`) e instala `@capacitor-community/admob@8.3.0`; verifica el meta-data de AdMob, el plugin y `ads-config.js` dentro del APK antes de subir el artifact.
- El banner se oculta con los modales abiertos, reserva su alto con la variable CSS `--admob-banner-h` y no se muestra si no hay consentimiento, internet o Google Play Services.
- AdMob **no paga** por un APK instalado a mano: queda documentado el checklist de publicación (Play, `app-ads.txt`, verificación de AdMob, firma release y datos de cobro) en `documentaci_n_de_la_aplicaci_n.md`.

## 12. Mejora posterior — Respaldo de datos y firma release para Play

**Estado:** ✅ respaldo validado en CI (run [#42536731536](https://github.com/linuxcoro/finanbcv/actions/runs/42536731536)); workflow de release listo, pendiente configurar los 4 secrets de firma y subir el AAB a Play (prueba interna).

- **Respaldo y restauración:** en **Ajustes → Respaldo y restauración** se genera un JSON con créditos, ajustes y tema; se puede copiar, compartir por el selector nativo (WhatsApp, Telegram, correo…) y restaurar con confirmación. Validado en Chrome headless: exportar → borrar → restaurar recupera créditos, ajustes y tema; un texto inválido no modifica los datos.
- **Firma release estable:** nuevo workflow manual `.github/workflows/build-release.yml` (Node 22, Java 21, SDK 36) que compila `bundleRelease` + `assembleRelease`, firma el AAB con `jarsigner` y el APK con `zipalign` + `apksigner` usando la clave de carga de los secrets `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS` y `ANDROID_KEY_PASSWORD`.
- **versionCode/versionName automáticos:** `scripts/patch-android-version.mjs` los calcula como `run_number * 100 + run_attempt` para que Play acepte cada subida.
- `.gitignore` excluye `.release/`, `*.jks`, `*.keystore` y `key.properties`; el keystore se entrega aparte y nunca se versiona.
- El APK release se firma con la misma clave en cada build, así que instalar/actualizar deja de fallar por firmas distintas.
- Documentación actualizada con el paso a paso de secrets, AAB y prueba interna de Play.

## 13. Mejora posterior — Selección EUR, mensaje de tasas e historial inline

**Estado:** ✅ hecho.

- La tarjeta **EURO · EUR** ahora es un botón como la del dólar: al tocarla aplica su tasa exacta al campo **Tasa BCV**, que cambia la etiqueta a `(Bs/€)` y el badge del formulario a `Tasa BCV · EUR`. La tarjeta activa se resalta y una tasa escrita a mano deja de mostrarse como aplicada.
- El autocompletado usa `lastAutoRate`/`lastAutoCurrency`: si el usuario eligió EUR, una actualización posterior refresca con el euro y no lo pisa con USD; una tasa personalizada se conserva.
- Se eliminó el mensaje fijo `Tasas actualizadas desde GitHub. Toca el dólar para usarlo en la calculadora.`; el estado queda oculto al éxito y se conservan los avisos de carga, respaldo sin conexión y error. El toast breve de la actualización manual se mantiene.
- El **historial de pagos** se muestra directamente al final de cada tarjeta de Créditos Activos, con parte, fecha, montos `$`/`Bs`, total abonado, estado vacío y resumen de créditos heredados. Se retiraron el botón “Historial de pagos (N)” y el modal `#modalHistory`.
- Verificado con `node --check` sobre el JS inline y una prueba headless en Chrome (27 comprobaciones PASS: tasas, EUR, persistencia tras actualizar, tasa manual, historial vacío/heredado/actualizado y aviso sin conexión), además de capturas móvil/escritorio.
- Documentación actualizada en `documentaci_n_de_la_aplicaci_n.md` y `README_tasas.md`; sin cambios en el esquema de `finanbcv_credits`, en `payments` ni en el formato de respaldo.

## 14. Mejora posterior — Moneda activa ($/€) en formulario y Créditos Activos

**Estado:** ✅ hecho.

- Al tocar la tarjeta **USD** o **EUR**, el formulario completo cambia de moneda: la etiqueta pasa a **Monto Total ($ USD)** o **Monto Total (€ EUR)**, el prefijo del campo y los cálculos en vivo usan `$` o `€`, la etiqueta de la tasa queda en `(Bs/$)` o `(Bs/€)` y el badge en `Tasa BCV` o `Tasa BCV · EUR`.
- La moneda elegida es un estado único (`formCurrency`) que también decide con qué tasa se autocompleta el campo en cada actualización; se guarda en `localStorage` (`finanbcv_moneda`) y se conserva tras registrar un crédito o recargar la app. Sustituye a `lastAutoCurrency`.
- Cada crédito guarda `currency` (`usd`/`eur`). **Créditos Activos**, el historial de pagos y el mensaje de **Pago Móvil** muestran el símbolo correcto del crédito (`$` o `€`), sin mezclarlo con la tasa elegida después. El desglose indica además el código de la moneda (`USD`/`EUR`).
- Compatibilidad: los créditos y respaldos antiguos sin `currency` se asumen en dólares (`usd`) y no cambian sus montos; al restaurar un respaldo o guardar de nuevo, el campo se completa. El formato de respaldo sigue siendo la versión 1 (campo aditivo).
- Verificado con `node --check` sobre los scripts inline y una prueba headless en Chrome con 58 comprobaciones PASS: selección USD→EUR→USD, etiquetas/prefijo/resultados, tasa manual, alta de crédito EUR y USD, historial y Pago Móvil en `€`, crédito heredado sin `currency`, respaldo y persistencia entre recargas (la moneda EUR vuelve y autocompleta la tasa correcta).
- Captura móvil (430 px) revisada visualmente en modo EUR: formulario, resultado `€150,00`, tarjeta EUR con `Bs/€` y tarjeta heredada en `$`.
- Documentación actualizada en `documentaci_n_de_la_aplicaci_n.md` (características, guía de uso, esquema JSON y `localStorage`) y `README_tasas.md`.

## 15. Mejora posterior — Lectura autorizada de tasas (repo privado)

**Estado:** ✅ hecho.

- `index.html` ya no descarga el raw: consulta la API de contenidos de GitHub con un PAT de solo lectura (`Accept: application/vnd.github.raw` + `Authorization`). El token no está en el repo: se inyecta al compilar el APK desde el secreto `BCV_TASAS_PAT` mediante `scripts/inject-rates-token.mjs`.
- Los workflows `build-apk.yml` y `build-release.yml` ejecutan la inyección antes de `cap sync`; `www/` sigue ignorado por git. Sin token (web desde el repo o `file://`), la app usa las últimas tasas de `localStorage`.
- Advertencia: el PAT es extraíble del APK; no publicar en Play Store con ese token. Antes de publicar, dejar el JSON público o usar un intermediario.
- Validación: `index.html` no lee `$GITHUB_TOKEN` ni variables de entorno; la cadena real es `BCV_TASAS_PAT` → inyección en `www/index.html` → `assets/public/index.html` del APK. Los workflows ahora fallan si el marcador `__RATES_PAT__` sobrevive en la copia compilada o en el APK/AAB.
- Documentación actualizada en `README_tasas.md` y `documentaci_n_de_la_aplicaci_n.md`.
