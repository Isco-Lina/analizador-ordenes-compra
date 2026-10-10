from pathlib import Path

from src.extractor import extraer_pdf
from src.parser_oc import parsear_oc
from src.articulos import extraer_articulos
from src.totales import extraer_totales, validar_totales
from src.moneda import detectar_moneda, obtener_simbolo
from src.validaciones import (
    sumar_totales_articulos,
    validar_subtotal_articulos,
)
from src.excel import (
    crear_fila_orden,
    crear_filas_detalle,
    exportar_excel,
)

# Carpeta donde se encuentran las órdenes de compra.
CARPETA_PDF = Path("data/pdf")

ARCHIVO_EXCEL = Path("data/output/ordenes_compra.xlsx")

def mostrar_datos(datos, totales, moneda):
    """Muestra los datos generales y totales de una OC."""

    simbolo = obtener_simbolo(moneda)

    print()
    print("=" * 70)
    print(f"OC:              {datos['numero_oc']}")
    print(f"HOSPITAL:        {datos['hospital']}")
    print(f"CÓDIGO HOSPITAL: {datos['codigo_hospital']}")
    print(f"FECHA:           {datos['fecha']}")
    print(f"MONEDA:          {moneda}")
    print("-" * 70)
    print(f"PROVEEDOR:       {datos['proveedor']}")
    print(f"RUT:             {datos['rut_proveedor']}")
    print(f"DIRECCIÓN:       {datos['direccion_proveedor']}")
    print(f"CIUDAD:          {datos['ciudad']}")
    print(f"VENDEDOR:        {datos['vendedor']}")
    print(f"TELÉFONO:        {datos['telefono']}")
    print(f"EMAIL:           {datos['email']}")
    print(f"FORMA DE PAGO:   {datos['forma_pago']}")
    print("-" * 70)
    print("DATOS INTERNOS")
    print(f"SOLICITUD:       {datos['solicitud']}")
    print(f"NOTA INTERNA:    {datos['nota_interna']}")
    print(f"SOLICITANTE OC:  {datos['solicitante_oc']}")
    print(f"1ER APROBADOR:   {datos['primer_aprobador']}")
    print("-" * 70)
    print("TOTALES")
    print(f"SUBTOTAL:        {simbolo}{totales['subtotal']}")
    print(f"DESCUENTO:       {simbolo}{totales['descuento']}")
    print(f"CARGOS:          {simbolo}{totales['cargos']}")
    print(f"NETO:            {simbolo}{totales['neto']}")
    print(f"IVA:             {simbolo}{totales['iva']}")
    print(f"OTROS IMPUESTOS: {simbolo}{totales['otros_impuestos']}")
    print(f"TOTAL:           {simbolo}{totales['total']}")

    if validar_totales(totales, moneda):
        print("VALIDACIÓN:      OK")
    else:
        print("VALIDACIÓN:      REVISAR")

    print("=" * 70)


def mostrar_articulos(articulos, moneda):
    """Muestra los artículos encontrados en la OC."""

    print()
    print(f"ARTÍCULOS - MONEDA: {moneda}")
    print("-" * 70)

    if not articulos:
        print("No se encontraron artículos.")
        return

    simbolo = obtener_simbolo(moneda)

    for articulo in articulos:
        print(f"ITEM:        {articulo['numero']}")
        print(f"CÓDIGO:      {articulo['codigo']}")
        print(f"DESCRIPCIÓN: {articulo['descripcion']}")
        print(f"UNIDAD:      {articulo['unidad']}")
        print(f"CANTIDAD:    {articulo['cantidad']}")
        print(
            f"P. UNITARIO: {simbolo}"
            f"{articulo['precio_unitario']}"
        )
        print(
            f"TOTAL LÍNEA: {simbolo}"
            f"{articulo['total_linea']}"
        )
        print("-" * 70)


def main():
    """Procesa todos los PDF encontrados."""

    print("=" * 70)
    print("              ANALIZADOR DE ÓRDENES DE COMPRA")
    print("=" * 70)

    archivos_pdf = sorted(CARPETA_PDF.glob("*.pdf"))

    if not archivos_pdf:
        print("\nNo se encontraron archivos PDF.")
        return

    print(f"\nSe encontraron {len(archivos_pdf)} archivo(s).")

    procesados_ok = 0
    con_error = 0
    para_revisar = 0
    duplicados = 0

    filas_ordenes = []
    filas_detalle = []
    oc_vistas = set()

    for archivo in archivos_pdf:
        print(f"\nProcesando: {archivo.name}")

        try:
            # Extrae toda la información necesaria del PDF.
            texto, paginas, numero_paginas = extraer_pdf(archivo)

            # Extrae los datos generales.
            datos = parsear_oc(texto, paginas)
            numero_oc = datos["numero_oc"]

            # Evita procesar dos veces la misma OC.
            if numero_oc and numero_oc in oc_vistas:
                duplicados += 1

                print()
                print("OC DUPLICADA")
                print("-" * 70)
                print(f"ARCHIVO: {archivo.name}")
                print(f"OC:      {numero_oc}")
                print("-" * 70)

                continue

            if numero_oc:
                oc_vistas.add(numero_oc)

            # Detecta la moneda utilizada.
            moneda = detectar_moneda(paginas)

            # Extrae los artículos.
            articulos = extraer_articulos(paginas, moneda)

            # Extrae los totales.
            totales = extraer_totales(paginas, moneda)

            # Valida la suma de los artículos.
            suma_articulos = sumar_totales_articulos(articulos)

            subtotal_valido = validar_subtotal_articulos(
                articulos,
                totales["subtotal"],
                moneda,
            )

            # Valida los totales generales.
            totales_validos = validar_totales(
                totales,
                moneda,
            )

            # Define el estado de procesamiento.
            if totales_validos and subtotal_valido:
                estado_proceso = "OK"
                error_proceso = ""
            else:
                estado_proceso = "REVISAR"
                error_proceso = ""

            # Prepara la fila principal de la OC.
            fila_orden = crear_fila_orden(
                datos=datos,
                totales=totales,
                moneda=moneda,
                simbolo_moneda=obtener_simbolo(moneda),
                archivo_origen=archivo.name,
                numero_paginas=numero_paginas,
                estado_proceso=estado_proceso,
                error_proceso=error_proceso,
                totales_validos=totales_validos,
                articulos_validos=subtotal_valido,
            )

            filas_ordenes.append(fila_orden)

            # Prepara las filas de artículos.
            detalle = crear_filas_detalle(
                numero_oc=numero_oc,
                articulos=articulos,
                moneda=moneda,
            )

            filas_detalle.extend(detalle)

            # Muestra los resultados.
            mostrar_datos(datos, totales, moneda)
            mostrar_articulos(articulos, moneda)

            print()
            print("VALIDACIÓN DE ARTÍCULOS")
            print("-" * 70)
            print(f"SUMA ARTÍCULOS: {suma_articulos}")
            print(f"SUBTOTAL OC:    {totales['subtotal']}")

            if subtotal_valido:
                print("RESULTADO:       OK")
            else:
                print("RESULTADO:       REVISAR")

            print("-" * 70)

            # Actualiza los contadores.
            if totales_validos and subtotal_valido:
                procesados_ok += 1
            else:
                para_revisar += 1

        except Exception as error:
            con_error += 1

            print()
            print("ERROR AL PROCESAR ARCHIVO")
            print("-" * 70)
            print(f"ARCHIVO: {archivo.name}")
            print(f"ERROR:   {error}")
            print("-" * 70)

            continue

    exportar_excel(
        filas_ordenes=filas_ordenes,
        filas_detalle=filas_detalle,
        ruta_salida=ARCHIVO_EXCEL,
    )

    print()
    print(f"Excel generado: {ARCHIVO_EXCEL}")

    print()
    print("=" * 70)
    print("RESUMEN DEL PROCESAMIENTO")
    print("=" * 70)
    print(f"Archivos encontrados: {len(archivos_pdf)}")
    print(f"Procesados OK:         {procesados_ok}")
    print(f"Para revisar:          {para_revisar}")
    print(f"Con error:             {con_error}")
    print(f"Duplicados:            {duplicados}")
    print(f"OC preparadas:         {len(filas_ordenes)}")
    print(f"Artículos preparados:  {len(filas_detalle)}")
    print("=" * 70)


if __name__ == "__main__":
    main()