# Widget para gestionar productos/servicios vinculados a una oportunidad

import os
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5 import uic
from app.repositories.producto_repository import ProductoRepository

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "ventas", "oportunidad_productos_widget.ui")


class OportunidadProductosWidget(QWidget):
    """
    Widget para agregar/eliminar productos de una oportunidad.
    Usa modelo en memoria: los items se guardan solo cuando el padre llama a get_items()
    y el servicio persiste los cambios junto con la oportunidad.
    """

    def __init__(self, oportunidad_id=None, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._oportunidad_id = oportunidad_id
        self._items = []           # lista de dicts en memoria
        self._productos = []       # productos activos cargados del catalogo

        self._setup_tabla()
        self._setup_signals()
        self._cargar_productos_combo()

        # ocultar formulario de agregar inicialmente
        self.formProductoContainer.hide()

        if oportunidad_id:
            self._cargar_items_desde_db()

    # ==============================
    # CONFIGURACION INICIAL
    # ==============================

    def _setup_tabla(self):
        h = self.tabla_op_productos.horizontalHeader()
        if h:
            h.setSectionResizeMode(QHeaderView.Stretch)
        v = self.tabla_op_productos.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(36)
        # ocultar columna ID (indice en la lista)
        self.tabla_op_productos.setColumnHidden(0, True)

    def _setup_signals(self):
        self.btn_agregar_producto.clicked.connect(self._mostrar_form_agregar)
        self.btn_eliminar_producto.clicked.connect(self._eliminar_item_seleccionado)
        self.btn_confirmar_agregar.clicked.connect(self._confirmar_agregar)
        self.btn_cancelar_agregar.clicked.connect(self._ocultar_form_agregar)
        self.combo_producto_op.currentIndexChanged.connect(self._on_producto_seleccionado)

    def _cargar_productos_combo(self):
        repo = ProductoRepository()
        self._productos = repo.find_activos()
        self.combo_producto_op.clear()
        self.combo_producto_op.addItem("-- Seleccionar --", None)
        for p in self._productos:
            label = f"{p.codigo} - {p.nombre}" if p.codigo else p.nombre
            self.combo_producto_op.addItem(label, p.producto_id)

    def _cargar_items_desde_db(self):
        from app.repositories.oportunidad_producto_repository import OportunidadProductoRepository
        repo = OportunidadProductoRepository()
        self._items = repo.find_by_oportunidad(self._oportunidad_id)
        self._actualizar_tabla()

    # ==============================
    # ACCESO PUBLICO
    # ==============================

    def get_items(self):
        """Retorna la lista actual de items en memoria para persistirlos desde el servicio."""
        return list(self._items)

    def set_oportunidad_id(self, oportunidad_id):
        """Permite asignar el oportunidad_id despues de crear la oportunidad."""
        self._oportunidad_id = oportunidad_id

    # ==============================
    # FORMULARIO AGREGAR
    # ==============================

    def _mostrar_form_agregar(self):
        self.combo_producto_op.setCurrentIndex(0)
        self.input_cantidad_op.setText("1")
        self.input_precio_op.clear()
        self.input_descuento_op.setText("0")
        self.input_notas_op.clear()
        self.formProductoContainer.show()

    def _ocultar_form_agregar(self):
        self.formProductoContainer.hide()

    def _on_producto_seleccionado(self, index):
        # auto-llenar precio desde el catalogo de productos
        producto_id = self.combo_producto_op.currentData()
        if producto_id is None:
            self.input_precio_op.clear()
            return
        producto = next((p for p in self._productos if p.producto_id == producto_id), None)
        if producto and producto.precio_unitario is not None:
            self.input_precio_op.setText(str(producto.precio_unitario))
        else:
            self.input_precio_op.clear()

    def _confirmar_agregar(self):
        producto_id = self.combo_producto_op.currentData()
        if not producto_id:
            QMessageBox.warning(self, "Atencion", "Selecciona un producto.")
            return

        cantidad_str = self.input_cantidad_op.text().strip()
        if not cantidad_str:
            QMessageBox.warning(self, "Atencion", "La cantidad es requerida.")
            return
        try:
            cantidad = float(cantidad_str)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Atencion", "La cantidad debe ser un numero positivo.")
            return

        precio_str = self.input_precio_op.text().strip()
        if not precio_str:
            QMessageBox.warning(self, "Atencion", "El precio unitario es requerido.")
            return
        try:
            precio = float(precio_str)
            if precio < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Atencion", "El precio unitario debe ser un numero valido.")
            return

        descuento_str = self.input_descuento_op.text().strip() or "0"
        try:
            descuento = float(descuento_str)
            if descuento < 0 or descuento > 100:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Atencion", "El descuento debe ser un numero entre 0 y 100.")
            return

        notas = self.input_notas_op.text().strip() or None
        producto = next((p for p in self._productos if p.producto_id == producto_id), None)
        nombre_producto = (f"{producto.codigo} - {producto.nombre}" if producto and producto.codigo else (producto.nombre if producto else ""))

        subtotal = round(cantidad * precio * (1 - descuento / 100.0), 2)

        self._items.append({
            "producto_id": producto_id,
            "cantidad": cantidad,
            "precio_unitario": precio,
            "descuento": descuento,
            "notas": notas,
            "nombre_producto": nombre_producto,
            "subtotal": subtotal,
        })

        self._actualizar_tabla()
        self._ocultar_form_agregar()

    # ==============================
    # ELIMINAR
    # ==============================

    def _eliminar_item_seleccionado(self):
        rows = self.tabla_op_productos.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Atencion", "Selecciona un producto para eliminar.")
            return
        row = rows[0].row()
        if 0 <= row < len(self._items):
            self._items.pop(row)
            self._actualizar_tabla()

    # ==============================
    # TABLA
    # ==============================

    def _actualizar_tabla(self):
        self.tabla_op_productos.setRowCount(0)
        total_general = 0.0

        for i, item in enumerate(self._items):
            r = self.tabla_op_productos.rowCount()
            self.tabla_op_productos.insertRow(r)
            subtotal = round(item["cantidad"] * item["precio_unitario"] * (1 - item.get("descuento", 0) / 100.0), 2)
            item["subtotal"] = subtotal
            total_general += subtotal

            self.tabla_op_productos.setItem(r, 0, QTableWidgetItem(str(i)))
            self.tabla_op_productos.setItem(r, 1, QTableWidgetItem(item.get("nombre_producto", "")))
            self.tabla_op_productos.setItem(r, 2, QTableWidgetItem(str(item["cantidad"])))
            self.tabla_op_productos.setItem(r, 3, QTableWidgetItem(f"${item['precio_unitario']:,.2f}"))
            self.tabla_op_productos.setItem(r, 4, QTableWidgetItem(f"{item.get('descuento', 0):.1f}%"))
            self.tabla_op_productos.setItem(r, 5, QTableWidgetItem(f"${subtotal:,.2f}"))
            self.tabla_op_productos.setItem(r, 6, QTableWidgetItem(item.get("notas") or ""))

        self.prodTotalValor.setText(f"${total_general:,.2f}")
