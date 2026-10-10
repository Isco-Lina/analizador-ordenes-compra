import re


# Relaciona el código de la OC con cada hospital.
HOSPITALES = {
    "HCN": "Hospital de Constitución",
    "HPR": "Hospital de Parral",
    "HCQ": "Hospital de Cauquenes",
}


def buscar_patron(patron, texto, flags=0):
    """Busca un dato en el texto. Si no existe, devuelve vacío."""

    resultado = re.search(patron, texto, flags)

    if resultado:
        return resultado.group(1).strip()

    return ""


def limpiar_texto(texto):
    """Elimina espacios repetidos y espacios sobrantes."""

    if not texto:
        return ""

    return re.sub(r"[ \t]+", " ", texto).strip()


def extraer_numero_oc(texto):
    """Extrae el número de OC."""

    numero_oc = buscar_patron(
        r"\b(RM-(?:HCN|HPR|HCQ)-\d+)\b",
        texto,
        re.IGNORECASE,
    )

    return numero_oc.upper()


def obtener_hospital(numero_oc):
    """Identifica el hospital usando HCN, HPR o HCQ."""

    if not numero_oc:
        return "", ""

    partes = numero_oc.split("-")

    if len(partes) < 3:
        return "", ""

    codigo = partes[1].upper()
    hospital = HOSPITALES.get(codigo, "")

    return codigo, hospital


def extraer_fecha(texto):
    """Extrae la fecha de emisión de la OC."""

    return buscar_patron(
        r"Fecha:\s*(\d{2}-\d{2}-\d{4})",
        texto,
        re.IGNORECASE,
    )


def extraer_proveedor(texto):
    """Extrae el nombre o razón social del proveedor."""

    proveedor = buscar_patron(
        r"ADQUIERASE DE\s*:?\s*(.+?)(?=\s*DIRECCI[ÓO]N)",
        texto,
        re.IGNORECASE | re.DOTALL,
    )

    proveedor = proveedor.replace("\n", " ")

    return limpiar_texto(proveedor)


def extraer_rut_proveedor(texto):
    """Extrae el RUT del proveedor."""

    seccion = buscar_patron(
        r"ADQUIERASE DE(.*?)(?=CIUDAD)",
        texto,
        re.IGNORECASE | re.DOTALL,
    )

    if not seccion:
        return ""

    return buscar_patron(
        r"R\.?U\.?T\.?\s*:?\s*([\d\.]+-[\dkK])",
        seccion,
        re.IGNORECASE,
    )

def extraer_direccion_proveedor(texto):
    """Extrae la dirección registrada del proveedor."""

    direccion = buscar_patron(
        r"DIRECCI[ÓO]N\s*:?\s*(.+?)(?=\s*R\.?U\.?T\.?)",
        texto,
        re.IGNORECASE | re.DOTALL,
    )

    direccion = direccion.replace("\n", " ")

    return limpiar_texto(direccion)

def extraer_ciudad(paginas):
    """Extrae la ciudad del proveedor usando su posición visual."""

    for pagina in paginas:

        palabras = pagina["palabras"]

        for palabra in palabras:

            x0, y0, x1, y1, texto, bloque, linea, posicion = palabra

            # Busca la etiqueta CIUDAD del bloque del proveedor.
            if texto.upper().strip() == "CIUDAD" and x0 < 100:

                palabras_ciudad = []

                for otra in palabras:

                    otro_x0 = otra[0]
                    otro_y0 = otra[1]
                    otro_texto = otra[4].strip()

                    # Toma solamente el contenido ubicado
                    # a la derecha de CIUDAD y antes de TELÉFONO.
                    if (
                        abs(otro_y0 - y0) <= 2
                        and 130 <= otro_x0 < 350
                        and otro_texto != ":"
                    ):
                        palabras_ciudad.append(otra)

                palabras_ciudad.sort(
                    key=lambda item: item[0]
                )

                return " ".join(
                    item[4].strip()
                    for item in palabras_ciudad
                )

    return ""


def extraer_vendedor(texto):
    """Extrae el vendedor o contacto comercial."""

    vendedor = buscar_patron(
        r"VENDEDOR\s*:?\s*(.+?)(?=\n|FORMA DE PAGO)",
        texto,
        re.IGNORECASE,
    )

    return limpiar_texto(vendedor)


def extraer_telefono(texto):
    """Extrae el teléfono del proveedor."""

    resultado = re.search(
        r"Telefono:[ \t]*([^\r\n]*)",
        texto,
        re.IGNORECASE,
    )

    if not resultado:
        return ""

    return limpiar_texto(resultado.group(1))


def extraer_email_vendedor(texto):
    """Extrae el correo ubicado en la sección del vendedor."""

    seccion = buscar_patron(
        r"VENDEDOR\s*:?\s*(.*?)(?=FORMA DE PAGO)",
        texto,
        re.IGNORECASE | re.DOTALL,
    )

    if not seccion:
        return ""

    lineas = [
        linea.strip()
        for linea in seccion.splitlines()
        if linea.strip() and linea.strip() != ":"
    ]

    if len(lineas) >= 2:
        return limpiar_texto(lineas[1])

    return ""


def extraer_forma_pago(texto):
    """Extrae la forma de pago indicada en la OC."""

    resultado = re.search(
        r"FORMA DE PAGO\s*\n:\s*\n([^\r\n]+)",
        texto,
        re.IGNORECASE,
    )

    if resultado:
        return limpiar_texto(resultado.group(1))

    resultado = re.search(
        r"FORMA DE PAGO[ \t]*:[ \t]*([^\r\n]+)",
        texto,
        re.IGNORECASE,
    )

    if resultado:
        return limpiar_texto(resultado.group(1))

    return ""

def extraer_nota_interna(texto):
    """Extrae el contenido completo de la nota interna."""

    nota = buscar_patron(
        r"NOTA\s+INTERNA:\s*(.*?)(?=DATOS\s+BANCARIOS:)",
        texto,
        re.IGNORECASE | re.DOTALL,
    )

    if not nota:
        return ""

    lineas = [
        limpiar_texto(linea)
        for linea in nota.splitlines()
        if limpiar_texto(linea)
    ]

    return " ".join(lineas)


def extraer_solicitud(texto):
    """Extrae el número de solicitud indicado en la nota interna."""

    nota = extraer_nota_interna(texto)

    if not nota:
        return ""

    resultado = re.search(
        r"\bSOLICITUD\s+N[°º]?\s*(\d+)\b",
        nota,
        re.IGNORECASE,
    )

    if resultado:
        return resultado.group(1).strip()

    return ""


def extraer_solicitante_oc(paginas):
    """Extrae el solicitante y su cargo."""

    for pagina in paginas:

        palabras = pagina["palabras"]

        etiquetas = [
            palabra
            for palabra in palabras
            if palabra[4].strip().lower() == "solicitante"
            and 50 <= palabra[0] < 180
        ]

        for etiqueta in etiquetas:

            y_etiqueta = etiqueta[1]

            palabras_solicitante = [
                palabra
                for palabra in palabras
                if (
                    y_etiqueta + 5 <= palabra[1] <= y_etiqueta + 30
                    and 25 <= palabra[0] < 220
                )
            ]

            if palabras_solicitante:

                palabras_solicitante.sort(
                    key=lambda palabra: (
                        palabra[1],
                        palabra[0],
                    )
                )

                return " ".join(
                    palabra[4].strip()
                    for palabra in palabras_solicitante
                    if palabra[4].strip()
                )

    return ""


def extraer_primer_aprobador(paginas):
    """Extrae el primer aprobador y su cargo."""

    for pagina in paginas:

        palabras = pagina["palabras"]

        for palabra in palabras:

            x0, y0, x1, y1, texto, bloque, linea, posicion = palabra

            if (
                texto.strip().lower() == "primer"
                and 220 <= x0 < 330
            ):

                existe_aprobador = any(
                    otra[4].strip().lower() == "aprobador"
                    and abs(otra[1] - y0) <= 2
                    for otra in palabras
                )

                if not existe_aprobador:
                    continue

                palabras_aprobador = [
                    otra
                    for otra in palabras
                    if (
                        y0 + 5 <= otra[1] <= y0 + 30
                        and 220 <= otra[0] < 400
                    )
                ]

                if palabras_aprobador:

                    palabras_aprobador.sort(
                        key=lambda otra: (
                            otra[1],
                            otra[0],
                        )
                    )

                    return " ".join(
                        otra[4].strip()
                        for otra in palabras_aprobador
                        if otra[4].strip()
                    )

    return ""

def parsear_oc(texto, paginas):
    """Extrae los datos generales de una orden de compra."""

    numero_oc = extraer_numero_oc(texto)

    codigo_hospital, hospital = obtener_hospital(numero_oc)

    datos = {
        "numero_oc": numero_oc,
        "codigo_hospital": codigo_hospital,
        "hospital": hospital,
        "fecha": extraer_fecha(texto),
        "proveedor": extraer_proveedor(texto),
        "rut_proveedor": extraer_rut_proveedor(texto),
        "direccion_proveedor": extraer_direccion_proveedor(texto),
        "ciudad": extraer_ciudad(paginas),
        "vendedor": extraer_vendedor(texto),
        "telefono": extraer_telefono(texto),
        "email": extraer_email_vendedor(texto),
        "forma_pago": extraer_forma_pago(texto),
        "solicitud": extraer_solicitud(texto),
        "nota_interna": extraer_nota_interna(texto),
        "solicitante_oc": extraer_solicitante_oc(paginas),
        "primer_aprobador": extraer_primer_aprobador(paginas),
    }

    return datos