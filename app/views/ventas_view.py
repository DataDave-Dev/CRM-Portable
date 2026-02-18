# Vista de Ventas - gestiona Oportunidades, Productos y Cotizaciones

import os
import datetime
from PyQt5.QtWidgets import (
    QWidget, QMessageBox, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QColor
from PyQt5 import uic
from app.database.connection import get_connection
from app.services.oportunidad_service import OportunidadService
from app.services.producto_service import ProductoService
from app.services.cotizacion_service import CotizacionService
from app.utils.catalog_cache import CatalogCache
from app.views.oportunidad_productos_widget import OportunidadProductosWidget
from app.views.historial_etapas_widget import HistorialEtapasWidget
from app.views.cotizacion_detalle_widget import CotizacionDetalleWidget

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "ventas", "ventas_view.ui")

_ESTADOS_OPORTUNIDAD = [
    ("Abierta (En Pipeline)", None),
    ("Ganada", 1),
    ("Perdida", 0),
]

_ESTADOS_COTIZACION = ["Borrador", "Enviada", "Aceptada", "Rechazada", "Vencida"]


class VentasView(QWidget):

    def __init__(self, usuario_actual, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._usuario_actual = usuario_actual
        self._oportunidad_service = OportunidadService()
        self._producto_service = ProductoService()
        self._cotizacion_service = CotizacionService()

        self._oportunidad_editando = None
        self._producto_editando = None
        self._cotizacion_editando = None
        self._oportunidades_cargadas = []
        self._productos_cargados = []
        self._cotizaciones_cargadas = []

        # widgets embebidos
        self._oportunidad_productos_widget = None
        self._historial_etapas_widget = None
        self._cotizacion_detalle_widget = None

        self._create_oportunidad_list()
        self._create_oportunidad_form()
        self._create_producto_list()
        self._create_producto_form()
        self._create_cotizacion_list()
        self._create_cotizacion_form()
        self._setup_tabs()

    # ==========================================
    # TABS
    # ==========================================

    def _setup_tabs(self):
        self.ventasTabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if index == 0:
            self._mostrar_lista_oportunidades()
        elif index == 1:
            self._mostrar_lista_productos()
        elif index == 2:
            self._mostrar_lista_cotizaciones()

    def cargar_datos(self):
        index = self.ventasTabs.currentIndex()
        if index == 0:
            self._cargar_tabla_oportunidades()
        elif index == 1:
            self._cargar_tabla_productos()
        elif index == 2:
            self._cargar_tabla_cotizaciones()

    # ==========================================
    # OPORTUNIDADES - LISTA
    # ==========================================

    def _create_oportunidad_list(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "ventas", "oportunidad_list.ui")
        self.lista_oportunidades_widget = QWidget()
        uic.loadUi(ui_path, self.lista_oportunidades_widget)

        self.btn_nueva_oportunidad = self.lista_oportunidades_widget.btn_nueva_oportunidad
        self.tabla_oportunidades = self.lista_oportunidades_widget.tabla_oportunidades
        self.stat_op_total = self.lista_oportunidades_widget.statValueTotal
        self.stat_op_abiertas = self.lista_oportunidades_widget.statValueAbiertas
        self.stat_op_ganadas = self.lista_oportunidades_widget.statValueGanadas
        self.stat_op_perdidas = self.lista_oportunidades_widget.statValuePerdidas

        self.btn_nueva_oportunidad.clicked.connect(self._mostrar_form_nueva_oportunidad)
        self.tabla_oportunidades.doubleClicked.connect(self._editar_oportunidad_seleccionada)

        h = self.tabla_oportunidades.horizontalHeader()
        if h:
            h.setSectionResizeMode(QHeaderView.Stretch)
        v = self.tabla_oportunidades.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(42)

        self.tabOportunidadesLayout.addWidget(self.lista_oportunidades_widget)

    def _cargar_tabla_oportunidades(self):
        try:
            oportunidades, error = self._oportunidad_service.obtener_todas(limit=200)
            if error:
                QMessageBox.critical(self, "Error", error)
                return

            self._oportunidades_cargadas = oportunidades or []
            total = len(self._oportunidades_cargadas)
            abiertas = sum(1 for o in self._oportunidades_cargadas if o.es_ganada is None)
            ganadas = sum(1 for o in self._oportunidades_cargadas if o.es_ganada == 1)
            perdidas = sum(1 for o in self._oportunidades_cargadas if o.es_ganada == 0)

            self.stat_op_total.setText(str(total))
            self.stat_op_abiertas.setText(str(abiertas))
            self.stat_op_ganadas.setText(str(ganadas))
            self.stat_op_perdidas.setText(str(perdidas))

            self.tabla_oportunidades.setRowCount(0)
            for op in self._oportunidades_cargadas:
                r = self.tabla_oportunidades.rowCount()
                self.tabla_oportunidades.insertRow(r)
                self.tabla_oportunidades.setItem(r, 0, QTableWidgetItem(str(op.oportunidad_id)))
                self.tabla_oportunidades.setItem(r, 1, QTableWidgetItem(op.nombre or ""))
                self.tabla_oportunidades.setItem(r, 2, QTableWidgetItem(op.nombre_empresa or "N/A"))
                self.tabla_oportunidades.setItem(r, 3, QTableWidgetItem(op.nombre_etapa or "N/A"))
                monto_str = f"${op.monto_estimado:,.2f}" if op.monto_estimado is not None else "N/A"
                self.tabla_oportunidades.setItem(r, 4, QTableWidgetItem(monto_str))
                prob_str = f"{op.probabilidad_cierre}%" if op.probabilidad_cierre is not None else "N/A"
                self.tabla_oportunidades.setItem(r, 5, QTableWidgetItem(prob_str))
                self.tabla_oportunidades.setItem(r, 6, QTableWidgetItem(op.fecha_cierre_estimada or "N/A"))
                self.tabla_oportunidades.setItem(r, 7, QTableWidgetItem(op.nombre_propietario or "N/A"))
                if op.es_ganada is None:
                    estado_str, color = "Abierta", QColor(237, 137, 54)
                elif op.es_ganada == 1:
                    estado_str, color = "Ganada", QColor(34, 139, 34)
                else:
                    estado_str, color = "Perdida", QColor(220, 53, 69)
                item_estado = QTableWidgetItem(estado_str)
                item_estado.setForeground(color)
                self.tabla_oportunidades.setItem(r, 8, item_estado)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las oportunidades: {str(e)}")

    def _mostrar_lista_oportunidades(self):
        self.form_oportunidades_widget.hide()
        self.lista_oportunidades_widget.show()
        self._limpiar_widgets_op_embebidos()
        self._cargar_tabla_oportunidades()

    # ==========================================
    # OPORTUNIDADES - FORMULARIO
    # ==========================================

    def _create_oportunidad_form(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "ventas", "oportunidad_form.ui")
        self.form_oportunidades_widget = QWidget()
        uic.loadUi(ui_path, self.form_oportunidades_widget)

        self.op_form_titulo = self.form_oportunidades_widget.form_titulo
        self.op_form_subtitulo = self.form_oportunidades_widget.form_subtitulo
        self.op_input_nombre = self.form_oportunidades_widget.input_nombre
        self.op_combo_empresa = self.form_oportunidades_widget.combo_empresa
        self.op_combo_contacto = self.form_oportunidades_widget.combo_contacto
        self.op_input_descripcion = self.form_oportunidades_widget.input_descripcion
        self.op_combo_etapa = self.form_oportunidades_widget.combo_etapa
        self.op_combo_propietario = self.form_oportunidades_widget.combo_propietario
        self.op_input_monto_estimado = self.form_oportunidades_widget.input_monto_estimado
        self.op_combo_moneda = self.form_oportunidades_widget.combo_moneda
        self.op_input_probabilidad = self.form_oportunidades_widget.input_probabilidad
        self.op_combo_origen = self.form_oportunidades_widget.combo_origen
        self.op_input_fecha_cierre_estimada = self.form_oportunidades_widget.input_fecha_cierre_estimada
        self.op_combo_estado = self.form_oportunidades_widget.combo_estado
        self.op_input_fecha_cierre_real = self.form_oportunidades_widget.input_fecha_cierre_real
        self.op_combo_motivo_perdida = self.form_oportunidades_widget.combo_motivo_perdida
        self.op_input_notas_perdida = self.form_oportunidades_widget.input_notas_perdida
        self.op_label_motivo_perdida = self.form_oportunidades_widget.label_motivo_perdida
        self.op_label_notas_perdida = self.form_oportunidades_widget.label_notas_perdida
        self.op_btn_guardar = self.form_oportunidades_widget.btn_guardar
        self.op_btn_limpiar = self.form_oportunidades_widget.btn_limpiar
        self.op_btn_cancelar = self.form_oportunidades_widget.btn_cancelar

        self.op_btn_guardar.clicked.connect(self._guardar_oportunidad)
        self.op_btn_limpiar.clicked.connect(self._limpiar_formulario_oportunidad)
        self.op_btn_cancelar.clicked.connect(self._mostrar_lista_oportunidades)
        self.op_combo_estado.currentIndexChanged.connect(self._on_op_estado_changed)
        self.op_combo_empresa.currentIndexChanged.connect(self._on_op_empresa_changed)

        self._cargar_combos_oportunidad()
        self.form_oportunidades_widget.hide()
        self.tabOportunidadesLayout.addWidget(self.form_oportunidades_widget)

    def _cargar_combos_oportunidad(self):
        conn = get_connection()

        self.op_combo_etapa.clear()
        self.op_combo_etapa.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_etapas_venta():
            self.op_combo_etapa.addItem(nombre, id_val)

        self.op_combo_propietario.clear()
        self.op_combo_propietario.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_usuarios():
            self.op_combo_propietario.addItem(nombre, id_val)

        self.op_combo_empresa.clear()
        self.op_combo_empresa.addItem("-- Seleccionar --", None)
        cursor = conn.execute(
            "SELECT EmpresaID, RazonSocial FROM Empresas WHERE Activo = 1 ORDER BY RazonSocial"
        )
        for row in cursor.fetchall():
            self.op_combo_empresa.addItem(row["RazonSocial"], row["EmpresaID"])

        self._cargar_combo_contactos_op(empresa_id=None)

        self.op_combo_moneda.clear()
        self.op_combo_moneda.addItem("-- Seleccionar --", None)
        cursor = conn.execute("SELECT MonedaID, Nombre, Codigo FROM Monedas ORDER BY Codigo")
        for row in cursor.fetchall():
            self.op_combo_moneda.addItem(f"{row['Codigo']} - {row['Nombre']}", row["MonedaID"])

        self.op_combo_origen.clear()
        self.op_combo_origen.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_origenes_contacto():
            self.op_combo_origen.addItem(nombre, id_val)

        self.op_combo_estado.clear()
        for label, valor in _ESTADOS_OPORTUNIDAD:
            self.op_combo_estado.addItem(label, valor)

        self.op_combo_motivo_perdida.clear()
        self.op_combo_motivo_perdida.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_motivos_perdida():
            self.op_combo_motivo_perdida.addItem(nombre, id_val)

        self._actualizar_visibilidad_perdida()

    def _cargar_combo_contactos_op(self, empresa_id=None):
        conn = get_connection()
        self.op_combo_contacto.clear()
        self.op_combo_contacto.addItem("-- Seleccionar --", None)
        if empresa_id:
            cursor = conn.execute(
                "SELECT ContactoID, (Nombre || ' ' || ApellidoPaterno) AS NC FROM Contactos WHERE EmpresaID = ? AND Activo = 1 ORDER BY Nombre",
                (empresa_id,),
            )
        else:
            cursor = conn.execute(
                "SELECT ContactoID, (Nombre || ' ' || ApellidoPaterno) AS NC FROM Contactos WHERE Activo = 1 ORDER BY Nombre"
            )
        for row in cursor.fetchall():
            self.op_combo_contacto.addItem(row["NC"], row["ContactoID"])

    def _on_op_empresa_changed(self, index):
        self._cargar_combo_contactos_op(empresa_id=self.op_combo_empresa.currentData())

    def _on_op_estado_changed(self, index):
        self._actualizar_visibilidad_perdida()

    def _actualizar_visibilidad_perdida(self):
        es_perdida = self.op_combo_estado.currentData() == 0
        self.op_combo_motivo_perdida.setVisible(es_perdida)
        self.op_label_motivo_perdida.setVisible(es_perdida)
        self.op_input_notas_perdida.setVisible(es_perdida)
        self.op_label_notas_perdida.setVisible(es_perdida)

    def _mostrar_form_nueva_oportunidad(self):
        self._oportunidad_editando = None
        self.lista_oportunidades_widget.hide()
        self.form_oportunidades_widget.show()
        self.op_form_titulo.setText("Nueva Oportunidad")
        self.op_form_subtitulo.setText(
            "Completa la informacion de la nueva oportunidad. Los campos con * son obligatorios."
        )
        self.op_btn_guardar.setText("Guardar Oportunidad")
        self._cargar_combos_oportunidad()
        self._limpiar_formulario_oportunidad()
        self._limpiar_widgets_op_embebidos()
        self._crear_widget_productos_op(oportunidad_id=None)

    def _editar_oportunidad_seleccionada(self, index):
        row = index.row()
        id_item = self.tabla_oportunidades.item(row, 0)
        if not id_item:
            return
        oportunidad_id = int(id_item.text())
        op = next((o for o in self._oportunidades_cargadas if o.oportunidad_id == oportunidad_id), None)
        if not op:
            return

        self._oportunidad_editando = op
        self.lista_oportunidades_widget.hide()
        self.form_oportunidades_widget.show()
        self.op_form_titulo.setText("Editar Oportunidad")
        self.op_form_subtitulo.setText(f"Editando oportunidad: {op.nombre}.")
        self.op_btn_guardar.setText("Actualizar Oportunidad")

        self._cargar_combos_oportunidad()

        self.op_input_nombre.setText(op.nombre or "")
        self.op_input_descripcion.setText(op.descripcion or "")
        self.op_input_monto_estimado.setText(
            str(op.monto_estimado) if op.monto_estimado is not None else ""
        )
        self.op_input_probabilidad.setText(
            str(op.probabilidad_cierre) if op.probabilidad_cierre is not None else ""
        )
        self.op_input_fecha_cierre_estimada.setText(op.fecha_cierre_estimada or "")
        self.op_input_fecha_cierre_real.setText(op.fecha_cierre_real or "")
        self.op_input_notas_perdida.setText(op.notas_perdida or "")

        self._seleccionar_combo(self.op_combo_empresa, op.empresa_id)
        self._cargar_combo_contactos_op(empresa_id=op.empresa_id)
        self._seleccionar_combo(self.op_combo_contacto, op.contacto_id)
        self._seleccionar_combo(self.op_combo_etapa, op.etapa_id)
        self._seleccionar_combo(self.op_combo_propietario, op.propietario_id)
        self._seleccionar_combo(self.op_combo_moneda, op.moneda_id)
        self._seleccionar_combo(self.op_combo_origen, op.origen_id)
        self._seleccionar_combo(self.op_combo_motivo_perdida, op.motivos_perdida_id)
        self._seleccionar_combo_estado_op(op.es_ganada)
        self._actualizar_visibilidad_perdida()

        self._limpiar_widgets_op_embebidos()
        self._crear_widget_productos_op(oportunidad_id=op.oportunidad_id)
        self._crear_widget_historial(oportunidad_id=op.oportunidad_id)

    def _crear_widget_productos_op(self, oportunidad_id):
        self._oportunidad_productos_widget = OportunidadProductosWidget(
            oportunidad_id=oportunidad_id,
            parent=self.form_oportunidades_widget,
        )
        layout = self.form_oportunidades_widget.layout()
        if layout:
            layout.addWidget(self._oportunidad_productos_widget)
        self._oportunidad_productos_widget.show()

    def _crear_widget_historial(self, oportunidad_id):
        self._historial_etapas_widget = HistorialEtapasWidget(
            oportunidad_id=oportunidad_id,
            parent=self.form_oportunidades_widget,
        )
        layout = self.form_oportunidades_widget.layout()
        if layout:
            layout.addWidget(self._historial_etapas_widget)
        self._historial_etapas_widget.show()

    def _limpiar_widgets_op_embebidos(self):
        if self._oportunidad_productos_widget:
            self._oportunidad_productos_widget.setParent(None)
            self._oportunidad_productos_widget.deleteLater()
            self._oportunidad_productos_widget = None
        if self._historial_etapas_widget:
            self._historial_etapas_widget.setParent(None)
            self._historial_etapas_widget.deleteLater()
            self._historial_etapas_widget = None

    def _seleccionar_combo_estado_op(self, es_ganada):
        for i in range(self.op_combo_estado.count()):
            if self.op_combo_estado.itemData(i) == es_ganada:
                self.op_combo_estado.setCurrentIndex(i)
                return
        self.op_combo_estado.setCurrentIndex(0)

    def _guardar_oportunidad(self):
        es_ganada = self.op_combo_estado.currentData()
        datos = {
            "nombre": self.op_input_nombre.text(),
            "empresa_id": self.op_combo_empresa.currentData(),
            "contacto_id": self.op_combo_contacto.currentData(),
            "etapa_id": self.op_combo_etapa.currentData(),
            "monto_estimado": self.op_input_monto_estimado.text(),
            "moneda_id": self.op_combo_moneda.currentData(),
            "probabilidad_cierre": self.op_input_probabilidad.text(),
            "fecha_cierre_estimada": self.op_input_fecha_cierre_estimada.text(),
            "fecha_cierre_real": self.op_input_fecha_cierre_real.text(),
            "origen_id": self.op_combo_origen.currentData(),
            "propietario_id": self.op_combo_propietario.currentData(),
            "motivos_perdida_id": self.op_combo_motivo_perdida.currentData() if es_ganada == 0 else None,
            "notas_perdida": self.op_input_notas_perdida.text() if es_ganada == 0 else "",
            "descripcion": self.op_input_descripcion.text(),
            "es_ganada": es_ganada,
        }
        usuario_id = self._usuario_actual.usuario_id

        if self._oportunidad_editando:
            op, error = self._oportunidad_service.actualizar_oportunidad(
                self._oportunidad_editando.oportunidad_id, datos, usuario_id
            )
            titulo_error, titulo_exito, msg_exito = "Error al Actualizar", "Oportunidad Actualizada", "actualizada"
        else:
            op, error = self._oportunidad_service.crear_oportunidad(datos, usuario_id)
            titulo_error, titulo_exito, msg_exito = "Error al Crear", "Oportunidad Creada", "creada"

        if error:
            QMessageBox.critical(self, titulo_error, error)
            return

        if op and self._oportunidad_productos_widget:
            items = self._oportunidad_productos_widget.get_items()
            self._oportunidad_service.guardar_productos(op.oportunidad_id, items)

        if op:
            QMessageBox.information(
                self, titulo_exito,
                f"La oportunidad '{op.nombre}' ha sido {msg_exito} exitosamente."
            )
            self._mostrar_lista_oportunidades()

    def _limpiar_formulario_oportunidad(self):
        self.op_input_nombre.clear()
        self.op_combo_empresa.setCurrentIndex(0)
        self._cargar_combo_contactos_op(empresa_id=None)
        self.op_input_descripcion.clear()
        self.op_combo_etapa.setCurrentIndex(0)
        self.op_combo_propietario.setCurrentIndex(0)
        self.op_input_monto_estimado.clear()
        self.op_combo_moneda.setCurrentIndex(0)
        self.op_input_probabilidad.clear()
        self.op_combo_origen.setCurrentIndex(0)
        self.op_input_fecha_cierre_estimada.clear()
        self.op_combo_estado.setCurrentIndex(0)
        self.op_input_fecha_cierre_real.clear()
        self.op_combo_motivo_perdida.setCurrentIndex(0)
        self.op_input_notas_perdida.clear()
        self._actualizar_visibilidad_perdida()
        self.op_input_nombre.setFocus()

    # ==========================================
    # PRODUCTOS - LISTA
    # ==========================================

    def _create_producto_list(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "ventas", "producto_list.ui")
        self.lista_productos_widget = QWidget()
        uic.loadUi(ui_path, self.lista_productos_widget)

        self.btn_nuevo_producto = self.lista_productos_widget.btn_nuevo_producto
        self.tabla_productos = self.lista_productos_widget.tabla_productos
        self.stat_prod_total = self.lista_productos_widget.statValueTotal
        self.stat_prod_activos = self.lista_productos_widget.statValueActivos
        self.stat_prod_inactivos = self.lista_productos_widget.statValueInactivos

        self.btn_nuevo_producto.clicked.connect(self._mostrar_form_nuevo_producto)
        self.tabla_productos.doubleClicked.connect(self._editar_producto_seleccionado)

        h = self.tabla_productos.horizontalHeader()
        if h:
            h.setSectionResizeMode(QHeaderView.Stretch)
        v = self.tabla_productos.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(42)

        self.tabProductosLayout.addWidget(self.lista_productos_widget)

    def _cargar_tabla_productos(self):
        try:
            productos, error = self._producto_service.obtener_todos(limit=500)
            if error:
                QMessageBox.critical(self, "Error", error)
                return

            self._productos_cargados = productos or []
            total = len(self._productos_cargados)
            activos = sum(1 for p in self._productos_cargados if p.activo == 1)

            self.stat_prod_total.setText(str(total))
            self.stat_prod_activos.setText(str(activos))
            self.stat_prod_inactivos.setText(str(total - activos))

            self.tabla_productos.setRowCount(0)
            for prod in self._productos_cargados:
                r = self.tabla_productos.rowCount()
                self.tabla_productos.insertRow(r)
                self.tabla_productos.setItem(r, 0, QTableWidgetItem(str(prod.producto_id)))
                self.tabla_productos.setItem(r, 1, QTableWidgetItem(prod.codigo or ""))
                self.tabla_productos.setItem(r, 2, QTableWidgetItem(prod.nombre or ""))
                self.tabla_productos.setItem(r, 3, QTableWidgetItem(prod.categoria or "N/A"))
                precio_str = f"${prod.precio_unitario:,.2f}" if prod.precio_unitario is not None else "N/A"
                self.tabla_productos.setItem(r, 4, QTableWidgetItem(precio_str))
                self.tabla_productos.setItem(r, 5, QTableWidgetItem(prod.nombre_moneda or "N/A"))
                estado = "Activo" if prod.activo == 1 else "Inactivo"
                item_estado = QTableWidgetItem(estado)
                item_estado.setForeground(
                    QColor(34, 139, 34) if prod.activo == 1 else QColor(220, 53, 69)
                )
                self.tabla_productos.setItem(r, 6, item_estado)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los productos: {str(e)}")

    def _mostrar_lista_productos(self):
        self.form_productos_widget.hide()
        self.lista_productos_widget.show()
        self._cargar_tabla_productos()

    # ==========================================
    # PRODUCTOS - FORMULARIO
    # ==========================================

    def _create_producto_form(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "ventas", "producto_form.ui")
        self.form_productos_widget = QWidget()
        uic.loadUi(ui_path, self.form_productos_widget)

        self.prod_form_titulo = self.form_productos_widget.form_titulo
        self.prod_form_subtitulo = self.form_productos_widget.form_subtitulo
        self.prod_input_codigo = self.form_productos_widget.input_codigo
        self.prod_input_nombre = self.form_productos_widget.input_nombre
        self.prod_input_categoria = self.form_productos_widget.input_categoria
        self.prod_input_unidad_medida = self.form_productos_widget.input_unidad_medida
        self.prod_input_descripcion = self.form_productos_widget.input_descripcion
        self.prod_input_precio_unitario = self.form_productos_widget.input_precio_unitario
        self.prod_combo_moneda = self.form_productos_widget.combo_moneda
        self.prod_check_activo = self.form_productos_widget.check_activo
        self.prod_btn_guardar = self.form_productos_widget.btn_guardar
        self.prod_btn_limpiar = self.form_productos_widget.btn_limpiar
        self.prod_btn_cancelar = self.form_productos_widget.btn_cancelar

        self.prod_btn_guardar.clicked.connect(self._guardar_producto)
        self.prod_btn_limpiar.clicked.connect(self._limpiar_formulario_producto)
        self.prod_btn_cancelar.clicked.connect(self._mostrar_lista_productos)

        self._cargar_combos_producto()
        self.form_productos_widget.hide()
        self.tabProductosLayout.addWidget(self.form_productos_widget)

    def _cargar_combos_producto(self):
        conn = get_connection()
        self.prod_combo_moneda.clear()
        self.prod_combo_moneda.addItem("-- Seleccionar --", None)
        cursor = conn.execute("SELECT MonedaID, Nombre, Codigo FROM Monedas ORDER BY Codigo")
        for row in cursor.fetchall():
            self.prod_combo_moneda.addItem(f"{row['Codigo']} - {row['Nombre']}", row["MonedaID"])

    def _mostrar_form_nuevo_producto(self):
        self._producto_editando = None
        self.lista_productos_widget.hide()
        self.form_productos_widget.show()
        self.prod_form_titulo.setText("Nuevo Producto / Servicio")
        self.prod_form_subtitulo.setText(
            "Completa la informacion del nuevo producto. Los campos con * son obligatorios."
        )
        self.prod_btn_guardar.setText("Guardar Producto")
        self._limpiar_formulario_producto()

    def _editar_producto_seleccionado(self, index):
        row = index.row()
        id_item = self.tabla_productos.item(row, 0)
        if not id_item:
            return
        producto_id = int(id_item.text())
        prod = next((p for p in self._productos_cargados if p.producto_id == producto_id), None)
        if not prod:
            return

        self._producto_editando = prod
        self.lista_productos_widget.hide()
        self.form_productos_widget.show()
        self.prod_form_titulo.setText("Editar Producto / Servicio")
        self.prod_form_subtitulo.setText(f"Editando producto: {prod.nombre}.")
        self.prod_btn_guardar.setText("Actualizar Producto")

        self.prod_input_codigo.setText(prod.codigo or "")
        self.prod_input_nombre.setText(prod.nombre or "")
        self.prod_input_categoria.setText(prod.categoria or "")
        self.prod_input_unidad_medida.setText(prod.unidad_medida or "")
        self.prod_input_descripcion.setText(prod.descripcion or "")
        self.prod_input_precio_unitario.setText(
            str(prod.precio_unitario) if prod.precio_unitario is not None else ""
        )
        self.prod_check_activo.setChecked(prod.activo == 1)
        self._seleccionar_combo(self.prod_combo_moneda, prod.moneda_id)

    def _guardar_producto(self):
        datos = {
            "codigo": self.prod_input_codigo.text(),
            "nombre": self.prod_input_nombre.text(),
            "categoria": self.prod_input_categoria.text(),
            "unidad_medida": self.prod_input_unidad_medida.text(),
            "descripcion": self.prod_input_descripcion.text(),
            "precio_unitario": self.prod_input_precio_unitario.text(),
            "moneda_id": self.prod_combo_moneda.currentData(),
            "activo": 1 if self.prod_check_activo.isChecked() else 0,
        }

        if self._producto_editando:
            prod, error = self._producto_service.actualizar_producto(
                self._producto_editando.producto_id, datos
            )
            titulo_error, titulo_exito, msg = "Error al Actualizar", "Producto Actualizado", "actualizado"
        else:
            prod, error = self._producto_service.crear_producto(datos)
            titulo_error, titulo_exito, msg = "Error al Crear", "Producto Creado", "creado"

        if error:
            QMessageBox.critical(self, titulo_error, error)
        elif prod:
            QMessageBox.information(
                self, titulo_exito,
                f"El producto '{prod.nombre}' ha sido {msg} exitosamente."
            )
            self._mostrar_lista_productos()

    def _limpiar_formulario_producto(self):
        self.prod_input_codigo.clear()
        self.prod_input_nombre.clear()
        self.prod_input_categoria.clear()
        self.prod_input_unidad_medida.clear()
        self.prod_input_descripcion.clear()
        self.prod_input_precio_unitario.clear()
        self.prod_combo_moneda.setCurrentIndex(0)
        self.prod_check_activo.setChecked(True)
        self.prod_input_nombre.setFocus()

    # ==========================================
    # COTIZACIONES - LISTA
    # ==========================================

    def _create_cotizacion_list(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "ventas", "cotizacion_list.ui")
        self.lista_cotizaciones_widget = QWidget()
        uic.loadUi(ui_path, self.lista_cotizaciones_widget)

        self.btn_nueva_cotizacion = self.lista_cotizaciones_widget.btn_nueva_cotizacion
        self.tabla_cotizaciones = self.lista_cotizaciones_widget.tabla_cotizaciones
        self.stat_cot_total = self.lista_cotizaciones_widget.statValueTotal
        self.stat_cot_borradores = self.lista_cotizaciones_widget.statValueBorradores
        self.stat_cot_enviadas = self.lista_cotizaciones_widget.statValueEnviadas
        self.stat_cot_aceptadas = self.lista_cotizaciones_widget.statValueAceptadas

        self.btn_nueva_cotizacion.clicked.connect(self._mostrar_form_nueva_cotizacion)
        self.tabla_cotizaciones.doubleClicked.connect(self._editar_cotizacion_seleccionada)

        h = self.tabla_cotizaciones.horizontalHeader()
        if h:
            h.setSectionResizeMode(QHeaderView.Stretch)
        v = self.tabla_cotizaciones.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(42)

        self.tabCotizacionesLayout.addWidget(self.lista_cotizaciones_widget)

    def _cargar_tabla_cotizaciones(self):
        _COLOR_ESTADO = {
            "Borrador": QColor(160, 160, 160),
            "Enviada": QColor(100, 100, 220),
            "Aceptada": QColor(34, 139, 34),
            "Rechazada": QColor(220, 53, 69),
            "Vencida": QColor(200, 100, 0),
        }
        try:
            cots, error = self._cotizacion_service.obtener_todas(limit=200)
            if error:
                QMessageBox.critical(self, "Error", error)
                return

            self._cotizaciones_cargadas = cots or []
            total = len(self._cotizaciones_cargadas)
            borradores = sum(1 for c in self._cotizaciones_cargadas if c.estado == "Borrador")
            enviadas = sum(1 for c in self._cotizaciones_cargadas if c.estado == "Enviada")
            aceptadas = sum(1 for c in self._cotizaciones_cargadas if c.estado == "Aceptada")

            self.stat_cot_total.setText(str(total))
            self.stat_cot_borradores.setText(str(borradores))
            self.stat_cot_enviadas.setText(str(enviadas))
            self.stat_cot_aceptadas.setText(str(aceptadas))

            self.tabla_cotizaciones.setRowCount(0)
            for cot in self._cotizaciones_cargadas:
                r = self.tabla_cotizaciones.rowCount()
                self.tabla_cotizaciones.insertRow(r)
                self.tabla_cotizaciones.setItem(r, 0, QTableWidgetItem(str(cot.cotizacion_id)))
                self.tabla_cotizaciones.setItem(r, 1, QTableWidgetItem(cot.numero_cotizacion or ""))
                self.tabla_cotizaciones.setItem(r, 2, QTableWidgetItem(cot.nombre_oportunidad or "N/A"))
                self.tabla_cotizaciones.setItem(r, 3, QTableWidgetItem(cot.nombre_contacto or "N/A"))
                self.tabla_cotizaciones.setItem(r, 4, QTableWidgetItem(cot.fecha_emision or "N/A"))
                self.tabla_cotizaciones.setItem(r, 5, QTableWidgetItem(cot.fecha_vigencia or "N/A"))
                total_str = f"${cot.total:,.2f}" if cot.total is not None else "$0.00"
                self.tabla_cotizaciones.setItem(r, 6, QTableWidgetItem(total_str))
                item_estado = QTableWidgetItem(cot.estado or "")
                item_estado.setForeground(_COLOR_ESTADO.get(cot.estado, QColor(0, 0, 0)))
                self.tabla_cotizaciones.setItem(r, 7, item_estado)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las cotizaciones: {str(e)}")

    def _mostrar_lista_cotizaciones(self):
        self.form_cotizaciones_widget.hide()
        self.lista_cotizaciones_widget.show()
        self._limpiar_widget_cotizacion_embebido()
        self._cargar_tabla_cotizaciones()

    # ==========================================
    # COTIZACIONES - FORMULARIO
    # ==========================================

    def _create_cotizacion_form(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "ventas", "cotizacion_form.ui")
        self.form_cotizaciones_widget = QWidget()
        uic.loadUi(ui_path, self.form_cotizaciones_widget)

        self.cot_form_titulo = self.form_cotizaciones_widget.form_titulo
        self.cot_form_subtitulo = self.form_cotizaciones_widget.form_subtitulo
        self.cot_input_numero = self.form_cotizaciones_widget.input_numero_cotizacion
        self.cot_combo_oportunidad = self.form_cotizaciones_widget.combo_oportunidad_cot
        self.cot_combo_contacto = self.form_cotizaciones_widget.combo_contacto_cot
        self.cot_combo_moneda = self.form_cotizaciones_widget.combo_moneda_cot
        self.cot_input_fecha_emision = self.form_cotizaciones_widget.input_fecha_emision
        self.cot_input_fecha_vigencia = self.form_cotizaciones_widget.input_fecha_vigencia
        self.cot_combo_estado = self.form_cotizaciones_widget.combo_estado_cot
        self.cot_input_notas = self.form_cotizaciones_widget.input_notas_cot
        self.cot_input_terminos = self.form_cotizaciones_widget.input_terminos_cot
        self.cot_label_subtotal = self.form_cotizaciones_widget.labelSubtotalValor
        self.cot_label_iva = self.form_cotizaciones_widget.labelIVAValor
        self.cot_label_total = self.form_cotizaciones_widget.labelTotalValor
        self.cot_btn_guardar = self.form_cotizaciones_widget.btn_guardar
        self.cot_btn_limpiar = self.form_cotizaciones_widget.btn_limpiar
        self.cot_btn_cancelar = self.form_cotizaciones_widget.btn_cancelar

        self.cot_btn_guardar.clicked.connect(self._guardar_cotizacion)
        self.cot_btn_limpiar.clicked.connect(self._limpiar_formulario_cotizacion)
        self.cot_btn_cancelar.clicked.connect(self._mostrar_lista_cotizaciones)

        self._simbolo_moneda_actual = "$"
        self._subtotal_actual = 0
        self._iva_actual = 0
        self._total_actual = 0
        self._monedas_simbolos = {}
        self.cot_combo_moneda.currentIndexChanged.connect(self._on_moneda_cot_changed)

        self._cargar_combos_cotizacion()
        self.form_cotizaciones_widget.hide()
        self.tabCotizacionesLayout.addWidget(self.form_cotizaciones_widget)

    def _cargar_combos_cotizacion(self):
        conn = get_connection()

        self.cot_combo_oportunidad.clear()
        self.cot_combo_oportunidad.addItem("-- Seleccionar --", None)
        cursor = conn.execute("SELECT OportunidadID, Nombre FROM Oportunidades ORDER BY Nombre")
        for row in cursor.fetchall():
            self.cot_combo_oportunidad.addItem(row["Nombre"], row["OportunidadID"])

        self.cot_combo_contacto.clear()
        self.cot_combo_contacto.addItem("-- Seleccionar --", None)
        cursor = conn.execute(
            "SELECT ContactoID, (Nombre || ' ' || ApellidoPaterno) AS NC FROM Contactos WHERE Activo = 1 ORDER BY Nombre"
        )
        for row in cursor.fetchall():
            self.cot_combo_contacto.addItem(row["NC"], row["ContactoID"])

        self.cot_combo_moneda.clear()
        self.cot_combo_moneda.addItem("-- Seleccionar --", None)
        self._monedas_simbolos = {}
        cursor = conn.execute("SELECT MonedaID, Nombre, Codigo, Simbolo FROM Monedas ORDER BY Codigo")
        for row in cursor.fetchall():
            self.cot_combo_moneda.addItem(f"{row['Codigo']} - {row['Nombre']}", row["MonedaID"])
            self._monedas_simbolos[row["MonedaID"]] = row["Simbolo"] or "$"

        self.cot_combo_estado.clear()
        for estado in _ESTADOS_COTIZACION:
            self.cot_combo_estado.addItem(estado, estado)

    def _mostrar_form_nueva_cotizacion(self):
        self._cotizacion_editando = None
        self.lista_cotizaciones_widget.hide()
        self.form_cotizaciones_widget.show()
        self.cot_form_titulo.setText("Nueva Cotizacion")
        self.cot_form_subtitulo.setText(
            "Completa la informacion de la nueva cotizacion. Los campos con * son obligatorios."
        )
        self.cot_btn_guardar.setText("Guardar Cotizacion")
        self._cargar_combos_cotizacion()
        self._limpiar_formulario_cotizacion()
        self.cot_input_numero.setText(self._cotizacion_service.generar_numero())
        self._limpiar_widget_cotizacion_embebido()
        self._crear_widget_detalle_cot()

    def _editar_cotizacion_seleccionada(self, index):
        row = index.row()
        id_item = self.tabla_cotizaciones.item(row, 0)
        if not id_item:
            return
        cotizacion_id = int(id_item.text())
        cot = next((c for c in self._cotizaciones_cargadas if c.cotizacion_id == cotizacion_id), None)
        if not cot:
            return

        self._cotizacion_editando = cot
        self.lista_cotizaciones_widget.hide()
        self.form_cotizaciones_widget.show()
        self.cot_form_titulo.setText("Editar Cotizacion")
        self.cot_form_subtitulo.setText(f"Editando cotizacion: {cot.numero_cotizacion}.")
        self.cot_btn_guardar.setText("Actualizar Cotizacion")

        self._cargar_combos_cotizacion()

        self.cot_input_numero.setText(cot.numero_cotizacion or "")
        self.cot_input_fecha_emision.setText(cot.fecha_emision or "")
        self.cot_input_fecha_vigencia.setText(cot.fecha_vigencia or "")
        self.cot_input_notas.setText(cot.notas or "")
        self.cot_input_terminos.setText(cot.terminos_condiciones or "")
        self._seleccionar_combo(self.cot_combo_oportunidad, cot.oportunidad_id)
        self._seleccionar_combo(self.cot_combo_contacto, cot.contacto_id)
        self._seleccionar_combo(self.cot_combo_moneda, cot.moneda_id)
        for i in range(self.cot_combo_estado.count()):
            if self.cot_combo_estado.itemData(i) == cot.estado:
                self.cot_combo_estado.setCurrentIndex(i)
                break

        self._actualizar_totales_cotizacion(cot.subtotal or 0, cot.iva or 0, cot.total or 0)

        self._limpiar_widget_cotizacion_embebido()
        self._crear_widget_detalle_cot()
        if self._cotizacion_detalle_widget:
            self._cotizacion_detalle_widget.load_items(cot.cotizacion_id)

    def _crear_widget_detalle_cot(self):
        self._cotizacion_detalle_widget = CotizacionDetalleWidget(
            parent=self.form_cotizaciones_widget
        )
        self._cotizacion_detalle_widget.totales_changed.connect(self._actualizar_totales_cotizacion)
        layout = self.form_cotizaciones_widget.layout()
        if layout:
            layout.addWidget(self._cotizacion_detalle_widget)
        self._cotizacion_detalle_widget.show()

    def _limpiar_widget_cotizacion_embebido(self):
        if self._cotizacion_detalle_widget:
            self._cotizacion_detalle_widget.setParent(None)
            self._cotizacion_detalle_widget.deleteLater()
            self._cotizacion_detalle_widget = None

    def _on_moneda_cot_changed(self):
        moneda_id = self.cot_combo_moneda.currentData()
        self._simbolo_moneda_actual = self._monedas_simbolos.get(moneda_id, "$") if moneda_id else "$"
        self._actualizar_totales_cotizacion(self._subtotal_actual, self._iva_actual, self._total_actual)

    def _actualizar_totales_cotizacion(self, subtotal, iva, total):
        self._subtotal_actual = subtotal
        self._iva_actual = iva
        self._total_actual = total
        simbolo = self._simbolo_moneda_actual
        self.cot_label_subtotal.setText(f"{simbolo}{subtotal:,.2f}")
        self.cot_label_iva.setText(f"{simbolo}{iva:,.2f}")
        self.cot_label_total.setText(f"{simbolo}{total:,.2f}")

    def _guardar_cotizacion(self):
        items_detalle = (
            self._cotizacion_detalle_widget.get_items()
            if self._cotizacion_detalle_widget else []
        )
        datos = {
            "numero_cotizacion": self.cot_input_numero.text(),
            "oportunidad_id": self.cot_combo_oportunidad.currentData(),
            "contacto_id": self.cot_combo_contacto.currentData(),
            "moneda_id": self.cot_combo_moneda.currentData(),
            "fecha_emision": self.cot_input_fecha_emision.text(),
            "fecha_vigencia": self.cot_input_fecha_vigencia.text(),
            "estado": self.cot_combo_estado.currentData(),
            "notas": self.cot_input_notas.text(),
            "terminos_condiciones": self.cot_input_terminos.text(),
        }
        usuario_id = self._usuario_actual.usuario_id

        if self._cotizacion_editando:
            cot, error = self._cotizacion_service.actualizar_cotizacion(
                self._cotizacion_editando.cotizacion_id, datos, items_detalle
            )
            titulo_error, titulo_exito, msg = "Error al Actualizar", "Cotizacion Actualizada", "actualizada"
        else:
            cot, error = self._cotizacion_service.crear_cotizacion(datos, items_detalle, usuario_id)
            titulo_error, titulo_exito, msg = "Error al Crear", "Cotizacion Creada", "creada"

        if error:
            QMessageBox.critical(self, titulo_error, error)
        elif cot:
            QMessageBox.information(
                self, titulo_exito,
                f"La cotizacion '{cot.numero_cotizacion}' ha sido {msg} exitosamente."
            )
            self._mostrar_lista_cotizaciones()

    def _limpiar_formulario_cotizacion(self):
        self.cot_input_numero.clear()
        self.cot_combo_oportunidad.setCurrentIndex(0)
        self.cot_combo_contacto.setCurrentIndex(0)
        self.cot_combo_moneda.setCurrentIndex(0)
        self.cot_input_fecha_emision.setText(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.cot_input_fecha_vigencia.clear()
        self.cot_combo_estado.setCurrentIndex(0)
        self.cot_input_notas.clear()
        self.cot_input_terminos.clear()
        self._actualizar_totales_cotizacion(0, 0, 0)
        if self._cotizacion_detalle_widget:
            self._cotizacion_detalle_widget.limpiar()

    # ==========================================
    # UTILIDADES
    # ==========================================

    @staticmethod
    def _seleccionar_combo(combo, valor):
        if valor is None:
            combo.setCurrentIndex(0)
            return
        for i in range(combo.count()):
            if combo.itemData(i) == valor:
                combo.setCurrentIndex(i)
                return
        combo.setCurrentIndex(0)
