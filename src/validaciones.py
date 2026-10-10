from decimal import Decimal


TOLERANCIAS_SUBTOTAL = {
    "CLP": Decimal("3"),
    "USD": Decimal("0.05"),
    "EUR": Decimal("0.05"),
    "UF": Decimal("0.0001"),
}


def sumar_totales_articulos(articulos):
    """Suma los totales de todos los artículos."""

    return sum(
        (
            articulo["total_linea"]
            for articulo in articulos
        ),
        Decimal("0"),
    )


def validar_subtotal_articulos(
    articulos,
    subtotal,
    moneda,
):
    """Compara los artículos con el subtotal de la OC."""

    if not articulos:
        return False

    suma_articulos = (
        sumar_totales_articulos(
            articulos
        )
    )

    diferencia = abs(
        suma_articulos - subtotal
    )

    tolerancia = TOLERANCIAS_SUBTOTAL.get(
        moneda,
        Decimal("0.01"),
    )

    return diferencia <= tolerancia