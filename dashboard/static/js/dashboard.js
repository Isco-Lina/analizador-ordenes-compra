document.addEventListener("DOMContentLoaded", function () {

    console.log("ComprasAnalytics iniciado correctamente.");


    // ========================================================
    // CONFIGURACIÓN GLOBAL DE CHART.JS
    // ========================================================

    if (typeof Chart !== "undefined") {

        Chart.defaults.font.family =
            "'Segoe UI', Arial, sans-serif";

        Chart.defaults.color =
            "#64748b";

        Chart.defaults.borderColor =
            "#e5e7eb";

    }


    // ========================================================
    // LEER JSON DESDE HTML
    // ========================================================

    function leerJson(id) {

        const elemento =
            document.getElementById(id);


        if (!elemento) {
            return null;
        }


        try {

            return JSON.parse(
                elemento.textContent
            );

        } catch (error) {

            console.error(
                "Error leyendo " + id,
                error
            );

            return null;

        }

    }


    // ========================================================
    // DASHBOARD GENERAL
    // ========================================================

    const datos =
        leerJson("dashboard-data");


    if (datos && typeof Chart !== "undefined") {

        const simbolo =
            datos.simbolo || "";


        function formatearMonto(valor) {

            const numero =
                Number(valor);


            if (!Number.isFinite(numero)) {
                return "-";
            }


            if (datos.moneda === "CLP") {

                return (
                    "$ " +
                    new Intl.NumberFormat(
                        "es-CL",
                        {
                            maximumFractionDigits: 0
                        }
                    ).format(numero)
                );

            }


            if (datos.moneda === "UF") {

                return (
                    "UF " +
                    new Intl.NumberFormat(
                        "es-CL",
                        {
                            minimumFractionDigits: 4,
                            maximumFractionDigits: 4
                        }
                    ).format(numero)
                );

            }


            if (datos.moneda === "USD") {

                return (
                    "US$ " +
                    new Intl.NumberFormat(
                        "es-CL",
                        {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                        }
                    ).format(numero)
                );

            }


            if (datos.moneda === "EUR") {

                return (
                    "EUR " +
                    new Intl.NumberFormat(
                        "es-CL",
                        {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                        }
                    ).format(numero)
                );

            }


            return (
                simbolo +
                " " +
                numero
            );

        }


        function formatoCompacto(valor) {

            const numero =
                Number(valor);


            if (!Number.isFinite(numero)) {
                return "";
            }


            let prefijo =
                simbolo;


            if (datos.moneda === "USD") {
                prefijo = "US$";
            }

            if (datos.moneda === "EUR") {
                prefijo = "EUR";
            }

            if (datos.moneda === "UF") {
                prefijo = "UF";
            }


            if (
                Math.abs(numero) >=
                1000000000
            ) {

                return (
                    prefijo +
                    " " +
                    (
                        numero /
                        1000000000
                    ).toFixed(1) +
                    "B"
                );

            }


            if (
                Math.abs(numero) >=
                1000000
            ) {

                return (
                    prefijo +
                    " " +
                    (
                        numero /
                        1000000
                    ).toFixed(1) +
                    "M"
                );

            }


            if (
                Math.abs(numero) >=
                1000
            ) {

                return (
                    prefijo +
                    " " +
                    (
                        numero /
                        1000
                    ).toFixed(0) +
                    "K"
                );

            }


            return (
                prefijo +
                " " +
                numero
            );

        }


        function opcionesGraficoMoneda() {

            return {

                responsive: true,

                maintainAspectRatio: false,

                interaction: {
                    intersect: false,
                    mode: "index"
                },

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {

                        backgroundColor:
                            "#111827",

                        padding: 12,

                        titleColor:
                            "#ffffff",

                        bodyColor:
                            "#e5e7eb",

                        displayColors:
                            false,

                        callbacks: {

                            label:
                                function (
                                    context
                                ) {

                                    return formatearMonto(
                                        context.raw
                                    );

                                }

                        }

                    }

                },

                scales: {

                    x: {

                        grid: {
                            display: false
                        }

                    },

                    y: {

                        beginAtZero: true,

                        grid: {
                            color: "#eef2f7"
                        },

                        ticks: {

                            callback:
                                function (
                                    value
                                ) {

                                    return formatoCompacto(
                                        value
                                    );

                                }

                        }

                    }

                }

            };

        }


        // ----------------------------------------------------
        // EVOLUCIÓN
        // ----------------------------------------------------

        const canvasEvolucion =
            document.getElementById(
                "graficoEvolucion"
            );


        if (
            canvasEvolucion &&
            datos.evolucion &&
            datos.evolucion.labels.length
        ) {

            new Chart(
                canvasEvolucion,
                {

                    type: "line",

                    data: {

                        labels:
                            datos.evolucion.labels,

                        datasets: [
                            {
                                label:
                                    "Monto comprado",

                                data:
                                    datos.evolucion.values,

                                borderColor:
                                    "#4f46e5",

                                backgroundColor:
                                    "rgba(79, 70, 229, 0.08)",

                                borderWidth: 2.5,

                                pointRadius: 3,

                                pointHoverRadius: 5,

                                pointBackgroundColor:
                                    "#4f46e5",

                                fill: true,

                                tension: 0.3
                            }
                        ]

                    },

                    options:
                        opcionesGraficoMoneda()

                }
            );

        }


        // ----------------------------------------------------
        // HOSPITALES
        // ----------------------------------------------------

        const canvasHospitales =
            document.getElementById(
                "graficoHospitales"
            );


        if (
            canvasHospitales &&
            datos.hospitales &&
            datos.hospitales.labels.length
        ) {

            new Chart(
                canvasHospitales,
                {

                    type: "doughnut",

                    data: {

                        labels:
                            datos.hospitales.labels,

                        datasets: [
                            {
                                data:
                                    datos
                                        .hospitales
                                        .values,

                                backgroundColor: [
                                    "#4f46e5",
                                    "#10b981",
                                    "#0f172a",
                                    "#f59e0b"
                                ],

                                borderWidth: 0,

                                hoverOffset: 5
                            }
                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        cutout: "70%",

                        plugins: {

                            legend: {

                                position:
                                    "bottom",

                                labels: {

                                    usePointStyle:
                                        true,

                                    pointStyle:
                                        "circle",

                                    padding: 18,

                                    boxWidth: 8

                                }

                            },

                            tooltip: {

                                backgroundColor:
                                    "#111827",

                                padding: 12,

                                displayColors:
                                    false,

                                callbacks: {

                                    label:
                                        function (
                                            context
                                        ) {

                                            return (
                                                context.label +
                                                ": " +
                                                formatearMonto(
                                                    context.raw
                                                )
                                            );

                                        }

                                }

                            }

                        }

                    }

                }
            );

        }


        // ----------------------------------------------------
        // PROVEEDORES
        // ----------------------------------------------------

        const canvasProveedores =
            document.getElementById(
                "graficoProveedores"
            );


        if (
            canvasProveedores &&
            datos.proveedores &&
            datos.proveedores.labels.length
        ) {

            new Chart(
                canvasProveedores,
                {

                    type: "bar",

                    data: {

                        labels:
                            datos
                                .proveedores
                                .labels,

                        datasets: [
                            {
                                label:
                                    "Monto comprado",

                                data:
                                    datos
                                        .proveedores
                                        .values,

                                backgroundColor:
                                    "#4f46e5",

                                borderRadius: 5,

                                borderSkipped:
                                    false,

                                barThickness: 18
                            }
                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        indexAxis: "y",

                        plugins: {

                            legend: {
                                display: false
                            },

                            tooltip: {

                                backgroundColor:
                                    "#111827",

                                padding: 12,

                                displayColors:
                                    false,

                                callbacks: {

                                    label:
                                        function (
                                            context
                                        ) {

                                            const monto = formatearMonto(
                                                context.raw
                                            );

                                            const ordenes =
                                                datos.proveedores.orders &&
                                                datos.proveedores.orders[context.dataIndex] !== undefined
                                                    ? datos.proveedores.orders[context.dataIndex]
                                                    : null;

                                            return ordenes === null
                                                ? monto
                                                : monto + " · " + ordenes + " OC";

                                        }

                                }

                            }

                        },

                        scales: {

                            x: {

                                beginAtZero:
                                    true,

                                grid: {
                                    color:
                                        "#eef2f7"
                                },

                                ticks: {

                                    callback:
                                        function (
                                            value
                                        ) {

                                            return formatoCompacto(
                                                value
                                            );

                                        }

                                }

                            },

                            y: {

                                grid: {
                                    display:
                                        false
                                },

                                ticks: {

                                    color:
                                        "#475569",

                                    font: {
                                        size: 11
                                    }

                                }

                            }

                        }

                    }

                }
            );

        }


        // ----------------------------------------------------
        // PRODUCTOS
        // ----------------------------------------------------

        const canvasProductos =
            document.getElementById(
                "graficoProductos"
            );


        if (
            canvasProductos &&
            datos.productos &&
            datos.productos.labels.length
        ) {

            const etiquetasCortas =
                datos.productos.labels.map(
                    function (texto) {

                        if (
                            texto.length > 45
                        ) {

                            return (
                                texto.substring(
                                    0,
                                    45
                                ) +
                                "..."
                            );

                        }

                        return texto;

                    }
                );


            new Chart(
                canvasProductos,
                {

                    type: "bar",

                    data: {

                        labels:
                            etiquetasCortas,

                        datasets: [
                            {
                                label:
                                    "Monto comprado",

                                data:
                                    datos
                                        .productos
                                        .values,

                                backgroundColor:
                                    "#111827",

                                borderRadius: 5,

                                borderSkipped:
                                    false,

                                barThickness: 18
                            }
                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        indexAxis: "y",

                        plugins: {

                            legend: {
                                display: false
                            },

                            tooltip: {

                                backgroundColor:
                                    "#111827",

                                padding: 12,

                                displayColors:
                                    false,

                                callbacks: {

                                    title:
                                        function (
                                            context
                                        ) {

                                            const indice =
                                                context[0]
                                                    .dataIndex;

                                            return (
                                                datos
                                                    .productos
                                                    .labels[
                                                        indice
                                                    ]
                                            );

                                        },

                                    label:
                                        function (
                                            context
                                        ) {

                                            return formatearMonto(
                                                context.raw
                                            );

                                        }

                                }

                            }

                        },

                        scales: {

                            x: {

                                beginAtZero:
                                    true,

                                grid: {
                                    color:
                                        "#eef2f7"
                                },

                                ticks: {

                                    callback:
                                        function (
                                            value
                                        ) {

                                            return formatoCompacto(
                                                value
                                            );

                                        }

                                }

                            },

                            y: {

                                grid: {
                                    display:
                                        false
                                },

                                ticks: {

                                    color:
                                        "#475569",

                                    font: {
                                        size: 11
                                    }

                                }

                            }

                        }

                    }

                }
            );

        }

    }


    // ========================================================
    // FICHA DE PROVEEDOR
    // ========================================================

    const proveedorDatos =
        leerJson("supplier-data");


    if (
        proveedorDatos &&
        typeof Chart !== "undefined"
    ) {


        // ----------------------------------------------------
        // ACTIVIDAD HISTÓRICA
        // ----------------------------------------------------

        const canvasActividad =
            document.getElementById(
                "graficoActividadProveedor"
            );


        if (
            canvasActividad &&
            proveedorDatos.actividad &&
            proveedorDatos
                .actividad
                .labels
                .length
        ) {

            new Chart(
                canvasActividad,
                {

                    type: "bar",

                    data: {

                        labels:
                            proveedorDatos
                                .actividad
                                .labels,

                        datasets: [
                            {
                                label:
                                    "Órdenes de compra",

                                data:
                                    proveedorDatos
                                        .actividad
                                        .values,

                                backgroundColor:
                                    "#4f46e5",

                                borderRadius: 6,

                                borderSkipped:
                                    false,

                                maxBarThickness:
                                    55
                            }
                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        plugins: {

                            legend: {
                                display: false
                            },

                            tooltip: {

                                backgroundColor:
                                    "#111827",

                                padding: 12,

                                displayColors:
                                    false,

                                callbacks: {

                                    label:
                                        function (
                                            context
                                        ) {

                                            return (
                                                context.raw +
                                                " OC"
                                            );

                                        }

                                }

                            }

                        },

                        scales: {

                            x: {

                                grid: {
                                    display:
                                        false
                                }

                            },

                            y: {

                                beginAtZero:
                                    true,

                                grid: {
                                    color:
                                        "#eef2f7"
                                },

                                ticks: {

                                    precision: 0

                                }

                            }

                        }

                    }

                }
            );

        }


        // ----------------------------------------------------
        // HOSPITALES
        // ----------------------------------------------------

        const canvasHospitalProveedor =
            document.getElementById(
                "graficoHospitalProveedor"
            );


        if (
            canvasHospitalProveedor &&
            proveedorDatos.hospitales &&
            proveedorDatos
                .hospitales
                .labels
                .length
        ) {

            new Chart(
                canvasHospitalProveedor,
                {

                    type: "doughnut",

                    data: {

                        labels:
                            proveedorDatos
                                .hospitales
                                .labels,

                        datasets: [
                            {
                                data:
                                    proveedorDatos
                                        .hospitales
                                        .values,

                                backgroundColor: [
                                    "#4f46e5",
                                    "#10b981",
                                    "#0f172a",
                                    "#f59e0b"
                                ],

                                borderWidth: 0,

                                hoverOffset: 5
                            }
                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        cutout: "68%",

                        plugins: {

                            legend: {

                                position:
                                    "bottom",

                                labels: {

                                    usePointStyle:
                                        true,

                                    pointStyle:
                                        "circle",

                                    padding: 18,

                                    boxWidth: 8

                                }

                            },

                            tooltip: {

                                backgroundColor:
                                    "#111827",

                                padding: 12,

                                displayColors:
                                    false,

                                callbacks: {

                                    label:
                                        function (
                                            context
                                        ) {

                                            return (
                                                context.label +
                                                ": " +
                                                context.raw +
                                                " OC"
                                            );

                                        }

                                }

                            }

                        }

                    }

                }
            );

        }

    }


    // ========================================================
    // INTELIGENCIA DE PRODUCTOS
    // ========================================================

    const productoDatos = leerJson("product-data");

    if (productoDatos && typeof Chart !== "undefined") {
        const canvasPrecio = document.getElementById("graficoPrecioProducto");

        function formatoMonedaProducto(valor) {
            const numero = Number(valor);
            if (!Number.isFinite(numero)) return "-";
            const moneda = productoDatos.moneda;
            if (moneda === "CLP") return "$ " + new Intl.NumberFormat("es-CL", {maximumFractionDigits: 0}).format(numero);
            if (moneda === "UF") return "UF " + new Intl.NumberFormat("es-CL", {minimumFractionDigits: 4, maximumFractionDigits: 4}).format(numero);
            if (moneda === "USD") return "US$ " + new Intl.NumberFormat("es-CL", {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(numero);
            if (moneda === "EUR") return "EUR " + new Intl.NumberFormat("es-CL", {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(numero);
            return numero.toLocaleString("es-CL");
        }

        if (canvasPrecio && productoDatos.labels.length) {
            new Chart(canvasPrecio, {
                type: "line",
                data: {
                    labels: productoDatos.labels,
                    datasets: [{
                        label: "Precio unitario",
                        data: productoDatos.values,
                        borderColor: "#4f46e5",
                        backgroundColor: "rgba(79, 70, 229, 0.08)",
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: "#4f46e5",
                        fill: true,
                        tension: 0.2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {intersect: false, mode: "nearest"},
                    plugins: {
                        legend: {display: false},
                        tooltip: {
                            backgroundColor: "#111827",
                            padding: 12,
                            displayColors: false,
                            callbacks: {
                                title: function(context) {
                                    const i = context[0].dataIndex;
                                    return productoDatos.labels[i] + " · " + productoDatos.ordenes[i];
                                },
                                label: function(context) {
                                    const i = context.dataIndex;
                                    return productoDatos.proveedores[i] + ": " + formatoMonedaProducto(context.raw);
                                }
                            }
                        }
                    },
                    scales: {
                        x: {grid: {display: false}, ticks: {maxTicksLimit: 12}},
                        y: {beginAtZero: false, grid: {color: "#eef2f7"}, ticks: {callback: formatoMonedaProducto}}
                    }
                }
            });
        }
    }

    document.querySelectorAll(".estimated-cost").forEach(function(elemento) {
        const precio = Number(elemento.dataset.price);
        const cantidad = Number(elemento.dataset.quantity);
        const moneda = elemento.dataset.currency;
        const total = precio * cantidad;
        if (!Number.isFinite(total)) return;
        let texto;
        if (moneda === "CLP") texto = "$ " + new Intl.NumberFormat("es-CL", {maximumFractionDigits: 0}).format(total);
        else if (moneda === "UF") texto = "UF " + new Intl.NumberFormat("es-CL", {minimumFractionDigits: 4, maximumFractionDigits: 4}).format(total);
        else if (moneda === "USD") texto = "US$ " + new Intl.NumberFormat("es-CL", {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(total);
        else if (moneda === "EUR") texto = "EUR " + new Intl.NumberFormat("es-CL", {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(total);
        else texto = total.toLocaleString("es-CL");
        elemento.textContent = texto;
    });

});
// ============================================================
// V1.0 · EVOLUCIÓN DE PRECIOS
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
    const dataEl = document.getElementById("price-data");
    const canvas = document.getElementById("priceEvolutionChart");
    if (!dataEl || !canvas || typeof Chart === "undefined") return;
    try {
        const datos = JSON.parse(dataEl.textContent);
        new Chart(canvas, {
            type: "line",
            data: {labels: datos.labels, datasets: [{label: "Precio unitario · " + datos.moneda, data: datos.values, tension: 0.25, pointRadius: 2, borderWidth: 2}]},
            options: {responsive: true, maintainAspectRatio: false, plugins: {legend: {display: false}}, scales: {x: {grid: {display: false}}, y: {beginAtZero: false}}}
        });
    } catch (error) { console.error("Error cargando evolución de precios", error); }
});
