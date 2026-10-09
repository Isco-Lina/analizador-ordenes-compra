from decimal import Decimal, InvalidOperation


MONEDAS = {
    "CLP": {
        "simbolo": "$",
        "nombre": "Peso chileno",
    },
    "USD": {
        "simbolo": "US$",
        "nombre": "Dólar estadounidense",
    },
    "EUR": {
        "simbolo": "EUR",
        "nombre": "Euro",
    },
    "UF": {
        "simbolo": "UF",
        "nombre": "Unidad de Fomento",
    },
}


def detectar_moneda(paginas):
    """Detecta la moneda utilizada en la OC."""

    # Primero busca monedas que tienen identificación explícita.
    for pagina in paginas:

        for palabra in pagina["palabras"]:

            texto = palabra[4].upper().strip()

            if texto.startswith("US$"):
                return "USD"

            if texto.startswith("EUR"):
                return "EUR"

            if texto.startswith("UF"):
                return "UF"

    # Si encuentra montos con $, corresponde a pesos chilenos.
    for pagina in paginas:

        for palabra in pagina["palabras"]:

            texto = palabra[4].strip()

            if texto.startswith("$"):
                return "CLP"

    return ""


def obtener_simbolo(moneda):
    """Devuelve el símbolo utilizado por cada moneda."""

    datos = MONEDAS.get(moneda, {})

    return datos.get("simbolo", "")


def limpiar_moneda(valor):
    """Elimina el símbolo de moneda del valor."""

    if valor is None:
        return ""

    valor = str(valor).strip()

    prefijos = [
        "US$",
        "EUR",
        "UF",
        "$",
    ]

    for prefijo in prefijos:

        if valor.upper().startswith(prefijo.upper()):
            return valor[len(prefijo):].strip()

    return valor


def convertir_numero(valor, moneda):
    """Convierte un valor monetario manteniendo su precisión."""

    if valor is None:
        return Decimal("0")

    valor = limpiar_moneda(valor)
    valor = valor.replace(" ", "")

    if not valor:
        return Decimal("0")

    # Pesos chilenos.
    if moneda == "CLP":

        # En CLP el punto se utiliza como separador de miles.
        valor = valor.replace(".", "")

        # Se mantiene soporte por si aparece una coma decimal.
        valor = valor.replace(",", ".")

    # USD, EUR y UF.
    elif moneda in ("USD", "EUR", "UF"):

        # El punto separa miles.
        valor = valor.replace(".", "")

        # La coma representa decimales.
        valor = valor.replace(",", ".")

    else:
        return Decimal("0")

    try:
        return Decimal(valor)

    except InvalidOperation:
        return Decimal("0")