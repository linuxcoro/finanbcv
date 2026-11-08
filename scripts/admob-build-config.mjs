#!/usr/bin/env node
/**
 * Configura AdMob para el build del APK de FinanBCV.
 *
 * Lo usa el workflow "Build APK" de GitHub Actions, que genera la carpeta
 * `android/` desde cero en cada ejecución (no se versiona). El script:
 *
 *   1. Escribe `www/ads-config.js` con los IDs de anuncio que consumirá la app.
 *   2. Parchea `android/app/src/main/AndroidManifest.xml` para declarar el
 *      Application ID de AdMob (meta-data que exige el SDK de Google).
 *   3. Parchea `android/app/src/main/res/values/strings.xml` con `admob_app_id`.
 *
 * Es idempotente: se puede ejecutar antes de `npx cap add android` (solo escribe
 * la config web) y otra vez después (parchea el proyecto nativo). Si la carpeta
 * `android/` todavía no existe, avisa y continúa.
 *
 * Variables de entorno:
 *   ADMOB_TEST_MODE        "true" (por defecto) usa los IDs de PRUEBA de Google.
 *   ADMOB_APP_ID           App ID real, formato ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX
 *   ADMOB_BANNER_ID        Unidad de banner, formato ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX
 *   ADMOB_INTERSTITIAL_ID  Unidad de interstitial, mismo formato que el banner.
 *
 * Con ADMOB_TEST_MODE=false los tres IDs reales son obligatorios; si falta uno
 * el script falla para no publicar una app con IDs de prueba mezclados.
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = process.cwd();
const WWW_DIR = join(ROOT, 'www');
const WWW_CONFIG = join(WWW_DIR, 'ads-config.js');
const ANDROID_DIR = join(ROOT, 'android');
const MANIFEST = join(ANDROID_DIR, 'app/src/main/AndroidManifest.xml');
const STRINGS = join(ANDROID_DIR, 'app/src/main/res/values/strings.xml');

const APP_ID_META = 'com.google.android.gms.ads.APPLICATION_ID';

// IDs de prueba oficiales de Google: sirven siempre y no generan tráfico inválido.
const TEST_IDS = {
    appId: 'ca-app-pub-3940256099942544~3347511713',
    bannerId: 'ca-app-pub-3940256099942544/6300978111',
    interstitialId: 'ca-app-pub-3940256099942544/1033173712'
};

const APP_ID_RE = /^ca-app-pub-\d{16}~\d{10}$/;
const UNIT_ID_RE = /^ca-app-pub-\d{16}\/\d{10}$/;

const log = (message) => console.log(`[admob] ${message}`);
const fail = (message) => {
    console.error(`[admob] ERROR: ${message}`);
    process.exit(1);
};

const env = (name) => (process.env[name] || '').trim();

const testMode = env('ADMOB_TEST_MODE').toLowerCase() !== 'false';

let ads;
if (testMode) {
    ads = { ...TEST_IDS };
} else {
    ads = {
        appId: env('ADMOB_APP_ID'),
        bannerId: env('ADMOB_BANNER_ID'),
        interstitialId: env('ADMOB_INTERSTITIAL_ID')
    };
    if (!APP_ID_RE.test(ads.appId)) {
        fail(`ADMOB_APP_ID inválido o ausente: "${ads.appId}" (formato ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX).`);
    }
    if (!UNIT_ID_RE.test(ads.bannerId)) {
        fail(`ADMOB_BANNER_ID inválido o ausente: "${ads.bannerId}" (formato ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX).`);
    }
    if (!UNIT_ID_RE.test(ads.interstitialId)) {
        fail(`ADMOB_INTERSTITIAL_ID inválido o ausente: "${ads.interstitialId}" (formato ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX).`);
    }
}

/* ------------------------------------------------------------------ */
/* 1. Config web (window.FINANBCV_ADS)                                 */
/* ------------------------------------------------------------------ */

function writeWebConfig() {
    const config = {
        enabled: true,
        testMode,
        appId: ads.appId,
        bannerId: ads.bannerId,
        interstitialId: ads.interstitialId
    };
    const content = [
        '/* Generado por scripts/admob-build-config.mjs — no editar a mano. */',
        `window.FINANBCV_ADS = ${JSON.stringify(config, null, 4)};`,
        ''
    ].join('\n');
    mkdirSync(WWW_DIR, { recursive: true });
    writeFileSync(WWW_CONFIG, content, 'utf8');
    log(`www/ads-config.js escrito (${testMode ? 'anuncios de PRUEBA' : 'anuncios REALES'}).`);
}

/* ------------------------------------------------------------------ */
/* 2. AndroidManifest.xml                                              */
/* ------------------------------------------------------------------ */

function patchManifest() {
    if (!existsSync(MANIFEST)) {
        log('android/app/src/main/AndroidManifest.xml todavía no existe; se omite el parche nativo.');
        return;
    }
    let xml = readFileSync(MANIFEST, 'utf8');

    if (!xml.includes('android.permission.INTERNET')) {
        const manifestTag = xml.match(/<manifest\b[^>]*>/);
        if (!manifestTag) {
            fail('AndroidManifest.xml no tiene la etiqueta <manifest>.');
        }
        xml = xml.replace(manifestTag[0], `${manifestTag[0]}\n    <uses-permission android:name="android.permission.INTERNET" />`);
        log('AndroidManifest.xml: permiso INTERNET agregado.');
    }

    const metaRe = new RegExp(`<meta-data[^>]*android:name="${APP_ID_META.replace(/\./g, '\\.')}"[^>]*/>`);
    if (metaRe.test(xml)) {
        log('AndroidManifest.xml: meta-data de AdMob ya presente; no se duplica.');
    } else {
        const applicationTag = xml.match(/<application\b[^>]*>/);
        if (!applicationTag) {
            fail('AndroidManifest.xml no tiene la etiqueta <application>.');
        }
        xml = xml.replace(
            applicationTag[0],
            `${applicationTag[0]}\n        <meta-data\n            android:name="${APP_ID_META}"\n            android:value="@string/admob_app_id" />`
        );
        log('AndroidManifest.xml: meta-data APPLICATION_ID agregada.');
    }

    writeFileSync(MANIFEST, xml, 'utf8');
}

/* ------------------------------------------------------------------ */
/* 3. res/values/strings.xml                                           */
/* ------------------------------------------------------------------ */

function patchStrings() {
    if (!existsSync(STRINGS)) {
        log('android/app/src/main/res/values/strings.xml todavía no existe; se omite el parche nativo.');
        return;
    }
    let xml = readFileSync(STRINGS, 'utf8');
    const stringRe = /<string name="admob_app_id">[^<]*<\/string>/;

    if (stringRe.test(xml)) {
        xml = xml.replace(stringRe, `<string name="admob_app_id">${ads.appId}</string>`);
        log('strings.xml: admob_app_id actualizado.');
    } else {
        if (!xml.includes('</resources>')) {
            fail('strings.xml no tiene </resources>.');
        }
        xml = xml.replace(
            '</resources>',
            `    <string name="admob_app_id">${ads.appId}</string>\n</resources>`
        );
        log('strings.xml: admob_app_id agregado.');
    }

    writeFileSync(STRINGS, xml, 'utf8');
}

/* ------------------------------------------------------------------ */

writeWebConfig();
patchManifest();
patchStrings();
log(`modo: ${testMode ? 'PRUEBA' : 'REAL'} · app ${ads.appId} · banner ${ads.bannerId} · interstitial ${ads.interstitialId}`);
