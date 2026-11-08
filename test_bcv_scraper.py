#!/usr/bin/env python3
"""Pruebas del scraper de tasas BCV (sin red).

Ejecutar: python -m unittest test_bcv_scraper -v
"""

import unittest

from bcv_scraper import (
    formatear_es,
    parsear_numero_ve,
    extraer_tasas,
    contexto_html,
)

HTML_EJEMPLO = """
<div id="euro" class="col-sm-12 col-xs-12 ">
  <div class="field-content">
    <div class="row recuadrotsmc">
      <div class="col-sm-6 col-xs-6">
        <img src="/sites/default/files/euro-04_2.png" class="icono_bss_blanco1">
        <span style="display: inline; margin-left: 15px;"> EUR </span>
      </div>
      <div class="col-sm-6 col-xs-6 centrado textp"><strong class="strong-tb"> 1.001,18602288</strong> </div>
    </div>
  </div>
</div>

<div id="dolar" class="col-sm-12 col-xs-12 ">
  <div class="field-content">
    <div class="row recuadrotsmc">
      <div class="col-sm-6 col-xs-6">
        <img src="/sites/default/files/dollar-04_2.png" class="icono_bss_blanco1">
        <span style="display: inline; margin-left: 15px;"> USD</span>
      </div>
      <div class="col-sm-6 col-xs-6 centrado textp" style="padding-top:2px;">
        <strong class="strong-tb">897,53830000</strong>
      </div>
    </div>
  </div>
</div>
"""

HTML_CON_FECHA = HTML_EJEMPLO.replace(
    '<span style="display: inline; margin-left: 15px;"> USD</span>',
    '<span style="display: inline; margin-left: 15px;"> USD</span>'
    '<span property="dc:date" datatype="xsd:dateTime" '
    'content="2026-11-09T00:00:00-04:00" class="date-display-single">'
    'Lunes, 09 Noviembre  2026</span>',
)


class TestNumeros(unittest.TestCase):
    def test_parseo_venezolano(self):
        self.assertAlmostEqual(parsear_numero_ve("1.001,18602288"), 1001.18602288)
        self.assertAlmostEqual(parsear_numero_ve(" 897,53830000 "), 897.5383)
        self.assertAlmostEqual(parsear_numero_ve("1.234.567,89"), 1234567.89)
        self.assertAlmostEqual(parsear_numero_ve("0,50"), 0.5)

    def test_punto_decimal(self):
        self.assertAlmostEqual(parsear_numero_ve("897.5383"), 897.5383)

    def test_numero_invalido(self):
        with self.assertRaises(ValueError):
            parsear_numero_ve("sin números")
        with self.assertRaises(ValueError):
            parsear_numero_ve("")


class TestFormato(unittest.TestCase):
    def test_formato_venezolano(self):
        self.assertEqual(formatear_es(897.5383), "897,54")
        self.assertEqual(formatear_es(1001.18602288), "1.001,19")
        self.assertEqual(formatear_es(1001.18602288, 8), "1.001,18602288")
        self.assertEqual(formatear_es(897.5383, 8), "897,53830000")


class TestExtraerTasas(unittest.TestCase):
    def test_extrae_dolar_y_euro(self):
        tasas = extraer_tasas(HTML_EJEMPLO)
        self.assertAlmostEqual(tasas.usd, 897.5383)
        self.assertAlmostEqual(tasas.eur, 1001.18602288)
        self.assertIsNone(tasas.fecha_valor)
        datos = tasas.a_dict()
        self.assertEqual(datos["usd_bs"], "897,54")
        self.assertEqual(datos["eur_bs"], "1.001,19")
        self.assertEqual(datos["usd_exacta"], "897,53830000")

    def test_extrae_fecha_valor(self):
        tasas = extraer_tasas(HTML_CON_FECHA)
        self.assertEqual(tasas.fecha_valor, "2026-11-09")
        self.assertEqual(tasas.fecha_valor_texto, "Lunes, 09 Noviembre 2026")

    def test_html_incompleto(self):
        with self.assertRaises(Exception):
            extraer_tasas("<html><body>sin divs</body></html>")

    def test_contexto_html(self):
        contexto = contexto_html(extraer_tasas(HTML_EJEMPLO), en_servidor=False)
        self.assertIn("usd_bs", contexto)
        self.assertFalse(contexto["en_servidor"])
        self.assertFalse(contexto["stale"])

        vacio = contexto_html(None)
        self.assertIn("error", vacio)
        self.assertEqual(vacio["usd_bs"], "—")


if __name__ == "__main__":
    unittest.main()
