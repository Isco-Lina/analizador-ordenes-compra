from decimal import Decimal

from src.moneda import convertir_numero


TOLERANCIAS = {
    "CLP": Decimal("1"),
    "USD": Decimal("0.01"),
    "EUR": Decimal("0.01"),
    "UF": Decimal("0.0001"),
}


def buscar_monto_en_linea(
    palabras,
    y_objetivo,
    moneda,
    tolerancia=2,
):
    """Busca el monto ubicado a la derecha de una línea."""

    candidatos = []

    for palabra in palabras:

        x0, y0, x1, y1, texto, bloque, linea, posicion = palabra

        if (
            x0 >= 520
            and abs(y0 - y_objetivo) <= tolerancia
        ):

            valor = convertir_numero(
                texto,
                moneda,
            )

            candidatos.append(
                (
                    x0,
                    texto,
                    valor,
                )
            )

    if not candidatos:
        return Decimal("0")

    candidatos.sort(
        key=lambda item: item[0]
    )

    return candidatos[-1][2]


def extraer_totales(paginas, moneda):
    """Extrae los totales generales de una OC."""

    totales = {
        "subtotal": Decimal("0"),
        "descuento": Decimal("0"),
        "cargos": Decimal("0"),
        "neto": Decimal("0"),
        "iva": Decimal("0"),
        "otros_impuestos": Decimal("0"),
        "total": Decimal("0"),
    }

    for pagina in paginas:

        palabras = pagina["palabras"]

        for palabra in palabras:

            (
                x0,
                y0,
                x1,
                y1,
                texto,
                bloque,
                linea,
                posicion,
            ) = palabra

            texto_mayuscula = texto.upper().strip()

            if (
                texto_mayuscula == "SUB"
                and x0 > 450
            ):

                totales["subtotal"] = (
                    buscar_monto_en_linea(
                        palabras,
                        y0,
                        moneda,
                    )
                )

            elif (
                texto_mayuscula == "DESCUENTOS"
                and x0 > 450
            ):

                totales["descuento"] = (
                    buscar_monto_en_linea(
                        palabras,
                        y0,
                        moneda,
                    )
                )

            elif (
                texto_mayuscula == "CARGOS"
                and x0 > 450
            ):

                totales["cargos"] = (
                    buscar_monto_en_linea(
                        palabras,
                        y0,
                        moneda,
                    )
                )

            elif (
                texto_mayuscula == "NETO"
                and x0 > 450
            ):

                totales["neto"] = (
                    buscar_monto_en_linea(
                        palabras,
                        y0,
                        moneda,
                    )
                )

            elif (
                texto_mayuscula in ("I.V.A", "IVA")
                and x0 > 450
            ):

                totales["iva"] = (
                    buscar_monto_en_linea(
                        palabras,
                        y0,
                        moneda,
                    )
                )

            elif (
                texto_mayuscula == "OTROS"
                and x0 > 430
            ):

                totales["otros_impuestos"] = (
                    buscar_monto_en_linea(
                        palabras,
                        y0,
                        moneda,
                    )
                )

            elif (
                texto_mayuscula == "TOTAL"
                and x0 > 450
            ):

                existe_sub = any(
                    otra[4].upper().strip() == "SUB"
                    and abs(otra[1] - y0) <= 2
                    for otra in palabras
                )

                if not existe_sub:

                    totales["total"] = (
                        buscar_monto_en_linea(
                            palabras,
                            y0,
                            moneda,
                        )
                    )

    return totales


def validar_totales(totales, moneda):
    """Comprueba que los totales generales sean coherentes."""

    total = totales["total"]

    if total <= 0:
        return False

    total_calculado = (
        totales["neto"]
        + totales["iva"]
        + totales["otros_impuestos"]
    )

    diferencia = abs(
        total_calculado - total
    )

    tolerancia = TOLERANCIAS.get(
        moneda,
        Decimal("0.01"),
    )

    return diferencia <= tolerancia