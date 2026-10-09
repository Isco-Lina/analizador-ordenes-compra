# Analizador de Órdenes de Compra

Aplicación desarrollada en Python para automatizar la extracción de información desde órdenes de compra en formato PDF.

El programa procesa múltiples órdenes de compra y obtiene automáticamente información como:

- Número de orden de compra
- Hospital o proyecto
- Fecha
- Proveedor
- Datos de contacto
- Forma de pago
- Solicitante y aprobador
- Artículos comprados
- Cantidad y unidad de medida
- Precio unitario
- Totales
- Moneda

La información extraída se organiza automáticamente en un archivo Excel, separando los datos generales de cada orden de compra y el detalle de sus artículos.

El proyecto incluye validaciones para detectar diferencias en los montos, documentos que requieren revisión y órdenes de compra duplicadas.

Actualmente ha sido probado con más de 2.000 órdenes de compra reales.

## Tecnologías

- Python
- PyMuPDF
- OpenPyXL
- Unittest

## Objetivo

Facilitar el análisis histórico de compras y disponer de información estructurada para posteriormente realizar análisis y visualizaciones en Power BI.