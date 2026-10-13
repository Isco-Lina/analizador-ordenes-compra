from pathlib import Path
import json

import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ARCHIVO_EXCEL = (
    BASE_DIR
    / "data"
    / "output"
    / "ordenes_compra.xlsx"
)

ARCHIVO_CSS = (
    BASE_DIR
    / "dashboard"
    / "static"
    / "css"
    / "styles.css"
)

ARCHIVO_SALIDA = (
    BASE_DIR
    / "data"
    / "output"
    / "dashboard.html"
)


# ============================================================
# CARGA
# ============================================================

def cargar_datos():
    if not ARCHIVO_EXCEL.exists():
        raise FileNotFoundError(
            f"No se encontró el Excel:\n{ARCHIVO_EXCEL}"
        )

    ordenes = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name="ORDENES",
    )

    detalle = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name="DETALLE_OC",
    )

    if "fecha" in ordenes.columns:
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

    columnas_texto_detalle = [
        "numero_oc",
        "codigo",
        "descripcion",
        "unidad_medida",
        "moneda",
    ]

    for columna in columnas_texto_ordenes:
        if columna in ordenes.columns:
            ordenes[columna] = (
                ordenes[columna]
                .fillna("")
                .astype(str)
            )

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

    columnas_numericas_detalle = [
        "cantidad",
        "precio_unitario",
        "total_linea",
    ]

    for columna in columnas_numericas_ordenes:
        if columna in ordenes.columns:
            ordenes[columna] = pd.to_numeric(
                ordenes[columna],
                errors="coerce",
            )

    for columna in columnas_numericas_detalle:
        if columna in detalle.columns:
            detalle[columna] = pd.to_numeric(
                detalle[columna],
                errors="coerce",
            )

    return ordenes, detalle


def dataframe_a_json(df):
    copia = df.copy()

    for columna in copia.columns:
        if pd.api.types.is_datetime64_any_dtype(
            copia[columna]
        ):
            copia[columna] = copia[columna].dt.strftime(
                "%Y-%m-%d"
            )

    texto = copia.to_json(
        orient="records",
        force_ascii=False,
    )

    # Evita cerrar accidentalmente la etiqueta script.
    return texto.replace("</", "<\\/")


# ============================================================
# HTML
# ============================================================

def generar_html(ordenes, detalle):
    if ARCHIVO_CSS.exists():
        css_original = ARCHIVO_CSS.read_text(
            encoding="utf-8"
        )
    else:
        css_original = ""

    ordenes_json = dataframe_a_json(ordenes)
    detalle_json = dataframe_a_json(detalle)

    css_extra = """
    .static-nav-button {
        width: 100%;
        border: 0;
        text-align: left;
        background: transparent;
        cursor: pointer;
    }

    .static-view {
        display: none;
    }

    .static-view.active {
        display: block;
    }

    .static-click {
        cursor: pointer;
    }

    .static-toolbar {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 20px;
    }

    .static-toolbar .form-control,
    .static-toolbar .form-select {
        min-width: 180px;
    }

    .static-grid {
        display: grid;
        grid-template-columns:
            repeat(auto-fit, minmax(240px, 1fr));
        gap: 18px;
    }

    .static-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 20px;
        box-shadow: var(--shadow-sm);
    }

    .static-card:hover {
        box-shadow: var(--shadow-md);
    }

    .static-table-wrap {
        overflow-x: auto;
    }

    .static-empty {
        padding: 40px;
        text-align: center;
        color: var(--secondary);
    }

    .static-note {
        margin-top: 14px;
        font-size: 12px;
        color: var(--secondary);
    }

    .static-number {
        font-size: 28px;
        font-weight: 700;
    }

    .static-subtitle {
        color: var(--secondary);
        font-size: 12px;
    }

    .static-chart {
        height: 360px;
    }

    @media (max-width: 900px) {
        .main-content {
            margin-left: 0 !important;
            padding: 20px !important;
        }

        .sidebar {
            position: relative !important;
            width: 100% !important;
        }
    }

/* ==========================================================
   MEJORA 2026 - INICIO + DASHBOARD
   ========================================================== */
.home-hero {
    position: relative;
    overflow: hidden;
    margin-bottom: 24px;
    padding: 30px;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: linear-gradient(135deg, #ffffff 0%, #f7f8ff 100%);
    box-shadow: var(--shadow-sm);
}
.home-hero::after {
    position: absolute;
    top: -110px;
    right: -90px;
    width: 330px;
    height: 330px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(79,70,229,.14) 0%, rgba(79,70,229,0) 70%);
    content: "";
    pointer-events: none;
}
.home-hero > * { position: relative; z-index: 1; }
.home-hero h1 { margin: 0; max-width: 800px; font-size: 31px; font-weight: 780; letter-spacing: -.8px; }
.home-hero p { max-width: 780px; margin: 10px 0 0; color: var(--secondary); font-size: 13px; line-height: 1.65; }
.home-search { margin-top: 22px; max-width: 900px; }
.home-search .input-group { box-shadow: 0 8px 24px rgba(15,23,42,.06); border-radius: 11px; }
.home-search .form-control { min-height: 48px; font-size: 13px; }
.home-search .btn { min-width: 118px; }
.home-search-hint { margin-top: 9px; color: var(--muted); font-size: 10px; }
.quick-actions-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 14px; }
.quick-action-card { display: flex; min-height: 155px; flex-direction: column; padding: 19px; border: 1px solid var(--border); border-radius: 12px; background: var(--surface); box-shadow: var(--shadow-sm); cursor: pointer; transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease; }
.quick-action-card:hover { transform: translateY(-3px); border-color: #c7d2fe; box-shadow: var(--shadow-md); }
.quick-action-top { display: flex; align-items: center; gap: 11px; }
.quick-action-icon { display: flex; width: 38px; height: 38px; flex: 0 0 38px; align-items: center; justify-content: center; border-radius: 9px; background: var(--primary-soft); color: var(--primary); font-size: 16px; }
.quick-action-card h3 { margin: 0; color: var(--text); font-size: 13px; font-weight: 720; }
.quick-action-card p { flex: 1; margin: 11px 0 15px; color: var(--secondary); font-size: 10px; line-height: 1.55; }
.quick-action-link { color: var(--primary); font-size: 10px; font-weight: 700; }
.home-recent-footer { display: flex; justify-content: flex-end; margin-top: 14px; }
.metric-trend { display: inline-flex; align-items: center; gap: 5px; margin-top: 7px; font-size: 10px; font-weight: 700; }
.metric-trend.positive { color: #047857; }
.metric-trend.negative { color: #b91c1c; }
.metric-trend.neutral { color: var(--muted); }
.dashboard-period-label { display: inline-flex; align-items: center; gap: 7px; padding: 6px 10px; border: 1px solid #e0e7ff; border-radius: 999px; background: #f8f9ff; color: var(--primary); font-size: 10px; font-weight: 700; }
.insight-grid { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 10px; margin-top: 18px; }
.insight-item { padding: 13px; border: 1px solid #edf0f3; border-radius: 9px; background: #fafbfc; }
.insight-item span { display: block; margin-bottom: 5px; color: var(--muted); font-size: 9px; text-transform: uppercase; letter-spacing: .03em; }
.insight-item strong { display: block; color: var(--text); font-size: 13px; font-weight: 740; }
.concentration-list { display: grid; gap: 11px; margin-top: 20px; }
.concentration-row { display: grid; grid-template-columns: 110px 1fr 58px; gap: 10px; align-items: center; }
.concentration-row span { color: var(--secondary); font-size: 10px; }
.concentration-track { height: 8px; overflow: hidden; border-radius: 999px; background: #eef2f7; }
.concentration-fill { height: 100%; border-radius: inherit; background: var(--primary); }
.concentration-row strong { color: var(--text); font-size: 11px; text-align: right; }
.summary-list { display: grid; gap: 10px; margin-top: 18px; }
.summary-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding-bottom: 10px; border-bottom: 1px solid #f0f2f5; }
.summary-row:last-child { padding-bottom: 0; border-bottom: 0; }
.summary-row span { color: var(--secondary); font-size: 10px; }
.summary-row strong { max-width: 65%; color: var(--text); font-size: 11px; font-weight: 700; text-align: right; }
.top-products-list { margin-top: 16px; }
.top-product-row { display: grid; grid-template-columns: minmax(0,1fr) 64px 74px; gap: 10px; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f2f5; }
.top-product-row:last-child { border-bottom: 0; }
.top-product-row strong { overflow: hidden; color: var(--text); font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
.top-product-row span { color: var(--secondary); font-size: 9px; text-align: right; }
.dashboard-empty { padding: 35px; border: 1px dashed #d7dce4; border-radius: 12px; background: #fff; color: var(--secondary); text-align: center; }

@media (max-width: 1100px) {
    .quick-actions-grid { grid-template-columns: repeat(2,minmax(0,1fr)); }
    .insight-grid { grid-template-columns: 1fr; }
}
@media (max-width: 700px) {
    .home-hero { padding: 22px 18px; }
    .home-hero h1 { font-size: 25px; }
    .home-search .input-group { display: flex; flex-direction: column; gap: 8px; box-shadow: none; }
    .home-search .input-group > * { width: 100%; border-radius: 8px !important; border: 1px solid #dfe3e9 !important; }
    .quick-actions-grid { grid-template-columns: 1fr; }
    .concentration-row { grid-template-columns: 95px 1fr 52px; }
    .top-product-row { grid-template-columns: minmax(0,1fr) 54px 64px; }
}

    """

    javascript = r"""
    const ORDENES = __ORDENES__;
    const DETALLE = __DETALLE__;

    let charts = [];
    let DASH_TOP_COMPRAS = 10;
    let PRECIO_RESULTADOS_ACTUALES = [];
    let PRECIO_STATS_ACTUALES = null;

    const MAPA_OC = new Map(
        ORDENES.map(o => [String(o.numero_oc || ""), o])
    );

    const DETALLE_COMPLETO = DETALLE.map(d => {
        const oc = MAPA_OC.get(
            String(d.numero_oc || "")
        ) || {};

        return {
            ...d,
            fecha: oc.fecha || "",
            hospital: oc.hospital || "",
            proveedor: oc.proveedor || "",
            rut_proveedor: oc.rut_proveedor || "",
            solicitante_oc: oc.solicitante_oc || "",
            primer_aprobador: oc.primer_aprobador || "",
            estado_proceso: oc.estado_proceso || ""
        };
    });


    // ========================================================
    // UTILIDADES
    // ========================================================

    function texto(v) {
        if (
            v === null ||
            v === undefined ||
            String(v) === "NaN"
        ) {
            return "";
        }

        return String(v);
    }


    function numero(v) {
        const n = Number(v);
        return Number.isFinite(n) ? n : 0;
    }


    function escapar(v) {
        return texto(v)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    function fechaValor(v) {
        const s = texto(v);

        if (!s) {
            return 0;
        }

        const d = new Date(
            s.substring(0, 10) + "T00:00:00"
        );

        return Number.isNaN(d.getTime())
            ? 0
            : d.getTime();
    }


    function fechaTexto(v) {
        const s = texto(v);

        if (!s) {
            return "-";
        }

        const p = s.substring(0, 10).split("-");

        if (p.length !== 3) {
            return s;
        }

        return `${p[2]}-${p[1]}-${p[0]}`;
    }


    function formatoNumero(v, decimales = 0) {
        return new Intl.NumberFormat(
            "es-CL",
            {
                minimumFractionDigits: decimales,
                maximumFractionDigits: decimales
            }
        ).format(numero(v));
    }


    function formatoMoneda(v, moneda) {
        const n = numero(v);

        if (moneda === "CLP") {
            return "$ " + formatoNumero(n, 0);
        }

        if (moneda === "USD") {
            return "US$ " + formatoNumero(n, 2);
        }

        if (moneda === "EUR") {
            return "EUR " + formatoNumero(n, 2);
        }

        if (moneda === "UF") {
            return "UF " + formatoNumero(n, 4);
        }

        return formatoNumero(n, 2);
    }


    function unicos(lista) {
        return [
            ...new Set(
                lista
                    .map(x => texto(x).trim())
                    .filter(Boolean)
            )
        ].sort(
            (a, b) => a.localeCompare(
                b,
                "es",
                { sensitivity: "base" }
            )
        );
    }


    function agrupar(lista, claveFn) {
        const mapa = new Map();

        lista.forEach(item => {
            const clave = claveFn(item);

            if (!mapa.has(clave)) {
                mapa.set(clave, []);
            }

            mapa.get(clave).push(item);
        });

        return mapa;
    }


    function mediana(valores) {
        const a = valores
            .map(numero)
            .filter(v => Number.isFinite(v))
            .sort((a, b) => a - b);

        if (!a.length) {
            return 0;
        }

        const mitad = Math.floor(a.length / 2);

        if (a.length % 2) {
            return a[mitad];
        }

        return (
            a[mitad - 1] + a[mitad]
        ) / 2;
    }


    function limpiarCharts() {
        charts.forEach(c => {
            try {
                c.destroy();
            } catch (_) {}
        });

        charts = [];
    }


    function crearChart(id, config) {
        if (typeof Chart === "undefined") {
            return;
        }

        const elemento =
            document.getElementById(id);

        if (!elemento) {
            return;
        }

        const chart =
            new Chart(elemento, config);

        charts.push(chart);
    }


    function irA(vista) {
        document
            .querySelectorAll(".static-view")
            .forEach(v => {
                v.classList.remove("active");
            });

        document
            .querySelectorAll(
                ".sidebar-nav .nav-link"
            )
            .forEach(v => {
                v.classList.remove("active");
            });

        const destino =
            document.getElementById(
                "view-" + vista
            );

        if (destino) {
            destino.classList.add("active");
        }

        const nav =
            document.querySelector(
                `[data-view="${vista}"]`
            );

        if (nav) {
            nav.classList.add("active");
        }

        limpiarCharts();

        if (vista === "inicio") {
            renderInicio();
        }

        if (vista === "dashboard") {
            renderDashboard();
        }

        if (vista === "productos") {
            renderProductos();
        }

        if (vista === "proveedores") {
            renderProveedores();
        }

        if (vista === "precios") {
            renderPrecios();
        }

        if (vista === "historial") {
            renderHistorial();
        }

        if (vista === "ordenes") {
            renderOrdenes();
        }

        window.scrollTo(0, 0);
    }


    // ========================================================
    // RESUMEN DE PRODUCTOS
    // ========================================================

    function resumenProductos(rows) {
        const validos = rows.filter(r =>
            texto(r.descripcion).trim() &&
            texto(r.moneda).trim() &&
            numero(r.precio_unitario) > 0
        );

        const grupos = agrupar(
            validos,
            r =>
                texto(r.descripcion) + "\x1f" +
                texto(r.unidad_medida) + "\x1f" +
                texto(r.moneda)
        );

        const salida = [];

        grupos.forEach(grupo => {
            grupo.sort(
                (a, b) =>
                    fechaValor(a.fecha) -
                    fechaValor(b.fecha)
            );

            const ultimo =
                grupo[grupo.length - 1];

            const anterior =
                grupo.length >= 2
                    ? grupo[group.length - 2]
                    : null;

            const precios =
                grupo.map(
                    x => numero(x.precio_unitario)
                );

            const proveedores =
                unicos(
                    grupo.map(x => x.proveedor)
                );

            const ocs =
                unicos(
                    grupo.map(x => x.numero_oc)
                );

            const precioAnterior =
                anterior
                    ? numero(
                        anterior.precio_unitario
                    )
                    : 0;

            let variacion = null;

            if (precioAnterior > 0) {
                variacion = (
                    (
                        numero(
                            ultimo.precio_unitario
                        ) -
                        precioAnterior
                    ) /
                    precioAnterior
                ) * 100;
            }

            salida.push({
                descripcion:
                    texto(ultimo.descripcion),
                unidad:
                    texto(
                        ultimo.unidad_medida
                    ),
                moneda:
                    texto(ultimo.moneda),
                proveedor:
                    texto(ultimo.proveedor),
                proveedores,
                cantidadProveedores:
                    proveedores.length,
                ordenes: ocs.length,
                movimientos:
                    grupo.length,
                ultimaFecha:
                    ultimo.fecha,
                ultimaOC:
                    texto(
                        ultimo.numero_oc
                    ),
                ultimoPrecio:
                    numero(
                        ultimo.precio_unitario
                    ),
                minimo:
                    Math.min(...precios),
                maximo:
                    Math.max(...precios),
                mediana:
                    mediana(precios),
                variacion
            });
        });

        return salida;
    }


    // ========================================================
    // INICIO
    // ========================================================

    function renderInicio() {
        const vista = document.getElementById("view-inicio");

        const resumen = resumenProductos(DETALLE_COMPLETO);
        const unicosProveedor = resumen.filter(x => x.cantidadProveedores === 1);
        const ultimas = [...ORDENES]
            .sort((a, b) => fechaValor(b.fecha) - fechaValor(a.fecha))
            .slice(0, 5);

        const totalOC = unicos(ORDENES.map(x => x.numero_oc)).length;
        const totalProveedores = unicos(ORDENES.map(x => x.proveedor)).length;
        const totalProductos = unicos(DETALLE_COMPLETO.map(x => texto(x.descripcion).trim()).filter(Boolean)).length;
        const totalComprasRegistradas = DETALLE_COMPLETO.filter(
            x => texto(x.descripcion).trim()
        ).length;

        const acciones = [
            { vista: "productos", icono: "bi-search", titulo: "Buscar Producto", texto: "Consulta un producto y revisa sus precios, proveedores y órdenes de compra anteriores.", accion: "Buscar producto" },
            { vista: "proveedores", icono: "bi-buildings", titulo: "Proveedores", texto: "Revisa el historial de compras, productos y actividad de cada proveedor.", accion: "Ver proveedores" },
            { vista: "precios", icono: "bi-graph-up-arrow", titulo: "Análisis de Precios", texto: "Compara precios históricos y revisa cómo han evolucionado en el tiempo.", accion: "Analizar precios" },
            { vista: "historial", icono: "bi-clock-history", titulo: "Historial y Control", texto: "Consulta antecedentes históricos y productos asociados a uno o más proveedores.", accion: "Revisar historial" },
            { vista: "ordenes", icono: "bi-file-earmark-text", titulo: "Órdenes de Compra", texto: "Encuentra una orden de compra y revisa su información completa.", accion: "Buscar OC" },
            { vista: "dashboard", icono: "bi-grid", titulo: "Dashboard", texto: "Revisa el comportamiento de las compras por período, hospital y proveedor.", accion: "Abrir dashboard" }
        ];

        vista.innerHTML = `
        <div class="container-fluid px-0">
            <div class="page-title">
                <div>
                    <span class="page-badge">CENTRO DE CONTROL</span>
                    <h2>Panorama de Compras</h2>
                    <p>Una visión clara del historial de compras para consultar, comparar y tomar decisiones.</p>
                </div>
                <div class="data-status"><span></span>Datos disponibles</div>
            </div>

            <div class="home-hero">
                <span class="section-eyebrow">COMPRASANALYTICS</span>
                <h1>Toda la información de compras, proveedores y órdenes de compra.</h1>
                <p>
                    Encuentra rápidamente la información que necesitas y accede a un análisis completo de precios, proveedores y compras históricas.
                </p>
                <div class="home-search">
                    <div class="input-group input-group-lg">
                        <span class="input-group-text"><i class="bi bi-search"></i></span>
                        <input id="inicio-q" class="form-control" placeholder="Buscar producto, proveedor o N° de OC...">
                        <button id="inicio-buscar" class="btn btn-primary">Buscar</button>
                    </div>
                    <div class="home-search-hint">Ejemplos: MEGADREN · BUDNIK · RM-HCN-2483</div>
                </div>
            </div>

            <div class="row g-4 mb-4">
                ${kpi("Órdenes de Compra", totalOC, "OC registradas")}
                ${kpi("Proveedores", totalProveedores, "proveedores registrados")}
                ${kpi("Productos / Conceptos", totalProductos, "descripciones únicas registradas")}
                ${kpi("Compras registradas", totalComprasRegistradas, "registros de productos y servicios procesados")}
            </div>

            <div class="home-section">
                <div class="home-section-header">
                    <span class="section-eyebrow">NAVEGACIÓN RÁPIDA</span>
                    <h2>¿Qué necesitas hacer?</h2>
                    <p>Accede directamente a la información que necesitas revisar.</p>
                </div>
                <div class="quick-actions-grid">
                    ${acciones.map(a => `
                        <div class="quick-action-card" onclick="irA('${a.vista}')">
                            <div class="quick-action-top">
                                <div class="quick-action-icon"><i class="bi ${a.icono}"></i></div>
                                <h3>${escapar(a.titulo)}</h3>
                            </div>
                            <p>${escapar(a.texto)}</p>
                            <span class="quick-action-link">${escapar(a.accion)} →</span>
                        </div>
                    `).join("")}
                </div>
            </div>

            <div class="card content-card mt-4">
                <div class="card-body">
                    <div class="card-title-area">
                        <div>
                            <h3>Actividad reciente</h3>
                            <p>Últimas órdenes incorporadas al historial de compras.</p>
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table class="table purchase-table">
                            <thead>
                                <tr><th>OC</th><th>Fecha</th><th>Hospital</th><th>Proveedor</th><th class="text-end">Total</th></tr>
                            </thead>
                            <tbody>
                                ${ultimas.map(o => `
                                    <tr class="static-click" onclick="abrirOC('${escapar(o.numero_oc)}')">
                                        <td><strong>${escapar(o.numero_oc)}</strong></td>
                                        <td>${fechaTexto(o.fecha)}</td>
                                        <td>${escapar(o.hospital)}</td>
                                        <td>${escapar(o.proveedor)}</td>
                                        <td class="text-end"><strong>${formatoMoneda(o.total, o.moneda)}</strong></td>
                                    </tr>
                                `).join("")}
                            </tbody>
                        </table>
                    </div>
                    <div class="home-recent-footer">
                        <button class="btn btn-outline-primary" onclick="irA('ordenes')">Ver todas las órdenes</button>
                    </div>
                </div>
            </div>
        </div>`;

        document.getElementById("inicio-buscar").addEventListener("click", buscarUniversalInicio);
        document.getElementById("inicio-q").addEventListener("keydown", e => {
            if (e.key === "Enter") buscarUniversalInicio();
        });
    }


    function buscarUniversalInicio() {
        const input = document.getElementById("inicio-q");
        const q = input ? input.value.trim() : "";
        if (!q) return;

        const qLower = q.toLowerCase();
        const ocExacta = ORDENES.find(x => texto(x.numero_oc).toLowerCase() === qLower);
        const pareceOC = /^(rm|oc)[-\s]/i.test(q) || qLower.includes("hcn-") || qLower.includes("hpr-") || qLower.includes("hcq-");

        if (ocExacta || pareceOC) {
            irA("ordenes");
            const campo = document.getElementById("oc-q");
            if (campo) campo.value = q;
            buscarOC();
            return;
        }

        const proveedor = ORDENES.find(x => texto(x.proveedor).toLowerCase().includes(qLower));
        if (proveedor) {
            irA("proveedores");
            const campo = document.getElementById("proveedor-q");
            if (campo) campo.value = q;
            buscarProveedores();
            return;
        }

        irA("productos");
        const campo = document.getElementById("producto-q");
        if (campo) campo.value = q;
        buscarProductos();
    }



    function kpi(titulo, valor, textoInferior) {
        return `
        <div class="col-xl-3 col-md-6">
            <div class="card kpi-card h-100">
                <div class="card-body">
                    <div class="kpi-header">
                        <span>${escapar(titulo)}</span>
                    </div>

                    <div class="kpi-value">
                        ${escapar(valor)}
                    </div>

                    <div class="kpi-description">
                        ${escapar(textoInferior)}
                    </div>
                </div>
            </div>
        </div>
        `;
    }


    function tablaReferencias(rows) {
        if (!rows.length) {
            return `
            <div class="static-empty">
                Sin referencias disponibles.
            </div>
            `;
        }

        return `
        <div class="table-responsive">
            <table class="table purchase-table">
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Proveedor</th>
                        <th>OC</th>
                        <th>Última compra</th>
                        <th class="text-end">
                            Último
                        </th>
                        <th class="text-end">
                            Mín.
                        </th>
                        <th class="text-end">
                            Máx.
                        </th>
                    </tr>
                </thead>

                <tbody>
                    ${rows.map(x => `
                    <tr>
                        <td>
                            <strong>
                                ${escapar(
                                    x.descripcion
                                )}
                            </strong>
                            <small class="d-block text-muted">
                                ${escapar(
                                    x.unidad || "-"
                                )}
                                ·
                                ${escapar(
                                    x.moneda
                                )}
                            </small>
                        </td>

                        <td>
                            ${escapar(
                                x.proveedor
                            )}
                        </td>

                        <td>
                            ${x.ordenes}
                        </td>

                        <td>
                            ${fechaTexto(
                                x.ultimaFecha
                            )}
                        </td>

                        <td class="text-end">
                            <strong>
                                ${formatoMoneda(
                                    x.ultimoPrecio,
                                    x.moneda
                                )}
                            </strong>
                        </td>

                        <td class="text-end price-min">
                            ${formatoMoneda(
                                x.minimo,
                                x.moneda
                            )}
                        </td>

                        <td class="text-end price-max">
                            ${formatoMoneda(
                                x.maximo,
                                x.moneda
                            )}
                        </td>
                    </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
        `;
    }


    // ========================================================
    // DASHBOARD
    // ========================================================

    function renderDashboard() {
        const vista = document.getElementById("view-dashboard");
        const hospitales = unicos(ORDENES.map(x => x.hospital));
        const monedas = unicos(ORDENES.map(x => x.moneda));
        const anios = unicos(
            ORDENES.map(x => texto(x.fecha).substring(0, 4)).filter(Boolean)
        ).sort().reverse();
        const monedaDefault = monedas.includes("CLP") ? "CLP" : (monedas[0] || "");
        const ultimoAnio = anios[0] || "";
        const meses = [
            ["01", "Enero"], ["02", "Febrero"], ["03", "Marzo"], ["04", "Abril"],
            ["05", "Mayo"], ["06", "Junio"], ["07", "Julio"], ["08", "Agosto"],
            ["09", "Septiembre"], ["10", "Octubre"], ["11", "Noviembre"], ["12", "Diciembre"]
        ];

        vista.innerHTML = `
        <div class="container-fluid px-0">
            <div class="page-title">
                <div>
                    <span class="page-badge">ANÁLISIS EJECUTIVO</span>
                    <h2>Dashboard de Compras</h2>
                    <p>Qué está ocurriendo en las compras durante el período seleccionado.</p>
                </div>
                <div class="data-status"><span></span>Datos disponibles</div>
            </div>

            <div class="filter-panel">
                <div class="row g-3 align-items-end">
                    <div class="col-xl-3">
                        <label class="form-label">Hospital</label>
                        <select id="dash-hospital" class="form-select">
                            <option value="">Todos los hospitales</option>
                            ${hospitales.map(x => `<option value="${escapar(x)}">${escapar(x)}</option>`).join("")}
                        </select>
                    </div>
                    <div class="col-xl-2">
                        <label class="form-label">Moneda</label>
                        <select id="dash-moneda" class="form-select">
                            ${monedas.map(x => `<option value="${escapar(x)}" ${x === monedaDefault ? "selected" : ""}>${escapar(x)}</option>`).join("")}
                        </select>
                    </div>
                    <div class="col-xl-2">
                        <label class="form-label">Año</label>
                        <select id="dash-anio" class="form-select">
                            <option value="">Todos</option>
                            ${anios.map(x => `<option value="${x}" ${x === ultimoAnio ? "selected" : ""}>${x}</option>`).join("")}
                        </select>
                    </div>
                    <div class="col-xl-2">
                        <label class="form-label">Mes</label>
                        <select id="dash-mes" class="form-select">
                            <option value="">Todos</option>
                            ${meses.map(([v, n]) => `<option value="${v}">${n}</option>`).join("")}
                        </select>
                    </div>
                    <div class="col-xl-2">
                        <label class="form-label">Ranking</label>
                        <select id="dash-limite" class="form-select">
                            <option value="10" selected>Top 10</option>
                            <option value="25">Top 25</option>
                            <option value="0">Todos</option>
                        </select>
                    </div>
                    <div class="col-xl-1">
                        <button id="dash-aplicar" class="btn btn-primary w-100">Aplicar</button>
                    </div>
                </div>
            </div>

            <div id="dash-contenido"></div>
        </div>`;

        document.getElementById("dash-aplicar").addEventListener("click", actualizarDashboard);
        ["dash-hospital", "dash-moneda", "dash-anio", "dash-mes", "dash-limite"].forEach(id => {
            document.getElementById(id).addEventListener("change", actualizarDashboard);
        });
        actualizarDashboard();
    }


    function nombreMes(numeroMes) {
        const nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
        const indice = Number(numeroMes) - 1;
        return indice >= 0 && indice < nombres.length ? nombres[indice] : "";
    }


    function variacionPorcentual(actual, anterior) {
        actual = numero(actual);
        anterior = numero(anterior);
        if (anterior === 0) return null;
        return ((actual - anterior) / anterior) * 100;
    }


    function textoVariacion(actual, anterior, etiquetaAnterior) {
        if (anterior === null || anterior === undefined) {
            return { texto: "Sin período comparable", clase: "neutral", icono: "bi-dash" };
        }
        const v = variacionPorcentual(actual, anterior);
        if (v === null) {
            return { texto: "Sin base comparable", clase: "neutral", icono: "bi-dash" };
        }
        const clase = v > 0 ? "positive" : (v < 0 ? "negative" : "neutral");
        const icono = v > 0 ? "bi-arrow-up" : (v < 0 ? "bi-arrow-down" : "bi-dash");
        const signo = v > 0 ? "+" : "";
        return { texto: `${signo}${formatoNumero(v, 1)}% vs ${etiquetaAnterior}`, clase, icono };
    }


    function kpiComparativo(titulo, valor, descripcion, comparacion) {
        return `
        <div class="col-xl-3 col-md-6">
            <div class="card kpi-card h-100">
                <div class="card-body">
                    <div class="kpi-header"><span>${escapar(titulo)}</span></div>
                    <div class="kpi-value">${escapar(valor)}</div>
                    <div class="kpi-description">${escapar(descripcion)}</div>
                    <div class="metric-trend ${comparacion.clase}">
                        <i class="bi ${comparacion.icono}"></i>${escapar(comparacion.texto)}
                    </div>
                </div>
            </div>
        </div>`;
    }


    function actualizarDashboard() {
        limpiarCharts();

        const hospital = document.getElementById("dash-hospital").value;
        const moneda = document.getElementById("dash-moneda").value;
        const anio = document.getElementById("dash-anio").value;
        const mes = document.getElementById("dash-mes").value;
        const limite = Number(document.getElementById("dash-limite").value);

        const filtrarBase = (o, filtroAnio = anio, filtroMes = mes) => {
            if (hospital && texto(o.hospital) !== hospital) return false;
            if (moneda && texto(o.moneda) !== moneda) return false;
            const fecha = texto(o.fecha);
            if (filtroAnio && fecha.substring(0, 4) !== filtroAnio) return false;
            if (filtroMes && fecha.substring(5, 7) !== filtroMes) return false;
            return true;
        };

        const df = ORDENES.filter(o => filtrarBase(o));

        if (!df.length) {
            document.getElementById("dash-contenido").innerHTML = `<div class="dashboard-empty"><i class="bi bi-inbox"></i><br><strong>Sin compras para los filtros seleccionados.</strong><br>Cambia el período, hospital o moneda.</div>`;
            return;
        }

        let anioAnterior = null;
        let mesAnterior = null;
        let etiquetaAnterior = "período anterior";

        if (anio && mes) {
            let y = Number(anio);
            let m = Number(mes) - 1;
            if (m === 0) { m = 12; y -= 1; }
            anioAnterior = String(y);
            mesAnterior = String(m).padStart(2, "0");
            etiquetaAnterior = `${nombreMes(mesAnterior)} ${anioAnterior}`;
        } else if (anio) {
            anioAnterior = String(Number(anio) - 1);
            mesAnterior = "";
            etiquetaAnterior = anioAnterior;
        }

        const dfAnterior = anioAnterior
            ? ORDENES.filter(o => filtrarBase(o, anioAnterior, mesAnterior))
            : [];

        const ocs = new Set(df.map(x => texto(x.numero_oc)));
        const det = DETALLE_COMPLETO.filter(x => ocs.has(texto(x.numero_oc)));
        const ocsAnterior = new Set(dfAnterior.map(x => texto(x.numero_oc)));

        const proveedoresAgrupados = agrupar(df.filter(x => texto(x.proveedor).trim()), x => texto(x.proveedor));
        const rankingCompleto = [...proveedoresAgrupados.entries()]
            .map(([nombre, rows]) => ({
                proveedor: nombre,
                ordenes: unicos(rows.map(x => x.numero_oc)).length,
                total: rows.reduce((s, x) => s + numero(x.total), 0)
            }))
            .sort((a, b) => b.total - a.total);

        const totalRanking = rankingCompleto.length;
        const ranking = limite > 0 ? rankingCompleto.slice(0, limite) : [...rankingCompleto];

        const hospitales = [...agrupar(df.filter(x => texto(x.hospital).trim()), x => texto(x.hospital)).entries()]
            .map(([nombre, rows]) => ({
                hospital: nombre,
                ordenes: unicos(rows.map(x => x.numero_oc)).length,
                total: rows.reduce((s, x) => s + numero(x.total), 0)
            }))
            .sort((a, b) => b.total - a.total);

        const totalComprado = df.reduce((s, x) => s + numero(x.total), 0);
        const totalAnterior = dfAnterior.reduce((s, x) => s + numero(x.total), 0);
        const cantidadOC = ocs.size;
        const cantidadOCAnterior = ocsAnterior.size;
        const proveedoresAnterior = unicos(dfAnterior.map(x => x.proveedor).filter(Boolean)).length;
        const ticketPromedio = cantidadOC ? totalComprado / cantidadOC : 0;
        const ticketAnterior = cantidadOCAnterior ? totalAnterior / cantidadOCAnterior : 0;

        const periodoTexto = anio
            ? (mes ? `${nombreMes(mes)} ${anio}` : anio)
            : (mes ? nombreMes(mes) : "Todo el historial");

        const comparacionDisponible = Boolean(anioAnterior);
        const cmpTotal = comparacionDisponible ? textoVariacion(totalComprado, totalAnterior, etiquetaAnterior) : textoVariacion(totalComprado, null, "");
        const cmpOC = comparacionDisponible ? textoVariacion(cantidadOC, cantidadOCAnterior, etiquetaAnterior) : textoVariacion(cantidadOC, null, "");
        const cmpProv = comparacionDisponible ? textoVariacion(totalRanking, proveedoresAnterior, etiquetaAnterior) : textoVariacion(totalRanking, null, "");
        const cmpTicket = comparacionDisponible ? textoVariacion(ticketPromedio, ticketAnterior, etiquetaAnterior) : textoVariacion(ticketPromedio, null, "");

        let evolucion;
        let evolucionTitulo;
        let evolucionSubtitulo;

        if (anio && mes) {
            const dias = agrupar(df.filter(x => x.fecha), x => texto(x.fecha).substring(0, 10));
            evolucion = [...dias.entries()].map(([periodo, rows]) => ({
                periodo,
                total: rows.reduce((s, x) => s + numero(x.total), 0),
                ordenes: unicos(rows.map(x => x.numero_oc)).length
            })).sort((a, b) => a.periodo.localeCompare(b.periodo));
            evolucionTitulo = `Evolución diaria · ${periodoTexto}`;
            evolucionSubtitulo = `Monto y cantidad de OC por día en ${escapar(moneda)}.`;
        } else {
            const mesesAgrupados = agrupar(df.filter(x => x.fecha), x => texto(x.fecha).substring(0, 7));
            evolucion = [...mesesAgrupados.entries()].map(([periodo, rows]) => ({
                periodo,
                total: rows.reduce((s, x) => s + numero(x.total), 0),
                ordenes: unicos(rows.map(x => x.numero_oc)).length
            })).sort((a, b) => a.periodo.localeCompare(b.periodo));
            evolucionTitulo = "Evolución de Compras";
            evolucionSubtitulo = `Monto y cantidad de OC por mes en ${escapar(moneda)}.`;
        }


        const montoLinea = x => {
            const totalLinea = numero(x.total_linea);
            if (totalLinea > 0) return totalLinea;
            return numero(x.cantidad) * numero(x.precio_unitario);
        };

        const totalDetallePeriodo = det.reduce(
            (s, x) => s + montoLinea(x),
            0
        );

        const principalesComprasTodas = [...agrupar(
            det.filter(x => texto(x.descripcion).trim()),
            x => texto(x.descripcion).trim()
        ).entries()]
            .map(([descripcion, rows]) => {
                const monto = rows.reduce(
                    (s, x) => s + montoLinea(x),
                    0
                );

                return {
                    descripcion,
                    monto,
                    ordenes: unicos(rows.map(x => x.numero_oc)).length,
                    proveedores: unicos(rows.map(x => x.proveedor).filter(Boolean)).length
                };
            })
            .filter(x => x.monto > 0)
            .sort((a, b) =>
                b.monto - a.monto ||
                b.ordenes - a.ordenes
            );

        const principalesCompras = principalesComprasTodas.slice(
            0,
            DASH_TOP_COMPRAS
        );

        const montoTopCompras = principalesCompras.reduce(
            (s, x) => s + x.monto,
            0
        );

        const participacionTopCompras = totalDetallePeriodo > 0
            ? (montoTopCompras / totalDetallePeriodo) * 100
            : 0;

        const hospitalBloque = !hospital ? `
            <div class="card content-card mt-4">
                <div class="card-body">
                    <div class="card-title-area">
                        <div>
                            <h3>Compras por Hospital</h3>
                            <p>Distribución del monto comprado en ${escapar(periodoTexto)}.</p>
                        </div>
                    </div>
                    <div class="chart-container"><canvas id="graficoHospitalStatic"></canvas></div>
                </div>
            </div>` : "";

        document.getElementById("dash-contenido").innerHTML = `
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                <span class="dashboard-period-label"><i class="bi bi-calendar3"></i>${escapar(periodoTexto)}</span>
                <small class="text-muted">${cantidadOC} OC · ${totalRanking} proveedores · ${det.length} líneas de artículos</small>
            </div>

            <div class="row g-4">
                ${kpiComparativo("Total Comprado", formatoMoneda(totalComprado, moneda), moneda, cmpTotal)}
                ${kpiComparativo("Órdenes de Compra", cantidadOC, "documentos", cmpOC)}
                ${kpiComparativo("Proveedores Activos", totalRanking, "proveedores distintos", cmpProv)}
                ${kpiComparativo("Ticket Promedio OC", formatoMoneda(ticketPromedio, moneda), "promedio por documento", cmpTicket)}
            </div>

            <div class="card content-card mt-4">
                <div class="card-body">
                    <div class="card-title-area"><div><h3>${evolucionTitulo}</h3><p>${evolucionSubtitulo}</p></div></div>
                    <div class="chart-container chart-large"><canvas id="graficoEvolucionStatic"></canvas></div>
                </div>
            </div>

            <div class="card content-card mt-4">
                <div class="card-body">
                    <div class="card-title-area">
                        <div>
                            <h3>Compras por proveedor</h3>
                            <p>Proveedores con mayor monto comprado en ${escapar(periodoTexto)}.</p>
                        </div>
                    </div>
                    <div class="chart-container" style="height:${Math.max(360, ranking.length * 30 + 80)}px"><canvas id="graficoProveedoresStatic"></canvas></div>
                </div>
            </div>

            ${hospitalBloque}

            <div class="card content-card mt-4">
                <div class="card-body">
                    <div class="card-title-area align-items-center">
                        <div>
                            <h3>Principales compras del período</h3>
                            <p>Productos y conceptos con mayor monto acumulado en ${escapar(periodoTexto)}.</p>
                        </div>
                        <div class="d-flex align-items-center gap-2 flex-wrap justify-content-end">
                            <span class="dashboard-period-label">
                                Top ${DASH_TOP_COMPRAS} · ${formatoNumero(participacionTopCompras, 1)}% del monto analizado
                            </span>
                            <select id="dash-top-compras-selector" class="form-select form-select-sm" style="width:auto;min-height:34px;">
                                <option value="10" ${DASH_TOP_COMPRAS === 10 ? "selected" : ""}>Top 10</option>
                                <option value="25" ${DASH_TOP_COMPRAS === 25 ? "selected" : ""}>Top 25</option>
                            </select>
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table class="table purchase-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Producto / concepto</th>
                                    <th class="text-end">Monto comprado</th>
                                    <th class="text-end">OC</th>
                                    <th class="text-end">Proveedores</th>
                                    <th class="text-end">% del período</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${principalesCompras.length ? principalesCompras.map((x, i) => `
                                    <tr>
                                        <td>${i + 1}</td>
                                        <td class="product-cell"><strong>${escapar(x.descripcion)}</strong></td>
                                        <td class="text-end"><strong>${formatoMoneda(x.monto, moneda)}</strong></td>
                                        <td class="text-end">${x.ordenes}</td>
                                        <td class="text-end">${x.proveedores}</td>
                                        <td class="text-end">${totalDetallePeriodo > 0 ? formatoNumero((x.monto / totalDetallePeriodo) * 100, 1) : "0,0"}%</td>
                                    </tr>`).join("") : `
                                    <tr><td colspan="6"><div class="static-empty">Sin compras con monto disponible para el período.</div></td></tr>`}
                            </tbody>
                        </table>
                    </div>
                    <div class="supplier-table-note mt-3">
                        <i class="bi bi-info-circle"></i>
                        <span>El ranking utiliza el monto de las líneas de artículos de las OC filtradas. Si una línea no trae total, se estima con cantidad × precio unitario.</span>
                    </div>
                </div>
            </div>`;

        const selectorTopCompras = document.getElementById("dash-top-compras-selector");
        if (selectorTopCompras) {
            selectorTopCompras.addEventListener("change", () => {
                DASH_TOP_COMPRAS = Number(selectorTopCompras.value) || 10;
                actualizarDashboard();
            });
        }

        setTimeout(() => {
            crearChart("graficoEvolucionStatic", {
                data: {
                    labels: evolucion.map(x => x.periodo),
                    datasets: [
                        { type: "line", label: "Monto comprado", data: evolucion.map(x => x.total), yAxisID: "y", borderWidth: 2, tension: .25 },
                        { type: "bar", label: "Cantidad de OC", data: evolucion.map(x => x.ordenes), yAxisID: "y1", borderWidth: 0 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: "index", intersect: false },
                    scales: {
                        y: { beginAtZero: true, position: "left" },
                        y1: { beginAtZero: true, position: "right", grid: { drawOnChartArea: false }, ticks: { precision: 0 } }
                    }
                }
            });

            crearChart("graficoProveedoresStatic", {
                type: "bar",
                data: { labels: ranking.map(x => x.proveedor), datasets: [{ label: "Monto", data: ranking.map(x => x.total) }] },
                options: { indexAxis: "y", responsive: true, maintainAspectRatio: false }
            });

            if (!hospital && document.getElementById("graficoHospitalStatic")) {
                crearChart("graficoHospitalStatic", {
                    type: "doughnut",
                    data: { labels: hospitales.map(x => x.hospital), datasets: [{ data: hospitales.map(x => x.total) }] },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }
        }, 0);
    }




    // ========================================================
    // PRODUCTOS
    // ========================================================

    function renderProductos() {
        const vista =
            document.getElementById(
                "view-productos"
            );

        vista.innerHTML = `
        <div class="container-fluid px-0">

            <div class="page-title">
                <div>
                    <h2>
                        Inteligencia de Productos
                    </h2>
                    <p>
                        Busca un producto y revisa su historial sin mezclar monedas.
                    </p>
                </div>
            </div>

            <div class="search-panel">
                <div class="input-group input-group-lg">
                    <input
                        id="producto-q"
                        class="form-control"
                        placeholder="Ejemplo: baldosa, perfil, acero..."
                    >

                    <button
                        id="producto-buscar"
                        class="btn btn-primary"
                    >
                        Buscar
                    </button>
                </div>
            </div>

            <div id="producto-resultado"></div>

        </div>
        `;

        document
            .getElementById(
                "producto-buscar"
            )
            .addEventListener(
                "click",
                buscarProductos
            );

        document
            .getElementById(
                "producto-q"
            )
            .addEventListener(
                "keydown",
                e => {
                    if (
                        e.key === "Enter"
                    ) {
                        buscarProductos();
                    }
                }
            );
    }


    function buscarProductos() {
        const q =
            document
                .getElementById(
                    "producto-q"
                )
                .value
                .trim()
                .toLowerCase();

        const contenedor =
            document.getElementById(
                "producto-resultado"
            );

        if (!q) {
            contenedor.innerHTML = `
            <div class="static-empty">
                Escribe un producto para buscar.
            </div>
            `;
            return;
        }

        const coincidencias =
            resumenProductos(
                DETALLE_COMPLETO.filter(
                    x =>
                        texto(
                            x.descripcion
                        )
                        .toLowerCase()
                        .includes(q)
                )
            )
            .sort(
                (a, b) =>
                    fechaValor(
                        b.ultimaFecha
                    ) -
                    fechaValor(
                        a.ultimaFecha
                    )
            )
            .slice(0, 100);

        if (!coincidencias.length) {
            contenedor.innerHTML = `
            <div class="static-empty">
                No encontramos productos.
            </div>
            `;
            return;
        }

        contenedor.innerHTML = `
        <div class="static-grid">
            ${coincidencias.map((x, i) => `
                <div
                    class="static-card static-click"
                    data-product-index="${i}"
                >
                    <strong>
                        ${escapar(
                            x.descripcion
                        )}
                    </strong>

                    <div class="static-subtitle">
                        ${escapar(
                            x.unidad || "-"
                        )}
                        ·
                        ${escapar(
                            x.moneda
                        )}
                    </div>

                    <hr>

                    <div>
                        Último:
                        <strong>
                            ${formatoMoneda(
                                x.ultimoPrecio,
                                x.moneda
                            )}
                        </strong>
                    </div>

                    <div>
                        Mínimo:
                        ${formatoMoneda(
                            x.minimo,
                            x.moneda
                        )}
                    </div>

                    <div>
                        ${x.ordenes} OC ·
                        ${x.cantidadProveedores}
                        proveedor(es)
                    </div>
                </div>
            `).join("")}
        </div>
        `;

        contenedor
            .querySelectorAll(
                "[data-product-index]"
            )
            .forEach(el => {
                el.addEventListener(
                    "click",
                    () => {
                        const x =
                            coincidencias[
                                Number(
                                    el.dataset
                                        .productIndex
                                )
                            ];

                        analizarProducto(
                            x.descripcion,
                            x.unidad,
                            x.moneda
                        );
                    }
                );
            });
    }


    function analizarProducto(
        descripcion,
        unidad,
        moneda
    ) {
        limpiarCharts();

        const rows =
            DETALLE_COMPLETO
                .filter(x =>
                    texto(
                        x.descripcion
                    ) === descripcion &&
                    texto(
                        x.unidad_medida
                    ) === unidad &&
                    texto(
                        x.moneda
                    ) === moneda &&
                    numero(
                        x.precio_unitario
                    ) > 0
                )
                .sort(
                    (a, b) =>
                        fechaValor(a.fecha) -
                        fechaValor(b.fecha)
                );

        if (!rows.length) {
            return;
        }

        const precios =
            rows.map(
                x =>
                    numero(
                        x.precio_unitario
                    )
            );

        const proveedores =
            agrupar(
                rows,
                x =>
                    texto(x.proveedor) ||
                    "Sin proveedor"
            );

        const comparacion =
            [...proveedores.entries()]
            .map(([nombre, grupo]) => ({
                proveedor: nombre,
                ordenes:
                    unicos(
                        grupo.map(
                            x =>
                                x.numero_oc
                        )
                    ).length,
                movimientos:
                    grupo.length,
                mediana:
                    mediana(
                        grupo.map(
                            x =>
                                x.precio_unitario
                        )
                    ),
                minimo:
                    Math.min(
                        ...grupo.map(
                            x =>
                                numero(
                                    x.precio_unitario
                                )
                        )
                    ),
                maximo:
                    Math.max(
                        ...grupo.map(
                            x =>
                                numero(
                                    x.precio_unitario
                                )
                        )
                    )
            }))
            .sort(
                (a, b) =>
                    a.mediana -
                    b.mediana
            );

        const ultimo =
            rows[rows.length - 1];

        const contenedor =
            document.getElementById(
                "producto-resultado"
            );

        contenedor.innerHTML = `
        <div class="card content-card mt-4">
            <div class="card-body">

                <div class="card-title-area">
                    <div>
                        <span class="section-eyebrow">
                            Producto seleccionado
                        </span>
                        <h2>
                            ${escapar(
                                descripcion
                            )}
                        </h2>
                        <p>
                            ${escapar(
                                unidad || "-"
                            )}
                            ·
                            ${escapar(
                                moneda
                            )}
                        </p>
                    </div>
                </div>

                <div class="row g-4">

                    ${kpi(
                        "Último precio",
                        formatoMoneda(
                            ultimo.precio_unitario,
                            moneda
                        ),
                        fechaTexto(
                            ultimo.fecha
                        )
                    )}

                    ${kpi(
                        "Mediana histórica",
                        formatoMoneda(
                            mediana(precios),
                            moneda
                        ),
                        rows.length +
                            " movimientos"
                    )}

                    ${kpi(
                        "Mínimo histórico",
                        formatoMoneda(
                            Math.min(
                                ...precios
                            ),
                            moneda
                        ),
                        "referencia histórica"
                    )}

                    ${kpi(
                        "Máximo histórico",
                        formatoMoneda(
                            Math.max(
                                ...precios
                            ),
                            moneda
                        ),
                        unicos(
                            rows.map(
                                x =>
                                    x.numero_oc
                            )
                        ).length +
                            " OC"
                    )}

                </div>

                <div class="card content-card mt-4">
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="graficoProductoStatic">
                            </canvas>
                        </div>
                    </div>
                </div>

                <div class="card content-card mt-4">
                    <div class="card-body">

                        <div class="card-title-area">
                            <div>
                                <h3>
                                    Comparación histórica por proveedor
                                </h3>
                                <p>
                                    Mediana, mínimo y máximo registrados.
                                </p>
                            </div>
                        </div>

                        <div class="table-responsive">
                            <table class="table purchase-table">
                                <thead>
                                    <tr>
                                        <th>
                                            Proveedor
                                        </th>
                                        <th>
                                            OC
                                        </th>
                                        <th>
                                            Movimientos
                                        </th>
                                        <th class="text-end">
                                            Mediana
                                        </th>
                                        <th class="text-end">
                                            Mín.
                                        </th>
                                        <th class="text-end">
                                            Máx.
                                        </th>
                                    </tr>
                                </thead>

                                <tbody>
                                    ${comparacion.map(x => `
                                    <tr>
                                        <td>
                                            ${escapar(
                                                x.proveedor
                                            )}
                                        </td>

                                        <td>
                                            ${x.ordenes}
                                        </td>

                                        <td>
                                            ${x.movimientos}
                                        </td>

                                        <td class="text-end">
                                            <strong>
                                                ${formatoMoneda(
                                                    x.mediana,
                                                    moneda
                                                )}
                                            </strong>
                                        </td>

                                        <td class="text-end">
                                            ${formatoMoneda(
                                                x.minimo,
                                                moneda
                                            )}
                                        </td>

                                        <td class="text-end">
                                            ${formatoMoneda(
                                                x.maximo,
                                                moneda
                                            )}
                                        </td>
                                    </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>

                    </div>
                </div>

                <div class="card content-card mt-4">
                    <div class="card-body">

                        <div class="card-title-area">
                            <div>
                                <h3>
                                    Movimientos históricos
                                </h3>
                            </div>
                        </div>

                        <div class="table-responsive">
                            <table class="table purchase-table">
                                <thead>
                                    <tr>
                                        <th>Fecha</th>
                                        <th>OC</th>
                                        <th>Proveedor</th>
                                        <th>Cantidad</th>
                                        <th class="text-end">
                                            Precio
                                        </th>
                                    </tr>
                                </thead>

                                <tbody>
                                    ${[...rows]
                                        .reverse()
                                        .slice(0, 100)
                                        .map(x => `
                                        <tr>
                                            <td>
                                                ${fechaTexto(
                                                    x.fecha
                                                )}
                                            </td>

                                            <td
                                                class="static-click"
                                                onclick="abrirOC('${escapar(
                                                    x.numero_oc
                                                )}')"
                                            >
                                                <strong>
                                                    ${escapar(
                                                        x.numero_oc
                                                    )}
                                                </strong>
                                            </td>

                                            <td>
                                                ${escapar(
                                                    x.proveedor
                                                )}
                                            </td>

                                            <td>
                                                ${formatoNumero(
                                                    x.cantidad,
                                                    2
                                                )}
                                            </td>

                                            <td class="text-end">
                                                ${formatoMoneda(
                                                    x.precio_unitario,
                                                    moneda
                                                )}
                                            </td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>

                    </div>
                </div>

            </div>
        </div>
        `;

        setTimeout(() => {
            crearChart(
                "graficoProductoStatic",
                {
                    type: "line",
                    data: {
                        labels:
                            rows.map(
                                x =>
                                    fechaTexto(
                                        x.fecha
                                    )
                            ),
                        datasets: [{
                            label:
                                "Precio unitario",
                            data:
                                rows.map(
                                    x =>
                                        numero(
                                            x.precio_unitario
                                        )
                                ),
                            borderWidth: 2,
                            tension: 0.2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                }
            );
        }, 0);
    }


    // ========================================================
    // PROVEEDORES
    // ========================================================

    function renderProveedores() {
        const vista =
            document.getElementById(
                "view-proveedores"
            );

        vista.innerHTML = `
        <div class="container-fluid px-0">

            <div class="page-title">
                <div>
                    <h2>Proveedores</h2>
                    <p>
                        Consulta historial, productos y actividad.
                    </p>
                </div>
            </div>

            <div class="search-panel">
                <div class="row g-3 align-items-end">
                    <div class="col-xl-9 col-lg-8">
                        <label class="form-label">Buscar proveedor</label>
                        <input
                            id="proveedor-q"
                            class="form-control"
                            placeholder="Nombre, RUT o producto..."
                        >
                    </div>
                    <div class="col-xl-2 col-lg-2">
                        <label class="form-label">Mostrar</label>
                        <select id="proveedor-limite" class="form-select">
                            <option value="10" selected>Top 10</option>
                            <option value="25">Top 25</option>
                            <option value="0">Todos</option>
                        </select>
                    </div>
                    <div class="col-xl-1 col-lg-2">
                        <button
                            id="proveedor-buscar"
                            class="btn btn-primary w-100"
                        >
                            Buscar
                        </button>
                    </div>
                </div>
            </div>

            <div id="proveedor-resultado"></div>

        </div>
        `;

        document
            .getElementById("proveedor-buscar")
            .addEventListener("click", buscarProveedores);

        document
            .getElementById("proveedor-limite")
            .addEventListener("change", buscarProveedores);

        document
            .getElementById("proveedor-q")
            .addEventListener("keydown", e => {
                if (e.key === "Enter") buscarProveedores();
            });

        buscarProveedores();
    }


    function catalogoProveedores() {
        const grupos =
            agrupar(
                ORDENES.filter(
                    x =>
                        texto(
                            x.proveedor
                        ).trim()
                ),
                x =>
                    texto(x.proveedor)
            );

        return [...grupos.entries()]
            .map(([nombre, rows]) => {
                const detalles =
                    DETALLE_COMPLETO.filter(
                        x =>
                            texto(
                                x.proveedor
                            ) === nombre
                    );

                const productos =
                    unicos(
                        detalles.map(
                            x =>
                                x.descripcion
                        )
                    );

                return {
                    nombre,
                    rut:
                        texto(
                            rows[0]
                                ?.rut_proveedor
                        ),
                    ordenes:
                        unicos(
                            rows.map(
                                x =>
                                    x.numero_oc
                            )
                        ).length,
                    productos:
                        productos.length,
                    ultimaCompra:
                        rows.reduce(
                            (max, x) =>
                                fechaValor(
                                    x.fecha
                                ) > fechaValor(
                                    max
                                )
                                    ? x.fecha
                                    : max,
                            ""
                        ),
                    muestras:
                        productos.slice(
                            0,
                            3
                        )
                };
            })
            .sort(
                (a, b) =>
                    b.ordenes -
                        a.ordenes ||
                    fechaValor(
                        b.ultimaCompra
                    ) -
                    fechaValor(
                        a.ultimaCompra
                    )
            );
    }


    function buscarProveedores() {
        const input =
            document.getElementById(
                "proveedor-q"
            );

        const q =
            input
                ? input.value
                    .trim()
                    .toLowerCase()
                : "";

        let catalogo =
            catalogoProveedores();

        if (q) {
            catalogo =
                catalogo.filter(x =>
                    x.nombre
                        .toLowerCase()
                        .includes(q) ||
                    x.rut
                        .toLowerCase()
                        .includes(q) ||
                    x.muestras.some(
                        p =>
                            p
                            .toLowerCase()
                            .includes(q)
                    )
                );
        }

        const selectorLimite = document.getElementById("proveedor-limite");
        const limite = selectorLimite ? Number(selectorLimite.value) : 10;
        if (limite > 0) {
            catalogo = catalogo.slice(0, limite);
        }

        const contenedor =
            document.getElementById(
                "proveedor-resultado"
            );

        if (!catalogo.length) {
            contenedor.innerHTML = `
            <div class="static-empty">
                Sin proveedores.
            </div>
            `;
            return;
        }

        contenedor.innerHTML = `
        <div class="static-grid">
            ${catalogo.map((x, i) => `
            <div
                class="static-card static-click"
                data-supplier-index="${i}"
            >
                <h3>
                    ${escapar(
                        x.nombre
                    )}
                </h3>

                <div class="static-subtitle">
                    RUT:
                    ${escapar(
                        x.rut || "-"
                    )}
                </div>

                <hr>

                <div>
                    <strong>
                        ${x.ordenes}
                    </strong>
                    OC
                </div>

                <div>
                    <strong>
                        ${x.productos}
                    </strong>
                    productos
                </div>

                <div>
                    Última:
                    ${fechaTexto(
                        x.ultimaCompra
                    )}
                </div>

                <div class="static-note">
                    ${escapar(
                        x.muestras.join(
                            " · "
                        )
                    )}
                </div>
            </div>
            `).join("")}
        </div>
        `;

        contenedor
            .querySelectorAll(
                "[data-supplier-index]"
            )
            .forEach(el => {
                el.addEventListener(
                    "click",
                    () => {
                        const x =
                            catalogo[
                                Number(
                                    el.dataset
                                        .supplierIndex
                                )
                            ];

                        verProveedor(
                            x.nombre
                        );
                    }
                );
            });
    }


    function verProveedor(nombre) {
        const ordenes =
            ORDENES.filter(
                x =>
                    texto(
                        x.proveedor
                    ) === nombre
            );

        const detalle =
            DETALLE_COMPLETO.filter(
                x =>
                    texto(
                        x.proveedor
                    ) === nombre
            );

        const monedas =
            agrupar(
                ordenes,
                x =>
                    texto(x.moneda)
            );

        const totales =
            [...monedas.entries()]
            .map(([moneda, rows]) => ({
                moneda,
                ordenes:
                    unicos(
                        rows.map(
                            x =>
                                x.numero_oc
                        )
                    ).length,
                total:
                    rows.reduce(
                        (s, x) =>
                            s +
                            numero(x.total),
                        0
                    )
            }));

        const productos =
            resumenProductos(detalle)
                .sort(
                    (a, b) =>
                        fechaValor(
                            b.ultimaFecha
                        ) -
                        fechaValor(
                            a.ultimaFecha
                        )
                )
                .slice(0, 100);

        const contenedor =
            document.getElementById(
                "proveedor-resultado"
            );

        contenedor.innerHTML = `
        <div class="card content-card">
            <div class="card-body">

                <div class="card-title-area">
                    <div>
                        <span class="section-eyebrow">
                            Ficha del proveedor
                        </span>

                        <h2>
                            ${escapar(
                                nombre
                            )}
                        </h2>

                        <p>
                            RUT
                            ${escapar(
                                ordenes[0]
                                    ?.rut_proveedor ||
                                "-"
                            )}
                        </p>
                    </div>
                </div>

                <div class="row g-4">

                    ${kpi(
                        "Órdenes de Compra",
                        unicos(
                            ordenes.map(
                                x =>
                                    x.numero_oc
                            )
                        ).length,
                        "OC registradas"
                    )}

                    ${kpi(
                        "Productos",
                        unicos(
                            detalle.map(
                                x =>
                                    x.descripcion
                            )
                        ).length,
                        "descripciones distintas"
                    )}

                    ${kpi(
                        "Primera compra",
                        fechaTexto(
                            [...ordenes]
                                .sort(
                                    (a, b) =>
                                        fechaValor(
                                            a.fecha
                                        ) -
                                        fechaValor(
                                            b.fecha
                                        )
                                )[0]
                                ?.fecha
                        ),
                        "historial"
                    )}

                    ${kpi(
                        "Última compra",
                        fechaTexto(
                            [...ordenes]
                                .sort(
                                    (a, b) =>
                                        fechaValor(
                                            b.fecha
                                        ) -
                                        fechaValor(
                                            a.fecha
                                        )
                                )[0]
                                ?.fecha
                        ),
                        "actividad reciente"
                    )}

                </div>

                <div class="card content-card mt-4">
                    <div class="card-body">
                        <div class="card-title-area">
                            <div>
                                <h3>
                                    Totales por moneda
                                </h3>
                                <p>
                                    Las monedas se mantienen separadas.
                                </p>
                            </div>
                        </div>

                        <div class="static-grid">
                            ${totales.map(x => `
                            <div class="static-card">
                                <strong>
                                    ${escapar(
                                        x.moneda
                                    )}
                                </strong>

                                <div class="static-number">
                                    ${formatoMoneda(
                                        x.total,
                                        x.moneda
                                    )}
                                </div>

                                <div class="static-subtitle">
                                    ${x.ordenes}
                                    OC
                                </div>
                            </div>
                            `).join("")}
                        </div>
                    </div>
                </div>

                <div class="card content-card mt-4">
                    <div class="card-body">

                        <div class="card-title-area">
                            <div>
                                <h3>
                                    Productos del proveedor
                                </h3>
                            </div>
                        </div>

                        ${tablaReferencias(
                            productos
                        )}

                    </div>
                </div>

            </div>
        </div>
        `;
    }


    // ========================================================
    // PRECIOS
    // ========================================================

    function renderPrecios() {
        const vista =
            document.getElementById(
                "view-precios"
            );

        const monedas =
            unicos(
                DETALLE_COMPLETO.map(
                    x => x.moneda
                )
            );

        const hospitales =
            unicos(
                DETALLE_COMPLETO.map(
                    x => x.hospital
                )
            );

        vista.innerHTML = `
        <div class="container-fluid px-0">

            <div class="page-title">
                <div>
                    <h2>
                        Análisis de Precios
                    </h2>
                    <p>
                        Consulta precios históricos por producto, proveedor, moneda y hospital.
                    </p>
                </div>
            </div>

            <div class="filter-panel">
                <div class="row g-3">

                    <div class="col-xl-4">
                        <label class="form-label">
                            Producto
                        </label>
                        <input
                            id="precio-producto"
                            class="form-control"
                            placeholder="Ej.: cable, adhesivo, perfil, drenaje..."
                        >
                    </div>

                    <div class="col-xl-3">
                        <label class="form-label">
                            Proveedor
                        </label>
                        <input
                            id="precio-proveedor"
                            class="form-control"
                            placeholder="Ej.: Budnik, Dartel, Rhona..."
                        >
                    </div>

                    <div class="col-xl-2">
                        <label class="form-label">
                            Moneda
                        </label>
                        <select
                            id="precio-moneda"
                            class="form-select"
                        >
                            <option value="">
                                Todas
                            </option>

                            ${monedas.map(x => `
                            <option value="${escapar(x)}">
                                ${escapar(x)}
                            </option>
                            `).join("")}
                        </select>
                    </div>

                    <div class="col-xl-3">
                        <label class="form-label">
                            Hospital
                        </label>
                        <select
                            id="precio-hospital"
                            class="form-select"
                        >
                            <option value="">
                                Todos
                            </option>

                            ${hospitales.map(x => `
                            <option value="${escapar(x)}">
                                ${escapar(x)}
                            </option>
                            `).join("")}
                        </select>
                    </div>

                </div>

                <div class="mt-3">
                    <button
                        id="precio-aplicar"
                        class="btn btn-primary"
                    >
                        Aplicar filtros
                    </button>
                </div>
            </div>

            <div id="precio-resultado"></div>

        </div>
        `;

        document
            .getElementById(
                "precio-aplicar"
            )
            .addEventListener(
                "click",
                aplicarPrecios
            );

        ["precio-producto", "precio-proveedor"].forEach(id => {
            document.getElementById(id).addEventListener("keydown", event => {
                if (event.key === "Enter") aplicarPrecios();
            });
        });
    }


    function aplicarPrecios() {
        const producto =
            document.getElementById(
                "precio-producto"
            ).value.trim().toLowerCase();

        const proveedor =
            document.getElementById(
                "precio-proveedor"
            ).value.trim().toLowerCase();

        const moneda =
            document.getElementById(
                "precio-moneda"
            ).value;

        const hospital =
            document.getElementById(
                "precio-hospital"
            ).value;

        const df =
            DETALLE_COMPLETO.filter(x => {
                if (
                    producto &&
                    !texto(
                        x.descripcion
                    )
                    .toLowerCase()
                    .includes(producto)
                ) {
                    return false;
                }

                if (
                    proveedor &&
                    !texto(
                        x.proveedor
                    )
                    .toLowerCase()
                    .includes(proveedor)
                ) {
                    return false;
                }

                if (
                    moneda &&
                    texto(
                        x.moneda
                    ) !== moneda
                ) {
                    return false;
                }

                if (
                    hospital &&
                    texto(
                        x.hospital
                    ) !== hospital
                ) {
                    return false;
                }

                return (
                    numero(
                        x.precio_unitario
                    ) > 0
                );
            });

        const contenedor =
            document.getElementById(
                "precio-resultado"
            );

        if (!df.length) {
            contenedor.innerHTML = `
            <div class="static-empty">
                Sin resultados.
            </div>
            `;
            return;
        }

        const stats =
            agrupar(
                DETALLE_COMPLETO.filter(
                    x =>
                        numero(
                            x.precio_unitario
                        ) > 0
                ),
                x =>
                    texto(x.descripcion) +
                    "\x1f" +
                    texto(
                        x.unidad_medida
                    ) +
                    "\x1f" +
                    texto(x.moneda)
            );

        PRECIO_RESULTADOS_ACTUALES = [...df];
        PRECIO_STATS_ACTUALES = stats;

        contenedor.innerHTML = `
        <div class="card content-card">
            <div class="card-body">

                <div class="card-title-area mb-3">
                    <div>
                        <h3>Movimientos encontrados</h3>
                        <p>${df.length} registros coinciden con los filtros principales.</p>
                    </div>
                </div>

                <div class="row g-3 align-items-end mb-3">
                    <div class="col-xl-6">
                        <label class="form-label">Buscar dentro de los resultados</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-search"></i></span>
                            <input
                                id="precio-buscar-resultados"
                                class="form-control"
                                placeholder="OC, producto, proveedor u hospital..."
                            >
                        </div>
                    </div>

                    <div class="col-xl-3">
                        <label class="form-label">Mostrar</label>
                        <select id="precio-limite-resultados" class="form-select">
                            <option value="10" selected>Top 10</option>
                            <option value="25">Top 25</option>
                            <option value="0">Todos</option>
                        </select>
                    </div>

                    <div class="col-xl-3">
                        <label class="form-label">Ordenar por</label>
                        <select id="precio-orden-resultados" class="form-select">
                            <option value="recientes" selected>Más recientes</option>
                            <option value="antiguos">Más antiguos</option>
                            <option value="precio-desc">Precio mayor</option>
                            <option value="precio-asc">Precio menor</option>
                        </select>
                    </div>
                </div>

                <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-2">
                    <small id="precio-contador-resultados" class="text-muted"></small>
                    <small class="text-muted">La tabla conserva fecha, OC, producto, unidad, proveedor, hospital, cantidad, moneda, precio, mínimo y máximo.</small>
                </div>

                <div class="table-responsive">
                    <table class="table purchase-table">
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th>OC</th>
                                <th>Producto</th>
                                <th>Unidad</th>
                                <th>Proveedor</th>
                                <th>Hospital</th>
                                <th>Cantidad</th>
                                <th>Moneda</th>
                                <th class="text-end">Precio</th>
                                <th class="text-end">Mín.</th>
                                <th class="text-end">Máx.</th>
                            </tr>
                        </thead>
                        <tbody id="precio-tabla-body"></tbody>
                    </table>
                </div>

            </div>
        </div>
        `;

        [
            "precio-buscar-resultados",
            "precio-limite-resultados",
            "precio-orden-resultados"
        ].forEach(id => {
            const elemento = document.getElementById(id);
            elemento.addEventListener(
                id === "precio-buscar-resultados" ? "input" : "change",
                actualizarTablaPrecios
            );
        });

        actualizarTablaPrecios();
    }


    function actualizarTablaPrecios() {
        const cuerpo = document.getElementById("precio-tabla-body");
        const contador = document.getElementById("precio-contador-resultados");
        if (!cuerpo || !contador) return;

        const q = texto(
            document.getElementById("precio-buscar-resultados")?.value
        ).trim().toLowerCase();

        const limite = Number(
            document.getElementById("precio-limite-resultados")?.value || 10
        );

        const orden = texto(
            document.getElementById("precio-orden-resultados")?.value || "recientes"
        );

        let filas = PRECIO_RESULTADOS_ACTUALES.filter(x => {
            if (!q) return true;
            const combinado = [
                x.numero_oc,
                x.descripcion,
                x.unidad_medida,
                x.proveedor,
                x.hospital,
                x.moneda
            ].map(texto).join(" ").toLowerCase();
            return combinado.includes(q);
        });

        filas.sort((a, b) => {
            if (orden === "antiguos") {
                return fechaValor(a.fecha) - fechaValor(b.fecha);
            }
            if (orden === "precio-desc") {
                return numero(b.precio_unitario) - numero(a.precio_unitario);
            }
            if (orden === "precio-asc") {
                return numero(a.precio_unitario) - numero(b.precio_unitario);
            }
            return fechaValor(b.fecha) - fechaValor(a.fecha);
        });

        const totalFiltrado = filas.length;
        const visibles = limite > 0 ? filas.slice(0, limite) : filas;

        contador.textContent = `Mostrando ${visibles.length} de ${totalFiltrado} movimientos`;

        if (!visibles.length) {
            cuerpo.innerHTML = `
                <tr>
                    <td colspan="11">
                        <div class="static-empty">No hay movimientos que coincidan con esta búsqueda.</div>
                    </td>
                </tr>`;
            return;
        }

        cuerpo.innerHTML = visibles.map(x => {
            const clave =
                texto(x.descripcion) +
                "\x1f" +
                texto(x.unidad_medida) +
                "\x1f" +
                texto(x.moneda);

            const hist = PRECIO_STATS_ACTUALES?.get(clave) || [];
            const valores = hist
                .map(z => numero(z.precio_unitario))
                .filter(v => v > 0);

            const minimo = valores.length
                ? Math.min(...valores)
                : numero(x.precio_unitario);

            const maximo = valores.length
                ? Math.max(...valores)
                : numero(x.precio_unitario);

            return `
            <tr>
                <td>${fechaTexto(x.fecha)}</td>
                <td class="static-click" onclick="abrirOC('${escapar(x.numero_oc)}')">
                    <strong>${escapar(x.numero_oc)}</strong>
                </td>
                <td>${escapar(x.descripcion)}</td>
                <td>${escapar(x.unidad_medida)}</td>
                <td>${escapar(x.proveedor)}</td>
                <td>${escapar(x.hospital)}</td>
                <td>${formatoNumero(x.cantidad, 2)}</td>
                <td>${escapar(x.moneda)}</td>
                <td class="text-end"><strong>${formatoMoneda(x.precio_unitario, x.moneda)}</strong></td>
                <td class="text-end">${formatoMoneda(minimo, x.moneda)}</td>
                <td class="text-end">${formatoMoneda(maximo, x.moneda)}</td>
            </tr>`;
        }).join("");
    }


    // ========================================================
    // HISTORIAL Y CONTROL
    // ========================================================

    function renderHistorial() {
        const vista =
            document.getElementById(
                "view-historial"
            );

        const monedas =
            unicos(
                DETALLE_COMPLETO.map(
                    x => x.moneda
                )
            );

        const hospitales =
            unicos(
                DETALLE_COMPLETO.map(
                    x => x.hospital
                )
            );

        const proveedores =
            unicos(
                DETALLE_COMPLETO.map(
                    x => x.proveedor
                )
            );

        vista.innerHTML = `
        <div class="container-fluid px-0">

            <div class="page-title">
                <div>
                    <span class="page-badge">
                        CONTROL HISTÓRICO
                    </span>
                    <h2>
                        Historial y Control de Precios
                    </h2>
                    <p>
                        Productos comprados a un solo proveedor.
                    </p>
                </div>
            </div>

            <div class="filter-panel">
                <div class="row g-3">

                    <div class="col-xl-3">
                        <input
                            id="hist-q"
                            class="form-control"
                            placeholder="Producto o proveedor..."
                        >
                    </div>

                    <div class="col-xl-2">
                        <select
                            id="hist-moneda"
                            class="form-select"
                        >
                            ${monedas.map(x => `
                            <option value="${escapar(x)}"
                                ${x === "CLP"
                                    ? "selected"
                                    : ""}
                            >
                                ${escapar(x)}
                            </option>
                            `).join("")}
                        </select>
                    </div>

                    <div class="col-xl-3">
                        <select
                            id="hist-hospital"
                            class="form-select"
                        >
                            <option value="">
                                Todos los hospitales
                            </option>
                            ${hospitales.map(x => `
                            <option value="${escapar(x)}">
                                ${escapar(x)}
                            </option>
                            `).join("")}
                        </select>
                    </div>

                    <div class="col-xl-3">
                        <select
                            id="hist-proveedor"
                            class="form-select"
                        >
                            <option value="">
                                Todos los proveedores
                            </option>
                            ${proveedores.map(x => `
                            <option value="${escapar(x)}">
                                ${escapar(x)}
                            </option>
                            `).join("")}
                        </select>
                    </div>

                    <div class="col-xl-1">
                        <button
                            id="hist-aplicar"
                            class="btn btn-primary"
                        >
                            Aplicar
                        </button>
                    </div>

                </div>
            </div>

            <div id="hist-resultado"></div>

        </div>
        `;

        document
            .getElementById(
                "hist-aplicar"
            )
            .addEventListener(
                "click",
                aplicarHistorial
            );

        aplicarHistorial();
    }


    function aplicarHistorial() {
        const q =
            document.getElementById(
                "hist-q"
            ).value.trim().toLowerCase();

        const moneda =
            document.getElementById(
                "hist-moneda"
            ).value;

        const hospital =
            document.getElementById(
                "hist-hospital"
            ).value;

        const proveedor =
            document.getElementById(
                "hist-proveedor"
            ).value;

        const base =
            DETALLE_COMPLETO.filter(x => {
                if (
                    moneda &&
                    texto(
                        x.moneda
                    ) !== moneda
                ) {
                    return false;
                }

                if (
                    hospital &&
                    texto(
                        x.hospital
                    ) !== hospital
                ) {
                    return false;
                }

                if (
                    numero(
                        x.precio_unitario
                    ) <= 0
                ) {
                    return false;
                }

                if (q) {
                    const combinado =
                        (
                            texto(
                                x.descripcion
                            ) +
                            " " +
                            texto(
                                x.proveedor
                            )
                        ).toLowerCase();

                    if (
                        !combinado.includes(q)
                    ) {
                        return false;
                    }
                }

                return true;
            });

        let resumen =
            resumenProductos(base)
                .filter(
                    x =>
                        x.cantidadProveedores === 1
                );

        if (proveedor) {
            resumen =
                resumen.filter(
                    x =>
                        x.proveedor === proveedor
                );
        }

        resumen.sort(
            (a, b) =>
                a.proveedor.localeCompare(
                    b.proveedor
                ) ||
                b.ordenes - a.ordenes
        );

        const contenedor =
            document.getElementById(
                "hist-resultado"
            );

        const conHistorial =
            resumen.filter(
                x =>
                    x.ordenes >= 2
            ).length;

        contenedor.innerHTML = `
        <div class="row g-4 mb-4">

            ${kpi(
                "Productos con proveedor único",
                resumen.length,
                "con filtros actuales"
            )}

            ${kpi(
                "Proveedores involucrados",
                unicos(
                    resumen.map(
                        x => x.proveedor
                    )
                ).length,
                "proveedores distintos"
            )}

            ${kpi(
                "Con historial comparable",
                conHistorial,
                "productos con 2 o más OC"
            )}

        </div>

        <div class="historical-warning mb-4">
            El mínimo, máximo y variación son referencias históricas.
            No representan automáticamente ahorro ni una alerta.
        </div>

        <div class="card content-card">
            <div class="card-body">
                ${tablaHistorial(
                    resumen.slice(0, 500)
                )}
            </div>
        </div>
        `;
    }


    function tablaHistorial(rows) {
        if (!rows.length) {
            return `
            <div class="static-empty">
                Sin resultados.
            </div>
            `;
        }

        return `
        <div class="table-responsive">
            <table class="table purchase-table">
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Proveedor</th>
                        <th>OC</th>
                        <th>Última compra</th>
                        <th>Última OC</th>
                        <th class="text-end">
                            Último
                        </th>
                        <th class="text-end">
                            Mín.
                        </th>
                        <th class="text-end">
                            Máx.
                        </th>
                        <th class="text-end">
                            Vs. anterior
                        </th>
                    </tr>
                </thead>

                <tbody>
                    ${rows.map(x => `
                    <tr>
                        <td>
                            <strong>
                                ${escapar(
                                    x.descripcion
                                )}
                            </strong>
                            <small class="d-block text-muted">
                                ${escapar(
                                    x.unidad || "-"
                                )}
                                ·
                                ${escapar(
                                    x.moneda
                                )}
                            </small>
                        </td>

                        <td>
                            ${escapar(
                                x.proveedor
                            )}
                        </td>

                        <td>
                            ${x.ordenes}
                        </td>

                        <td>
                            ${fechaTexto(
                                x.ultimaFecha
                            )}
                        </td>

                        <td
                            class="static-click"
                            onclick="abrirOC('${escapar(
                                x.ultimaOC
                            )}')"
                        >
                            ${escapar(
                                x.ultimaOC
                            )}
                        </td>

                        <td class="text-end">
                            ${formatoMoneda(
                                x.ultimoPrecio,
                                x.moneda
                            )}
                        </td>

                        <td class="text-end">
                            ${formatoMoneda(
                                x.minimo,
                                x.moneda
                            )}
                        </td>

                        <td class="text-end">
                            ${formatoMoneda(
                                x.maximo,
                                x.moneda
                            )}
                        </td>

                        <td class="text-end">
                            ${
                                x.variacion === null
                                    ? "Sin anterior"
                                    : (
                                        (
                                            x.variacion > 0
                                                ? "+"
                                                : ""
                                        ) +
                                        formatoNumero(
                                            x.variacion,
                                            1
                                        ) +
                                        "%"
                                    )
                            }
                        </td>
                    </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
        `;
    }


    // ========================================================
    // ÓRDENES
    // ========================================================

    function renderOrdenes() {
        const vista = document.getElementById("view-ordenes");

        const anios = unicos(
            ORDENES
                .map(x => texto(x.fecha).substring(0, 4))
                .filter(Boolean)
        ).sort().reverse();

        const ultimoAnio = anios[0] || "";
        const meses = [
            ["01", "Enero"], ["02", "Febrero"], ["03", "Marzo"], ["04", "Abril"],
            ["05", "Mayo"], ["06", "Junio"], ["07", "Julio"], ["08", "Agosto"],
            ["09", "Septiembre"], ["10", "Octubre"], ["11", "Noviembre"], ["12", "Diciembre"]
        ];

        vista.innerHTML = `
        <div class="container-fluid px-0">
            <div class="page-title">
                <div>
                    <span class="page-badge">CONSULTA DE DOCUMENTOS</span>
                    <h2>Órdenes de Compra</h2>
                    <p>Busca una OC o revisa las órdenes emitidas por año y mes.</p>
                </div>
                <div class="data-status"><span></span>Datos disponibles</div>
            </div>

            <div class="filter-panel">
                <div class="row g-3 align-items-end">
                    <div class="col-xl-5">
                        <label class="form-label">Buscar orden de compra</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-search"></i></span>
                            <input
                                id="oc-q"
                                class="form-control"
                                placeholder="Ejemplo: RM-HCN-2482, HCN-2482..."
                            >
                        </div>
                    </div>

                    <div class="col-xl-2 col-md-4">
                        <label class="form-label">Año</label>
                        <select id="oc-anio" class="form-select">
                            <option value="">Todos los años</option>
                            ${anios.map(x => `<option value="${x}" ${x === ultimoAnio ? "selected" : ""}>${x}</option>`).join("")}
                        </select>
                    </div>

                    <div class="col-xl-2 col-md-4">
                        <label class="form-label">Mes</label>
                        <select id="oc-mes" class="form-select">
                            <option value="">Todos los meses</option>
                            ${meses.map(([v, n]) => `<option value="${v}">${n}</option>`).join("")}
                        </select>
                    </div>

                    <div class="col-xl-2 col-md-4">
                        <label class="form-label">Mostrar</label>
                        <select id="oc-limite" class="form-select">
                            <option value="10" selected>10 OC</option>
                            <option value="25">25 OC</option>
                            <option value="0">Todas</option>
                        </select>
                    </div>

                    <div class="col-xl-1">
                        <button id="oc-buscar" class="btn btn-primary w-100">Buscar</button>
                    </div>
                </div>

                <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mt-3 pt-3 border-top">
                    <small class="text-muted">
                        Puedes combinar el buscador con los filtros de año y mes.
                    </small>
                    <button id="oc-limpiar" class="btn btn-outline-secondary btn-sm">
                        <i class="bi bi-arrow-counterclockwise me-1"></i>Limpiar filtros
                    </button>
                </div>
            </div>

            <div id="oc-resultado"></div>
        </div>`;

        document.getElementById("oc-buscar").addEventListener("click", listarOrdenes);
        document.getElementById("oc-q").addEventListener("keydown", e => {
            if (e.key === "Enter") listarOrdenes();
        });
        ["oc-anio", "oc-mes", "oc-limite"].forEach(id => {
            document.getElementById(id).addEventListener("change", listarOrdenes);
        });
        document.getElementById("oc-limpiar").addEventListener("click", () => {
            document.getElementById("oc-q").value = "";
            document.getElementById("oc-anio").value = ultimoAnio;
            document.getElementById("oc-mes").value = "";
            document.getElementById("oc-limite").value = "10";
            listarOrdenes();
        });

        listarOrdenes();
    }


    function listarOrdenes() {
        const q = texto(document.getElementById("oc-q")?.value).trim().toLowerCase();
        const anio = texto(document.getElementById("oc-anio")?.value);
        const mes = texto(document.getElementById("oc-mes")?.value);
        const limite = Number(document.getElementById("oc-limite")?.value || 10);
        const contenedor = document.getElementById("oc-resultado");

        let resultados = ORDENES.filter(o => {
            const fecha = texto(o.fecha);
            if (anio && fecha.substring(0, 4) !== anio) return false;
            if (mes && fecha.substring(5, 7) !== mes) return false;

            if (q) {
                const combinado = [
                    o.numero_oc,
                    o.proveedor,
                    o.hospital,
                    o.rut_proveedor
                ].map(texto).join(" ").toLowerCase();

                if (!combinado.includes(q)) return false;
            }

            return true;
        });

        resultados.sort((a, b) =>
            fechaValor(b.fecha) - fechaValor(a.fecha) ||
            texto(b.numero_oc).localeCompare(texto(a.numero_oc), "es")
        );

        const totalEncontradas = resultados.length;
        const visibles = limite > 0 ? resultados.slice(0, limite) : resultados;

        const periodo = anio
            ? (mes ? `${nombreMes(mes)} ${anio}` : anio)
            : (mes ? nombreMes(mes) : "todo el historial");

        if (!resultados.length) {
            contenedor.innerHTML = `
            <div class="static-empty">
                <i class="bi bi-file-earmark-x"></i><br>
                <strong>No se encontraron órdenes de compra.</strong><br>
                Cambia el número de OC, año o mes seleccionado.
            </div>`;
            return;
        }

        contenedor.innerHTML = `
        <div class="card content-card">
            <div class="card-body">
                <div class="results-header">
                    <div>
                        <strong>Órdenes encontradas</strong>
                        <span>${totalEncontradas}</span>
                    </div>
                    <small class="text-muted">
                        ${limite > 0
                            ? `Mostrando ${visibles.length} de ${totalEncontradas} · ${escapar(periodo)}`
                            : `Mostrando todas · ${escapar(periodo)}`}
                    </small>
                </div>

                <div class="table-responsive">
                    <table class="table purchase-table">
                        <thead>
                            <tr>
                                <th>OC</th>
                                <th>Fecha</th>
                                <th>Hospital</th>
                                <th>Proveedor</th>
                                <th>Moneda</th>
                                <th class="text-end">Total</th>
                                <th class="text-center">Detalle</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${visibles.map(o => `
                            <tr>
                                <td>
                                    <button
                                        class="btn btn-link table-link p-0 text-start"
                                        onclick="abrirOC('${escapar(o.numero_oc)}')"
                                    >
                                        ${escapar(o.numero_oc)}
                                    </button>
                                </td>
                                <td>${fechaTexto(o.fecha)}</td>
                                <td>${escapar(o.hospital || "-")}</td>
                                <td>${escapar(o.proveedor || "-")}</td>
                                <td><span class="currency-badge">${escapar(o.moneda || "-")}</span></td>
                                <td class="text-end"><strong>${formatoMoneda(o.total, o.moneda)}</strong></td>
                                <td class="text-center">
                                    <button
                                        class="table-action"
                                        title="Ver detalle de la OC"
                                        onclick="abrirOC('${escapar(o.numero_oc)}')"
                                    >
                                        <i class="bi bi-eye"></i>
                                    </button>
                                </td>
                            </tr>`).join("")}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>`;
    }


    function abrirOC(numeroOC) {
        const vistaActiva = document.getElementById("view-ordenes")?.classList.contains("active");
        if (!vistaActiva) irA("ordenes");

        const input = document.getElementById("oc-q");
        if (input) input.value = numeroOC;

        mostrarDetalleOC(numeroOC);
    }


    // Mantiene compatibilidad con el buscador universal del Inicio.
    function buscarOC() {
        const q = texto(document.getElementById("oc-q")?.value).trim();
        if (!q) {
            listarOrdenes();
            return;
        }

        const exacta = ORDENES.find(
            x => texto(x.numero_oc).toLowerCase() === q.toLowerCase()
        );

        if (exacta) {
            mostrarDetalleOC(exacta.numero_oc);
            return;
        }

        listarOrdenes();
    }


    function mostrarDetalleOC(numeroOC) {
        const contenedor = document.getElementById("oc-resultado");
        const oc = ORDENES.find(
            x => texto(x.numero_oc) === texto(numeroOC)
        );

        if (!oc) {
            contenedor.innerHTML = `
            <div class="static-empty">
                No se encontró la OC.
            </div>`;
            return;
        }

        const articulos = DETALLE.filter(
            x => texto(x.numero_oc) === texto(oc.numero_oc)
        );

        contenedor.innerHTML = `
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
            <button class="btn btn-outline-secondary" onclick="listarOrdenes()">
                <i class="bi bi-arrow-left me-1"></i>Volver al listado
            </button>
            <span class="dashboard-period-label">
                <i class="bi bi-file-earmark-text"></i>${escapar(oc.numero_oc)}
            </span>
        </div>

        <div class="row g-4">
            ${kpi("Orden de Compra", oc.numero_oc, oc.hospital)}
            ${kpi("Fecha", fechaTexto(oc.fecha), "fecha de emisión")}
            ${kpi("Moneda", oc.moneda, "moneda de la OC")}
            ${kpi("Total", formatoMoneda(oc.total, oc.moneda), "total documento")}
        </div>

        <div class="row g-4 mt-1">
            <div class="col-xl-6">
                <div class="card content-card h-100">
                    <div class="card-body">
                        <div class="card-title-area"><div><h3>Proveedor</h3></div></div>
                        ${detalleDato("Proveedor", oc.proveedor)}
                        ${detalleDato("RUT", oc.rut_proveedor)}
                        ${detalleDato("Dirección", oc.direccion_proveedor)}
                        ${detalleDato("Ciudad", oc.ciudad)}
                        ${detalleDato("Vendedor", oc.vendedor)}
                        ${detalleDato("Teléfono", oc.telefono)}
                        ${detalleDato("Email", oc.email)}
                        ${detalleDato("Forma de pago", oc.forma_pago)}
                    </div>
                </div>
            </div>

            <div class="col-xl-6">
                <div class="card content-card h-100">
                    <div class="card-body">
                        <div class="card-title-area"><div><h3>Información Interna</h3></div></div>
                        ${detalleDato("Solicitante", oc.solicitante_oc)}
                        ${detalleDato("Primer aprobador", oc.primer_aprobador)}
                        ${detalleDato("Solicitud", oc.solicitud)}
                        ${detalleDato("Estado", oc.estado_proceso)}
                        ${detalleDato("Subtotal", formatoMoneda(oc.subtotal, oc.moneda))}
                        ${detalleDato("IVA", formatoMoneda(oc.iva, oc.moneda))}
                    </div>
                </div>
            </div>
        </div>

        ${texto(oc.nota_interna).trim() ? `
        <div class="card content-card mt-4">
            <div class="card-body">
                <div class="card-title-area"><div><h3>Nota Interna</h3></div></div>
                <p>${escapar(oc.nota_interna)}</p>
            </div>
        </div>` : ""}

        <div class="card content-card mt-4">
            <div class="card-body">
                <div class="card-title-area">
                    <div>
                        <h3>Detalle de artículos</h3>
                        <p>${articulos.length} líneas.</p>
                    </div>
                </div>

                <div class="table-responsive">
                    <table class="table purchase-table">
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Código</th>
                                <th>Descripción</th>
                                <th>Unidad</th>
                                <th>Cantidad</th>
                                <th class="text-end">Precio Unit.</th>
                                <th class="text-end">Total Línea</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${articulos.map(x => `
                            <tr>
                                <td>${escapar(x.numero_item)}</td>
                                <td>${escapar(x.codigo)}</td>
                                <td>${escapar(x.descripcion)}</td>
                                <td>${escapar(x.unidad_medida)}</td>
                                <td>${formatoNumero(x.cantidad, 2)}</td>
                                <td class="text-end">${formatoMoneda(x.precio_unitario, x.moneda)}</td>
                                <td class="text-end"><strong>${formatoMoneda(x.total_linea, x.moneda)}</strong></td>
                            </tr>`).join("")}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>`;
    }


    function detalleDato(etiqueta, valor) {
        return `
        <div class="detail-list">
            <div>
                <span>
                    ${escapar(
                        etiqueta
                    )}
                </span>

                <strong>
                    ${escapar(
                        texto(valor) || "-"
                    )}
                </strong>
            </div>
        </div>
        `;
    }


    // ========================================================
    // INICIO DE LA APP ESTÁTICA
    // ========================================================

    document.addEventListener(
        "DOMContentLoaded",
        () => {
            document
                .querySelectorAll(
                    "[data-view]"
                )
                .forEach(el => {
                    el.addEventListener(
                        "click",
                        e => {
                            e.preventDefault();

                            irA(
                                el.dataset.view
                            );
                        }
                    );
                });

            irA("inicio");
        }
    );
    """

    # Corrige un typo deliberadamente evitado en la
    # construcción larga del JavaScript.
    javascript = javascript.replace(
        "grupo[group.length - 2]",
        "grupo[grupo.length - 2]",
    )

    javascript = javascript.replace(
        "__ORDENES__",
        ordenes_json,
    )

    javascript = javascript.replace(
        "__DETALLE__",
        detalle_json,
    )

    html_final = f"""<!doctype html>
<html lang="es">

<head>

<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>
    ComprasAnalytics · Dashboard Autónomo
</title>

<link
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
    rel="stylesheet"
>

<link
    href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css"
    rel="stylesheet"
>

<style>
{css_original}

{css_extra}
</style>

</head>

<body>

<div class="app-layout">

<aside class="sidebar">

    <div class="sidebar-brand">

        <div class="brand-icon">
            <i class="bi bi-bar-chart-fill"></i>
        </div>

        <div>
            <h1>ComprasAnalytics</h1>
            <p>GrupoPuentes</p>
        </div>

    </div>

    <nav class="nav flex-column sidebar-nav">

        <button
            class="nav-link static-nav-button"
            data-view="inicio"
        >
            <i class="bi bi-house-door"></i>
            <span>Inicio</span>
        </button>

        <button
            class="nav-link static-nav-button"
            data-view="dashboard"
        >
            <i class="bi bi-grid"></i>
            <span>Dashboard</span>
        </button>

        <button
            class="nav-link static-nav-button"
            data-view="productos"
        >
            <i class="bi bi-search"></i>
            <span>Buscar Producto</span>
        </button>

        <button
            class="nav-link static-nav-button"
            data-view="proveedores"
        >
            <i class="bi bi-buildings"></i>
            <span>Proveedores</span>
        </button>

        <button
            class="nav-link static-nav-button"
            data-view="precios"
        >
            <i class="bi bi-graph-up-arrow"></i>
            <span>Análisis de Precios</span>
        </button>

        <button
            class="nav-link static-nav-button"
            data-view="historial"
        >
            <i class="bi bi-clock-history"></i>
            <span>Historial y Control</span>
        </button>

        <button
            class="nav-link static-nav-button"
            data-view="ordenes"
        >
            <i class="bi bi-file-earmark-text"></i>
            <span>Órdenes de Compra</span>
        </button>

    </nav>

    <div class="sidebar-footer">
        <strong>
            Sistema de Compras
        </strong>

        <span>
            Constitución · Parral · Cauquenes
        </span>

        <span>
            HTML autónomo
        </span>
    </div>

</aside>


<main class="main-content">

    <section
        id="view-inicio"
        class="static-view"
    ></section>

    <section
        id="view-dashboard"
        class="static-view"
    ></section>

    <section
        id="view-productos"
        class="static-view"
    ></section>

    <section
        id="view-proveedores"
        class="static-view"
    ></section>

    <section
        id="view-precios"
        class="static-view"
    ></section>

    <section
        id="view-historial"
        class="static-view"
    ></section>

    <section
        id="view-ordenes"
        class="static-view"
    ></section>

</main>

</div>

<script
    src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js">
</script>

<script>
{javascript}
</script>

</body>
</html>
"""

    return html_final


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("     GENERADOR DE DASHBOARD HTML AUTÓNOMO")
    print("=" * 70)

    ordenes, detalle = cargar_datos()

    html = generar_html(
        ordenes,
        detalle,
    )

    ARCHIVO_SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ARCHIVO_SALIDA.write_text(
        html,
        encoding="utf-8",
    )

    print()
    print(f"Excel leído:      {ARCHIVO_EXCEL}")
    print(f"Órdenes:          {len(ordenes)}")
    print(f"Artículos:        {len(detalle)}")
    print(f"Dashboard:        {ARCHIVO_SALIDA}")
    print()
    print("HTML generado correctamente.")
    print("=" * 70)


if __name__ == "__main__":
    main()