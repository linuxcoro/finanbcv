#!/usr/bin/env node
/**
 * Inyecta el PAT de solo lectura de GitHub en la copia de index.html que va
 * dentro del APK (www/index.html).
 *
 * El repositorio público solo contiene el marcador __RATES_PAT__; el token
 * real vive en el secreto BCV_TASAS_PAT de GitHub Actions y nunca se imprime.
 *
 * Uso local:
 *   BCV_TASAS_PAT=github_pat_... node scripts/inject-rates-token.mjs
 * (requiere haber copiado antes index.html a www/index.html).
 */

import { access, readFile, writeFile } from 'node:fs/promises';

const MARCADOR = '__RATES_PAT__';
const RUTA = new URL('../www/index.html', import.meta.url);

function fallar(mensaje) {
    console.error(`::error::${mensaje}`);
    process.exit(1);
}

const token = (process.env.BCV_TASAS_PAT || '').trim();

if (!token) {
    fallar(
        'Falta el secreto BCV_TASAS_PAT (PAT fine-grained con Contents: Read-only sobre linuxcoro/bcv_scraper). No se usa GITHUB_TOKEN.'
    );
}
if (token.includes(MARCADOR) || token.length < 20) {
    fallar('BCV_TASAS_PAT no parece un PAT válido.');
}

try {
    await access(RUTA);
} catch {
    fallar(
        'No existe www/index.html; ejecuta este script después de copiar index.html a www/.'
    );
}

const html = await readFile(RUTA, 'utf8');
const apariciones = html.split(MARCADOR).length - 1;
if (apariciones !== 1) {
    fallar(
        `Se esperaba exactamente un marcador ${MARCADOR} en www/index.html; hay ${apariciones}.`
    );
}

// Se usa una función de reemplazo para que un "$" en el token no se interprete.
const inyectado = html.replace(MARCADOR, () => token);
await writeFile(RUTA, inyectado, 'utf8');

// Verifica el archivo escrito: sin marcador y con la línea exacta del token.
const verificado = await readFile(RUTA, 'utf8');
if (verificado.includes(MARCADOR)) {
    fallar('La copia www/index.html todavía contiene el marcador __RATES_PAT__.');
}
const lineaToken = `const RATES_TOKEN = '${token}'`;
if (verificado.split(lineaToken).length - 1 !== 1) {
    fallar('No se pudo verificar la línea const RATES_TOKEN en www/index.html.');
}

console.log('PAT de GitHub inyectado en www/index.html (no se muestra).');
