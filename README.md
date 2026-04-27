# HTML Table Visual Editor v2

Editor visual de tablas HTML hecho con **Python + PyQt6 + QWebEngineView**.

Esta versión está pensada especialmente para editar tablas HTML de manera visual.

## Mejoras de esta versión

- Menú más compacto con símbolos Unicode
- Botón de guardar con símbolo 💾
- Deshacer y rehacer:
  - `Ctrl + Z`
  - `Ctrl + Y`
  - historial amplio de hasta 100 cambios
- Recuerda la última carpeta abierta o guardada
- Combinar celdas verticalmente:
  - **⇵ Unir ↓**
  - **⇵ Unir ↑**
- Separar celdas combinadas verticalmente:
  - **↕ Separar**
- Insertar y eliminar filas
- Insertar y eliminar columnas
- Editar el contenido directamente dentro de las celdas

## Instalación en Debian 12 / MX Linux 23

```bash
sudo apt update
sudo apt install python3-pyqt6 python3-pyqt6.qtwebengine qt6-translations-l10n
```

## Ejecutar

```bash
python3 html_table_visual_editor.py
```

## Cómo combinar dos filas dentro de una tabla

Para el caso como el de la captura, donde hay dos filas y quieres que una celda ocupe ambas filas:

1. Haz clic en la celda de arriba.
2. Pulsa **⇵ Unir ↓**.
3. El programa combina esa celda con la celda de abajo usando `rowspan`.

También puedes hacerlo al revés:

1. Haz clic en la celda de abajo.
2. Pulsa **⇵ Unir ↑**.

## Deshacer y rehacer

Puedes usar:

```text
Ctrl + Z  = deshacer
Ctrl + Y  = rehacer
```

También están los botones:

```text
↶  deshacer
↷  rehacer
```

El historial guarda hasta 100 cambios.

## Última carpeta abierta

El programa guarda automáticamente la última carpeta usada al abrir o guardar archivos.

Esta configuración se guarda con `QSettings`, sin que tengas que crear ningún archivo manualmente.

## Limitaciones actuales

Esta versión ya permite combinar celdas verticalmente con `rowspan`, pero todavía no maneja perfectamente todos los casos avanzados de tablas con:

- muchas celdas combinadas mezcladas
- `colspan` complejo
- tablas anidadas muy complicadas
- edición visual avanzada estilo Dreamweaver completo

Aun así, ya sirve como una base mucho más útil para editar tablas HTML reales.
