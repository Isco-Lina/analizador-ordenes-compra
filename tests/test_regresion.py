import unittest
from decimal import Decimal
from pathlib import Path

from src.extractor import extraer_pdf
from src.parser_oc import parsear_oc
from src.articulos import extraer_articulos
from src.totales import extraer_totales, validar_totales
from src.moneda import detectar_moneda
from src.validaciones import validar_subtotal_articulos


CARPETA_PDF = Path("data/pdf")


CASOS = {
    "RM-HCN-2307": {
        "archivo": "Documento RM-HCN-2307.pdf",
        "paginas": 2,
        "moneda": "EUR",
        "articulos": 27,
        "total": Decimal("9294.15"),
    },
    "RM-HCN-2451": {
        "archivo": "Documento RM-HCN-2451.pdf",
        "paginas": 2,
        "moneda": "USD",
        "articulos": 8,
        "total": Decimal("1808.01"),
    },
    "RM-HCN-2481": {
        "archivo": "Documento RM-HCN-2481.pdf",
        "paginas": 1,
        "moneda": "UF",
        "articulos": 3,
        "total": Decimal("143.5354"),
    },
    "RM-HCN-2482": {
        "archivo": "Documento RM-HCN-2482.pdf",
        "paginas": 1,
        "moneda": "CLP",
        "articulos": 5,
        "total": Decimal("8022701"),
    },
    "RM-HCN-2483": {
        "archivo": "Documento RM-HCN-2483.pdf",
        "paginas": 1,
        "moneda": "CLP",
        "articulos": 3,
        "total": Decimal("5918816"),
    },
    "RM-HCN-2487": {
        "archivo": "Documento RM-HCN-2487.pdf",
        "paginas": 1,
        "moneda": "CLP",
        "articulos": 1,
        "total": Decimal("409461"),
    },
}


def procesar_pdf(nombre_archivo):
    """Procesa un PDF utilizando los módulos reales del proyecto."""

    ruta = CARPETA_PDF / nombre_archivo

    texto, paginas, numero_paginas = extraer_pdf(ruta)

    datos = parsear_oc(texto, paginas)
    moneda = detectar_moneda(paginas)
    articulos = extraer_articulos(paginas, moneda)
    totales = extraer_totales(paginas, moneda)

    return {
        "datos": datos,
        "moneda": moneda,
        "articulos": articulos,
        "totales": totales,
        "numero_paginas": numero_paginas,
    }


class TestRegresionOC(unittest.TestCase):

    def test_seis_oc_principales(self):
        """Comprueba los resultados principales de las seis OC."""

        for numero_oc, esperado in CASOS.items():

            with self.subTest(oc=numero_oc):

                resultado = procesar_pdf(esperado["archivo"])

                datos = resultado["datos"]
                articulos = resultado["articulos"]
                totales = resultado["totales"]
                moneda = resultado["moneda"]

                self.assertEqual(
                    datos["numero_oc"],
                    numero_oc,
                )

                self.assertEqual(
                    resultado["numero_paginas"],
                    esperado["paginas"],
                )

                self.assertEqual(
                    moneda,
                    esperado["moneda"],
                )

                self.assertEqual(
                    len(articulos),
                    esperado["articulos"],
                )

                self.assertEqual(
                    totales["total"],
                    esperado["total"],
                )

                self.assertTrue(
                    validar_totales(totales, moneda)
                )

                self.assertTrue(
                    validar_subtotal_articulos(
                        articulos,
                        totales["subtotal"],
                        moneda,
                    )
                )

    def test_email_dialum(self):
        """Evita confundir el email del vendedor con el email bancario."""

        resultado = procesar_pdf(
            "Documento RM-HCN-2451.pdf"
        )

        self.assertEqual(
            resultado["datos"]["email"],
            "correo@no_registrado.cl",
        )

    def test_email_puntomaestro(self):
        """Conserva exactamente el email incompleto del PDF."""

        resultado = procesar_pdf(
            "Documento RM-HCN-2487.pdf"
        )

        self.assertEqual(
            resultado["datos"]["email"],
            "FMARTINEZ@PUNTOMAEST",
        )

    def test_solicitud_budnik(self):
        """Comprueba la solicitud 786 en ambas OC de Budnik."""

        archivos = [
            "Documento RM-HCN-2482.pdf",
            "Documento RM-HCN-2483.pdf",
        ]

        for archivo in archivos:

            with self.subTest(archivo=archivo):

                resultado = procesar_pdf(archivo)

                self.assertEqual(
                    resultado["datos"]["solicitud"],
                    "786",
                )

    def test_transporte_aereo_cortizo(self):
        """Comprueba que el último artículo de la OC 2307 exista."""

        resultado = procesar_pdf(
            "Documento RM-HCN-2307.pdf"
        )

        articulos = resultado["articulos"]

        self.assertEqual(len(articulos), 27)

        ultimo = articulos[-1]

        self.assertEqual(
            ultimo["numero"],
            27,
        )

        self.assertIn(
            "TRANSPORTE AEREO DAP",
            ultimo["descripcion"],
        )

        self.assertEqual(
            ultimo["cantidad"],
            Decimal("1.00"),
        )

        self.assertEqual(
            ultimo["precio_unitario"],
            Decimal("4000.00"),
        )

        self.assertEqual(
            ultimo["total_linea"],
            Decimal("4000.00"),
        )


if __name__ == "__main__":
    unittest.main()