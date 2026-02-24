# Vista de Segmentacion - gestiona Etiquetas y Segmentos

import os
from PyQt5.QtWidgets import (
    QWidget, QMessageBox, QTableWidgetItem, QHeaderView, QListWidgetItem
)
from PyQt5.QtGui import QColor
from PyQt5 import uic

from app.database.connection import get_connection
from app.services.etiqueta_service import EtiquetaService
from app.services.segmento_service import SegmentoService

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "segmentacion", "segmentacion_view.ui")


class SegmentacionView(QWidget):

    def __init__(self, usuario_actual, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._usuario_actual = usuario_actual
        self._etiqueta_service = EtiquetaService()
        self._segmento_service = SegmentoService()

        self._etiqueta_editando = None
        self._segmento_editando = None
        self._etiquetas_cargadas = []
        self._segmentos_cargados = []

        self._create_etiqueta_list()
        self._create_etiqueta_form()
        self._create_segmento_list()
        self._create_segmento_form()
        self._create_segmento_members()
        self._setup_tabs()

    # ==========================================
    # TABS
    # ==========================================

    def _setup_tabs(self):
        self.segmentacionTabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if index == 0:
            self._mostrar_lista_etiquetas()
        elif index == 1:
            self._mostrar_lista_segmentos()

    def cargar_datos(self):
        index = self.segmentacionTabs.currentIndex()
        if index == 0:
            self._cargar_tabla_etiquetas()
        elif index == 1:
            self._cargar_tabla_segmentos()

    # ==========================================
    # ETIQUETAS - LISTA
    # ==========================================

    def _create_etiqueta_list(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "segmentacion", "etiqueta_list.ui")
        self.lista_etiquetas_widget = QWidget()
        uic.loadUi(ui_path, self.lista_etiquetas_widget)

        self.btn_nueva_etiqueta = self.lista_etiquetas_widget.btn_nueva_etiqueta
        self.tabla_etiquetas = self.lista_etiquetas_widget.tabla_etiquetas
        self.stat_etq_total = self.lista_etiquetas_widget.statValueTotal
        self.stat_etq_contactos = self.lista_etiquetas_widget.statValueContactos
        self.stat_etq_empresas = self.lista_etiquetas_widget.statValueEmpresas

        self.btn_nueva_etiqueta.clicked.connect(self._mostrar_form_nueva_etiqueta)
        self.tabla_etiquetas.doubleClicked.connect(self._editar_etiqueta_seleccionada)

        h = self.tabla_etiquetas.horizontalHeader()
        if h:
            h.setStretchLastSection(False)
            h.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
            h.setSectionResizeMode(1, QHeaderView.Stretch)           # Nombre
            h.setSectionResizeMode(2, QHeaderView.Interactive)       # Categoria
            h.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Color
            h.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Contactos
            h.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Empresas
            h.setMinimumSectionSize(60)
        v = self.tabla_etiquetas.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(42)

        self.tabEtiquetasLayout.addWidget(self.lista_etiquetas_widget)

    def _cargar_tabla_etiquetas(self):
        try:
            etiquetas, error = self._etiqueta_service.obtener_todas()
            if error:
                QMessageBox.critical(self, "Error", error)
                return

            self._etiquetas_cargadas = etiquetas or []
            total = len(self._etiquetas_cargadas)
            total_contactos = sum(e.num_contactos for e in self._etiquetas_cargadas)
            total_empresas = sum(e.num_empresas for e in self._etiquetas_cargadas)

            self.stat_etq_total.setText(str(total))
            self.stat_etq_contactos.setText(str(total_contactos))
            self.stat_etq_empresas.setText(str(total_empresas))

            self.tabla_etiquetas.setRowCount(0)
            for etq in self._etiquetas_cargadas:
                r = self.tabla_etiquetas.rowCount()
                self.tabla_etiquetas.insertRow(r)
                self.tabla_etiquetas.setItem(r, 0, QTableWidgetItem(str(etq.etiqueta_id)))
                item_nombre = QTableWidgetItem(etq.nombre)
                if etq.color:
                    item_nombre.setForeground(QColor(etq.color))
                self.tabla_etiquetas.setItem(r, 1, item_nombre)
                self.tabla_etiquetas.setItem(r, 2, QTableWidgetItem(etq.categoria or ""))
                item_color = QTableWidgetItem(etq.color or "")
                if etq.color:
                    item_color.setBackground(QColor(etq.color))
                    item_color.setForeground(QColor("#ffffff"))
                self.tabla_etiquetas.setItem(r, 3, item_color)
                self.tabla_etiquetas.setItem(r, 4, QTableWidgetItem(str(etq.num_contactos)))
                self.tabla_etiquetas.setItem(r, 5, QTableWidgetItem(str(etq.num_empresas)))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las etiquetas: {str(e)}")

    def _mostrar_lista_etiquetas(self):
        self.form_etiquetas_widget.hide()
        self.lista_etiquetas_widget.show()
        self._cargar_tabla_etiquetas()

    # ==========================================
    # ETIQUETAS - FORMULARIO
    # ==========================================

    def _create_etiqueta_form(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "segmentacion", "etiqueta_form.ui")
        self.form_etiquetas_widget = QWidget()
        uic.loadUi(ui_path, self.form_etiquetas_widget)

        self.etq_form_titulo = self.form_etiquetas_widget.form_titulo
        self.etq_form_subtitulo = self.form_etiquetas_widget.form_subtitulo
        self.etq_input_nombre = self.form_etiquetas_widget.input_nombre
        self.etq_input_categoria = self.form_etiquetas_widget.input_categoria
        self.etq_input_color = self.form_etiquetas_widget.input_color
        self.etq_label_color_preview = self.form_etiquetas_widget.label_color_preview
        self.etq_section_asignaciones = self.form_etiquetas_widget.sectionAsignaciones
        self.etq_combo_add_contacto = self.form_etiquetas_widget.combo_add_contacto
        self.etq_btn_add_contacto = self.form_etiquetas_widget.btn_add_contacto
        self.etq_lista_contactos = self.form_etiquetas_widget.lista_contactos_asignados
        self.etq_btn_quitar_contacto = self.form_etiquetas_widget.btn_quitar_contacto
        self.etq_combo_add_empresa = self.form_etiquetas_widget.combo_add_empresa
        self.etq_btn_add_empresa = self.form_etiquetas_widget.btn_add_empresa
        self.etq_lista_empresas = self.form_etiquetas_widget.lista_empresas_asignadas
        self.etq_btn_quitar_empresa = self.form_etiquetas_widget.btn_quitar_empresa
        self.etq_btn_guardar = self.form_etiquetas_widget.btn_guardar
        self.etq_btn_limpiar = self.form_etiquetas_widget.btn_limpiar
        self.etq_btn_cancelar = self.form_etiquetas_widget.btn_cancelar

        self.etq_btn_guardar.clicked.connect(self._guardar_etiqueta)
        self.etq_btn_limpiar.clicked.connect(self._limpiar_formulario_etiqueta)
        self.etq_btn_cancelar.clicked.connect(self._mostrar_lista_etiquetas)
        self.etq_input_color.textChanged.connect(self._actualizar_preview_color)
        self.etq_btn_add_contacto.clicked.connect(self._agregar_contacto_etiqueta)
        self.etq_btn_quitar_contacto.clicked.connect(self._quitar_contacto_etiqueta)
        self.etq_btn_add_empresa.clicked.connect(self._agregar_empresa_etiqueta)
        self.etq_btn_quitar_empresa.clicked.connect(self._quitar_empresa_etiqueta)

        self.etq_section_asignaciones.hide()
        self.form_etiquetas_widget.hide()
        self.tabEtiquetasLayout.addWidget(self.form_etiquetas_widget)

    def _actualizar_preview_color(self, texto):
        color = texto.strip()
        if color and len(color) == 7 and color.startswith("#"):
            try:
                qc = QColor(color)
                if qc.isValid():
                    self.etq_label_color_preview.setStyleSheet(
                        f"border-radius: 6px; background-color: {color}; border: 1px solid #cbd5e0;"
                    )
                    return
            except Exception:
                pass
        self.etq_label_color_preview.setStyleSheet(
            "border-radius: 6px; background-color: #e2e8f0; border: 1px solid #cbd5e0;"
        )

    def _cargar_combos_asignacion(self):
        conn = get_connection()

        self.etq_combo_add_contacto.clear()
        self.etq_combo_add_contacto.addItem("-- Seleccionar contacto --", None)
        cursor = conn.execute(
            "SELECT ContactoID, (Nombre || ' ' || ApellidoPaterno) AS NC "
            "FROM Contactos WHERE Activo = 1 ORDER BY Nombre"
        )
        for row in cursor.fetchall():
            self.etq_combo_add_contacto.addItem(row["NC"], row["ContactoID"])

        self.etq_combo_add_empresa.clear()
        self.etq_combo_add_empresa.addItem("-- Seleccionar empresa --", None)
        cursor = conn.execute(
            "SELECT EmpresaID, RazonSocial FROM Empresas WHERE Activo = 1 ORDER BY RazonSocial"
        )
        for row in cursor.fetchall():
            self.etq_combo_add_empresa.addItem(row["RazonSocial"], row["EmpresaID"])

    def _cargar_asignaciones(self, etiqueta_id):
        self.etq_lista_contactos.clear()
        rows, _ = self._etiqueta_service.get_contactos_asignados(etiqueta_id)
        if rows:
            for row in rows:
                label = row["NombreCompleto"]
                if row["Empresa"]:
                    label += f"  ({row['Empresa']})"
                item = QListWidgetItem(label)
                item.setData(256, row["ContactoID"])
                self.etq_lista_contactos.addItem(item)

        self.etq_lista_empresas.clear()
        rows, _ = self._etiqueta_service.get_empresas_asignadas(etiqueta_id)
        if rows:
            for row in rows:
                item = QListWidgetItem(row["RazonSocial"])
                item.setData(256, row["EmpresaID"])
                self.etq_lista_empresas.addItem(item)

    def _agregar_contacto_etiqueta(self):
        if not self._etiqueta_editando:
            return
        contacto_id = self.etq_combo_add_contacto.currentData()
        if not contacto_id:
            QMessageBox.warning(self, "Aviso", "Selecciona un contacto para agregar.")
            return
        ok, error = self._etiqueta_service.asignar_contacto(
            self._etiqueta_editando.etiqueta_id,
            contacto_id,
            self._usuario_actual.usuario_id,
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_asignaciones(self._etiqueta_editando.etiqueta_id)

    def _quitar_contacto_etiqueta(self):
        if not self._etiqueta_editando:
            return
        item = self.etq_lista_contactos.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecciona un contacto de la lista para quitarlo.")
            return
        contacto_id = item.data(256)
        ok, error = self._etiqueta_service.quitar_contacto(
            self._etiqueta_editando.etiqueta_id, contacto_id
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_asignaciones(self._etiqueta_editando.etiqueta_id)

    def _agregar_empresa_etiqueta(self):
        if not self._etiqueta_editando:
            return
        empresa_id = self.etq_combo_add_empresa.currentData()
        if not empresa_id:
            QMessageBox.warning(self, "Aviso", "Selecciona una empresa para agregar.")
            return
        ok, error = self._etiqueta_service.asignar_empresa(
            self._etiqueta_editando.etiqueta_id,
            empresa_id,
            self._usuario_actual.usuario_id,
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_asignaciones(self._etiqueta_editando.etiqueta_id)

    def _quitar_empresa_etiqueta(self):
        if not self._etiqueta_editando:
            return
        item = self.etq_lista_empresas.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecciona una empresa de la lista para quitarla.")
            return
        empresa_id = item.data(256)
        ok, error = self._etiqueta_service.quitar_empresa(
            self._etiqueta_editando.etiqueta_id, empresa_id
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_asignaciones(self._etiqueta_editando.etiqueta_id)

    def _mostrar_form_nueva_etiqueta(self):
        self._etiqueta_editando = None
        self._limpiar_formulario_etiqueta()
        self.etq_form_titulo.setText("Nueva Etiqueta")
        self.etq_form_subtitulo.setText(
            "Completa la informacion de la nueva etiqueta. El nombre es obligatorio."
        )
        self.etq_btn_guardar.setText("Guardar Etiqueta")
        self.etq_section_asignaciones.hide()
        self.lista_etiquetas_widget.hide()
        self.form_etiquetas_widget.show()

    def _editar_etiqueta_seleccionada(self, index):
        row = index.row()
        item_id = self.tabla_etiquetas.item(row, 0)
        if not item_id:
            return

        etiqueta_id = int(item_id.text())
        etiqueta = next(
            (e for e in self._etiquetas_cargadas if e.etiqueta_id == etiqueta_id), None
        )
        if not etiqueta:
            return

        self._etiqueta_editando = etiqueta
        self._limpiar_formulario_etiqueta()

        self.etq_form_titulo.setText("Editar Etiqueta")
        self.etq_form_subtitulo.setText(f"Editando: {etiqueta.nombre}")
        self.etq_btn_guardar.setText("Actualizar Etiqueta")

        self.etq_input_nombre.setText(etiqueta.nombre)
        self.etq_input_categoria.setText(etiqueta.categoria or "")
        self.etq_input_color.setText(etiqueta.color or "")

        self._cargar_combos_asignacion()
        self._cargar_asignaciones(etiqueta.etiqueta_id)
        self.etq_section_asignaciones.show()

        self.lista_etiquetas_widget.hide()
        self.form_etiquetas_widget.show()

    def _guardar_etiqueta(self):
        datos = {
            "nombre": self.etq_input_nombre.text().strip(),
            "categoria": self.etq_input_categoria.text().strip(),
            "color": self.etq_input_color.text().strip(),
        }

        if self._etiqueta_editando:
            etiqueta, error = self._etiqueta_service.actualizar_etiqueta(
                self._etiqueta_editando.etiqueta_id, datos
            )
            titulo_error = "Error al Actualizar Etiqueta"
            titulo_exito = "Etiqueta Actualizada"
            msg_exito = "ha sido actualizada exitosamente."
        else:
            etiqueta, error = self._etiqueta_service.crear_etiqueta(datos)
            titulo_error = "Error al Crear Etiqueta"
            titulo_exito = "Etiqueta Creada"
            msg_exito = "ha sido creada exitosamente."

        if error:
            QMessageBox.critical(self, titulo_error, error)
        elif etiqueta:
            QMessageBox.information(
                self, titulo_exito,
                f"La etiqueta '{etiqueta.nombre}' {msg_exito}"
            )
            self._mostrar_lista_etiquetas()

    def _eliminar_etiqueta(self, etiqueta_id, nombre):
        resp = QMessageBox.question(
            self,
            "Eliminar Etiqueta",
            f"Seguro que deseas eliminar la etiqueta '{nombre}'?\n"
            "Se eliminaran todas sus asignaciones a contactos y empresas.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            ok, error = self._etiqueta_service.eliminar_etiqueta(etiqueta_id)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                self._mostrar_lista_etiquetas()

    def _limpiar_formulario_etiqueta(self):
        self.etq_input_nombre.clear()
        self.etq_input_categoria.clear()
        self.etq_input_color.clear()
        self.etq_lista_contactos.clear()
        self.etq_lista_empresas.clear()
        self.etq_input_nombre.setFocus()

    # ==========================================
    # SEGMENTOS - LISTA
    # ==========================================

    def _create_segmento_list(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "segmentacion", "segmento_list.ui")
        self.lista_segmentos_widget = QWidget()
        uic.loadUi(ui_path, self.lista_segmentos_widget)

        self.btn_nuevo_segmento = self.lista_segmentos_widget.btn_nuevo_segmento
        self.tabla_segmentos = self.lista_segmentos_widget.tabla_segmentos
        self.stat_seg_total = self.lista_segmentos_widget.statValueTotal
        self.stat_seg_contactos = self.lista_segmentos_widget.statValueContactos
        self.stat_seg_empresas = self.lista_segmentos_widget.statValueEmpresas

        self.btn_nuevo_segmento.clicked.connect(self._mostrar_form_nuevo_segmento)
        self.tabla_segmentos.doubleClicked.connect(self._mostrar_miembros_segmento)

        h = self.tabla_segmentos.horizontalHeader()
        if h:
            h.setStretchLastSection(False)
            h.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
            h.setSectionResizeMode(1, QHeaderView.Stretch)           # Nombre
            h.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Tipo
            h.setSectionResizeMode(3, QHeaderView.Interactive)       # Creado Por
            h.setMinimumSectionSize(60)
        v = self.tabla_segmentos.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(42)

        self.tabSegmentosLayout.addWidget(self.lista_segmentos_widget)

    def _cargar_tabla_segmentos(self):
        try:
            segmentos, error = self._segmento_service.obtener_todos()
            if error:
                QMessageBox.critical(self, "Error", error)
                return

            self._segmentos_cargados = segmentos or []
            total = len(self._segmentos_cargados)
            de_contactos = sum(1 for s in self._segmentos_cargados if s.tipo_entidad == "Contactos")
            de_empresas = sum(1 for s in self._segmentos_cargados if s.tipo_entidad == "Empresas")

            self.stat_seg_total.setText(str(total))
            self.stat_seg_contactos.setText(str(de_contactos))
            self.stat_seg_empresas.setText(str(de_empresas))

            self.tabla_segmentos.setRowCount(0)
            for seg in self._segmentos_cargados:
                r = self.tabla_segmentos.rowCount()
                self.tabla_segmentos.insertRow(r)
                self.tabla_segmentos.setItem(r, 0, QTableWidgetItem(str(seg.segmento_id)))
                self.tabla_segmentos.setItem(r, 1, QTableWidgetItem(seg.nombre))
                self.tabla_segmentos.setItem(r, 2, QTableWidgetItem(seg.tipo_entidad or ""))
                self.tabla_segmentos.setItem(r, 3, QTableWidgetItem(seg.nombre_creador or ""))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los segmentos: {str(e)}")

    def _mostrar_lista_segmentos(self):
        self.form_segmentos_widget.hide()
        self.members_segmento_widget.hide()
        self.lista_segmentos_widget.show()
        self._cargar_tabla_segmentos()

    # ==========================================
    # SEGMENTOS - FORMULARIO
    # ==========================================

    def _create_segmento_form(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "segmentacion", "segmento_form.ui")
        self.form_segmentos_widget = QWidget()
        uic.loadUi(ui_path, self.form_segmentos_widget)

        self.seg_form_titulo = self.form_segmentos_widget.form_titulo
        self.seg_form_subtitulo = self.form_segmentos_widget.form_subtitulo
        self.seg_input_nombre = self.form_segmentos_widget.input_nombre
        self.seg_input_descripcion = self.form_segmentos_widget.input_descripcion
        self.seg_combo_tipo = self.form_segmentos_widget.combo_tipo_entidad
        self.seg_btn_guardar = self.form_segmentos_widget.btn_guardar
        self.seg_btn_limpiar = self.form_segmentos_widget.btn_limpiar
        self.seg_btn_cancelar = self.form_segmentos_widget.btn_cancelar

        self.seg_btn_guardar.clicked.connect(self._guardar_segmento)
        self.seg_btn_limpiar.clicked.connect(self._limpiar_formulario_segmento)
        self.seg_btn_cancelar.clicked.connect(self._mostrar_lista_segmentos)

        self.form_segmentos_widget.hide()
        self.tabSegmentosLayout.addWidget(self.form_segmentos_widget)

    def _mostrar_form_nuevo_segmento(self):
        self._segmento_editando = None
        self._limpiar_formulario_segmento()
        self.seg_form_titulo.setText("Nuevo Segmento")
        self.seg_form_subtitulo.setText(
            "Define un grupo de contactos o empresas. El nombre es obligatorio."
        )
        self.seg_btn_guardar.setText("Guardar Segmento")
        self.lista_segmentos_widget.hide()
        self.form_segmentos_widget.show()

    def _mostrar_miembros_segmento(self, index):
        row = index.row()
        item_id = self.tabla_segmentos.item(row, 0)
        if not item_id:
            return

        segmento_id = int(item_id.text())
        segmento = next(
            (s for s in self._segmentos_cargados if s.segmento_id == segmento_id), None
        )
        if not segmento:
            return

        self._segmento_editando = segmento
        self._cargar_vista_miembros(segmento)

        self.lista_segmentos_widget.hide()
        self.form_segmentos_widget.hide()
        self.members_segmento_widget.show()

    def _guardar_segmento(self):
        datos = {
            "nombre": self.seg_input_nombre.text().strip(),
            "descripcion": self.seg_input_descripcion.text().strip(),
            "tipo_entidad": self.seg_combo_tipo.currentText(),
        }

        if self._segmento_editando:
            segmento, error = self._segmento_service.actualizar_segmento(
                self._segmento_editando.segmento_id, datos
            )
            titulo_error = "Error al Actualizar Segmento"
            titulo_exito = "Segmento Actualizado"
            msg_exito = "ha sido actualizado exitosamente."
        else:
            segmento, error = self._segmento_service.crear_segmento(
                datos, self._usuario_actual.usuario_id
            )
            titulo_error = "Error al Crear Segmento"
            titulo_exito = "Segmento Creado"
            msg_exito = "ha sido creado exitosamente."

        if error:
            QMessageBox.critical(self, titulo_error, error)
        elif segmento:
            QMessageBox.information(
                self, titulo_exito,
                f"El segmento '{segmento.nombre}' {msg_exito}"
            )
            self._mostrar_lista_segmentos()

    def _limpiar_formulario_segmento(self):
        self.seg_input_nombre.clear()
        self.seg_input_descripcion.clear()
        self.seg_combo_tipo.setCurrentIndex(0)
        self.seg_input_nombre.setFocus()

    # ==========================================
    # SEGMENTOS - VISTA DE MIEMBROS
    # ==========================================

    def _create_segmento_members(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "segmentacion", "segmento_members.ui")
        self.members_segmento_widget = QWidget()
        uic.loadUi(ui_path, self.members_segmento_widget)

        self.mem_titulo = self.members_segmento_widget.mem_titulo
        self.mem_subtitulo = self.members_segmento_widget.mem_subtitulo
        self.mem_stat_miembros = self.members_segmento_widget.statValueMiembros
        self.mem_info_tipo = self.members_segmento_widget.mem_info_tipo
        self.mem_tabla = self.members_segmento_widget.tabla_miembros
        self.mem_combo_add = self.members_segmento_widget.combo_add_miembro
        self.mem_btn_add = self.members_segmento_widget.btn_add_miembro
        self.mem_btn_quitar = self.members_segmento_widget.btn_quitar_miembro
        self.mem_btn_editar = self.members_segmento_widget.btn_editar_segmento
        self.mem_btn_eliminar = self.members_segmento_widget.btn_eliminar_segmento
        self.mem_btn_volver = self.members_segmento_widget.btn_volver_segmentos

        self.mem_btn_editar.clicked.connect(self._editar_desde_miembros)
        self.mem_btn_eliminar.clicked.connect(self._eliminar_desde_miembros)
        self.mem_btn_volver.clicked.connect(self._mostrar_lista_segmentos)
        self.mem_btn_add.clicked.connect(self._agregar_miembro_segmento)
        self.mem_btn_quitar.clicked.connect(self._quitar_miembro_segmento)

        v = self.mem_tabla.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(42)

        self.members_segmento_widget.hide()
        self.tabSegmentosLayout.addWidget(self.members_segmento_widget)

    def _cargar_vista_miembros(self, segmento):
        self.mem_titulo.setText(segmento.nombre)
        self.mem_subtitulo.setText(f"Segmento de {segmento.tipo_entidad or '-'}")
        self.mem_info_tipo.setText(segmento.tipo_entidad or "-")

        self._cargar_combo_miembros(segmento)
        self._cargar_tabla_miembros(segmento)

    def _cargar_combo_miembros(self, segmento):
        conn = get_connection()
        self.mem_combo_add.clear()

        if segmento.tipo_entidad == "Contactos":
            self.mem_combo_add.addItem("-- Seleccionar contacto --", None)
            cursor = conn.execute(
                "SELECT ContactoID, (Nombre || ' ' || ApellidoPaterno) AS NC "
                "FROM Contactos WHERE Activo = 1 ORDER BY Nombre"
            )
            for row in cursor.fetchall():
                self.mem_combo_add.addItem(row["NC"], row["ContactoID"])
        else:
            self.mem_combo_add.addItem("-- Seleccionar empresa --", None)
            cursor = conn.execute(
                "SELECT EmpresaID, RazonSocial FROM Empresas WHERE Activo = 1 ORDER BY RazonSocial"
            )
            for row in cursor.fetchall():
                self.mem_combo_add.addItem(row["RazonSocial"], row["EmpresaID"])

    def _cargar_tabla_miembros(self, segmento):
        miembros, error = self._segmento_service.obtener_miembros(segmento)
        if error:
            QMessageBox.critical(self, "Error", error)
            return

        miembros = miembros or []
        self.mem_stat_miembros.setText(str(len(miembros)))

        self.mem_tabla.clear()
        if segmento.tipo_entidad == "Contactos":
            headers = ["ID", "Nombre", "Email", "Puesto", "Empresa", "Ciudad"]
            col_keys = ["ID", "NombreCompleto", "Email", "Puesto", "Empresa", "Ciudad"]
        else:
            headers = ["ID", "Razon Social", "Email", "Industria", "Tamano", "Ciudad"]
            col_keys = ["ID", "NombreCompleto", "Email", "Industria", "Tamano", "Ciudad"]

        self.mem_tabla.setColumnCount(len(headers))
        self.mem_tabla.setHorizontalHeaderLabels(headers)

        h = self.mem_tabla.horizontalHeader()
        if h:
            h.setStretchLastSection(False)
            h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            h.setSectionResizeMode(1, QHeaderView.Stretch)
            for col in range(2, len(headers)):
                h.setSectionResizeMode(col, QHeaderView.Interactive)
            h.setMinimumSectionSize(60)

        self.mem_tabla.setRowCount(0)
        for m in miembros:
            r = self.mem_tabla.rowCount()
            self.mem_tabla.insertRow(r)
            for col, key in enumerate(col_keys):
                val = str(m.get(key, "") or "")
                item = QTableWidgetItem(val)
                if col == 0:
                    item.setData(256, m.get("ID"))
                self.mem_tabla.setItem(r, col, item)

    def _agregar_miembro_segmento(self):
        if not self._segmento_editando:
            return
        entidad_id = self.mem_combo_add.currentData()
        if not entidad_id:
            QMessageBox.warning(self, "Aviso", "Selecciona un elemento para agregar.")
            return
        ok, error = self._segmento_service.agregar_miembro(
            self._segmento_editando.segmento_id,
            entidad_id,
            self._segmento_editando.tipo_entidad,
            self._usuario_actual.usuario_id,
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_tabla_miembros(self._segmento_editando)

    def _quitar_miembro_segmento(self):
        if not self._segmento_editando:
            return
        selected = self.mem_tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecciona una fila para quitar.")
            return
        row = self.mem_tabla.currentRow()
        id_item = self.mem_tabla.item(row, 0)
        if not id_item:
            return
        entidad_id = id_item.data(256)
        if not entidad_id:
            return
        ok, error = self._segmento_service.quitar_miembro(
            self._segmento_editando.segmento_id,
            entidad_id,
            self._segmento_editando.tipo_entidad,
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_tabla_miembros(self._segmento_editando)

    def _editar_desde_miembros(self):
        if not self._segmento_editando:
            return
        segmento = self._segmento_editando
        self._limpiar_formulario_segmento()

        self.seg_form_titulo.setText("Editar Segmento")
        self.seg_form_subtitulo.setText(f"Editando: {segmento.nombre}")
        self.seg_btn_guardar.setText("Actualizar Segmento")

        self.seg_input_nombre.setText(segmento.nombre)
        self.seg_input_descripcion.setText(segmento.descripcion or "")

        for i in range(self.seg_combo_tipo.count()):
            if self.seg_combo_tipo.itemText(i) == segmento.tipo_entidad:
                self.seg_combo_tipo.setCurrentIndex(i)
                break

        self.members_segmento_widget.hide()
        self.form_segmentos_widget.show()

    def _eliminar_desde_miembros(self):
        if not self._segmento_editando:
            return
        segmento = self._segmento_editando
        resp = QMessageBox.question(
            self,
            "Eliminar Segmento",
            f"Seguro que deseas eliminar el segmento '{segmento.nombre}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            ok, error = self._segmento_service.eliminar_segmento(segmento.segmento_id)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                self._segmento_editando = None
                self._mostrar_lista_segmentos()
