# HTML Table Visual Editor v2

Editor visual de tablas HTML hecho con **Python + PyQt6 + QWebEngineView**.

El programa permite abrir, editar y guardar archivos HTML con una vista visual editable y una vista de código. Está pensado especialmente para trabajar con tablas HTML sin tener que modificar manualmente cada etiqueta.

## Funciones principales

- Menú **Archivo** compacto con:
  - **📄 Nuevo**
  - **📂 Abrir**
  - **💾 Guardar**
  - **💾 Guardar como ...**
- Crear un documento HTML nuevo vacío.
- Abrir archivos `.html` y `.htm`.
- Guardar el archivo actual o guardar una copia con otro nombre.
- Recordar la última carpeta usada para abrir o guardar.
- Editar visualmente el contenido del documento.
- Alternar entre vista **Visual** y vista **HTML**.
- Actualizar el código desde la vista visual con **🔄 Ver HTML**.
- Aplicar cambios escritos en el código con **✅ Aplicar**.
- Insertar una tabla básica.
- Insertar filas arriba o abajo de la celda seleccionada.
- Eliminar la fila actual.
- Insertar columnas a la izquierda o derecha de la celda seleccionada.
- Eliminar la columna actual.
- Seleccionar celdas con clic.
- Seleccionar dos celdas con `Ctrl` para combinarlas.
- Combinar celdas verticalmente con:
  - **⇵ Unir**
  - **⇵ Unir ↓**
  - **⇵ Unir ↑**
- Separar celdas combinadas verticalmente con **↕ Separar**.
- Aplicar formato básico:
  - **𝐁** negrita
  - **𝐼** cursiva
  - **U̲** subrayado
- Deshacer y rehacer con botones o atajos de teclado.

## Atajos de teclado

```text
Ctrl + N        Nuevo archivo
Ctrl + O        Abrir archivo
Ctrl + S        Guardar
Ctrl + Shift + S Guardar como
Ctrl + Z        Deshacer
Ctrl + Y        Rehacer
Ctrl + B        Negrita
Ctrl + I        Cursiva
Ctrl + U        Subrayado
```

## Instalación en Debian 12 / MX Linux 23 / Ubuntu

Instala las dependencias desde los repositorios del sistema:

```bash
sudo apt update
sudo apt install python3-pyqt6 python3-pyqt6.qtwebengine qt6-translations-l10n
```

Ejecuta el programa:

```bash
python3 html_table_visual_editor.py
```

## Instalación en Windows

1. Instala Python 3 desde <https://www.python.org/downloads/windows/>.
2. Durante la instalación, marca la opción **Add python.exe to PATH**.
3. Abre PowerShell o Símbolo del sistema dentro de la carpeta del proyecto.
4. Crea un entorno virtual:

```powershell
py -m venv .venv
```

5. Activa el entorno virtual:

```powershell
.\.venv\Scripts\activate
```

6. Instala las dependencias:

```powershell
py -m pip install --upgrade pip
py -m pip install PyQt6 PyQt6-WebEngine
```

7. Ejecuta el programa:

```powershell
py html_table_visual_editor.py
```

## Instalación en macOS

1. Instala Python 3. Una forma sencilla es usar Homebrew:

```bash
brew install python
```

2. Abre Terminal dentro de la carpeta del proyecto.
3. Crea un entorno virtual:

```bash
python3 -m venv .venv
```

4. Activa el entorno virtual:

```bash
source .venv/bin/activate
```

5. Instala las dependencias:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install PyQt6 PyQt6-WebEngine
```

6. Ejecuta el programa:

```bash
python3 html_table_visual_editor.py
```

## Uso básico

Para empezar desde cero, usa **Archivo > Nuevo**. Esto crea un documento HTML vacío listo para editar.

Para abrir un archivo existente, usa **Archivo > Abrir** y selecciona un archivo `.html` o `.htm`.

Para guardar los cambios, usa **Archivo > Guardar**. Si el documento todavía no tiene ruta, el programa pedirá dónde guardarlo. También puedes usar **Archivo > Guardar como ...** para elegir otro nombre o ubicación.

## Cómo combinar celdas verticalmente

Para hacer que una celda ocupe dos filas:

1. Haz clic en la celda de arriba.
2. Pulsa **⇵ Unir ↓**.
3. El programa combina esa celda con la celda de abajo usando `rowspan`.

También puedes hacerlo al revés:

1. Haz clic en la celda de abajo.
2. Pulsa **⇵ Unir ↑**.

Otra opción es seleccionar dos celdas contiguas de la misma columna usando `Ctrl` y luego pulsar **⇵ Unir**.

## Vista HTML

La pestaña **HTML** muestra el código del documento. Al cambiar a esa pestaña, el programa actualiza el código desde la vista visual.

Si editas el código manualmente, pulsa **✅ Aplicar** para volver a cargarlo en la vista visual.

## Configuración guardada

El programa guarda automáticamente la última carpeta usada al abrir o guardar archivos mediante `QSettings`.

No es necesario crear archivos de configuración manualmente.

## Limitaciones actuales

Esta versión maneja edición visual básica y combinación vertical con `rowspan`, pero todavía no cubre todos los casos avanzados de un editor HTML completo, como:

- tablas anidadas muy complejas
- combinaciones mixtas muy avanzadas de `rowspan` y `colspan`
- edición visual completa tipo Dreamweaver
- validación avanzada de HTML

Aun así, ya sirve como una base práctica para editar tablas HTML reales.
