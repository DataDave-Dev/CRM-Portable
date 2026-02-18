# Widget para gestionar el detalle (lineas de producto) de una cotizacion

import os
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5 import uic
from app.repositories.producto_repository import ProductoRepository

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "ventas", "cotizacion_detalle_widget.ui")

IVA_RATE = 0.16


class CotizacionDetalleWidget(QWidget):
    """
    Widget en memoria para las lineas de detalle de una cotizacion.
    Emite totales_changed cuando los items cambian para que el formulario padre
    actualice los labels de Subtotal / IVA / Total.
    """

    totales_changed = pyqtSignal(float, float, float)  # subtotal, iva, total

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._items = []
        self._productos = []

        self._setup_tabla()
        self._setup_signals()
        self._cargar_productos_combo()
        self.formItemContainer.hide()

    # ==============================
    # CONFIGURACION INICIAL
    # ==============================

    def _setup_tabla(self):
        h = self.tabla_detalle.horizontalHeader()
        if h:
            h.setSectionResizeMode(QHeaderView.Stretch)
        v = self.tabla_detalle.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(36)
        self.tabla_detalle.setColumnHidden(0, True)

    def _setup_signals(self):
        self.btn_agregar_item.clicked.connect(self._mostrar_form_item)
        self.btn_eliminar_item.clicked.connect(self._eliminar_item_seleccionado)
        self.btn_confirmar_item.clicked.connect(self._confirmar_item)
        self.btn_cancelar_item.clicked.connect(self._ocultar_form_item)
        self.combo_producto_cot.currentIndexChanged.connect(self._on_producto_seleccionado)

    def _cargar_productos_combo(self):
        repo = ProductoRepository()
        self._productos = repo.find_activos()
        self.combo_producto_cot.clear()
        self.combo_producto_cot.addItem("-- Seleccionar --", None)
        for p in self._productos:
            label = f"{p.codigo} - {p.nombre}" if p.codigo else p.nombre
            self.combo_producto_cot.addItem(label, p.producto_id)

    # ==============================
    # ACCESO PUBLICO
    # ==============================

    def get_items(self):
        """Retorna la lista de items en memoria."""
        return list(self._items)

    def load_items(self, cotizacion_id):
        """Carga items desde BD cuando se edita una cotizacion existente."""
        from app.repositories.cotizacion_detalle_repository import CotizacionDetalleRepository
        repo = CotizacionDetalleRepository()
        db_items = repo.find_by_cotizacion(cotizacion_id)
        self._items = []
        for item in db_items:
            self._items.append({
                "producto_id": item["producto_id"],
                "descripcion": item.get("descripcion"),
                "cantidad": item["cantidad"],
                "precio_unitario": item["precio_unitario"],
                "descuento": item.get("descuento", 0),
                "nombre_producto": item["nombre_producto"],
                "subtotal": item["subtotal"],
            })
        self._actualizar_tabla()

    def limpiar(self):
        """Limpia todos los items."""
        self._items = []
        self._actualizar_tabla()

    # ==============================
    # FORMULARIO
    # ==============================

    def _mostrar_form_item(self):
        self.combo_producto_cot.setCurrentIndex(0)
        self.input_descripcion_cot.clear()
        self.input_cantidad_cot.setText("1")
        self.input_precio_cot.clear()
        self.input_descuento_cot.setText("0")
        self.formItemContainer.show()

    def _ocultar_form_item(self):
        self.formItemContainer.hide()

    def _on_producto_seleccionado(self, index):
        producto_id = self.combo_producto_cot.currentData()
        if producto_id is None:
            self.input_precio_cot.clear()
            return
        producto = next((p for p in self._productos if p.producto_id == producto_id), None)
        if producto and producto.precio_unitario is not None:
            self.input_precio_cot.setText(str(producto.precio_unitario))
        else:
            self.input_precio_cot.clear()

    def _confirmar_item(self):
        producto_id = self.combo_producto_cot.currentData()
        if not producto_id:
            QMessageBox.warning(self, "Atencion", "Selecciona un producto.")
            return

        cantidad_str = self.input_cantidad_cot.text().strip()
        try:
            cantidad = float(cantidad_str)
            if cantidad <= 0:
                raise ValueError
        except (ValueError, TypeError):
            QMessageBox.warning(self, "Atencion", "La cantidad debe ser un numero positivo.")
            return

        precio_str = self.input_precio_cot.text().strip()
        try:
            precio = float(precio_str)
            if precio < 0:
                raise ValueError
        except (ValueError, TypeError):
            QMessageBox.warning(self, "Atencion", "El precio unitario debe ser un numero valido.")
            return

        descuento_str = self.input_descuento_cot.text().strip() or "0"
        try:
            descuento = float(descuento_str)
            if descuento < 0 or descuento > 100:
                raise ValueError
        except (ValueError, TypeError):
            QMessageBox.warning(self, "Atencion", "El descuento debe ser entre 0 y 100.")
            return

        descripcion = self.input_descripcion_cot.text().strip() or None
        producto = next((p for p in self._productos if p.producto_id == producto_id), None)
        nombre_producto = (f"{producto.codigo} - {producto.nombre}" if producto and producto.codigo else (producto.nombre if producto else ""))

        subtotal = round(cantidad * precio * (1 - descuento / 100.0), 2)

        self._items.append({
            "producto_id": producto_id,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "precio_unitario": precio,
            "descuento": descuento,
            "nombre_producto": nombre_producto,
            "subtotal": subtotal,
        })

        self._actualizar_tabla()
        self._ocultar_form_item()

    # ==============================
    # ELIMINAR
    # ==============================

    def _eliminar_item_seleccionado(self):
        rows = self.tabla_detalle.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Atencion", "Selecciona un item para eliminar.")
            return
        row = rows[0].row()
        if 0 <= row < len(self._items):
            self._items.pop(row)
            self._actualizar_tabla()

    # ==============================
    # TABLA Y TOTALES
    # ==============================

    def _actualizar_tabla(self):
        self.tabla_detalle.setRowCount(0)
        subtotal_total = 0.0

        for i, item in enumerate(self._items):
            r = self.tabla_detalle.rowCount()
            self.tabla_detalle.insertRow(r)
            sub = round(item["cantidad"] * item["precio_unitario"] * (1 - item.get("descuento", 0) / 100.0), 2)
            item["subtotal"] = sub
            subtotal_total += sub

            self.tabla_detalle.setItem(r, 0, QTableWidgetItem(str(i)))
            self.tabla_detalle.setItem(r, 1, QTableWidgetItem(item.get("nombre_producto", "")))
            self.tabla_detalle.setItem(r, 2, QTableWidgetItem(item.get("descripcion") or ""))
            self.tabla_detalle.setItem(r, 3, QTableWidgetItem(str(item["cantidad"])))
            self.tabla_detalle.setItem(r, 4, QTableWidgetItem(f"${item['precio_unitario']:,.2f}"))
            self.tabla_detalle.setItem(r, 5, QTableWidgetItem(f"{item.get('descuento', 0):.1f}%"))
            self.tabla_detalle.setItem(r, 6, QTableWidgetItem(f"${sub:,.2f}"))

        subtotal_total = round(subtotal_total, 2)
        iva = round(subtotal_total * IVA_RATE, 2)
        total = round(subtotal_total + iva, 2)
        self.totales_changed.emit(subtotal_total, iva, total)
