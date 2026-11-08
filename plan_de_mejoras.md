# Plan de mejoras — FinanBCV

**Fecha:** 2026-11-08 · **Estado global:** ✅ 5 de 5 pasos ejecutados en local (pendiente el push a GitHub) · Historial de pagos: ✅ añadido como mejora posterior · Pago inicial: ✅ eliminado
**Archivo de la app:** `index.html` (602 líneas, SPA de un solo archivo)
**Documentación:** `documentaci_n_de_la_aplicaci_n.md`

> Este documento es el plan de trabajo **por pasos**. Los pasos 1–5 están ejecutados en local (ver Bitácora); solo queda el `git push` a GitHub, que requiere las credenciales del usuario. El **workflow de GitHub** fue deliberadamente el último, por pedido del usuario. Al cerrar cada paso se marca el estado (`✅ hecho`), se actualiza la tabla y se añade una línea a la Bitácora.

---

## 1. Objetivo y criterios de éxito

Corregir las inconsistencias detectadas en la aplicación y dejarla lista para compilarse como APK, ejecutando el trabajo por pasos.

Se considera terminado cuando:

1. El archivo de la app se llama `index.html` (requisito de la documentación para GitHub/APK) y el proyecto es un repositorio git con un commit por paso.
2. La tarjeta de crédito muestra la **inicial pagada**, no solo el total y la cuota.
3. El mensaje de Pago Móvil indica la **parte/cuota correcta** ("Parte 2 de 3"; "Parte a pagar: 1 de N" si aún no hay abonos) y ya no queda la variable muerta `currentInstallmentNum`.
4. La documentación refleja la realidad: nombre del archivo, funcionalidad y workflow existente.
5. Existe `.github/workflows/build-apk.yml` que produce un **APK debug** descargable como artifact, validado sintácticamente en local.

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
| 5 | **Último:** workflow de GitHub Actions para el APK | ✅ hecho en local / pendiente el push |

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

## Paso 5 — ÚLTIMO: workflow de GitHub Actions para el APK

**Archivos nuevos:** `.github/workflows/build-apk.yml` y `capacitor.config.json` (identidad de la app versionada).

`capacitor.config.json`:

```json
{
  "appId": "com.finanbcv.app",
  "appName": "FinanBCV",
  "webDir": "www",
  "server": { "androidScheme": "https" }
}
```

`build-apk.yml`:

- Disparadores: `push` a `main` y `workflow_dispatch`. `permissions: contents: read`.
- Runner `ubuntu-latest`, con estos pasos en orden:
  1. `actions/checkout@v4`
  2. `actions/setup-node@v4` con Node 20.
  3. `actions/setup-java@v4` con temurin **17** (requisito de Capacitor 6).
  4. `android-actions/setup-android@v3`.
  5. `npm init -y` y `npm install @capacitor/core@6 @capacitor/cli@6 @capacitor/android@6` (versiones fijadas para no depender de Java 21).
  6. `mkdir -p www && cp index.html www/index.html`.
  7. `npx cap add android && npx cap sync android`.
  8. `cd android && chmod +x gradlew && ./gradlew assembleDebug --no-daemon`.
  9. `actions/upload-artifact@v4` publicando `android/app/build/outputs/apk/debug/app-debug.apk` como `FinanBCV-apk`.
- Validación local: parsear el YAML con PyYAML, revisar la indentación de las claves de Actions y confirmar que no hay secretos.
- Commit: `ci: compilar APK Android con Capacitor en GitHub Actions`.
- Cierre: marcar este paso como "hecho en local / pendiente el push" y añadir la lista manual para el usuario:

  ```bash
  git remote add origin https://github.com/<usuario>/finanbcv.git
  git push -u origin main
  ```

  Después: pestaña **Actions** → workflow "Build APK" → descargar el artifact → instalar.

  **Estado:** ✅ hecho en local / pendiente el push (requiere las credenciales del usuario).

**Plan B:** si el build de Capacitor fallara en CI, publicar como artifact un `.zip` con `index.html` (no bloquea los pasos 1–4).

**Aceptación:** el YAML parsea sin errores, la estructura de pasos es válida y el workflow queda listo para ejecutarse al hacer push.

---

## 4. Verificación (aplicable a los pasos 2–4)

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
- **Grep de control:** `grep -rn "gestor_de_ventas_financiadas_bcv\|currentInstallmentNum" .` no debe devolver resultados en código/documentación (solo pueden quedar referencias históricas en este mismo plan).

## 5. Riesgos y reversión

- El rename se hace con `git mv` después del commit inicial, por lo que es recuperable con `git checkout`.
- Los cambios no alteran el esquema de `localStorage`: no hay migración ni pérdida de datos de créditos.
- El APK depende de CDNs (sin internet no hay estilos ni iconos) y de versiones fijadas de Capacitor; se documenta como limitación y su fallo afecta solo a ese archivo.
- No se modifica ni se elimina ningún crédito del usuario.
- El push a GitHub requiere credenciales del usuario: el agente deja el commit local listo y documenta el comando.

## 6. Bitácora

| Fecha | Paso | Resultado |
|-------|------|-----------|
| 2026-11-08 | — | Plan creado. Ningún paso ejecutado todavía; el repositorio sigue con `gestor_de_ventas_financiadas_bcv.html` y `documentaci_n_de_la_aplicaci_n.md`. |
| 2026-11-08 | 1 | Repositorio git creado en rama `main` con commit inicial de los 3 archivos; rename con `git mv` de `gestor_de_ventas_financiadas_bcv.html` a `index.html`. Único HTML de la raíz y app sin rutas relativas. |
| 2026-11-08 | 2 | `renderCredits()` muestra la celda "Inicial (X%)" con `$X (Bs Y)` junto a "Total Venta" (fallback 0 % para créditos heredados) y "Monto por Cuota" pasa a fila `col-span-2`. Verificado con arnés Node sobre el JS inline: $100 al 30 % → `$30.00 (Bs 1.095,00)`; sin `initialPercent` → `$0.00 (Bs 0,00)`. |
| 2026-11-08 | 3 | `prepareShareMessage()` elimina la variable muerta `currentInstallmentNum` y calcula `paidParts`; el mensaje muestra `🧾 *Parte a pagar:* paidParts+1 de N` o `Parte N de N` al liquidar. Verificado: 3 partes con 1 abono → "Parte a pagar: 2 de 3" y "Te restan 2 parte(s)"; sin abonos → "1 de N"; liquidado → "Parte 3 de 3". Se corrigieron también el comando de extracción JS del §4 y el smoke para que coincidan con la numeración "Parte a pagar". |
| 2026-11-08 | 4 | `documentaci_n_de_la_aplicaci_n.md` actualizada: nombre `index.html`, características de la inicial en la tarjeta y del comprobante automático al abonar, estructura del repositorio, guía APK reescrita (workflow, disparadores, artifact en Actions, instalación por fuentes desconocidas o `adb`), limitación de CDN y referencia al plan como roadmap. Verificado: sin referencias al nombre viejo. |
| 2026-11-08 | 5 | `capacitor.config.json` y `.github/workflows/build-apk.yml` creados: disparadores `push` a `main` + `workflow_dispatch`, `permissions: contents: read`, Ubuntu + Node 20 + Java 17 (temurin) + Android SDK, Capacitor 6 con versiones fijadas, copia de `index.html` a `www/`, `assembleDebug` y artifact `FinanBCV-apk`. Validado en local con PyYAML y comprobación de estructura (24/24 PASS, sin secretos). **Pendiente solo el push** (`git remote add origin …` + `git push -u origin main`). |
| 2026-11-08 | Post-plan | **Historial de pagos por crédito:** campo aditivo `payments` en `finanbcv_credits`, botón "Historial de pagos (N)" en cada tarjeta y modal con la inicial + abonos (fecha, parte, $ y Bs), compatible con créditos heredados (resumen "pagos anteriores sin detalle"). Documentación actualizada. Commit `feat: mostrar historial de pagos por crédito`. |
| 2026-11-08 | Post-plan | Se quitó la inicial del historial de pagos: ahora solo lista abonos de cuota y el total mostrado es el de cuotas. En ese momento la tarjeta aún mostraba la inicial. Documentación actualizada. Commit `fix: excluir la inicial del historial de pagos`. |
| 2026-11-08 | Post-plan | Se eliminó el **% de pago inicial**: sin campo en el formulario, sin "Monto Inicial" en el resumen y sin celda "Inicial (X%)" en la tarjeta; el cálculo ahora financia el monto total (`cuota = totalUsd / partes`) y los créditos nuevos no guardan `initialPercent` (los antiguos se leen igual). Documentación actualizada. Commit `refactor: eliminar el % de pago inicial`. |

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
