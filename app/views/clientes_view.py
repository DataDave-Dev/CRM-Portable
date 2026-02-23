# Vista de Clientes - gestiona Empresas y Contactos con tabs

import os
from PyQt5.QtWidgets import (
    QWidget, QMessageBox, QTableWidgetItem, QHeaderView, QListWidgetItem
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QDate
from PyQt5 import uic

_FECHA_NAC_NULA = QDate(1900, 1, 1)
from app.database.connection import get_connection
from app.services.empresa_service import EmpresaService
from app.services.contacto_service import ContactoService
from app.services.etiqueta_service import EtiquetaService
from app.utils.catalog_cache import CatalogCache
from app.views.notas_empresa_widget import NotasEmpresaWidget
from app.views.notas_contacto_widget import NotasContactoWidget

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "clientes", "clientes_view.ui")


class ClientesView(QWidget):

    def __init__(self, usuario_actual, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._usuario_actual = usuario_actual
        self._empresa_service = EmpresaService()
        self._contacto_service = ContactoService()
        self._etiqueta_service = EtiquetaService()
        self._empresa_editando = None
        self._contacto_editando = None
        self._empresas_cargadas = []
        self._contactos_cargados = []
        self._notas_empresa_widget = None
        self._notas_contacto_widget = None

        self._create_empresa_list()
        self._create_empresa_form()
        self._create_contacto_list()
        self._create_contacto_form()
        self._setup_tabs()

    # ==========================================
    # TABS
    # ==========================================

    def _setup_tabs(self):
        self.clientesTabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if index == 0:
            self._mostrar_lista_empresas()
        elif index == 1:
            self._mostrar_lista_contactos()

    def cargar_datos(self):
        index = self.clientesTabs.currentIndex()
        if index == 0:
            self._cargar_tabla_empresas()
        elif index == 1:
            self._cargar_tabla_contactos()

    # ==========================================
    # EMPRESAS - LISTA
    # ==========================================

    def _create_empresa_list(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "clientes", "empresa_list.ui")
        self.lista_empresas_widget = QWidget()
        uic.loadUi(ui_path, self.lista_empresas_widget)

        # referencias directas
        self.btn_nueva_empresa = self.lista_empresas_widget.btn_nueva_empresa
        self.tabla_empresas = self.lista_empresas_widget.tabla_empresas
        self.stat_emp_total = self.lista_empresas_widget.statValueTotal
        self.stat_emp_activas = self.lista_empresas_widget.statValueActivas
        self.stat_emp_inactivas = self.lista_empresas_widget.statValueInactivas

        # senales
        self.btn_nueva_empresa.clicked.connect(self._mostrar_form_nueva_empresa)
        self.tabla_empresas.doubleClicked.connect(self._editar_empresa_seleccionada)

        # configurar headers
        h_header = self.tabla_empresas.horizontalHeader()
        if h_header:
            h_header.setStretchLastSection(False)
            h_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
            h_header.setSectionResizeMode(1, QHeaderView.Stretch)           # Razon Social
            h_header.setSectionResizeMode(2, QHeaderView.Interactive)       # Nombre Comercial
            h_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Industria
            h_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Telefono
            h_header.setSectionResizeMode(5, QHeaderView.Interactive)       # Email
            h_header.setSectionResizeMode(6, QHeaderView.Interactive)       # Propietario
            h_header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Estado
            h_header.setMinimumSectionSize(60)
        v_header = self.tabla_empresas.verticalHeader()
        if v_header:
            v_header.setVisible(False)
            v_header.setDefaultSectionSize(42)

        self.tabEmpresasLayout.addWidget(self.lista_empresas_widget)

    def _cargar_tabla_empresas(self):
        try:
            # cargar con limite de 200 registros para mejorar rendimiento
            empresas, error = self._empresa_service.obtener_todas(limit=200)
            if error:
                QMessageBox.critical(self, "Error", error)
                return

            self._empresas_cargadas = empresas or []

            total = len(self._empresas_cargadas)
            activas = sum(1 for e in self._empresas_cargadas if e.activo == 1)
            inactivas = total - activas

            self.stat_emp_total.setText(str(total))
            self.stat_emp_activas.setText(str(activas))
            self.stat_emp_inactivas.setText(str(inactivas))

            self.tabla_empresas.setRowCount(0)

            for empresa in self._empresas_cargadas:
                row = self.tabla_empresas.rowCount()
                self.tabla_empresas.insertRow(row)

                self.tabla_empresas.setItem(row, 0, QTableWidgetItem(str(empresa.empresa_id)))
                self.tabla_empresas.setItem(row, 1, QTableWidgetItem(empresa.razon_social or ""))
                self.tabla_empresas.setItem(row, 2, QTableWidgetItem(empresa.nombre_comercial or ""))
                self.tabla_empresas.setItem(row, 3, QTableWidgetItem(empresa.nombre_industria or "N/A"))
                self.tabla_empresas.setItem(row, 4, QTableWidgetItem(empresa.telefono or "N/A"))
                self.tabla_empresas.setItem(row, 5, QTableWidgetItem(empresa.email or "N/A"))
                self.tabla_empresas.setItem(row, 6, QTableWidgetItem(empresa.nombre_propietario or "N/A"))

                estado = "Activo" if empresa.activo == 1 else "Inactivo"
                item_estado = QTableWidgetItem(estado)
                if empresa.activo == 1:
                    item_estado.setForeground(QColor(34, 139, 34))
                else:
                    item_estado.setForeground(QColor(220, 53, 69))
                self.tabla_empresas.setItem(row, 7, item_estado)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las empresas: {str(e)}")

    def _mostrar_lista_empresas(self):
        self.form_empresas_widget.hide()
        self.lista_empresas_widget.show()
        self._cargar_tabla_empresas()

    # ==========================================
    # EMPRESAS - FORMULARIO
    # ==========================================

    def _create_empresa_form(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "clientes", "empresa_form.ui")
        self.form_empresas_widget = QWidget()
        uic.loadUi(ui_path, self.form_empresas_widget)

        # referencias directas
        self.emp_form_titulo = self.form_empresas_widget.form_titulo
        self.emp_form_subtitulo = self.form_empresas_widget.form_subtitulo
        self.emp_input_razon_social = self.form_empresas_widget.input_razon_social
        self.emp_input_nombre_comercial = self.form_empresas_widget.input_nombre_comercial
        self.emp_input_rfc = self.form_empresas_widget.input_rfc
        self.emp_input_sitio_web = self.form_empresas_widget.input_sitio_web
        self.emp_input_descripcion = self.form_empresas_widget.input_descripcion
        self.emp_combo_industria = self.form_empresas_widget.combo_industria
        self.emp_combo_tamano = self.form_empresas_widget.combo_tamano
        self.emp_combo_origen = self.form_empresas_widget.combo_origen
        self.emp_combo_moneda = self.form_empresas_widget.combo_moneda
        self.emp_input_ingreso_anual = self.form_empresas_widget.input_ingreso_anual
        self.emp_input_num_empleados = self.form_empresas_widget.input_num_empleados
        self.emp_input_telefono = self.form_empresas_widget.input_telefono
        self.emp_input_email = self.form_empresas_widget.input_email
        self.emp_input_direccion = self.form_empresas_widget.input_direccion
        self.emp_combo_ciudad = self.form_empresas_widget.combo_ciudad
        self.emp_input_codigo_postal = self.form_empresas_widget.input_codigo_postal
        self.emp_combo_propietario = self.form_empresas_widget.combo_propietario
        self.emp_check_activo = self.form_empresas_widget.check_activo
        self.emp_btn_guardar = self.form_empresas_widget.btn_guardar
        self.emp_btn_limpiar = self.form_empresas_widget.btn_limpiar
        self.emp_btn_cancelar = self.form_empresas_widget.btn_cancelar
        self.emp_section_etiquetas = self.form_empresas_widget.sectionEtiquetas
        self.emp_combo_add_etiqueta = self.form_empresas_widget.combo_add_etiqueta
        self.emp_btn_add_etiqueta = self.form_empresas_widget.btn_add_etiqueta
        self.emp_lista_etiquetas = self.form_empresas_widget.lista_etiquetas_asignadas
        self.emp_btn_quitar_etiqueta = self.form_empresas_widget.btn_quitar_etiqueta

        # senales
        self.emp_btn_guardar.clicked.connect(self._guardar_empresa)
        self.emp_btn_limpiar.clicked.connect(self._limpiar_formulario_empresa)
        self.emp_btn_cancelar.clicked.connect(self._mostrar_lista_empresas)
        self.emp_btn_add_etiqueta.clicked.connect(self._agregar_etiqueta_empresa)
        self.emp_btn_quitar_etiqueta.clicked.connect(self._quitar_etiqueta_empresa)
        self.emp_section_etiquetas.hide()

        self._cargar_combos_empresa()
        self.form_empresas_widget.hide()
        self.tabEmpresasLayout.addWidget(self.form_empresas_widget)

    def _cargar_combos_empresa(self):
        # usar cache para mejorar rendimiento - evita consultas repetitivas a la BD

        # Industrias
        self.emp_combo_industria.clear()
        self.emp_combo_industria.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_industrias():
            self.emp_combo_industria.addItem(nombre, id_val)

        # Tamanos de empresa
        self.emp_combo_tamano.clear()
        self.emp_combo_tamano.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_tamanos_empresa():
            self.emp_combo_tamano.addItem(nombre, id_val)

        # Origenes de contacto
        self.emp_combo_origen.clear()
        self.emp_combo_origen.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_origenes_contacto():
            self.emp_combo_origen.addItem(nombre, id_val)

        # Monedas (requiere consulta especial para mostrar codigo)
        self.emp_combo_moneda.clear()
        self.emp_combo_moneda.addItem("-- Seleccionar --", None)
        conn = get_connection()
        cursor = conn.execute("SELECT MonedaID, Nombre, Codigo FROM Monedas ORDER BY Codigo")
        for row in cursor.fetchall():
            self.emp_combo_moneda.addItem(f"{row['Codigo']} - {row['Nombre']}", row["MonedaID"])

        # Ciudades (requiere consulta especial para mostrar estado)
        self.emp_combo_ciudad.clear()
        self.emp_combo_ciudad.addItem("-- Seleccionar --", None)
        cursor = conn.execute(
            """
            SELECT c.CiudadID, c.Nombre AS CiudadNombre, e.Nombre AS EstadoNombre
            FROM Ciudades c
            LEFT JOIN Estados e ON c.EstadoID = e.EstadoID
            ORDER BY e.Nombre, c.Nombre
            """
        )
        for row in cursor.fetchall():
            estado = row["EstadoNombre"] or ""
            display = f"{row['CiudadNombre']} - {estado}" if estado else row["CiudadNombre"]
            self.emp_combo_ciudad.addItem(display, row["CiudadID"])

        # Propietarios (usuarios activos)
        self.emp_combo_propietario.clear()
        self.emp_combo_propietario.addItem("-- Seleccionar --", None)
        for id_val, nombre_completo in CatalogCache.get_usuarios():
            self.emp_combo_propietario.addItem(nombre_completo, id_val)

    def _mostrar_form_nueva_empresa(self):
        self._empresa_editando = None
        self.lista_empresas_widget.hide()
        self.form_empresas_widget.show()
        self.emp_form_titulo.setText("Nueva Empresa")
        self.emp_form_subtitulo.setText(
            "Completa la informacion de la nueva empresa. "
            "Los campos marcados con * son obligatorios."
        )
        self.emp_btn_guardar.setText("Guardar Empresa")
        self._limpiar_formulario_empresa()

        # ocultar secciones no disponibles para nueva empresa
        self.emp_section_etiquetas.hide()
        self._ocultar_notas_empresa()

    def _editar_empresa_seleccionada(self, index):
        row = index.row()
        id_item = self.tabla_empresas.item(row, 0)
        if not id_item:
            return

        empresa_id = int(id_item.text())
        empresa = next((e for e in self._empresas_cargadas if e.empresa_id == empresa_id), None)
        if not empresa:
            return

        self._empresa_editando = empresa
        self.lista_empresas_widget.hide()
        self.form_empresas_widget.show()
        self.emp_form_titulo.setText("Editar Empresa")
        self.emp_form_subtitulo.setText(
            f"Editando empresa: {empresa.razon_social}."
        )
        self.emp_btn_guardar.setText("Actualizar Empresa")

        # poblar formulario
        self.emp_input_razon_social.setText(empresa.razon_social or "")
        self.emp_input_nombre_comercial.setText(empresa.nombre_comercial or "")
        self.emp_input_rfc.setText(empresa.rfc or "")
        self.emp_input_sitio_web.setText(empresa.sitio_web or "")
        self.emp_input_descripcion.setText(empresa.descripcion or "")
        self.emp_input_ingreso_anual.setText(
            str(empresa.ingreso_anual_estimado) if empresa.ingreso_anual_estimado is not None else ""
        )
        self.emp_input_num_empleados.setText(
            str(empresa.num_empleados) if empresa.num_empleados is not None else ""
        )
        self.emp_input_telefono.setText(empresa.telefono or "")
        self.emp_input_email.setText(empresa.email or "")
        self.emp_input_direccion.setText(empresa.direccion or "")
        self.emp_input_codigo_postal.setText(empresa.codigo_postal or "")
        self.emp_check_activo.setChecked(empresa.activo == 1)

        # seleccionar combos
        self._seleccionar_combo(self.emp_combo_industria, empresa.industria_id)
        self._seleccionar_combo(self.emp_combo_tamano, empresa.tamano_id)
        self._seleccionar_combo(self.emp_combo_origen, empresa.origen_id)
        self._seleccionar_combo(self.emp_combo_moneda, empresa.moneda_id)
        self._seleccionar_combo(self.emp_combo_ciudad, empresa.ciudad_id)
        self._seleccionar_combo(self.emp_combo_propietario, empresa.propietario_id)

        # cargar etiquetas de la empresa
        self._cargar_combo_etiquetas_empresa()
        self._cargar_etiquetas_empresa(empresa.empresa_id)
        self.emp_section_etiquetas.show()

        # crear o actualizar widget de notas para empresa existente
        self._mostrar_notas_empresa(empresa.empresa_id)

    def _guardar_empresa(self):
        datos = {
            "razon_social": self.emp_input_razon_social.text(),
            "nombre_comercial": self.emp_input_nombre_comercial.text(),
            "rfc": self.emp_input_rfc.text(),
            "sitio_web": self.emp_input_sitio_web.text(),
            "descripcion": self.emp_input_descripcion.text(),
            "industria_id": self.emp_combo_industria.currentData(),
            "tamano_id": self.emp_combo_tamano.currentData(),
            "origen_id": self.emp_combo_origen.currentData(),
            "moneda_id": self.emp_combo_moneda.currentData(),
            "ingreso_anual_estimado": self.emp_input_ingreso_anual.text(),
            "num_empleados": self.emp_input_num_empleados.text(),
            "telefono": self.emp_input_telefono.text(),
            "email": self.emp_input_email.text(),
            "direccion": self.emp_input_direccion.text(),
            "ciudad_id": self.emp_combo_ciudad.currentData(),
            "codigo_postal": self.emp_input_codigo_postal.text(),
            "propietario_id": self.emp_combo_propietario.currentData(),
            "activo": 1 if self.emp_check_activo.isChecked() else 0,
        }

        usuario_id = self._usuario_actual.usuario_id

        if self._empresa_editando:
            empresa, error = self._empresa_service.actualizar_empresa(
                self._empresa_editando.empresa_id, datos, usuario_id
            )
            titulo_error = "Error al Actualizar"
            titulo_exito = "Empresa Actualizada"
            msg_exito = "ha sido actualizada exitosamente."
        else:
            empresa, error = self._empresa_service.crear_empresa(datos, usuario_id)
            titulo_error = "Error al Crear"
            titulo_exito = "Empresa Creada"
            msg_exito = "ha sido creada exitosamente."

        if error:
            QMessageBox.critical(self, titulo_error, error)
        elif empresa:
            QMessageBox.information(
                self, titulo_exito,
                f"La empresa {empresa.razon_social} {msg_exito}"
            )
            self._mostrar_lista_empresas()

    def _limpiar_formulario_empresa(self):
        self.emp_input_razon_social.clear()
        self.emp_input_nombre_comercial.clear()
        self.emp_input_rfc.clear()
        self.emp_input_sitio_web.clear()
        self.emp_input_descripcion.clear()
        self.emp_combo_industria.setCurrentIndex(0)
        self.emp_combo_tamano.setCurrentIndex(0)
        self.emp_combo_origen.setCurrentIndex(0)
        self.emp_combo_moneda.setCurrentIndex(0)
        self.emp_input_ingreso_anual.clear()
        self.emp_input_num_empleados.clear()
        self.emp_input_telefono.clear()
        self.emp_input_email.clear()
        self.emp_input_direccion.clear()
        self.emp_combo_ciudad.setCurrentIndex(0)
        self.emp_input_codigo_postal.clear()
        self.emp_combo_propietario.setCurrentIndex(0)
        self.emp_check_activo.setChecked(True)
        self.emp_input_razon_social.setFocus()

    def _mostrar_notas_empresa(self, empresa_id):
        # crear widget de notas si no existe o recrearlo con nuevo empresa_id
        if self._notas_empresa_widget:
            self._notas_empresa_widget.setParent(None)
            self._notas_empresa_widget.deleteLater()

        self._notas_empresa_widget = NotasEmpresaWidget(
            empresa_id, self._usuario_actual.usuario_id, self.form_empresas_widget
        )
        # añadir al layout del formulario (asumiendo que hay un layout vertical)
        layout = self.form_empresas_widget.layout()
        if layout:
            layout.addWidget(self._notas_empresa_widget)
        self._notas_empresa_widget.show()

    def _ocultar_notas_empresa(self):
        if self._notas_empresa_widget:
            self._notas_empresa_widget.hide()

    # ---- Etiquetas de empresa ----

    def _cargar_combo_etiquetas_empresa(self):
        self.emp_combo_add_etiqueta.clear()
        self.emp_combo_add_etiqueta.addItem("-- Seleccionar etiqueta --", None)
        for etq_id, nombre in CatalogCache.get_etiquetas():
            self.emp_combo_add_etiqueta.addItem(nombre, etq_id)

    def _cargar_etiquetas_empresa(self, empresa_id):
        self.emp_lista_etiquetas.clear()
        rows, _ = self._etiqueta_service.get_etiquetas_de_empresa(empresa_id)
        for row in (rows or []):
            item = QListWidgetItem(row["Nombre"])
            item.setData(256, row["EtiquetaID"])
            if row["Color"]:
                item.setForeground(QColor(row["Color"]))
            self.emp_lista_etiquetas.addItem(item)

    def _agregar_etiqueta_empresa(self):
        if not self._empresa_editando:
            return
        etiqueta_id = self.emp_combo_add_etiqueta.currentData()
        if not etiqueta_id:
            QMessageBox.warning(self, "Aviso", "Selecciona una etiqueta para agregar.")
            return
        ok, error = self._etiqueta_service.asignar_empresa(
            etiqueta_id,
            self._empresa_editando.empresa_id,
            self._usuario_actual.usuario_id,
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_etiquetas_empresa(self._empresa_editando.empresa_id)

    def _quitar_etiqueta_empresa(self):
        if not self._empresa_editando:
            return
        item = self.emp_lista_etiquetas.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecciona una etiqueta de la lista para quitarla.")
            return
        etiqueta_id = item.data(256)
        ok, error = self._etiqueta_service.quitar_empresa(
            etiqueta_id,
            self._empresa_editando.empresa_id,
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_etiquetas_empresa(self._empresa_editando.empresa_id)

    # ==========================================
    # CONTACTOS - LISTA
    # ==========================================

    def _create_contacto_list(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "clientes", "contacto_list.ui")
        self.lista_contactos_widget = QWidget()
        uic.loadUi(ui_path, self.lista_contactos_widget)

        # referencias directas
        self.btn_nuevo_contacto = self.lista_contactos_widget.btn_nuevo_contacto
        self.tabla_contactos = self.lista_contactos_widget.tabla_contactos
        self.stat_ct_total = self.lista_contactos_widget.statValueTotal
        self.stat_ct_activos = self.lista_contactos_widget.statValueActivos
        self.stat_ct_inactivos = self.lista_contactos_widget.statValueInactivos

        # senales
        self.btn_nuevo_contacto.clicked.connect(self._mostrar_form_nuevo_contacto)
        self.tabla_contactos.doubleClicked.connect(self._editar_contacto_seleccionado)

        # configurar headers
        h_header = self.tabla_contactos.horizontalHeader()
        if h_header:
            h_header.setStretchLastSection(False)
            h_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
            h_header.setSectionResizeMode(1, QHeaderView.Stretch)           # Nombre Completo
            h_header.setSectionResizeMode(2, QHeaderView.Interactive)       # Email
            h_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Telefono Celular
            h_header.setSectionResizeMode(4, QHeaderView.Interactive)       # Puesto
            h_header.setSectionResizeMode(5, QHeaderView.Interactive)       # Empresa
            h_header.setSectionResizeMode(6, QHeaderView.Interactive)       # Propietario
            h_header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Estado
            h_header.setMinimumSectionSize(60)
        v_header = self.tabla_contactos.verticalHeader()
        if v_header:
            v_header.setVisible(False)
            v_header.setDefaultSectionSize(42)

        self.tabContactosLayout.addWidget(self.lista_contactos_widget)

    def _cargar_tabla_contactos(self):
        try:
            # cargar con limite de 200 registros para mejorar rendimiento
            contactos, error = self._contacto_service.obtener_todos(limit=200)
            if error:
                QMessageBox.critical(self, "Error", error)
                return

            self._contactos_cargados = contactos or []

            total = len(self._contactos_cargados)
            activos = sum(1 for c in self._contactos_cargados if c.activo == 1)
            inactivos = total - activos

            self.stat_ct_total.setText(str(total))
            self.stat_ct_activos.setText(str(activos))
            self.stat_ct_inactivos.setText(str(inactivos))

            self.tabla_contactos.setRowCount(0)

            for contacto in self._contactos_cargados:
                row = self.tabla_contactos.rowCount()
                self.tabla_contactos.insertRow(row)

                self.tabla_contactos.setItem(row, 0, QTableWidgetItem(str(contacto.contacto_id)))

                nombre_completo = f"{contacto.nombre} {contacto.apellido_paterno}"
                if contacto.apellido_materno:
                    nombre_completo += f" {contacto.apellido_materno}"
                self.tabla_contactos.setItem(row, 1, QTableWidgetItem(nombre_completo))

                self.tabla_contactos.setItem(row, 2, QTableWidgetItem(contacto.email or "N/A"))
                self.tabla_contactos.setItem(row, 3, QTableWidgetItem(contacto.telefono_celular or "N/A"))
                self.tabla_contactos.setItem(row, 4, QTableWidgetItem(contacto.puesto or "N/A"))
                self.tabla_contactos.setItem(row, 5, QTableWidgetItem(contacto.nombre_empresa or "N/A"))
                self.tabla_contactos.setItem(row, 6, QTableWidgetItem(contacto.nombre_propietario or "N/A"))

                estado = "Activo" if contacto.activo == 1 else "Inactivo"
                item_estado = QTableWidgetItem(estado)
                if contacto.activo == 1:
                    item_estado.setForeground(QColor(34, 139, 34))
                else:
                    item_estado.setForeground(QColor(220, 53, 69))
                self.tabla_contactos.setItem(row, 7, item_estado)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los contactos: {str(e)}")

    def _mostrar_lista_contactos(self):
        self.form_contactos_widget.hide()
        self.lista_contactos_widget.show()
        self._cargar_tabla_contactos()

    # ==========================================
    # CONTACTOS - FORMULARIO
    # ==========================================

    def _create_contacto_form(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "clientes", "contacto_form.ui")
        self.form_contactos_widget = QWidget()
        uic.loadUi(ui_path, self.form_contactos_widget)

        # referencias directas
        self.ct_form_titulo = self.form_contactos_widget.form_titulo
        self.ct_form_subtitulo = self.form_contactos_widget.form_subtitulo
        self.ct_input_nombre = self.form_contactos_widget.input_nombre
        self.ct_input_apellido_paterno = self.form_contactos_widget.input_apellido_paterno
        self.ct_input_apellido_materno = self.form_contactos_widget.input_apellido_materno
        self.ct_input_fecha_nacimiento = self.form_contactos_widget.input_fecha_nacimiento
        self.ct_input_email = self.form_contactos_widget.input_email
        self.ct_input_email_secundario = self.form_contactos_widget.input_email_secundario
        self.ct_input_telefono_oficina = self.form_contactos_widget.input_telefono_oficina
        self.ct_input_telefono_celular = self.form_contactos_widget.input_telefono_celular
        self.ct_input_linkedin_url = self.form_contactos_widget.input_linkedin_url
        self.ct_combo_empresa = self.form_contactos_widget.combo_empresa
        self.ct_input_puesto = self.form_contactos_widget.input_puesto
        self.ct_input_departamento = self.form_contactos_widget.input_departamento
        self.ct_input_direccion = self.form_contactos_widget.input_direccion
        self.ct_combo_ciudad = self.form_contactos_widget.combo_ciudad
        self.ct_input_codigo_postal = self.form_contactos_widget.input_codigo_postal
        self.ct_combo_origen = self.form_contactos_widget.combo_origen
        self.ct_combo_propietario = self.form_contactos_widget.combo_propietario
        self.ct_check_contacto_principal = self.form_contactos_widget.check_contacto_principal
        self.ct_check_no_contactar = self.form_contactos_widget.check_no_contactar
        self.ct_check_activo = self.form_contactos_widget.check_activo
        self.ct_btn_guardar = self.form_contactos_widget.btn_guardar
        self.ct_btn_limpiar = self.form_contactos_widget.btn_limpiar
        self.ct_btn_cancelar = self.form_contactos_widget.btn_cancelar
        self.ct_section_etiquetas = self.form_contactos_widget.sectionEtiquetas
        self.ct_combo_add_etiqueta = self.form_contactos_widget.combo_add_etiqueta
        self.ct_btn_add_etiqueta = self.form_contactos_widget.btn_add_etiqueta
        self.ct_lista_etiquetas = self.form_contactos_widget.lista_etiquetas_asignadas
        self.ct_btn_quitar_etiqueta = self.form_contactos_widget.btn_quitar_etiqueta

        # senales
        self.ct_btn_guardar.clicked.connect(self._guardar_contacto)
        self.ct_btn_limpiar.clicked.connect(self._limpiar_formulario_contacto)
        self.ct_btn_cancelar.clicked.connect(self._mostrar_lista_contactos)
        self.ct_btn_add_etiqueta.clicked.connect(self._agregar_etiqueta_contacto)
        self.ct_btn_quitar_etiqueta.clicked.connect(self._quitar_etiqueta_contacto)
        self.ct_section_etiquetas.hide()

        self._cargar_combos_contacto()
        self.form_contactos_widget.hide()
        self.tabContactosLayout.addWidget(self.form_contactos_widget)

    def _cargar_combos_contacto(self):
        # usar cache para mejorar rendimiento - evita consultas repetitivas a la BD
        conn = get_connection()

        # Empresas activas (no cacheado - datos dinamicos de usuario)
        self.ct_combo_empresa.clear()
        self.ct_combo_empresa.addItem("-- Seleccionar --", None)
        cursor = conn.execute(
            "SELECT EmpresaID, RazonSocial FROM Empresas WHERE Activo = 1 ORDER BY RazonSocial"
        )
        for row in cursor.fetchall():
            self.ct_combo_empresa.addItem(row["RazonSocial"], row["EmpresaID"])

        # Ciudades (requiere consulta especial para mostrar estado)
        self.ct_combo_ciudad.clear()
        self.ct_combo_ciudad.addItem("-- Seleccionar --", None)
        cursor = conn.execute(
            """
            SELECT c.CiudadID, c.Nombre AS CiudadNombre, e.Nombre AS EstadoNombre
            FROM Ciudades c
            LEFT JOIN Estados e ON c.EstadoID = e.EstadoID
            ORDER BY e.Nombre, c.Nombre
            """
        )
        for row in cursor.fetchall():
            estado = row["EstadoNombre"] or ""
            display = f"{row['CiudadNombre']} - {estado}" if estado else row["CiudadNombre"]
            self.ct_combo_ciudad.addItem(display, row["CiudadID"])

        # Origenes de contacto
        self.ct_combo_origen.clear()
        self.ct_combo_origen.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_origenes_contacto():
            self.ct_combo_origen.addItem(nombre, id_val)

        # Propietarios (usuarios activos)
        self.ct_combo_propietario.clear()
        self.ct_combo_propietario.addItem("-- Seleccionar --", None)
        for id_val, nombre_completo in CatalogCache.get_usuarios():
            self.ct_combo_propietario.addItem(nombre_completo, id_val)

    def _mostrar_form_nuevo_contacto(self):
        self._contacto_editando = None
        self.lista_contactos_widget.hide()
        self.form_contactos_widget.show()
        self.ct_form_titulo.setText("Nuevo Contacto")
        self.ct_form_subtitulo.setText(
            "Completa la informacion del nuevo contacto. "
            "Los campos marcados con * son obligatorios."
        )
        self.ct_btn_guardar.setText("Guardar Contacto")
        # recargar combo de empresas por si se agrego una nueva
        self._cargar_combos_contacto()
        self._limpiar_formulario_contacto()

        # ocultar secciones no disponibles para nuevo contacto
        self.ct_section_etiquetas.hide()
        self._ocultar_notas_contacto()

    def _editar_contacto_seleccionado(self, index):
        row = index.row()
        id_item = self.tabla_contactos.item(row, 0)
        if not id_item:
            return

        contacto_id = int(id_item.text())
        contacto = next(
            (c for c in self._contactos_cargados if c.contacto_id == contacto_id), None
        )
        if not contacto:
            return

        self._contacto_editando = contacto
        self.lista_contactos_widget.hide()
        self.form_contactos_widget.show()
        self.ct_form_titulo.setText("Editar Contacto")
        nombre = f"{contacto.nombre} {contacto.apellido_paterno}"
        self.ct_form_subtitulo.setText(f"Editando contacto: {nombre}.")
        self.ct_btn_guardar.setText("Actualizar Contacto")

        # recargar combos
        self._cargar_combos_contacto()

        # poblar formulario
        self.ct_input_nombre.setText(contacto.nombre or "")
        self.ct_input_apellido_paterno.setText(contacto.apellido_paterno or "")
        self.ct_input_apellido_materno.setText(contacto.apellido_materno or "")
        _fecha = QDate.fromString(contacto.fecha_nacimiento, "yyyy-MM-dd") if contacto.fecha_nacimiento else _FECHA_NAC_NULA
        self.ct_input_fecha_nacimiento.setDate(_fecha if _fecha.isValid() else _FECHA_NAC_NULA)
        self.ct_input_email.setText(contacto.email or "")
        self.ct_input_email_secundario.setText(contacto.email_secundario or "")
        self.ct_input_telefono_oficina.setText(contacto.telefono_oficina or "")
        self.ct_input_telefono_celular.setText(contacto.telefono_celular or "")
        self.ct_input_linkedin_url.setText(contacto.linkedin_url or "")
        self.ct_input_puesto.setText(contacto.puesto or "")
        self.ct_input_departamento.setText(contacto.departamento or "")
        self.ct_input_direccion.setText(contacto.direccion or "")
        self.ct_input_codigo_postal.setText(contacto.codigo_postal or "")
        self.ct_check_contacto_principal.setChecked(contacto.es_contacto_principal == 1)
        self.ct_check_no_contactar.setChecked(contacto.no_contactar == 1)
        self.ct_check_activo.setChecked(contacto.activo == 1)

        # seleccionar combos
        self._seleccionar_combo(self.ct_combo_empresa, contacto.empresa_id)
        self._seleccionar_combo(self.ct_combo_ciudad, contacto.ciudad_id)
        self._seleccionar_combo(self.ct_combo_origen, contacto.origen_id)
        self._seleccionar_combo(self.ct_combo_propietario, contacto.propietario_id)

        # cargar etiquetas del contacto
        self._cargar_combo_etiquetas_contacto()
        self._cargar_etiquetas_contacto(contacto.contacto_id)
        self.ct_section_etiquetas.show()

        # crear o actualizar widget de notas para contacto existente
        self._mostrar_notas_contacto(contacto.contacto_id)

    def _guardar_contacto(self):
        datos = {
            "nombre": self.ct_input_nombre.text(),
            "apellido_paterno": self.ct_input_apellido_paterno.text(),
            "apellido_materno": self.ct_input_apellido_materno.text(),
            "fecha_nacimiento": "" if self.ct_input_fecha_nacimiento.date() == _FECHA_NAC_NULA else self.ct_input_fecha_nacimiento.date().toString("yyyy-MM-dd"),
            "email": self.ct_input_email.text(),
            "email_secundario": self.ct_input_email_secundario.text(),
            "telefono_oficina": self.ct_input_telefono_oficina.text(),
            "telefono_celular": self.ct_input_telefono_celular.text(),
            "linkedin_url": self.ct_input_linkedin_url.text(),
            "empresa_id": self.ct_combo_empresa.currentData(),
            "puesto": self.ct_input_puesto.text(),
            "departamento": self.ct_input_departamento.text(),
            "direccion": self.ct_input_direccion.text(),
            "ciudad_id": self.ct_combo_ciudad.currentData(),
            "codigo_postal": self.ct_input_codigo_postal.text(),
            "origen_id": self.ct_combo_origen.currentData(),
            "propietario_id": self.ct_combo_propietario.currentData(),
            "es_contacto_principal": 1 if self.ct_check_contacto_principal.isChecked() else 0,
            "no_contactar": 1 if self.ct_check_no_contactar.isChecked() else 0,
            "activo": 1 if self.ct_check_activo.isChecked() else 0,
        }

        usuario_id = self._usuario_actual.usuario_id

        if self._contacto_editando:
            contacto, error = self._contacto_service.actualizar_contacto(
                self._contacto_editando.contacto_id, datos, usuario_id
            )
            titulo_error = "Error al Actualizar"
            titulo_exito = "Contacto Actualizado"
            msg_exito = "ha sido actualizado exitosamente."
        else:
            contacto, error = self._contacto_service.crear_contacto(datos, usuario_id)
            titulo_error = "Error al Crear"
            titulo_exito = "Contacto Creado"
            msg_exito = "ha sido creado exitosamente."

        if error:
            QMessageBox.critical(self, titulo_error, error)
        elif contacto:
            nombre = f"{contacto.nombre} {contacto.apellido_paterno}"
            QMessageBox.information(
                self, titulo_exito,
                f"El contacto {nombre} {msg_exito}"
            )
            self._mostrar_lista_contactos()

    def _limpiar_formulario_contacto(self):
        self.ct_input_nombre.clear()
        self.ct_input_apellido_paterno.clear()
        self.ct_input_apellido_materno.clear()
        self.ct_input_fecha_nacimiento.setDate(QDate.currentDate())
        self.ct_input_email.clear()
        self.ct_input_email_secundario.clear()
        self.ct_input_telefono_oficina.clear()
        self.ct_input_telefono_celular.clear()
        self.ct_input_linkedin_url.clear()
        self.ct_combo_empresa.setCurrentIndex(0)
        self.ct_input_puesto.clear()
        self.ct_input_departamento.clear()
        self.ct_input_direccion.clear()
        self.ct_combo_ciudad.setCurrentIndex(0)
        self.ct_input_codigo_postal.clear()
        self.ct_combo_origen.setCurrentIndex(0)
        self.ct_combo_propietario.setCurrentIndex(0)
        self.ct_check_contacto_principal.setChecked(False)
        self.ct_check_no_contactar.setChecked(False)
        self.ct_check_activo.setChecked(True)
        self.ct_input_nombre.setFocus()

    def _mostrar_notas_contacto(self, contacto_id):
        # crear widget de notas si no existe o recrearlo con nuevo contacto_id
        if self._notas_contacto_widget:
            self._notas_contacto_widget.setParent(None)
            self._notas_contacto_widget.deleteLater()

        self._notas_contacto_widget = NotasContactoWidget(
            contacto_id, self._usuario_actual.usuario_id, self.form_contactos_widget
        )
        # añadir al layout del formulario (asumiendo que hay un layout vertical)
        layout = self.form_contactos_widget.layout()
        if layout:
            layout.addWidget(self._notas_contacto_widget)
        self._notas_contacto_widget.show()

    def _ocultar_notas_contacto(self):
        if self._notas_contacto_widget:
            self._notas_contacto_widget.hide()

    # ---- Etiquetas de contacto ----

    def _cargar_combo_etiquetas_contacto(self):
        self.ct_combo_add_etiqueta.clear()
        self.ct_combo_add_etiqueta.addItem("-- Seleccionar etiqueta --", None)
        for etq_id, nombre in CatalogCache.get_etiquetas():
            self.ct_combo_add_etiqueta.addItem(nombre, etq_id)

    def _cargar_etiquetas_contacto(self, contacto_id):
        self.ct_lista_etiquetas.clear()
        rows, _ = self._etiqueta_service.get_etiquetas_de_contacto(contacto_id)
        for row in (rows or []):
            item = QListWidgetItem(row["Nombre"])
            item.setData(256, row["EtiquetaID"])
            if row["Color"]:
                item.setForeground(QColor(row["Color"]))
            self.ct_lista_etiquetas.addItem(item)

    def _agregar_etiqueta_contacto(self):
        if not self._contacto_editando:
            return
        etiqueta_id = self.ct_combo_add_etiqueta.currentData()
        if not etiqueta_id:
            QMessageBox.warning(self, "Aviso", "Selecciona una etiqueta para agregar.")
            return
        ok, error = self._etiqueta_service.asignar_contacto(
            etiqueta_id,
            self._contacto_editando.contacto_id,
            self._usuario_actual.usuario_id,
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_etiquetas_contacto(self._contacto_editando.contacto_id)

    def _quitar_etiqueta_contacto(self):
        if not self._contacto_editando:
            return
        item = self.ct_lista_etiquetas.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecciona una etiqueta de la lista para quitarla.")
            return
        etiqueta_id = item.data(256)
        ok, error = self._etiqueta_service.quitar_contacto(
            etiqueta_id,
            self._contacto_editando.contacto_id,
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_etiquetas_contacto(self._contacto_editando.contacto_id)

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
