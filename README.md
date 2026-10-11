# ComprasAnalytics

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

La aplicación muestra referencias históricas objetivas.

No intenta convertir diferencias de precio en alertas automáticas de ahorro, porque una misma descripción puede corresponder a compras con cantidades, presentaciones o alcances distintos.

Los campos de precio se comparan dentro de la misma descripción, unidad de medida y moneda.

La variación porcentual del módulo **Historial y Control** es informativa y compara el último precio con el antecedente inmediatamente anterior.

## Regla monetaria

Las monedas se analizan de forma independiente.

**CLP, USD, EUR y UF nunca se suman ni promedian entre sí.**

---

## Requisitos

Se recomienda utilizar Python 3.14.

Para comprobar la versión instalada:

```powershell
python --version
```

---

## Instalación

### 1. Clonar el repositorio

```powershell
git clone https://github.com/Isco-Lina/analizador-ordenes-compra.git
```

Ingresar a la carpeta del proyecto:

```powershell
cd analizador-ordenes-compra
```

### 2. Crear entorno virtual

```powershell
python -m venv .venv
```

### 3. Activar el entorno virtual

Si PowerShell bloquea la ejecución de scripts, ejecutar primero:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Luego activar el entorno virtual:

```powershell
.venv\Scripts\Activate.ps1
```

Si se activó correctamente, la terminal debería mostrar algo similar a:

```text
(.venv) PS C:\...\analizador-ordenes-compra>
```

### 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

---

## Crear estructura de datos

Las carpetas de datos no se almacenan en GitHub, ya que contienen archivos PDF locales y archivos generados durante el procesamiento.

Antes de utilizar el analizador se debe crear la siguiente estructura:

```text
data/
├── pdf/
└── output/
```

Desde PowerShell se puede crear ejecutando:

```powershell
mkdir data
mkdir data\pdf
mkdir data\output
```

La carpeta:

```text
data/pdf/
```

se utiliza para guardar las órdenes de compra en formato PDF que se quieran procesar.

La carpeta:

```text
data/output/
```

se utiliza para guardar el archivo Excel generado por el analizador.

La estructura del proyecto debería quedar aproximadamente así:

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
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

---

## Procesar órdenes de compra PDF

Primero se deben copiar las órdenes de compra dentro de:

```text
data/pdf/
```

Luego ejecutar:

```powershell
python app.py
```

El analizador procesará los archivos PDF encontrados y generará el archivo:

```text
data/output/ordenes_compra.xlsx
```

El Excel contiene principalmente las hojas:

```text
ORDENES
DETALLE_OC
```

- **ORDENES:** contiene una fila por orden de compra.
- **DETALLE_OC:** contiene el detalle de los productos o servicios incluidos en cada orden.

---

## Ejecutar dashboard

Una vez generado el archivo:

```text
data/output/ordenes_compra.xlsx
```

ejecutar:

```powershell
python dashboard\dashboard.py
```

Luego abrir en el navegador:

```text
http://127.0.0.1:5000
```

---

## Generar dashboard HTML autónomo

Además del dashboard Flask, el proyecto puede generar una versión HTML independiente utilizando directamente el archivo:

```text
data/output/ordenes_compra.xlsx
```

---

## Flujo completo de uso

Después de clonar el repositorio, el flujo recomendado es:

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

Luego copiar las órdenes de compra PDF dentro de:

```text
data/pdf/
```

Procesar los archivos:

```powershell
python app.py
```

Una vez generado el Excel, iniciar el dashboard:

```powershell
python dashboard\dashboard.py
```

Finalmente abrir:

```text
http://127.0.0.1:5000
```

---

## Datos utilizados por el dashboard

El dashboard utiliza como fuente principal:

```text
data/output/ordenes_compra.xlsx
```

y trabaja principalmente con las hojas:

```text
ORDENES
DETALLE_OC
```

El sistema mantiene una caché en memoria para mejorar el rendimiento.

Cuando cambia la fecha de modificación del archivo Excel, el dashboard detecta automáticamente el cambio y vuelve a cargar la información.

---

## Analizador PDF

El código encargado de leer, interpretar y procesar las órdenes de compra se encuentra en:

```text
src/
```

El dashboard funciona como una capa de consulta y análisis sobre la información consolidada en Excel.

Las mejoras visuales y los módulos de análisis del dashboard no modifican el proceso original de extracción de los PDF.

---

## Archivos locales no incluidos en GitHub

Por seguridad y para evitar almacenar archivos pesados o información de trabajo, el repositorio no incluye:

- entorno virtual `.venv/`
- órdenes de compra PDF
- archivo `ordenes_compra.xlsx`
- archivos generados dentro de `data/output/`
- archivos temporales de Python

Por este motivo, después de clonar el proyecto cada usuario debe crear localmente:

```text
data/pdf/
data/output/
```

Luego debe colocar sus órdenes de compra dentro de `data/pdf/`, ejecutar `python app.py` para generar el Excel y finalmente ejecutar el dashboard.

---

## Tecnologías

- Python
- Flask
- Pandas
- OpenPyXL
- PyMuPDF
- PDFPlumber
- Bootstrap
- Chart.js