#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML Table Visual Editor v2
Editor visual de tablas HTML hecho con PyQt6 + QWebEngineView.

Mejoras v2:
- Menú compacto con símbolos Unicode
- Deshacer / Rehacer con historial amplio
- Recuerda la última carpeta abierta/guardada
- Combinar celda con la celda de abajo
- Combinar celda con la celda de arriba
- Separar una celda combinada verticalmente si tiene rowspan
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QTimer, QUrl, QSettings
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QToolBar,
    QTabWidget,
    QTextEdit,
    QWidget,
    QVBoxLayout,
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWebEngineWidgets import QWebEngineView


DEFAULT_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Tabla HTML editable</title>
<style>
    body {
        font-family: Arial, sans-serif;
        margin: 20px;
        line-height: 1.5;
    }

    table {
        border-collapse: collapse;
        margin: 15px 0;
        width: 100%;
    }

    td, th {
        border: 1px solid #444;
        padding: 8px;
        min-width: 80px;
        vertical-align: top;
    }

    th {
        background: #e8e8e8;
    }

    .selected-cell {
        outline: 3px solid #1C99E0 !important;
        background: #eaf6ff !important;
    }
</style>
</head>
<body contenteditable="true">

<h1>HTML Table Visual Editor</h1>

<p>Haz clic dentro de una celda y usa los botones para editar la tabla.</p>

<table>
    <tr>
        <th>País</th>
        <th>Condiciones</th>
        <th>Método</th>
        <th>Microorganismos</th>
        <th>Ref.</th>
    </tr>
    <tr>
        <td>Malasia</td>
        <td>18 g de GKA, 50 g de azúcar cruda orgánica y 500 mL de agua mineral.</td>
        <td>Secuenciación de ARNr 16S</td>
        <td>Lb. hilgardii, Lb. harbinensis, Acetobacter lovaniensis</td>
        <td>[16]</td>
    </tr>
    <tr>
        <td></td>
        <td>24 h a temperatura ambiente</td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
</table>

</body>
</html>
"""


EDITOR_JS = r"""
(function () {
    function ensureEditorStyles() {
        if (document.getElementById("html-table-visual-editor-style")) {
            return;
        }

        const style = document.createElement("style");
        style.id = "html-table-visual-editor-style";
        style.textContent = `
            td.selected-cell,
            th.selected-cell {
                outline: 3px solid #1C99E0 !important;
                outline-offset: -3px !important;
                background: #dff5ff !important;
                box-shadow: inset 0 0 0 2px #1C99E0 !important;
            }
        `;
        document.head.appendChild(style);
    }

    ensureEditorStyles();

    if (window.htmlTableVisualEditorInstalled) {
        return;
    }

    window.htmlTableVisualEditorInstalled = true;

    window.currentCell = null;
    window.selectedCells = [];
    window.suppressNextCtrlClick = false;
    window.undoStack = [];
    window.redoStack = [];
    window.maxHistory = 100;

    function clearSelection() {
        document.querySelectorAll(".selected-cell").forEach(function (cell) {
            cell.classList.remove("selected-cell");
        });
        window.selectedCells = [];
    }

    function setSingleSelectedCell(cell) {
        clearSelection();
        window.currentCell = cell;
        window.selectedCells = [cell];
        cell.classList.add("selected-cell");
    }

    function toggleSelectedCell(cell) {
        const index = window.selectedCells.indexOf(cell);

        if (index >= 0) {
            window.selectedCells.splice(index, 1);
            cell.classList.remove("selected-cell");
            window.currentCell = window.selectedCells[window.selectedCells.length - 1] || null;
            return;
        }

        window.selectedCells.push(cell);
        window.currentCell = cell;
        cell.classList.add("selected-cell");
    }

    function getCleanBodyHtml() {
        const clone = document.body.cloneNode(true);
        clone.querySelectorAll(".selected-cell").forEach(function (cell) {
            cell.classList.remove("selected-cell");
        });
        return clone.innerHTML;
    }

    function saveState() {
        const html = getCleanBodyHtml();

        if (window.undoStack.length === 0 || window.undoStack[window.undoStack.length - 1] !== html) {
            window.undoStack.push(html);
        }

        if (window.undoStack.length > window.maxHistory) {
            window.undoStack.shift();
        }

        window.redoStack = [];
    }

    function restoreBodyHtml(html) {
        clearSelection();
        document.body.innerHTML = html;
        document.body.setAttribute("contenteditable", "true");
        window.currentCell = null;
        window.selectedCells = [];
    }

    window.saveEditorState = saveState;

    window.undoEdit = function () {
        if (window.undoStack.length <= 1) {
            alert("No hay más cambios para deshacer.");
            return;
        }

        const current = window.undoStack.pop();
        window.redoStack.push(current);

        const previous = window.undoStack[window.undoStack.length - 1];
        restoreBodyHtml(previous);
    };

    window.redoEdit = function () {
        if (window.redoStack.length === 0) {
            alert("No hay más cambios para rehacer.");
            return;
        }

        const next = window.redoStack.pop();
        window.undoStack.push(next);
        restoreBodyHtml(next);
    };

    function afterChange() {
        saveState();
    }

    document.addEventListener("click", function (event) {
        const cell = event.target.closest("td, th");
        if (cell) {
            if (event.ctrlKey || event.metaKey) {
                event.preventDefault();
                if (window.suppressNextCtrlClick) {
                    window.suppressNextCtrlClick = false;
                    return;
                }
                toggleSelectedCell(cell);
            } else {
                setSingleSelectedCell(cell);
            }
        }
    });

    document.addEventListener("mousedown", function (event) {
        const cell = event.target.closest("td, th");
        if (!cell || (!event.ctrlKey && !event.metaKey)) {
            return;
        }

        event.preventDefault();
        window.suppressNextCtrlClick = true;
        toggleSelectedCell(cell);
    }, true);

    document.addEventListener("input", function () {
        saveState();
    });

    window.getFullHtml = function () {
        clearSelection();

        let clone = document.documentElement.cloneNode(true);
        const editorStyle = clone.querySelector("#html-table-visual-editor-style");
        if (editorStyle) {
            editorStyle.remove();
        }

        clone.querySelectorAll(".selected-cell").forEach(function (cell) {
            cell.classList.remove("selected-cell");
        });

        return "<!DOCTYPE html>\n" + clone.outerHTML;
    };

    window.setEditableMode = function () {
        if (document.body) {
            document.body.setAttribute("contenteditable", "true");
        }

        if (window.undoStack.length === 0) {
            saveState();
        }
    };

    function getSelectedCell() {
        if (!window.currentCell || !document.body.contains(window.currentCell)) {
            alert("Primero haz clic dentro de una celda de una tabla.");
            return null;
        }

        return window.currentCell;
    }

    function getCellIndex(cell) {
        return Array.prototype.indexOf.call(cell.parentNode.children, cell);
    }

    function numericSpan(cell, attributeName) {
        return parseInt(cell.getAttribute(attributeName) || "1", 10);
    }

    function buildTableMap(table) {
        const rows = Array.from(table.rows);
        const map = [];

        rows.forEach(function (row, rowIndex) {
            map[rowIndex] = map[rowIndex] || [];

            let columnIndex = 0;
            Array.from(row.children).forEach(function (cell) {
                while (map[rowIndex][columnIndex]) {
                    columnIndex++;
                }

                const rowspan = numericSpan(cell, "rowspan");
                const colspan = numericSpan(cell, "colspan");

                for (let r = rowIndex; r < rowIndex + rowspan; r++) {
                    map[r] = map[r] || [];
                    for (let c = columnIndex; c < columnIndex + colspan; c++) {
                        map[r][c] = cell;
                    }
                }

                columnIndex += colspan;
            });
        });

        return {rows: rows, map: map};
    }

    function getCellSlot(cell) {
        const table = cell.closest("table");
        if (!table) return null;

        const tableMap = buildTableMap(table);

        for (let r = 0; r < tableMap.map.length; r++) {
            const row = tableMap.map[r] || [];
            for (let c = 0; c < row.length; c++) {
                if (row[c] === cell) {
                    return {
                        table: table,
                        row: r,
                        col: c,
                        rowspan: numericSpan(cell, "rowspan"),
                        colspan: numericSpan(cell, "colspan"),
                        map: tableMap.map,
                    };
                }
            }
        }

        return null;
    }

    function findCellAtVisualPosition(table, rowIndex, columnIndex) {
        const tableMap = buildTableMap(table);
        return tableMap.map[rowIndex] ? tableMap.map[rowIndex][columnIndex] || null : null;
    }

    function areCellsVerticallyMergeable(firstCell, secondCell) {
        if (!firstCell || !secondCell || firstCell === secondCell) return false;
        if (firstCell.closest("table") !== secondCell.closest("table")) return false;

        const firstSlot = getCellSlot(firstCell);
        const secondSlot = getCellSlot(secondCell);
        if (!firstSlot || !secondSlot) return false;

        const sameColumn = firstSlot.col === secondSlot.col;
        const sameWidth = firstSlot.colspan === secondSlot.colspan;
        const touching = (
            firstSlot.row + firstSlot.rowspan === secondSlot.row ||
            secondSlot.row + secondSlot.rowspan === firstSlot.row
        );

        return sameColumn && sameWidth && touching;
    }

    function selectedCellsForMerge() {
        return window.selectedCells.filter(function (cell) {
            return document.body.contains(cell);
        });
    }

    window.canMergeSelectedCells = function () {
        const cells = selectedCellsForMerge();
        return cells.length === 2 && areCellsVerticallyMergeable(cells[0], cells[1]);
    };

    function realColumnIndex(cell) {
        let index = 0;
        const cells = Array.from(cell.parentNode.children);

        for (const c of cells) {
            if (c === cell) {
                return index;
            }
            index += parseInt(c.getAttribute("colspan") || "1", 10);
        }

        return index;
    }

    function findCellAtRealColumn(row, targetIndex) {
        let index = 0;

        for (const cell of Array.from(row.children)) {
            const colspan = parseInt(cell.getAttribute("colspan") || "1", 10);
            if (targetIndex >= index && targetIndex < index + colspan) {
                return cell;
            }
            index += colspan;
        }

        return null;
    }

    function findAdjacentVerticalCell(cell, direction) {
        const slot = getCellSlot(cell);
        if (!slot) return null;

        const targetRow = direction === "down" ? slot.row + slot.rowspan : slot.row - 1;
        if (targetRow < 0) return null;

        const adjacentCell = findCellAtVisualPosition(slot.table, targetRow, slot.col);
        if (!adjacentCell || adjacentCell === cell) return null;

        return adjacentCell;
    }

    function createSameTypeCell(referenceCell) {
        const tag = referenceCell && referenceCell.tagName.toLowerCase() === "th" ? "th" : "td";
        const cell = document.createElement(tag);
        cell.innerHTML = "";
        return cell;
    }

    function appendMergedContent(targetCell, sourceCell) {
        const sourceText = sourceCell.innerHTML.trim();

        if (sourceText !== "") {
            if (targetCell.innerHTML.trim() !== "") {
                targetCell.innerHTML += "<br>";
            }
            targetCell.innerHTML += sourceCell.innerHTML;
        }
    }

    window.insertRowAbove = function () {
        const cell = getSelectedCell();
        if (!cell) return;

        const row = cell.parentNode;
        const newRow = row.cloneNode(true);

        newRow.querySelectorAll("td, th").forEach(function (c) {
            c.innerHTML = "";
            c.classList.remove("selected-cell");
            c.removeAttribute("rowspan");
        });

        row.parentNode.insertBefore(newRow, row);
        afterChange();
    };

    window.insertRowBelow = function () {
        const cell = getSelectedCell();
        if (!cell) return;

        const row = cell.parentNode;
        const newRow = row.cloneNode(true);

        newRow.querySelectorAll("td, th").forEach(function (c) {
            c.innerHTML = "";
            c.classList.remove("selected-cell");
            c.removeAttribute("rowspan");
        });

        if (row.nextSibling) {
            row.parentNode.insertBefore(newRow, row.nextSibling);
        } else {
            row.parentNode.appendChild(newRow);
        }

        afterChange();
    };

    window.deleteCurrentRow = function () {
        const cell = getSelectedCell();
        if (!cell) return;

        const row = cell.parentNode;
        const section = row.parentNode;

        if (section.rows.length <= 1) {
            alert("No se puede eliminar la única fila de esta sección de la tabla.");
            return;
        }

        row.remove();
        window.currentCell = null;
        afterChange();
    };

    window.insertColumnLeft = function () {
        const cell = getSelectedCell();
        if (!cell) return;

        const table = cell.closest("table");
        const visualIndex = realColumnIndex(cell);

        Array.from(table.rows).forEach(function (row) {
            const referenceCell = findCellAtRealColumn(row, visualIndex);
            const newCell = createSameTypeCell(referenceCell);

            if (referenceCell) {
                row.insertBefore(newCell, referenceCell);
            } else {
                row.appendChild(newCell);
            }
        });

        afterChange();
    };

    window.insertColumnRight = function () {
        const cell = getSelectedCell();
        if (!cell) return;

        const table = cell.closest("table");
        const visualIndex = realColumnIndex(cell);

        Array.from(table.rows).forEach(function (row) {
            const referenceCell = findCellAtRealColumn(row, visualIndex);
            const newCell = createSameTypeCell(referenceCell);

            if (referenceCell && referenceCell.nextSibling) {
                row.insertBefore(newCell, referenceCell.nextSibling);
            } else {
                row.appendChild(newCell);
            }
        });

        afterChange();
    };

    window.deleteCurrentColumn = function () {
        const cell = getSelectedCell();
        if (!cell) return;

        const table = cell.closest("table");
        const visualIndex = realColumnIndex(cell);

        Array.from(table.rows).forEach(function (row) {
            const cellToRemove = findCellAtRealColumn(row, visualIndex);
            if (cellToRemove && row.children.length > 1) {
                cellToRemove.remove();
            }
        });

        window.currentCell = null;
        afterChange();
    };

    window.mergeCellDown = function () {
        const cell = getSelectedCell();
        if (!cell) return;

        const cellBelow = findAdjacentVerticalCell(cell, "down");

        if (!cellBelow) {
            alert("No se encontró una celda debajo en la misma columna.");
            return;
        }

        if (!areCellsVerticallyMergeable(cell, cellBelow)) {
            alert("Estas celdas no se pueden unir porque no ocupan la misma columna visual.");
            return;
        }

        appendMergedContent(cell, cellBelow);

        const oldRowspan = numericSpan(cell, "rowspan");
        const belowRowspan = numericSpan(cellBelow, "rowspan");
        cell.setAttribute("rowspan", String(oldRowspan + belowRowspan));

        cellBelow.remove();
        setSingleSelectedCell(cell);
        afterChange();
    };

    window.mergeCellUp = function () {
        const cell = getSelectedCell();
        if (!cell) return;

        const cellAbove = findAdjacentVerticalCell(cell, "up");

        if (!cellAbove) {
            alert("No se encontró una celda arriba en la misma columna.");
            return;
        }

        if (!areCellsVerticallyMergeable(cellAbove, cell)) {
            alert("Estas celdas no se pueden unir porque no ocupan la misma columna visual.");
            return;
        }

        appendMergedContent(cellAbove, cell);

        const aboveRowspan = numericSpan(cellAbove, "rowspan");
        const currentRowspan = numericSpan(cell, "rowspan");
        cellAbove.setAttribute("rowspan", String(aboveRowspan + currentRowspan));

        setSingleSelectedCell(cellAbove);

        cell.remove();
        afterChange();
    };

    window.mergeSelectedCells = function () {
        const cells = selectedCellsForMerge();

        if (cells.length !== 2) {
            alert("Selecciona dos celdas contiguas manteniendo presionado Ctrl.");
            return;
        }

        if (!areCellsVerticallyMergeable(cells[0], cells[1])) {
            alert("Solo se pueden unir dos celdas contiguas en la misma columna visual.");
            return;
        }

        const firstSlot = getCellSlot(cells[0]);
        const secondSlot = getCellSlot(cells[1]);
        const topCell = firstSlot.row <= secondSlot.row ? cells[0] : cells[1];
        const bottomCell = topCell === cells[0] ? cells[1] : cells[0];

        appendMergedContent(topCell, bottomCell);
        topCell.setAttribute("rowspan", String(numericSpan(topCell, "rowspan") + numericSpan(bottomCell, "rowspan")));

        bottomCell.remove();
        setSingleSelectedCell(topCell);
        afterChange();
    };

    window.splitVerticalCell = function () {
        const cell = getSelectedCell();
        if (!cell) return;

        const rowspan = parseInt(cell.getAttribute("rowspan") || "1", 10);

        if (rowspan <= 1) {
            alert("Esta celda no tiene combinación vertical.");
            return;
        }

        const row = cell.parentNode;
        const columnIndex = realColumnIndex(cell);
        const table = cell.closest("table");

        cell.setAttribute("rowspan", "1");

        let currentRow = row;
        for (let i = 1; i < rowspan; i++) {
            currentRow = currentRow.nextElementSibling;
            if (!currentRow) break;

            const newCell = createSameTypeCell(cell);
            const referenceCell = findCellAtRealColumn(currentRow, columnIndex);

            if (referenceCell) {
                currentRow.insertBefore(newCell, referenceCell);
            } else {
                currentRow.appendChild(newCell);
            }
        }

        afterChange();
    };

    window.makeBold = function () {
        document.execCommand("bold", false, null);
        afterChange();
    };

    window.makeItalic = function () {
        document.execCommand("italic", false, null);
        afterChange();
    };

    window.makeUnderline = function () {
        document.execCommand("underline", false, null);
        afterChange();
    };

    window.insertBasicTable = function () {
        const html = `
        <table>
            <tr>
                <th>Encabezado 1</th>
                <th>Encabezado 2</th>
                <th>Encabezado 3</th>
            </tr>
            <tr>
                <td>Dato 1</td>
                <td>Dato 2</td>
                <td>Dato 3</td>
            </tr>
        </table>
        `;
        document.execCommand("insertHTML", false, html);
        afterChange();
    };

    saveState();
})();
"""


class HtmlTableVisualEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HTML Table Visual Editor v2")
        self.resize(1200, 800)

        self.settings = QSettings("Wachin", "HTMLTableVisualEditor")
        self.current_file: Path | None = None
        self.merge_selected_action = None

        self.tabs = QTabWidget()
        self.web_view = QWebEngineView()
        self.code_editor = QTextEdit()
        self.code_editor.setAcceptRichText(False)
        self.code_editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        visual_container = QWidget()
        visual_layout = QVBoxLayout(visual_container)
        visual_layout.setContentsMargins(0, 0, 0, 0)
        visual_layout.addWidget(self.web_view)

        self.tabs.addTab(visual_container, "👁 Visual")
        self.tabs.addTab(self.code_editor, "🧾 HTML")

        self.setCentralWidget(self.tabs)

        self.create_toolbar()

        self.web_view.loadFinished.connect(self.on_load_finished)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.merge_state_timer = QTimer(self)
        self.merge_state_timer.setInterval(250)
        self.merge_state_timer.timeout.connect(self.update_merge_selected_state)

        self.load_html(DEFAULT_HTML)
        self.merge_state_timer.start()

    def create_toolbar(self):
        toolbar = QToolBar("Herramientas")
        self.toolbar = toolbar
        toolbar.setMovable(False)
        toolbar.setIconSize(toolbar.iconSize())
        self.addToolBar(toolbar)

        self.add_action(toolbar, "📄 Nuevo", self.new_file, "Ctrl+N")
        self.add_action(toolbar, "📂 Abrir", self.open_file, "Ctrl+O")
        self.add_action(toolbar, "💾 Guardar", self.save_file, "Ctrl+S")
        self.add_action(toolbar, "💾…", self.save_file_as, "Ctrl+Shift+S")

        toolbar.addSeparator()

        self.add_action(toolbar, "↶", lambda: self.run_js("undoEdit()"), "Ctrl+Z", "Deshacer")
        self.add_action(toolbar, "↷", lambda: self.run_js("redoEdit()"), "Ctrl+Y", "Rehacer")

        toolbar.addSeparator()

        self.add_action(toolbar, "𝐁", lambda: self.run_js("makeBold()"), "Ctrl+B", "Negrita")
        self.add_action(toolbar, "𝐼", lambda: self.run_js("makeItalic()"), "Ctrl+I", "Cursiva")
        self.add_action(toolbar, "U̲", lambda: self.run_js("makeUnderline()"), "Ctrl+U", "Subrayado")

        toolbar.addSeparator()

        self.add_action(toolbar, "▦ Tabla", lambda: self.run_js("insertBasicTable()"), tooltip="Insertar tabla básica")
        self.add_action(toolbar, "↥ Fila", lambda: self.run_js("insertRowAbove()"), tooltip="Insertar fila arriba")
        self.add_action(toolbar, "↧ Fila", lambda: self.run_js("insertRowBelow()"), tooltip="Insertar fila abajo")
        self.add_action(toolbar, "🗑 Fila", lambda: self.run_js("deleteCurrentRow()"), tooltip="Eliminar fila actual")

        toolbar.addSeparator()

        self.add_action(toolbar, "↤ Col.", lambda: self.run_js("insertColumnLeft()"), tooltip="Insertar columna a la izquierda")
        self.add_action(toolbar, "↦ Col.", lambda: self.run_js("insertColumnRight()"), tooltip="Insertar columna a la derecha")
        self.add_action(toolbar, "🗑 Col.", lambda: self.run_js("deleteCurrentColumn()"), tooltip="Eliminar columna actual")

        toolbar.addSeparator()

        self.merge_selected_action = self.add_action(
            toolbar,
            "⇵ Unir",
            lambda: self.run_js("mergeSelectedCells()"),
            tooltip="Combinar las dos celdas seleccionadas con Ctrl",
        )
        self.merge_selected_action.setEnabled(False)

        self.add_action(toolbar, "⇵ Unir ↓", lambda: self.run_js("mergeCellDown()"), tooltip="Combinar esta celda con la celda de abajo")
        self.add_action(toolbar, "⇵ Unir ↑", lambda: self.run_js("mergeCellUp()"), tooltip="Combinar esta celda con la celda de arriba")
        self.add_action(toolbar, "↕ Separar", lambda: self.run_js("splitVerticalCell()"), tooltip="Separar una celda combinada verticalmente")

        toolbar.addSeparator()

        self.add_action(toolbar, "🔄 Ver HTML", self.visual_to_code, tooltip="Actualizar código desde la vista visual")
        self.add_action(toolbar, "✅ Aplicar", self.code_to_visual, tooltip="Aplicar código HTML a la vista visual")

    def add_action(self, toolbar, text, callback, shortcut=None, tooltip=None):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if tooltip:
            action.setToolTip(tooltip)
        else:
            action.setToolTip(text)
        action.triggered.connect(callback)
        toolbar.addAction(action)
        return action

    def get_last_folder(self) -> str:
        folder = self.settings.value("last_folder", str(Path.home()))
        return str(folder) if folder else str(Path.home())

    def remember_folder(self, path: Path):
        if path:
            self.settings.setValue("last_folder", str(path.parent))

    def load_html(self, html: str):
        self.web_view.setHtml(html, QUrl("file:///"))
        self.code_editor.setPlainText(html)

    def on_load_finished(self):
        self.web_view.page().runJavaScript(EDITOR_JS)
        self.web_view.page().runJavaScript("setEditableMode()")

    def run_js(self, js_call: str):
        if self.tabs.currentIndex() != 0:
            self.tabs.setCurrentIndex(0)
        self.web_view.page().runJavaScript(EDITOR_JS)
        self.web_view.page().runJavaScript(js_call)

    def update_merge_selected_state(self):
        if not self.merge_selected_action or self.tabs.currentIndex() != 0:
            return

        def apply_state(can_merge):
            enabled = bool(can_merge)
            self.merge_selected_action.setEnabled(enabled)
            button = self.toolbar.widgetForAction(self.merge_selected_action)

            if button:
                if enabled:
                    button.setStyleSheet(
                        "QToolButton {"
                        "background-color: #ffe066;"
                        "border: 2px solid #1c99e0;"
                        "border-radius: 4px;"
                        "font-weight: 700;"
                        "padding: 3px 7px;"
                        "}"
                    )
                else:
                    button.setStyleSheet("")

        self.web_view.page().runJavaScript(
            "typeof canMergeSelectedCells === 'function' && canMergeSelectedCells()",
            apply_state,
        )

    def on_tab_changed(self, index: int):
        if index == 1:
            self.visual_to_code()

    def visual_to_code(self):
        def update_code(html):
            if html:
                self.code_editor.setPlainText(html)

        self.web_view.page().runJavaScript("getFullHtml()", update_code)

    def code_to_visual(self):
        html = self.code_editor.toPlainText()
        self.web_view.setHtml(html, QUrl("file:///"))
        self.tabs.setCurrentIndex(0)

    def new_file(self):
        if self.ask_discard_changes():
            self.current_file = None
            self.load_html(DEFAULT_HTML)
            self.setWindowTitle("HTML Table Visual Editor v2 - Nuevo archivo")

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo HTML",
            self.get_last_folder(),
            "Archivos HTML (*.html *.htm);;Todos los archivos (*)",
        )

        if not file_name:
            return

        path = Path(file_name)

        try:
            html = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            html = path.read_text(encoding="latin-1")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{error}")
            return

        self.current_file = path
        self.remember_folder(path)
        self.load_html(html)
        self.setWindowTitle(f"HTML Table Visual Editor v2 - {path.name}")

    def save_file(self):
        if self.current_file is None:
            self.save_file_as()
            return

        self.save_to_path(self.current_file)

    def save_file_as(self):
        start_path = str(Path(self.get_last_folder()) / "tabla.html")

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo HTML",
            start_path,
            "Archivos HTML (*.html *.htm);;Todos los archivos (*)",
        )

        if not file_name:
            return

        path = Path(file_name)

        if path.suffix.lower() not in [".html", ".htm"]:
            path = path.with_suffix(".html")

        self.current_file = path
        self.remember_folder(path)
        self.save_to_path(path)
        self.setWindowTitle(f"HTML Table Visual Editor v2 - {path.name}")

    def save_to_path(self, path: Path):
        if self.tabs.currentIndex() == 1:
            html = self.code_editor.toPlainText()
            self.write_html(path, html)
        else:
            def save_html(html):
                self.write_html(path, html)

            self.web_view.page().runJavaScript("getFullHtml()", save_html)

    def write_html(self, path: Path, html: str):
        try:
            path.write_text(html, encoding="utf-8")
            self.remember_folder(path)
            QMessageBox.information(self, "Guardado", f"Archivo guardado:\n{path}")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{error}")

    def ask_discard_changes(self) -> bool:
        answer = QMessageBox.question(
            self,
            "Nuevo archivo",
            "¿Deseas crear un nuevo archivo? Los cambios no guardados se perderán.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes


def main():
    app = QApplication(sys.argv)
    window = HtmlTableVisualEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
