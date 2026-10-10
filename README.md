# ComprasAnalytics v1.1

Aplicación local en Python + Flask para extraer, consolidar y analizar órdenes de compra de iConstruye.

## Módulos

- **Centro de Control:** OC, proveedores, movimientos, productos con proveedor único, referencias históricas y últimas OC.
- **Dashboard General:** indicadores, evolución, hospitales y ranking ampliable de proveedores por monto.
- **Buscar Producto:** búsqueda rápida con último precio, mínimo histórico, último proveedor y acceso al análisis detallado.
- **Proveedores:** Top 25 visible al entrar, catálogo completo, búsqueda y ficha histórica detallada.
- **Análisis de Precios:** filtros, estadísticas por moneda, evolución y mínimo/máximo histórico por producto.
- **Historial y Control:** productos con proveedor único, último precio, mínimo, máximo, variación contra el antecedente anterior y filtros de búsqueda.
- **Órdenes de Compra:** búsqueda y consulta del detalle de una OC.

## Enfoque de análisis

La aplicación muestra referencias históricas objetivas. No intenta convertir diferencias de precio en alertas automáticas de ahorro, porque una misma descripción puede corresponder a compras con cantidades, presentaciones o alcances distintos.

Los campos de precio se comparan dentro de la misma descripción, unidad de medida y moneda. La variación porcentual del módulo Historial y Control es informativa y compara el último precio con el antecedente inmediatamente anterior.

## Regla monetaria

CLP, USD, EUR y UF nunca se suman ni promedian entre sí.

## Requisitos

Python 3.14 recomendado. Instalar dependencias:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecutar dashboard

```powershell
python dashboard\dashboard.py
```

Abrir `http://127.0.0.1:5000`.

## Datos

El dashboard lee `data/output/ordenes_compra.xlsx`, hojas `ORDENES` y `DETALLE_OC`. Mantiene una caché en memoria y recarga automáticamente cuando cambia la fecha de modificación del Excel.

## Analizador PDF

El código de extracción permanece en `src/`. El rediseño del dashboard no modifica el proceso de lectura de PDF ni el formato del Excel generado.
