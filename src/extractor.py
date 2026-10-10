import pymupdf


def extraer_pdf(ruta_pdf):
    """Extrae texto, palabras y cantidad de páginas de un PDF."""

    texto_completo = ""
    paginas = []

    with pymupdf.open(ruta_pdf) as documento:

        numero_paginas = len(documento)

        for numero_pagina, pagina in enumerate(
            documento,
            start=1,
        ):
            # Extrae el texto general de la página.
            texto_completo += pagina.get_text()

            # Extrae palabras junto con sus coordenadas.
            palabras = pagina.get_text("words")

            paginas.append(
                {
                    "pagina": numero_pagina,
                    "ancho": pagina.rect.width,
                    "alto": pagina.rect.height,
                    "palabras": palabras,
                }
            )

    return texto_completo, paginas, numero_paginas