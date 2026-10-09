from decimal import Decimal, InvalidOperation

from src.moneda import convertir_numero


def convertir_cantidad(valor):
    """Convierte cantidades como 2.160,00 a Decimal."""

    if not valor:
        return Decimal("0")

    valor = str(valor).strip()
    valor = valor.replace(" ", "")
    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")

    try:
        return Decimal(valor)

    except InvalidOperation:
        return Decimal("0")


def unir_palabras(palabras):
    """Une palabras respetando su posición horizontal."""

    palabras_ordenadas = sorted(
        palabras,
        key=lambda palabra: palabra[0],
    )

    return " ".join(
        palabra[4].strip()
        for palabra in palabras_ordenadas
        if palabra[4].strip()
    )


def es_numero_item(texto):
    """Comprueba si un texto corresponde al número de un artículo."""

    return texto.strip().isdigit()


def buscar_limite_tabla(palabras, y_inicio):
    """Busca el límite inferior real de la tabla de artículos."""

    limites = []

    for palabra in palabras:

        x0, y0, x1, y1, texto, bloque, linea, posicion = palabra

        if y0 <= y_inicio:
            continue

        texto_mayuscula = texto.upper().strip()

        # Inicio del bloque de despacho.
        if (
            texto_mayuscula == "DESPACHAR"
            and 80 <= x0 <= 150
        ):
            limites.append(y0)

        # Inicio de los totales.
        elif (
            texto_mayuscula == "SUB"
            and x0 > 430
        ):
            limites.append(y0)

        # Pie de página.
        elif texto_mayuscula == "DOCUMENTO":
            limites.append(y0)

        # Código verificador del pie de página.
        elif (
            texto_mayuscula == "CÓDIGO"
            and x0 < 150
        ):
            limites.append(y0)

    if limites:
        return min(limites)

    return max(
        (
            palabra[3]
            for palabra in palabras
        ),
        default=y_inicio,
    )


def reconstruir_descripcion(palabras):
    """Reconstruye la descripción de un artículo."""

    if not palabras:
        return ""

    # CONTACTO y NÚMERO pueden formar parte
    # legítimamente del nombre de un producto.
    marcadores_fin = {
        "DESPACHAR",
    }

    palabras_validas = []

    palabras_ordenadas = sorted(
        palabras,
        key=lambda palabra: (
            palabra[1],
            palabra[0],
        ),
    )

    for palabra in palabras_ordenadas:

        texto = palabra[4].strip()
        texto_mayuscula = texto.upper()

        if texto_mayuscula in marcadores_fin:
            break

        palabras_validas.append(
            palabra
        )

    if not palabras_validas:
        return ""

    lineas = []

    for palabra in palabras_validas:

        y = palabra[1]

        linea_encontrada = None

        for linea in lineas:

            if abs(
                linea["y"] - y
            ) <= 2:

                linea_encontrada = linea
                break

        if linea_encontrada is None:

            linea_encontrada = {
                "y": y,
                "palabras": [],
            }

            lineas.append(
                linea_encontrada
            )

        linea_encontrada[
            "palabras"
        ].append(
            palabra
        )

    textos = []

    for linea in sorted(
        lineas,
        key=lambda linea: linea["y"],
    ):

        texto_linea = unir_palabras(
            linea["palabras"]
        )

        if texto_linea:
            textos.append(
                texto_linea
            )

    return " ".join(
        textos
    ).strip()


def extraer_articulos(paginas, moneda):
    """Extrae los artículos de todas las páginas de una OC."""

    articulos = []

    for pagina in paginas:

        palabras = pagina["palabras"]

        numeros_item = []

        # Localiza números que realmente pertenecen
        # a filas de artículos.
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

            if not (
                25 <= x0 <= 47
                and es_numero_item(texto)
            ):
                continue

            # Una fila real de artículo debe tener
            # una cantidad en la zona de la tabla.
            tiene_datos_articulo = any(
                390 <= otra[0] < 455
                and abs(
                    otra[1] - y0
                ) <= 3
                for otra in palabras
            )

            if tiene_datos_articulo:
                numeros_item.append(
                    palabra
                )

        numeros_item.sort(
            key=lambda palabra: palabra[1]
        )

        for indice, palabra_item in enumerate(
            numeros_item
        ):

            numero = int(
                palabra_item[4]
            )

            y_inicio = palabra_item[1]

            if indice + 1 < len(
                numeros_item
            ):

                y_fin = numeros_item[
                    indice + 1
                ][1]

            else:

                y_fin = buscar_limite_tabla(
                    palabras,
                    y_inicio,
                )

            palabras_item = [
                palabra
                for palabra in palabras
                if (
                    y_inicio - 3
                    <= palabra[1]
                    < y_fin - 2
                )
            ]

            codigo = ""
            unidad = ""

            cantidad = Decimal("0")
            precio_unitario = Decimal("0")
            total_linea = Decimal("0")

            cantidad_encontrada = False
            precio_encontrado = False
            total_encontrado = False

            palabras_descripcion = []

            for palabra in palabras_item:

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

                # Código del artículo.
                if 47 <= x0 < 101:

                    if (
                        texto.strip()
                        and not codigo
                    ):
                        codigo = (
                            texto.strip()
                        )

                # Descripción.
                elif 101 <= x0 < 350:

                    palabras_descripcion.append(
                        palabra
                    )

                # Unidad de medida.
                elif 350 <= x0 < 390:

                    if (
                        texto.strip()
                        and not unidad
                    ):
                        unidad = (
                            texto.strip()
                        )

                # Cantidad.
                elif 390 <= x0 < 455:

                    if not cantidad_encontrada:

                        cantidad = (
                            convertir_cantidad(
                                texto
                            )
                        )

                        cantidad_encontrada = True

                # Precio unitario.
                elif 455 <= x0 < 525:

                    if not precio_encontrado:

                        precio_unitario = (
                            convertir_numero(
                                texto,
                                moneda,
                            )
                        )

                        precio_encontrado = True

                # Total de la línea.
                elif x0 >= 525:

                    if not total_encontrado:

                        total_linea = (
                            convertir_numero(
                                texto,
                                moneda,
                            )
                        )

                        total_encontrado = True

            descripcion = (
                reconstruir_descripcion(
                    palabras_descripcion
                )
            )

            # Algunas OC antiguas no tienen código,
            # pero el artículo sigue siendo válido.
            if descripcion:

                articulos.append(
                    {
                        "numero": numero,
                        "codigo": codigo,
                        "descripcion": descripcion,
                        "unidad": unidad,
                        "cantidad": cantidad,
                        "precio_unitario": precio_unitario,
                        "total_linea": total_linea,
                    }
                )

    articulos.sort(
        key=lambda articulo: articulo[
            "numero"
        ]
    )

    return articulos