# ComprasAnalytics

ComprasAnalytics es una aplicación local desarrollada en Python para extraer, consolidar y analizar órdenes de compra de iConstruye.

El proyecto tiene dos componentes principales:

1. **Analizador PDF**, que procesa las órdenes de compra y genera un Excel consolidado.
2. **Dashboard de análisis**, que utiliza ese Excel para consultar órdenes, proveedores, productos, precios históricos y comportamiento de las compras.

El dashboard puede utilizarse de dos formas:

- **Dashboard Flask**, ejecutado localmente con Python.
- **Dashboard HTML autónomo**, generado como archivo independiente para abrirlo directamente en el navegador sin iniciar Flask.

---

## Funcionalidades principales

### Inicio / Centro de Control

Vista inicial de consulta rápida.

Muestra:

- total de órdenes de compra;
- total de proveedores;
- productos y conceptos únicos;
- compras registradas;
- buscador general por producto, proveedor o número de OC;
- accesos rápidos a los principales módulos;
- actividad reciente.

### Dashboard de Compras

Vista ejecutiva para analizar las compras según:

- hospital;
- moneda;
- año;
- mes;
- ranking de proveedores.

Incluye:

- total comprado;
- cantidad de órdenes de compra;
- proveedores activos;
- ticket promedio por OC;
- comparación con el período anterior;
- evolución mensual o diaria;
- ranking de proveedores por monto;
- distribución por hospital;
- principales compras del período;
- Top 10 o Top 25 de productos y conceptos por monto acumulado.

### Buscar Producto

Permite buscar productos o conceptos y revisar:

- descripción;
- unidad de medida;
- moneda;
- último proveedor;
- último precio;
- mínimo histórico;
- máximo histórico;
- órdenes de compra asociadas;
- evolución histórica.

### Proveedores

Permite consultar la actividad histórica de los proveedores.

Incluye:

- búsqueda por nombre, RUT o producto;
- Top 10;
- Top 25;
- catálogo completo;
- cantidad de OC;
- productos asociados;
- última compra;
- ficha histórica detallada.

### Análisis de Precios

Permite consultar movimientos históricos usando filtros por:

- producto;
- proveedor;
- moneda;
- hospital.

Además permite:

- buscar dentro de los resultados;
- mostrar Top 10, Top 25 o todos;
- ordenar por fecha;
- ordenar por precio mayor o menor;
- revisar fecha, OC, producto, unidad, proveedor, hospital, cantidad, moneda, precio, mínimo y máximo.

### Historial y Control

Permite revisar antecedentes históricos de productos y proveedores.

Incluye:

- productos asociados a proveedor único;
- último precio;
- mínimo histórico;
- máximo histórico;
- variación respecto del antecedente inmediatamente anterior;
- filtros de búsqueda.

La variación porcentual es informativa y no representa automáticamente una alerta de ahorro o sobreprecio.

### Órdenes de Compra

Permite buscar una OC y consultar su información completa, incluyendo cabecera, proveedor, condiciones comerciales, totales y detalle de artículos o servicios.

---

## Enfoque de análisis

ComprasAnalytics muestra referencias históricas objetivas obtenidas desde las órdenes de compra procesadas.

El sistema no interpreta automáticamente una diferencia de precio como ahorro, sobreprecio o alerta, porque una misma descripción puede corresponder a compras con distintas cantidades, unidades, presentaciones, condiciones comerciales, alcances o fechas.

Los precios se comparan dentro de la misma descripción, unidad de medida y moneda.

### Regla monetaria

Las monedas se analizan de forma independiente.

**CLP, USD, EUR y UF nunca se suman ni se promedian entre sí.**

---

## Requisitos

Se recomienda utilizar Python 3.14.

Comprobar la versión instalada:

```powershell
python --version
```

---

## Instalación

### 1. Clonar el repositorio

```powershell
git clone https://github.com/Isco-Lina/analizador-ordenes-compra.git
```

Entrar a la carpeta:

```powershell
cd analizador-ordenes-compra
```

### 2. Crear entorno virtual

```powershell
python -m venv .venv
```

### 3. Activar entorno virtual

Si PowerShell bloquea la ejecución de scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Luego activar:

```powershell
.venv\Scripts\Activate.ps1
```

La consola debería mostrar algo similar a:

```text
(.venv) PS C:\...\analizador-ordenes-compra>
```

### 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

---

## Crear estructura de datos

Los PDF y archivos generados no se almacenan en GitHub.

Crear:

```text
data/
├── pdf/
└── output/
```

Desde PowerShell:

```powershell
mkdir data
mkdir data\pdf
mkdir data\output
```

Uso:

```text
data/pdf/
```

Contiene las órdenes de compra PDF a procesar.

```text
data/output/
```

Contiene los archivos generados por el proyecto.

La estructura debería quedar aproximadamente así:

```text
analizador-ordenes-compra/
├── dashboard/
│   ├── static/
│   ├── templates/
│   └── dashboard.py
├── data/
│   ├── pdf/
│   └── output/
├── src/
├── tests/
├── generar_dashboard_html.py
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Procesar órdenes de compra PDF

Copiar los PDF a:

```text
data/pdf/
```

Luego ejecutar:

```powershell
python app.py
```

El sistema generará:

```text
data/output/ordenes_compra.xlsx
```

El Excel contiene principalmente:

```text
ORDENES
DETALLE_OC
```

- **ORDENES:** una fila por orden de compra.
- **DETALLE_OC:** detalle de productos o servicios de cada OC.

---

## Ejecutar Dashboard Flask

Una vez generado:

```text
data/output/ordenes_compra.xlsx
```

ejecutar:

```powershell
python dashboard\dashboard.py
```

Abrir en el navegador:

```text
http://127.0.0.1:5000
```

Mientras se use esta modalidad, la consola debe permanecer abierta.

Para detener Flask:

```text
Ctrl + C
```

---

# Generar y abrir el Dashboard HTML

Esta es la modalidad más simple para consultar el dashboard sin iniciar Flask cada vez.

El generador utiliza:

```text
data/output/ordenes_compra.xlsx
```

y crea:

```text
data/output/dashboard.html
```

## 1. Generar el HTML

Desde la carpeta principal del proyecto ejecutar:

```powershell
python generar_dashboard_html.py
```

Al terminar aparecerá un mensaje similar a:

```text
Excel leído:      ...\data\output\ordenes_compra.xlsx
Órdenes:          ...
Artículos:        ...
Dashboard:        ...\data\output\dashboard.html

HTML generado correctamente.
```

## 2. Abrir el Dashboard HTML

Ir a:

```text
data/output/
```

y abrir:

```text
dashboard.html
```

Se puede abrir de cualquiera de estas formas:

- doble clic sobre `dashboard.html`;
- clic derecho → **Abrir con** → Chrome o Edge;
- arrastrar el archivo al navegador.

También se puede abrir directamente desde PowerShell:

```powershell
start data\output\dashboard.html
```

## 3. Actualizar el HTML cuando existan nuevas OC

El HTML contiene los datos disponibles **al momento en que fue generado**.

Si se agregan nuevos PDF y se vuelve a ejecutar:

```powershell
python app.py
```

también se debe volver a ejecutar:

```powershell
python generar_dashboard_html.py
```

para actualizar:

```text
data/output/dashboard.html
```

Después solo hay que volver a abrir el archivo o actualizar la pestaña del navegador.

### Importante

El Dashboard HTML **no necesita Flask ejecutándose**.

Sin embargo, utiliza Bootstrap, Bootstrap Icons y Chart.js desde CDN, por lo que se recomienda conexión a Internet para cargar correctamente estilos, iconos y gráficos.

---

## Flujo completo recomendado

### Primera instalación

```powershell
git clone https://github.com/Isco-Lina/analizador-ordenes-compra.git

cd analizador-ordenes-compra

python -m venv .venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.venv\Scripts\Activate.ps1

pip install -r requirements.txt

mkdir data
mkdir data\pdf
mkdir data\output
```

Luego:

1. copiar los PDF a `data/pdf/`;
2. ejecutar `python app.py`;
3. elegir Dashboard Flask o Dashboard HTML.

### Opción A: Flask

```powershell
python dashboard\dashboard.py
```

Abrir:

```text
http://127.0.0.1:5000
```

### Opción B: HTML

```powershell
python generar_dashboard_html.py
```

Abrir:

```powershell
start data\output\dashboard.html
```

---

## Flujo habitual después de agregar nuevas OC

```text
PDF
 ↓
python app.py
 ↓
ordenes_compra.xlsx
 ↓
python generar_dashboard_html.py
 ↓
dashboard.html
```

En comandos:

```powershell
python app.py
python generar_dashboard_html.py
start data\output\dashboard.html
```

---

## Datos utilizados por el dashboard

Fuente principal:

```text
data/output/ordenes_compra.xlsx
```

Hojas utilizadas:

```text
ORDENES
DETALLE_OC
```

El Dashboard Flask trabaja sobre el Excel generado y puede recargar información cuando cambia el archivo.

El Dashboard HTML incorpora los datos existentes al momento de ejecutar:

```powershell
python generar_dashboard_html.py
```

Por eso debe regenerarse después de actualizar el Excel.

---

## Analizador PDF

El código encargado de leer e interpretar las órdenes de compra se encuentra principalmente en:

```text
src/
```

El dashboard funciona como una capa de consulta y análisis sobre la información consolidada en Excel.

Las mejoras visuales y analíticas del dashboard no modifican el proceso original de extracción de PDF.

---

## Archivos locales no incluidos en GitHub

Por seguridad y para evitar subir archivos pesados o información de trabajo, normalmente no se incluyen:

- `.venv/`;
- órdenes de compra PDF;
- `ordenes_compra.xlsx`;
- `dashboard.html`;
- archivos generados en `data/output/`;
- archivos temporales de Python;
- caché de Python.

Después de clonar el proyecto se deben crear:

```text
data/pdf/
data/output/
```

---

## Tecnologías

- Python
- Flask
- Pandas
- OpenPyXL
- PyMuPDF
- PDFPlumber
- JavaScript
- HTML
- CSS
- Bootstrap
- Bootstrap Icons
- Chart.js

---

## Resumen rápido

### Procesar órdenes de compra

```powershell
python app.py
```

### Ejecutar Dashboard Flask

```powershell
python dashboard\dashboard.py
```

### Generar Dashboard HTML

```powershell
python generar_dashboard_html.py
```

### Abrir Dashboard HTML

```powershell
start data\output\dashboard.html
```

---

**ComprasAnalytics**  
Herramienta local de apoyo para consulta, trazabilidad y análisis histórico de órdenes de compra.
