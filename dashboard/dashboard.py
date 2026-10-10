from pathlib import Path

import pandas as pd
from flask import Flask, render_template, request


# ============================================================
# CONFIGURACIÓN
# ============================================================

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

ARCHIVO_EXCEL = (
    BASE_DIR
    / "data"
    / "output"
    / "ordenes_compra.xlsx"
)


# ============================================================
# CARGA DE DATOS
# ============================================================

_CACHE_DATOS = None
_CACHE_MTIME = None


def cargar_datos():
    """Carga el Excel una sola vez y recarga únicamente si cambia."""

    global _CACHE_DATOS, _CACHE_MTIME

    if not ARCHIVO_EXCEL.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ARCHIVO_EXCEL}"
        )

    mtime_actual = ARCHIVO_EXCEL.stat().st_mtime

    if (
        _CACHE_DATOS is not None
        and _CACHE_MTIME == mtime_actual
    ):
        return _CACHE_DATOS

    ordenes = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name="ORDENES",
    )

    detalle = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name="DETALLE_OC",
    )

    ordenes["fecha"] = pd.to_datetime(
        ordenes["fecha"],
        errors="coerce",
    )

    columnas_texto_ordenes = [
        "numero_oc",
        "codigo_hospital",
        "hospital",
        "proveedor",
        "rut_proveedor",
        "direccion_proveedor",
        "ciudad",
        "vendedor",
        "telefono",
        "email",
        "forma_pago",
        "solicitud",
        "nota_interna",
        "solicitante_oc",
        "primer_aprobador",
        "moneda",
        "simbolo_moneda",
        "estado_proceso",
    ]

    for columna in columnas_texto_ordenes:
        if columna in ordenes.columns:
            ordenes[columna] = (
                ordenes[columna]
                .fillna("")
                .astype(str)
            )

    columnas_texto_detalle = [
        "numero_oc",
        "codigo",
        "descripcion",
        "unidad_medida",
        "moneda",
    ]

    for columna in columnas_texto_detalle:
        if columna in detalle.columns:
            detalle[columna] = (
                detalle[columna]
                .fillna("")
                .astype(str)
            )

    columnas_numericas_ordenes = [
        "subtotal",
        "descuento",
        "cargos",
        "neto",
        "iva",
        "otros_impuestos",
        "total",
    ]

    for columna in columnas_numericas_ordenes:
        if columna in ordenes.columns:
            ordenes[columna] = pd.to_numeric(
                ordenes[columna],
                errors="coerce",
            )

    columnas_numericas_detalle = [
        "cantidad",
        "precio_unitario",
        "total_linea",
    ]

    for columna in columnas_numericas_detalle:
        if columna in detalle.columns:
            detalle[columna] = pd.to_numeric(
                detalle[columna],
                errors="coerce",
            )

    columnas_relacion = [
        "numero_oc",
        "fecha",
        "codigo_hospital",
        "hospital",
        "proveedor",
        "rut_proveedor",
        "solicitante_oc",
        "primer_aprobador",
        "estado_proceso",
    ]

    detalle_completo = detalle.merge(
        ordenes[columnas_relacion],
        on="numero_oc",
        how="left",
    )

    _CACHE_DATOS = (
        ordenes,
        detalle,
        detalle_completo,
    )
    _CACHE_MTIME = mtime_actual

    return _CACHE_DATOS


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def formato_numero(valor, decimales=0):
    """Formatea números al formato utilizado en Chile."""

    try:
        numero = float(valor)

        texto = f"{numero:,.{decimales}f}"

        return (
            texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    except (TypeError, ValueError):
        return "0"


def formato_moneda(valor, moneda):
    """Formatea un monto respetando su moneda."""

    if pd.isna(valor):
        return "-"

    if moneda == "CLP":
        return f"$ {formato_numero(valor, 0)}"

    if moneda == "USD":
        return f"US$ {formato_numero(valor, 2)}"

    if moneda == "EUR":
        return f"EUR {formato_numero(valor, 2)}"

    if moneda == "UF":
        return f"UF {formato_numero(valor, 4)}"

    return formato_numero(valor, 2)


def fecha_texto(fecha):
    """Convierte una fecha a formato día-mes-año."""

    if pd.isna(fecha):
        return "-"

    return fecha.strftime("%d-%m-%Y")


def texto_seguro(valor):
    """Evita mostrar NaN en la web."""

    if pd.isna(valor):
        return ""

    return str(valor)


def lista_limpia(serie):
    """Obtiene valores únicos no vacíos."""

    valores = (
        serie
        .dropna()
        .astype(str)
        .str.strip()
    )

    valores = valores[
        valores != ""
    ]

    return sorted(
        valores.unique().tolist()
    )


def obtener_simbolo_moneda(moneda):
    """Devuelve el símbolo utilizado en los gráficos."""

    simbolos = {
        "CLP": "$",
        "USD": "US$",
        "EUR": "EUR",
        "UF": "UF",
    }

    return simbolos.get(
        moneda,
        moneda,
    )


# ============================================================
# HISTORIAL DE PRODUCTOS
# ============================================================

def construir_resumen_productos(detalle, moneda=None, hospital=None, busqueda=None):
    """Resume precios históricos por descripción + unidad + moneda.

    No intenta decidir si un precio es bueno o malo: entrega hechos
    históricos (último, mínimo, máximo y variación vs. antecedente previo).
    """

    columnas = [
        "numero_oc", "fecha", "hospital", "proveedor", "descripcion",
        "unidad_medida", "cantidad", "precio_unitario", "moneda",
    ]
    base = detalle[columnas].copy()
    base = base.loc[
        base["descripcion"].str.strip().ne("")
        & base["proveedor"].str.strip().ne("")
        & base["moneda"].str.strip().ne("")
        & base["precio_unitario"].notna()
        & base["precio_unitario"].gt(0)
        & base["fecha"].notna()
    ]

    if moneda:
        base = base.loc[base["moneda"].eq(moneda)]
    if hospital:
        base = base.loc[base["hospital"].eq(hospital)]
    if busqueda:
        texto = str(busqueda).strip()
        base = base.loc[
            base["descripcion"].str.contains(texto, case=False, na=False, regex=False)
            | base["proveedor"].str.contains(texto, case=False, na=False, regex=False)
        ]

    if base.empty:
        return pd.DataFrame(), pd.DataFrame()

    claves = ["descripcion", "unidad_medida", "moneda"]

    # Consolidamos líneas equivalentes dentro de una misma OC.
    historial = (
        base.groupby(
            claves + ["numero_oc", "fecha", "proveedor", "hospital"],
            as_index=False,
            dropna=False,
            sort=False,
        )
        .agg(
            cantidad=("cantidad", "sum"),
            precio_unitario=("precio_unitario", "median"),
        )
        .sort_values(claves + ["fecha", "numero_oc"], kind="mergesort")
        .reset_index(drop=True)
    )

    historial["_producto_id"] = historial.groupby(
        claves, dropna=False, sort=False
    ).ngroup()

    grp = historial.groupby("_producto_id", sort=False)
    resumen = grp.agg(
        cantidad_oc=("numero_oc", "nunique"),
        cantidad_proveedores=("proveedor", "nunique"),
        precio_minimo=("precio_unitario", "min"),
        precio_maximo=("precio_unitario", "max"),
        movimientos=("precio_unitario", "size"),
    )

    ultima = grp.tail(1).set_index("_producto_id")
    resumen = resumen.join(
        ultima[[
            "descripcion", "unidad_medida", "moneda", "numero_oc", "fecha",
            "proveedor", "hospital", "cantidad", "precio_unitario",
        ]].rename(columns={
            "numero_oc": "ultima_oc",
            "fecha": "ultima_fecha",
            "proveedor": "ultimo_proveedor",
            "hospital": "ultimo_hospital",
            "cantidad": "ultima_cantidad",
            "precio_unitario": "ultimo_precio",
        })
    )

    # Precio inmediatamente anterior, solo como referencia informativa.
    anterior = grp.nth(-2)
    if not anterior.empty:
        resumen = resumen.join(
            anterior[["precio_unitario"]].rename(
                columns={"precio_unitario": "precio_anterior"}
            ),
            how="left",
        )
    else:
        resumen["precio_anterior"] = pd.NA

    resumen["variacion_pct"] = pd.NA
    validos = resumen["precio_anterior"].notna() & resumen["precio_anterior"].gt(0)
    resumen.loc[validos, "variacion_pct"] = (
        (resumen.loc[validos, "ultimo_precio"] - resumen.loc[validos, "precio_anterior"])
        / resumen.loc[validos, "precio_anterior"] * 100
    )

    return historial, resumen


# ============================================================
# INICIO
# ============================================================

@app.route("/")
def inicio():
    """Centro de control principal basado en datos históricos objetivos."""

    ordenes, _, detalle_completo = cargar_datos()

    total_oc = ordenes["numero_oc"].nunique()
    total_proveedores = ordenes["proveedor"].replace("", pd.NA).dropna().nunique()
    total_movimientos = len(detalle_completo)

    # Productos con un solo proveedor histórico, sin exigir un mínimo de OC.
    _, resumen = construir_resumen_productos(detalle_completo)
    unicos = resumen.loc[resumen["cantidad_proveedores"].eq(1)].copy() if not resumen.empty else pd.DataFrame()
    total_proveedor_unico = len(unicos)

    referencias = []
    if not unicos.empty:
        unicos = unicos.sort_values(
            ["cantidad_oc", "ultima_fecha"], ascending=[False, False]
        ).head(10)
        for fila in unicos.itertuples():
            referencias.append({
                "descripcion": fila.descripcion,
                "unidad": texto_seguro(fila.unidad_medida),
                "moneda": fila.moneda,
                "proveedor": fila.ultimo_proveedor,
                "ordenes": int(fila.cantidad_oc),
                "ultima_compra": fecha_texto(fila.ultima_fecha),
                "ultimo_precio": formato_moneda(fila.ultimo_precio, fila.moneda),
                "minimo": formato_moneda(fila.precio_minimo, fila.moneda),
                "maximo": formato_moneda(fila.precio_maximo, fila.moneda),
            })

    ultimas_oc = []
    ultimas = ordenes.sort_values("fecha", ascending=False).head(10)
    for _, fila in ultimas.iterrows():
        ultimas_oc.append({
            "numero_oc": fila["numero_oc"],
            "fecha": fecha_texto(fila["fecha"]),
            "proveedor": fila["proveedor"],
            "hospital": fila["hospital"],
            "moneda": fila["moneda"],
            "total": formato_moneda(fila["total"], fila["moneda"]),
        })

    return render_template(
        "inicio.html",
        pagina="inicio",
        total_oc=formato_numero(total_oc),
        total_proveedores=formato_numero(total_proveedores),
        total_movimientos=formato_numero(total_movimientos),
        total_proveedor_unico=formato_numero(total_proveedor_unico),
        referencias=referencias,
        ultimas_oc=ultimas_oc,
    )


# ============================================================
# DASHBOARD GENERAL
# ============================================================

@app.route("/dashboard")
def dashboard():
    """Dashboard general de compras."""

    ordenes, _, detalle_completo = cargar_datos()

    hospitales_disponibles = lista_limpia(ordenes["hospital"])
    monedas_disponibles = lista_limpia(ordenes["moneda"])
    años_disponibles = sorted(
        ordenes["fecha"].dropna().dt.year.astype(int).unique().tolist(),
        reverse=True,
    )

    hospital = request.args.get("hospital", "").strip()
    moneda = request.args.get("moneda", "CLP").strip()
    año = request.args.get("anio", "").strip()
    limite_proveedores = request.args.get("proveedores", "25").strip().lower()
    if limite_proveedores not in {"10", "25", "todos"}:
        limite_proveedores = "25"

    df = ordenes.copy()
    if hospital:
        df = df[df["hospital"] == hospital]
    if moneda:
        df = df[df["moneda"] == moneda]
    if año:
        try:
            df = df[df["fecha"].dt.year == int(año)]
        except ValueError:
            pass

    numeros_oc = df["numero_oc"].unique()
    df_detalle = detalle_completo[detalle_completo["numero_oc"].isin(numeros_oc)].copy()

    total_oc = df["numero_oc"].nunique()
    total_proveedores = df["proveedor"].replace("", pd.NA).dropna().nunique()
    total_movimientos = len(df_detalle)
    total_comprado = pd.to_numeric(df["total"], errors="coerce").fillna(0).sum()

    por_hospital_df = (
        df[df["hospital"] != ""]
        .groupby("hospital", as_index=False)
        .agg(ordenes=("numero_oc", "nunique"), total=("total", "sum"))
        .sort_values("total", ascending=False)
    )
    hospitales = [
        {
            "hospital": fila["hospital"],
            "ordenes": int(fila["ordenes"]),
            "total": formato_moneda(fila["total"], moneda),
        }
        for _, fila in por_hospital_df.iterrows()
    ]
    grafico_hospitales = {
        "labels": por_hospital_df["hospital"].tolist(),
        "values": por_hospital_df["total"].fillna(0).astype(float).tolist(),
    }

    evolucion_df = df.dropna(subset=["fecha"]).copy()
    if not evolucion_df.empty:
        evolucion_df["periodo"] = evolucion_df["fecha"].dt.to_period("M")
        evolucion_df = (
            evolucion_df.groupby("periodo", as_index=False)
            .agg(total=("total", "sum"), ordenes=("numero_oc", "nunique"))
            .sort_values("periodo")
        )
        meses_es = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
        grafico_evolucion = {
            "labels": [f"{meses_es[p.month]} {p.year}" for p in evolucion_df["periodo"]],
            "values": evolucion_df["total"].fillna(0).astype(float).tolist(),
            "orders": evolucion_df["ordenes"].fillna(0).astype(int).tolist(),
        }
    else:
        grafico_evolucion = {"labels": [], "values": [], "orders": []}

    proveedores_df = (
        df[df["proveedor"] != ""]
        .groupby("proveedor", as_index=False)
        .agg(ordenes=("numero_oc", "nunique"), total=("total", "sum"))
        .sort_values("total", ascending=False)
    )
    total_proveedores_grafico = len(proveedores_df)
    if limite_proveedores != "todos":
        proveedores_df = proveedores_df.head(int(limite_proveedores))

    top_proveedores = [
        {
            "proveedor": fila["proveedor"],
            "ordenes": int(fila["ordenes"]),
            "total": formato_moneda(fila["total"], moneda),
        }
        for _, fila in proveedores_df.iterrows()
    ]
    grafico_proveedores = {
        "labels": proveedores_df["proveedor"].tolist(),
        "values": proveedores_df["total"].fillna(0).astype(float).tolist(),
        "orders": proveedores_df["ordenes"].fillna(0).astype(int).tolist(),
    }

    ultimas_df = df.dropna(subset=["fecha"]).sort_values("fecha", ascending=False).head(10)
    ultimas_ordenes = []
    for _, fila in ultimas_df.iterrows():
        ultimas_ordenes.append({
            "numero_oc": fila["numero_oc"],
            "fecha": fecha_texto(fila["fecha"]),
            "hospital": fila["hospital"],
            "proveedor": fila["proveedor"],
            "moneda": fila["moneda"],
            "total": formato_moneda(fila["total"], fila["moneda"]),
            "estado": fila["estado_proceso"],
        })

    return render_template(
        "dashboard.html",
        pagina="dashboard",
        hospitales_disponibles=hospitales_disponibles,
        monedas_disponibles=monedas_disponibles,
        años_disponibles=años_disponibles,
        hospital_seleccionado=hospital,
        moneda_seleccionada=moneda,
        año_seleccionado=año,
        limite_proveedores=limite_proveedores,
        total_proveedores_grafico=total_proveedores_grafico,
        simbolo_moneda=obtener_simbolo_moneda(moneda),
        total_oc=formato_numero(total_oc),
        total_proveedores=formato_numero(total_proveedores),
        total_movimientos=formato_numero(total_movimientos),
        total_comprado=formato_moneda(total_comprado, moneda),
        hospitales=hospitales,
        top_proveedores=top_proveedores,
        ultimas_ordenes=ultimas_ordenes,
        grafico_evolucion=grafico_evolucion,
        grafico_hospitales=grafico_hospitales,
        grafico_proveedores=grafico_proveedores,
    )


# ============================================================
# BUSCAR PRODUCTO / INTELIGENCIA DE COMPRAS
# ============================================================

@app.route("/productos")
def productos():
    """Busca productos, compara proveedores y estima costos históricos."""

    _, _, detalle = cargar_datos()

    busqueda = request.args.get("q", "").strip()
    descripcion_seleccionada = request.args.get("descripcion", "").strip()
    unidad_seleccionada = request.args.get("unidad", "").strip()
    codigo_seleccionado = request.args.get("codigo", "").strip()
    moneda_solicitada = request.args.get("moneda", "").strip().upper()

    try:
        cantidad_simulacion = float(
            request.args.get("cantidad", "").replace(",", ".")
        )
        if cantidad_simulacion <= 0:
            cantidad_simulacion = None
    except (TypeError, ValueError):
        cantidad_simulacion = None

    productos_encontrados = []
    analisis = None

    # --------------------------------------------------------
    # ETAPA 1: BUSCAR PRODUCTOS DISTINTOS
    # --------------------------------------------------------

    if busqueda and not descripcion_seleccionada:
        filtro = detalle["descripcion"].str.contains(
            busqueda, case=False, na=False, regex=False
        )

        encontrados = detalle[filtro].copy()
        encontrados = encontrados.loc[
            encontrados["descripcion"].str.strip().ne("")
            & encontrados["moneda"].str.strip().ne("")
            & encontrados["precio_unitario"].notna()
            & encontrados["precio_unitario"].gt(0)
        ]

        if not encontrados.empty:
            # La tarjeta representa descripción + unidad + moneda. El código no
            # se usa como identidad comercial porque en esta base no es
            # representativo del producto.
            claves = ["descripcion", "unidad_medida", "moneda"]
            agrupados = (
                encontrados.groupby(claves, dropna=False, as_index=False)
                .agg(
                    movimientos=("numero_oc", "size"),
                    ordenes=("numero_oc", "nunique"),
                    proveedores=("proveedor", "nunique"),
                    ultima_compra=("fecha", "max"),
                    precio_minimo=("precio_unitario", "min"),
                )
                .sort_values(["ultima_compra", "ordenes"], ascending=[False, False])
                .head(100)
            )

            for _, fila in agrupados.iterrows():
                grupo = encontrados.loc[
                    encontrados["descripcion"].eq(fila["descripcion"])
                    & encontrados["unidad_medida"].eq(fila["unidad_medida"])
                    & encontrados["moneda"].eq(fila["moneda"])
                ].sort_values(["fecha", "numero_oc"])

                ultima = grupo.iloc[-1]

                productos_encontrados.append({
                    "descripcion": fila["descripcion"],
                    "unidad": texto_seguro(fila["unidad_medida"]),
                    "codigo": "",
                    "movimientos": int(fila["movimientos"]),
                    "ordenes": int(fila["ordenes"]),
                    "proveedores": int(fila["proveedores"]),
                    "ultima_compra": fecha_texto(fila["ultima_compra"]),
                    "moneda": fila["moneda"],
                    "monedas": [fila["moneda"]],
                    "ultimo_precio": formato_moneda(ultima["precio_unitario"], fila["moneda"]),
                    "precio_minimo": formato_moneda(fila["precio_minimo"], fila["moneda"]),
                    "ultimo_proveedor": texto_seguro(ultima["proveedor"]),
                })

    # --------------------------------------------------------
    # ETAPA 2: ANALIZAR PRODUCTO EXACTO
    # --------------------------------------------------------

    if descripcion_seleccionada:
        producto = detalle[
            detalle["descripcion"] == descripcion_seleccionada
        ].copy()

        producto = producto[
            producto["unidad_medida"] == unidad_seleccionada
        ]

        monedas_disponibles = sorted(
            producto["moneda"]
            .replace("", pd.NA)
            .dropna()
            .unique()
            .tolist()
        )

        if moneda_solicitada in monedas_disponibles:
            moneda = moneda_solicitada
        elif "CLP" in monedas_disponibles:
            moneda = "CLP"
        elif monedas_disponibles:
            moneda = monedas_disponibles[0]
        else:
            moneda = ""

        historial = producto[producto["moneda"] == moneda].copy()
        historial = historial.dropna(subset=["precio_unitario"])
        historial = historial[historial["precio_unitario"] >= 0]
        historial = historial.sort_values("fecha")

        if not historial.empty:
            precios = historial["precio_unitario"].dropna()
            ultima_fila = historial.sort_values(
                "fecha", ascending=False
            ).iloc[0]

            # Comparación por proveedor. La mediana reduce el efecto
            # de compras históricas excepcionalmente altas o bajas.
            comparacion = []

            for proveedor, grupo in historial.groupby("proveedor"):
                grupo = grupo.sort_values("fecha")
                precios_proveedor = grupo["precio_unitario"].dropna()

                if precios_proveedor.empty:
                    continue

                ultima = grupo.sort_values(
                    "fecha", ascending=False
                ).iloc[0]

                referencia = float(precios_proveedor.median())

                comparacion.append(
                    {
                        "proveedor": proveedor or "Sin proveedor",
                        "ordenes": int(grupo["numero_oc"].nunique()),
                        "movimientos": int(len(grupo)),
                        "ultima_fecha_raw": grupo["fecha"].max(),
                        "ultima_compra": fecha_texto(grupo["fecha"].max()),
                        "ultimo_precio_raw": float(ultima["precio_unitario"]),
                        "ultimo_precio": formato_moneda(
                            ultima["precio_unitario"], moneda
                        ),
                        "promedio_raw": float(precios_proveedor.mean()),
                        "promedio": formato_moneda(
                            precios_proveedor.mean(), moneda
                        ),
                        "mediana_raw": referencia,
                        "mediana": formato_moneda(referencia, moneda),
                        "minimo": formato_moneda(
                            precios_proveedor.min(), moneda
                        ),
                        "maximo": formato_moneda(
                            precios_proveedor.max(), moneda
                        ),
                    }
                )

            # Proveedores con al menos 2 OC tienen evidencia suficiente
            # para participar en la recomendación principal.
            elegibles = [
                item for item in comparacion
                if item["ordenes"] >= 2
            ]

            if elegibles:
                elegibles.sort(
                    key=lambda x: (
                        x["mediana_raw"],
                        -x["ordenes"],
                        -(
                            x["ultima_fecha_raw"].timestamp()
                            if pd.notna(x["ultima_fecha_raw"])
                            else 0
                        ),
                    )
                )
                recomendado = elegibles[0]
            elif comparacion:
                comparacion_ordenada = sorted(
                    comparacion,
                    key=lambda x: x["mediana_raw"],
                )
                recomendado = comparacion_ordenada[0]
            else:
                recomendado = None

            comparacion.sort(
                key=lambda x: (
                    x["mediana_raw"],
                    -x["ordenes"],
                )
            )

            recomendacion = None

            if recomendado:
                otros = [
                    x["mediana_raw"]
                    for x in comparacion
                    if x["proveedor"] != recomendado["proveedor"]
                ]

                benchmark = (
                    float(pd.Series(otros).median())
                    if otros else None
                )

                diferencia_pct = None
                ahorro_unitario = None
                ahorro_estimado = None
                costo_recomendado = None
                costo_benchmark = None

                if benchmark and benchmark > 0:
                    diferencia_pct = (
                        (recomendado["mediana_raw"] - benchmark)
                        / benchmark
                        * 100
                    )
                    ahorro_unitario = max(
                        benchmark - recomendado["mediana_raw"], 0
                    )

                if cantidad_simulacion:
                    costo_recomendado = (
                        recomendado["mediana_raw"]
                        * cantidad_simulacion
                    )

                    if benchmark is not None:
                        costo_benchmark = benchmark * cantidad_simulacion
                        ahorro_estimado = max(
                            costo_benchmark - costo_recomendado, 0
                        )

                ultima_fecha = recomendado["ultima_fecha_raw"]
                dias_antiguedad = None

                if pd.notna(ultima_fecha):
                    hoy = pd.Timestamp.now().normalize()
                    dias_antiguedad = max(
                        int((hoy - ultima_fecha.normalize()).days), 0
                    )

                if recomendado["ordenes"] >= 4:
                    confianza = "Sólido"
                elif recomendado["ordenes"] >= 2:
                    confianza = "Moderado"
                else:
                    confianza = "Limitado"

                recomendacion = {
                    "proveedor": recomendado["proveedor"],
                    "precio_referencia": formato_moneda(
                        recomendado["mediana_raw"], moneda
                    ),
                    "ordenes": recomendado["ordenes"],
                    "ultima_compra": recomendado["ultima_compra"],
                    "confianza": confianza,
                    "diferencia_pct": (
                        round(diferencia_pct, 1)
                        if diferencia_pct is not None
                        else None
                    ),
                    "benchmark": (
                        formato_moneda(benchmark, moneda)
                        if benchmark is not None
                        else None
                    ),
                    "cantidad": cantidad_simulacion,
                    "cantidad_texto": (
                        formato_numero(cantidad_simulacion, 2)
                        if cantidad_simulacion else None
                    ),
                    "costo_recomendado": (
                        formato_moneda(costo_recomendado, moneda)
                        if costo_recomendado is not None
                        else None
                    ),
                    "costo_benchmark": (
                        formato_moneda(costo_benchmark, moneda)
                        if costo_benchmark is not None
                        else None
                    ),
                    "ahorro_estimado": (
                        formato_moneda(ahorro_estimado, moneda)
                        if ahorro_estimado is not None
                        else None
                    ),
                }

            # Datos del gráfico histórico.
            grafico = {
                "labels": [
                    fecha_texto(fecha)
                    for fecha in historial["fecha"].tolist()
                ],
                "values": [
                    float(valor)
                    for valor in historial["precio_unitario"].tolist()
                ],
                "proveedores": historial["proveedor"].tolist(),
                "ordenes": historial["numero_oc"].tolist(),
                "moneda": moneda,
                "simbolo": obtener_simbolo_moneda(moneda),
            }

            movimientos = []
            for _, fila in historial.sort_values(
                "fecha", ascending=False
            ).head(100).iterrows():
                movimientos.append(
                    {
                        "fecha": fecha_texto(fila["fecha"]),
                        "numero_oc": fila["numero_oc"],
                        "hospital": fila["hospital"],
                        "proveedor": fila["proveedor"],
                        "cantidad": formato_numero(fila["cantidad"], 2),
                        "precio": formato_moneda(
                            fila["precio_unitario"], moneda
                        ),
                        "total": formato_moneda(
                            fila["total_linea"], moneda
                        ),
                    }
                )

            analisis = {
                "descripcion": descripcion_seleccionada,
                "unidad": unidad_seleccionada,
                "codigo": codigo_seleccionado,
                "moneda": moneda,
                "monedas": monedas_disponibles,
                "ordenes": int(historial["numero_oc"].nunique()),
                "proveedores": int(historial["proveedor"].nunique()),
                "movimientos": int(len(historial)),
                "ultima_compra": fecha_texto(historial["fecha"].max()),
                "ultimo_precio": formato_moneda(
                    ultima_fila["precio_unitario"], moneda
                ),
                "promedio": formato_moneda(precios.mean(), moneda),
                "mediana": formato_moneda(precios.median(), moneda),
                "minimo": formato_moneda(precios.min(), moneda),
                "maximo": formato_moneda(precios.max(), moneda),
                "comparacion": comparacion,
                "recomendacion": recomendacion,
                "grafico": grafico,
                "movimientos_detalle": movimientos,
            }

    return render_template(
        "productos.html",
        pagina="productos",
        busqueda=busqueda,
        productos=productos_encontrados,
        analisis=analisis,
        descripcion_seleccionada=descripcion_seleccionada,
        unidad_seleccionada=unidad_seleccionada,
        codigo_seleccionado=codigo_seleccionado,
        moneda_solicitada=moneda_solicitada,
        cantidad_simulacion=cantidad_simulacion,
    )


# ============================================================
# PROVEEDORES
# ============================================================

@app.route("/proveedores")
def proveedores():
    """Consulta y analiza el historial de un proveedor."""

    ordenes, _, detalle = cargar_datos()

    busqueda = request.args.get(
        "q",
        "",
    ).strip()

    proveedor_seleccionado = request.args.get(
        "proveedor",
        "",
    ).strip()

    mostrar_todos = request.args.get("todos", "").strip() == "1"
    resultados_busqueda = []
    ficha = None

    # --------------------------------------------------------
    # CATÁLOGO / PRINCIPALES PROVEEDORES
    # --------------------------------------------------------

    ordenes_validas = ordenes.loc[ordenes["proveedor"].str.strip().ne("")].copy()
    catalogo_df = (
        ordenes_validas.groupby("proveedor", as_index=False)
        .agg(
            rut=("rut_proveedor", "first"),
            ordenes=("numero_oc", "nunique"),
            ultima_compra=("fecha", "max"),
        )
        .sort_values(["ordenes", "ultima_compra"], ascending=[False, False])
    )

    conteo_productos = (
        detalle.loc[detalle["descripcion"].str.strip().ne("")]
        .groupby("proveedor")["descripcion"]
        .nunique()
        .to_dict()
    )

    frecuentes = (
        detalle.loc[
            detalle["proveedor"].str.strip().ne("")
            & detalle["descripcion"].str.strip().ne("")
        ]
        .groupby(["proveedor", "descripcion"])
        .size()
        .reset_index(name="veces")
        .sort_values(["proveedor", "veces"], ascending=[True, False])
    )
    muestras_por_proveedor = (
        frecuentes.groupby("proveedor")["descripcion"]
        .apply(lambda serie: serie.head(3).tolist())
        .to_dict()
    )

    catalogo = []
    for _, fila in catalogo_df.iterrows():
        nombre = fila["proveedor"]
        catalogo.append({
            "nombre": nombre,
            "rut": texto_seguro(fila["rut"]),
            "ordenes": int(fila["ordenes"]),
            "productos": int(conteo_productos.get(nombre, 0)),
            "ultima_compra": fecha_texto(fila["ultima_compra"]),
            "muestras": muestras_por_proveedor.get(nombre, []),
        })

    total_catalogo = len(catalogo)

    if busqueda and not proveedor_seleccionado:
        termino = busqueda.lower()
        resultados_busqueda = [
            item for item in catalogo
            if termino in item["nombre"].lower()
            or termino in item["rut"].lower()
            or any(termino in producto.lower() for producto in item["muestras"])
        ][:100]
    elif not proveedor_seleccionado:
        resultados_busqueda = catalogo if mostrar_todos else catalogo[:25]

    # --------------------------------------------------------
    # FICHA DEL PROVEEDOR
    # --------------------------------------------------------

    if proveedor_seleccionado:

        oc_proveedor = ordenes[
            ordenes["proveedor"]
            == proveedor_seleccionado
        ].copy()

        detalle_proveedor = detalle[
            detalle["proveedor"]
            == proveedor_seleccionado
        ].copy()

        if not oc_proveedor.empty:

            # ------------------------------------------------
            # DATOS GENERALES
            # ------------------------------------------------

            rut = texto_seguro(
                oc_proveedor[
                    "rut_proveedor"
                ].iloc[0]
            )

            primera_compra = (
                oc_proveedor["fecha"].min()
            )

            ultima_compra = (
                oc_proveedor["fecha"].max()
            )

            total_oc = int(
                oc_proveedor[
                    "numero_oc"
                ].nunique()
            )

            total_productos = int(
                detalle_proveedor[
                    "descripcion"
                ]
                .replace("", pd.NA)
                .dropna()
                .nunique()
            )

            hospitales = lista_limpia(
                oc_proveedor["hospital"]
            )

            monedas = lista_limpia(
                oc_proveedor["moneda"]
            )

            # ------------------------------------------------
            # TOTALES POR MONEDA
            # Nunca mezclamos monedas.
            # ------------------------------------------------

            totales_moneda_df = (
                oc_proveedor
                .groupby(
                    "moneda",
                    as_index=False,
                )
                .agg(
                    total=(
                        "total",
                        "sum",
                    ),
                    ordenes=(
                        "numero_oc",
                        "nunique",
                    ),
                )
                .sort_values(
                    "total",
                    ascending=False,
                )
            )

            totales_moneda = []

            for _, fila in (
                totales_moneda_df.iterrows()
            ):

                totales_moneda.append(
                    {
                        "moneda": fila[
                            "moneda"
                        ],
                        "ordenes": int(
                            fila[
                                "ordenes"
                            ]
                        ),
                        "total": formato_moneda(
                            fila["total"],
                            fila["moneda"],
                        ),
                    }
                )

            # ------------------------------------------------
            # ACTIVIDAD POR AÑO
            # Usamos número de OC para no mezclar monedas.
            # ------------------------------------------------

            actividad_df = (
                oc_proveedor
                .dropna(
                    subset=["fecha"]
                )
                .copy()
            )

            if not actividad_df.empty:

                actividad_df["anio"] = (
                    actividad_df[
                        "fecha"
                    ].dt.year
                )

                actividad_df = (
                    actividad_df
                    .groupby(
                        "anio",
                        as_index=False,
                    )
                    .agg(
                        ordenes=(
                            "numero_oc",
                            "nunique",
                        )
                    )
                    .sort_values(
                        "anio"
                    )
                )

                grafico_actividad = {
                    "labels": (
                        actividad_df[
                            "anio"
                        ]
                        .astype(int)
                        .astype(str)
                        .tolist()
                    ),
                    "values": (
                        actividad_df[
                            "ordenes"
                        ]
                        .astype(int)
                        .tolist()
                    ),
                }

            else:

                grafico_actividad = {
                    "labels": [],
                    "values": [],
                }

            # ------------------------------------------------
            # DISTRIBUCIÓN POR HOSPITAL
            # Número de OC, no monto.
            # ------------------------------------------------

            hospital_df = (
                oc_proveedor[
                    oc_proveedor[
                        "hospital"
                    ] != ""
                ]
                .groupby(
                    "hospital",
                    as_index=False,
                )
                .agg(
                    ordenes=(
                        "numero_oc",
                        "nunique",
                    )
                )
                .sort_values(
                    "ordenes",
                    ascending=False,
                )
            )

            grafico_hospitales_proveedor = {
                "labels": (
                    hospital_df[
                        "hospital"
                    ].tolist()
                ),
                "values": (
                    hospital_df[
                        "ordenes"
                    ]
                    .astype(int)
                    .tolist()
                ),
            }

            # ------------------------------------------------
            # PRODUCTOS DEL PROVEEDOR
            # Separamos descripción + unidad + moneda.
            # ------------------------------------------------

            productos_proveedor = []

            detalle_productos = (
                detalle_proveedor[
                    detalle_proveedor[
                        "descripcion"
                    ] != ""
                ]
                .copy()
            )

            if not detalle_productos.empty:

                grupos = (
                    detalle_productos
                    .groupby(
                        [
                            "descripcion",
                            "unidad_medida",
                            "moneda",
                        ],
                        dropna=False,
                    )
                )

                for (
                    descripcion,
                    unidad,
                    moneda_producto,
                ), grupo in grupos:

                    grupo = grupo.sort_values(
                        "fecha"
                    )

                    precios = (
                        pd.to_numeric(
                            grupo[
                                "precio_unitario"
                            ],
                            errors="coerce",
                        )
                        .dropna()
                    )

                    ultima_fila = (
                        grupo
                        .sort_values(
                            "fecha",
                            ascending=False,
                        )
                        .iloc[0]
                    )

                    ultimo_precio = (
                        ultima_fila[
                            "precio_unitario"
                        ]
                    )

                    precio_promedio = (
                        precios.mean()
                        if not precios.empty
                        else None
                    )

                    precio_minimo = (
                        precios.min()
                        if not precios.empty
                        else None
                    )

                    precio_maximo = (
                        precios.max()
                        if not precios.empty
                        else None
                    )

                    productos_proveedor.append(
                        {
                            "descripcion": (
                                descripcion
                            ),
                            "unidad": (
                                texto_seguro(
                                    unidad
                                )
                            ),
                            "moneda": (
                                moneda_producto
                            ),
                            "compras": int(
                                grupo[
                                    "numero_oc"
                                ].nunique()
                            ),
                            "ultima_compra": (
                                fecha_texto(
                                    grupo[
                                        "fecha"
                                    ].max()
                                )
                            ),
                            "ultimo_precio": (
                                formato_moneda(
                                    ultimo_precio,
                                    moneda_producto,
                                )
                            ),
                            "promedio": (
                                formato_moneda(
                                    precio_promedio,
                                    moneda_producto,
                                )
                            ),
                            "minimo": (
                                formato_moneda(
                                    precio_minimo,
                                    moneda_producto,
                                )
                            ),
                            "maximo": (
                                formato_moneda(
                                    precio_maximo,
                                    moneda_producto,
                                )
                            ),
                            "_fecha": (
                                grupo[
                                    "fecha"
                                ].max()
                            ),
                        }
                    )

                productos_proveedor.sort(
                    key=lambda x: (
                        pd.Timestamp.min
                        if pd.isna(
                            x["_fecha"]
                        )
                        else x["_fecha"]
                    ),
                    reverse=True,
                )

                productos_proveedor = (
                    productos_proveedor[
                        :100
                    ]
                )

            # Quitamos campo interno de ordenamiento.

            for producto in (
                productos_proveedor
            ):
                producto.pop(
                    "_fecha",
                    None,
                )

            # ------------------------------------------------
            # HISTORIAL DE OC
            # ------------------------------------------------

            historial_oc = []

            historial_df = (
                oc_proveedor
                .sort_values(
                    "fecha",
                    ascending=False,
                )
            )

            for _, fila in (
                historial_df.iterrows()
            ):

                historial_oc.append(
                    {
                        "numero_oc": fila[
                            "numero_oc"
                        ],
                        "fecha": fecha_texto(
                            fila["fecha"]
                        ),
                        "hospital": fila[
                            "hospital"
                        ],
                        "moneda": fila[
                            "moneda"
                        ],
                        "total": formato_moneda(
                            fila["total"],
                            fila["moneda"],
                        ),
                        "solicitante": fila[
                            "solicitante_oc"
                        ],
                        "estado": fila[
                            "estado_proceso"
                        ],
                    }
                )

            # ------------------------------------------------
            # FICHA FINAL
            # ------------------------------------------------

            ficha = {
                "nombre": (
                    proveedor_seleccionado
                ),
                "rut": rut,
                "ordenes": total_oc,
                "productos": total_productos,
                "primera_compra": (
                    fecha_texto(
                        primera_compra
                    )
                ),
                "ultima_compra": (
                    fecha_texto(
                        ultima_compra
                    )
                ),
                "hospitales": hospitales,
                "monedas": monedas,
                "totales_moneda": (
                    totales_moneda
                ),
                "productos_detalle": (
                    productos_proveedor
                ),
                "historial_oc": (
                    historial_oc
                ),
                "grafico_actividad": (
                    grafico_actividad
                ),
                "grafico_hospitales": (
                    grafico_hospitales_proveedor
                ),
            }

    return render_template(
        "proveedores.html",
        pagina="proveedores",
        busqueda=busqueda,
        proveedor_seleccionado=(
            proveedor_seleccionado
        ),
        resultados=(
            resultados_busqueda
        ),
        ficha=ficha,
        mostrar_todos=mostrar_todos,
        total_catalogo=total_catalogo,
    )


# ============================================================
# ANÁLISIS DE PRECIOS
# ============================================================

@app.route("/precios")
def precios():
    """Análisis histórico de precios sin mezclar monedas."""

    _, _, detalle = cargar_datos()
    producto = request.args.get("producto", "").strip()
    proveedor = request.args.get("proveedor", "").strip()
    moneda = request.args.get("moneda", "").strip()
    hospital = request.args.get("hospital", "").strip()

    monedas = lista_limpia(detalle["moneda"])
    hospitales = lista_limpia(detalle["hospital"])
    df = detalle.copy()
    hay_filtros = any([producto, proveedor, moneda, hospital])

    if producto:
        df = df.loc[df["descripcion"].str.contains(producto, case=False, na=False, regex=False)]
    if proveedor:
        df = df.loc[df["proveedor"].str.contains(proveedor, case=False, na=False, regex=False)]
    if moneda:
        df = df.loc[df["moneda"].eq(moneda)]
    if hospital:
        df = df.loc[df["hospital"].eq(hospital)]

    resultados = []
    resumen_monedas = []
    evolucion = {"labels": [], "values": [], "moneda": moneda}

    # Estadísticas históricas globales por producto exacto, unidad y moneda.
    historico_valido = detalle.loc[
        detalle["descripcion"].str.strip().ne("")
        & detalle["moneda"].str.strip().ne("")
        & detalle["precio_unitario"].notna()
        & detalle["precio_unitario"].gt(0)
    ].copy()

    stats_historicas = (
        historico_valido.groupby(
            ["descripcion", "unidad_medida", "moneda"],
            dropna=False,
            as_index=False,
        )
        .agg(
            minimo_historico=("precio_unitario", "min"),
            maximo_historico=("precio_unitario", "max"),
        )
    )

    if hay_filtros and not df.empty:
        validos = df.loc[df["precio_unitario"].notna() & df["precio_unitario"].gt(0)].copy()

        for mon, g in validos.groupby("moneda"):
            ordenado = g.dropna(subset=["fecha"]).sort_values("fecha")
            ultimo_valor = ordenado.iloc[-1]["precio_unitario"] if not ordenado.empty else g.iloc[-1]["precio_unitario"]
            resumen_monedas.append({
                "moneda": mon,
                "movimientos": len(g),
                "productos": g["descripcion"].nunique(),
                "proveedores": g["proveedor"].nunique(),
                "ultimo": formato_moneda(ultimo_valor, mon),
                "promedio": formato_moneda(g["precio_unitario"].mean(), mon),
                "mediana": formato_moneda(g["precio_unitario"].median(), mon),
                "minimo": formato_moneda(g["precio_unitario"].min(), mon),
                "maximo": formato_moneda(g["precio_unitario"].max(), mon),
            })

        monedas_resultado = validos["moneda"].dropna().unique().tolist()
        if len(monedas_resultado) == 1:
            mon = monedas_resultado[0]
            evo = validos.dropna(subset=["fecha"]).sort_values("fecha").tail(80)
            evolucion = {
                "labels": [fecha_texto(x) for x in evo["fecha"]],
                "values": evo["precio_unitario"].astype(float).tolist(),
                "moneda": mon,
            }

        if not validos.empty:
            validos = validos.merge(
                stats_historicas,
                on=["descripcion", "unidad_medida", "moneda"],
                how="left",
            )

        for _, fila in validos.sort_values("fecha", ascending=False).head(300).iterrows():
            resultados.append({
                "fecha": fecha_texto(fila["fecha"]),
                "numero_oc": fila["numero_oc"],
                "hospital": fila["hospital"],
                "descripcion": fila["descripcion"],
                "unidad": fila["unidad_medida"],
                "proveedor": fila["proveedor"],
                "precio": formato_moneda(fila["precio_unitario"], fila["moneda"]),
                "cantidad": formato_numero(fila["cantidad"], 2),
                "moneda": fila["moneda"],
                "minimo_historico": formato_moneda(fila["minimo_historico"], fila["moneda"]),
                "maximo_historico": formato_moneda(fila["maximo_historico"], fila["moneda"]),
            })

    return render_template(
        "precios.html",
        pagina="precios",
        producto=producto,
        proveedor=proveedor,
        moneda=moneda,
        hospital=hospital,
        monedas=monedas,
        hospitales=hospitales,
        resultados=resultados,
        resumen_monedas=resumen_monedas,
        evolucion=evolucion,
        hay_filtros=hay_filtros,
    )


# ============================================================
# ÓRDENES DE COMPRA
# ============================================================

@app.route("/ordenes")
def ordenes_compra():
    """Busca una orden de compra."""

    ordenes, detalle, _ = cargar_datos()

    busqueda = request.args.get(
        "q",
        "",
    ).strip()

    oc = None
    articulos = []

    if busqueda:

        encontrados = ordenes[
            ordenes["numero_oc"]
            .str.contains(
                busqueda,
                case=False,
                na=False,
                regex=False,
            )
        ]

        if not encontrados.empty:

            fila = encontrados.iloc[0]

            oc = {
                "numero_oc": fila[
                    "numero_oc"
                ],
                "fecha": fecha_texto(
                    fila["fecha"]
                ),
                "hospital": fila[
                    "hospital"
                ],
                "proveedor": fila[
                    "proveedor"
                ],
                "rut": fila[
                    "rut_proveedor"
                ],
                "direccion": fila[
                    "direccion_proveedor"
                ],
                "ciudad": fila[
                    "ciudad"
                ],
                "vendedor": fila[
                    "vendedor"
                ],
                "telefono": fila[
                    "telefono"
                ],
                "email": fila[
                    "email"
                ],
                "forma_pago": fila[
                    "forma_pago"
                ],
                "solicitud": fila[
                    "solicitud"
                ],
                "solicitante": fila[
                    "solicitante_oc"
                ],
                "aprobador": fila[
                    "primer_aprobador"
                ],
                "nota": fila[
                    "nota_interna"
                ],
                "moneda": fila[
                    "moneda"
                ],
                "subtotal": formato_moneda(
                    fila["subtotal"],
                    fila["moneda"],
                ),
                "iva": formato_moneda(
                    fila["iva"],
                    fila["moneda"],
                ),
                "total": formato_moneda(
                    fila["total"],
                    fila["moneda"],
                ),
                "estado": fila[
                    "estado_proceso"
                ],
            }

            detalle_oc = detalle[
                detalle["numero_oc"]
                == fila["numero_oc"]
            ]

            for _, item in detalle_oc.iterrows():

                articulos.append(
                    {
                        "item": item[
                            "numero_item"
                        ],
                        "codigo": item[
                            "codigo"
                        ],
                        "descripcion": item[
                            "descripcion"
                        ],
                        "unidad": item[
                            "unidad_medida"
                        ],
                        "cantidad": formato_numero(
                            item["cantidad"],
                            2,
                        ),
                        "precio": formato_moneda(
                            item[
                                "precio_unitario"
                            ],
                            item["moneda"],
                        ),
                        "total": formato_moneda(
                            item[
                                "total_linea"
                            ],
                            item["moneda"],
                        ),
                    }
                )

    return render_template(
        "ordenes.html",
        pagina="ordenes",
        busqueda=busqueda,
        oc=oc,
        articulos=articulos,
    )


# ============================================================
# ALERTAS Y OPORTUNIDADES
# ============================================================

@app.route("/alertas")
def alertas():
    """Historial y control de precios centrado en proveedor único."""

    _, _, detalle = cargar_datos()

    moneda_filtro = request.args.get("moneda", "CLP").strip().upper()
    hospital_filtro = request.args.get("hospital", "").strip()
    proveedor_filtro = request.args.get("proveedor", "").strip()
    busqueda = request.args.get("q", "").strip()
    try:
        pagina_control = max(int(request.args.get("pagina", "1")), 1)
    except (TypeError, ValueError):
        pagina_control = 1
    por_pagina = 200

    base_valida = detalle.loc[
        detalle["descripcion"].str.strip().ne("")
        & detalle["proveedor"].str.strip().ne("")
        & detalle["moneda"].str.strip().ne("")
        & detalle["precio_unitario"].notna()
        & detalle["precio_unitario"].gt(0)
        & detalle["fecha"].notna()
    ].copy()

    monedas = lista_limpia(base_valida["moneda"])
    hospitales = lista_limpia(base_valida["hospital"])
    proveedores = lista_limpia(base_valida["proveedor"])

    _, resumen = construir_resumen_productos(
        base_valida,
        moneda=moneda_filtro or None,
        hospital=hospital_filtro or None,
        busqueda=busqueda or None,
    )

    proveedor_unico = []
    total_productos = 0
    total_proveedores_unicos = 0
    con_historial = 0
    total_paginas = 1

    if not resumen.empty:
        unicos = resumen.loc[resumen["cantidad_proveedores"].eq(1)].copy()

        if proveedor_filtro:
            unicos = unicos.loc[unicos["ultimo_proveedor"].eq(proveedor_filtro)]

        total_productos = len(unicos)
        total_proveedores_unicos = unicos["ultimo_proveedor"].nunique()
        con_historial = int(unicos["cantidad_oc"].ge(2).sum())
        total_paginas = max((total_productos + por_pagina - 1) // por_pagina, 1)
        pagina_control = min(pagina_control, total_paginas)

        unicos = unicos.sort_values(
            ["ultimo_proveedor", "cantidad_oc", "ultima_fecha"],
            ascending=[True, False, False],
        )

        inicio = (pagina_control - 1) * por_pagina
        unicos = unicos.iloc[inicio:inicio + por_pagina]

        for fila in unicos.itertuples():
            variacion = fila.variacion_pct
            if pd.isna(variacion):
                variacion_texto = "Sin anterior"
                variacion_clase = "neutral"
            else:
                variacion_float = float(variacion)
                signo = "+" if variacion_float > 0 else ""
                variacion_texto = f"{signo}{formato_numero(variacion_float, 1)}%"
                variacion_clase = "up" if variacion_float > 0 else "down" if variacion_float < 0 else "neutral"

            proveedor_unico.append({
                "descripcion": fila.descripcion,
                "unidad": texto_seguro(fila.unidad_medida),
                "moneda": fila.moneda,
                "proveedor": fila.ultimo_proveedor,
                "ordenes": int(fila.cantidad_oc),
                "ultima_compra": fecha_texto(fila.ultima_fecha),
                "ultima_oc": fila.ultima_oc,
                "ultimo_precio": formato_moneda(fila.ultimo_precio, fila.moneda),
                "minimo": formato_moneda(fila.precio_minimo, fila.moneda),
                "maximo": formato_moneda(fila.precio_maximo, fila.moneda),
                "variacion": variacion_texto,
                "variacion_clase": variacion_clase,
            })

    return render_template(
        "alertas.html",
        pagina="alertas",
        moneda_seleccionada=moneda_filtro,
        hospital_seleccionado=hospital_filtro,
        proveedor_seleccionado=proveedor_filtro,
        busqueda=busqueda,
        monedas=monedas,
        hospitales=hospitales,
        proveedores=proveedores,
        proveedor_unico=proveedor_unico,
        total_productos=total_productos,
        total_proveedores_unicos=total_proveedores_unicos,
        con_historial=con_historial,
        pagina_control=pagina_control,
        total_paginas=total_paginas,
        por_pagina=por_pagina,
    )


# ============================================================
# INICIAR APLICACIÓN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )