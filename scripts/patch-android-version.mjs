#!/usr/bin/env node
/**
 * Ajusta versionCode y versionName del proyecto Android generado por
 * `npx cap add android` (la carpeta `android/` no se versiona).
 *
 * Google Play exige que cada AAB subido tenga un versionCode mayor que el
 * anterior, por eso el workflow de release lo calcula a partir del número de
 * ejecución de GitHub Actions.
 *
 * Variables de entorno:
 *   APP_VERSION_CODE  entero positivo (por defecto 1)
 *   APP_VERSION_NAME  texto (por defecto "1.0")
 */

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const BUILD_GRADLE = join(process.cwd(), 'android/app/build.gradle');

const log = (message) => console.log(`[version] ${message}`);
const fail = (message) => {
    console.error(`[version] ERROR: ${message}`);
    process.exit(1);
};

const versionCode = (process.env.APP_VERSION_CODE || '').trim() || '1';
const versionName = (process.env.APP_VERSION_NAME || '').trim() || '1.0';

if (!/^\d+$/.test(versionCode) || Number(versionCode) < 1) {
    fail(`APP_VERSION_CODE inválido: "${versionCode}" (debe ser un entero >= 1).`);
}
if (!versionName) {
    fail('APP_VERSION_NAME está vacío.');
}

if (!existsSync(BUILD_GRADLE)) {
    fail('No existe android/app/build.gradle. Ejecuta el script después de "npx cap add android".');
}

let gradle = readFileSync(BUILD_GRADLE, 'utf8');

// La plantilla de Capacitor usa la forma Groovy `versionCode 1` /
// `versionName "1.0"`. Se conserva el separador por si alguna versión futura
// usa `versionCode = 1`.
const codeMatch = gradle.match(/versionCode(\s*=?\s*)\d+/);
if (!codeMatch) {
    fail('No se encontró "versionCode" en android/app/build.gradle.');
}
gradle = gradle.replace(/versionCode(\s*=?\s*)\d+/, `versionCode${codeMatch[1]}${versionCode}`);

const nameMatch = gradle.match(/versionName(\s*=?\s*)"[^"]*"/);
if (!nameMatch) {
    fail('No se encontró "versionName" en android/app/build.gradle.');
}
gradle = gradle.replace(/versionName(\s*=?\s*)"[^"]*"/, `versionName${nameMatch[1]}"${versionName}"`);

writeFileSync(BUILD_GRADLE, gradle, 'utf8');
log(`versionCode = ${versionCode}`);
log(`versionName = "${versionName}"`);
