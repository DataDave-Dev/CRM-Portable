# Vista de Notificaciones y Recordatorios (Modulo 7)

import os
from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QColor
from PyQt5 import uic

from app.services.notificacion_service import NotificacionService
from app.repositories.contacto_repository import ContactoRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.oportunidad_repository import OportunidadRepository

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "notificaciones", "notificaciones_view.ui")
UI_FORM_PATH = os.path.join(os.path.dirname(__file__), "ui", "notificaciones", "recordatorio_form.ui")


class NotificacionesView(QWidget):

    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._usuario = usuario
        self._service = NotificacionService()
        self._contacto_repo = ContactoRepository()
        self._empresa_repo = EmpresaRepository()
        self._oportunidad_repo = OportunidadRepository()
        self._recordatorio_editando = None
        self._setup_tablas()
        self._connect_signals()

    # ==========================================
    # SETUP
    # ==========================================

    def _setup_tablas(self):
        # Tabla notificaciones
        h = self.tablaNotificaciones.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)   # Tipo
        h.setSectionResizeMode(1, QHeaderView.Stretch)             # Titulo
        h.setSectionResizeMode(2, QHeaderView.Stretch)             # Mensaje
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)    # Fecha
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)    # Estado
        self.tablaNotificaciones.verticalHeader().setVisible(False)
        self.tablaNotificaciones.verticalHeader().setDefaultSectionSize(40)
        self.tablaNotificaciones.setSelectionMode(QAbstractItemView.SingleSelection)

        # Tabla recordatorios
        h2 = self.tablaRecordatorios.horizontalHeader()
        h2.setSectionResizeMode(0, QHeaderView.Stretch)            # Titulo
        h2.setSectionResizeMode(1, QHeaderView.ResizeToContents)   # Fecha
        h2.setSectionResizeMode(2, QHeaderView.ResizeToContents)   # Recurrencia
        h2.setSectionResizeMode(3, QHeaderView.Stretch)            # Vinculado a
        h2.setSectionResizeMode(4, QHeaderView.ResizeToContents)   # Estado
        self.tablaRecordatorios.verticalHeader().setVisible(False)
        self.tablaRecordatorios.verticalHeader().setDefaultSectionSize(40)
        self.tablaRecordatorios.setSelectionMode(QAbstractItemView.SingleSelection)

    def _connect_signals(self):
        self.btnMarcarLeida.clicked.connect(self._marcar_seleccionada_leida)
        self.btnMarcarTodasLeidas.clicked.connect(self._marcar_todas_leidas)
        self.btnNuevoRecordatorio.clicked.connect(self._mostrar_form_nuevo)
        self.btnEditarRecordatorio.clicked.connect(self._editar_recordatorio)
        self.btnCompletarRecordatorio.clicked.connect(self._completar_recordatorio)
        self.btnEliminarRecordatorio.clicked.connect(self._eliminar_recordatorio)
        self.tablaRecordatorios.doubleClicked.connect(self._editar_recordatorio)

    # ==========================================
    # CARGA DE DATOS
    # ==========================================

    def cargar_datos(self):
        self._cargar_notificaciones()
        self._cargar_recordatorios()
        self._actualizar_contador()

    def _cargar_notificaciones(self):
        notifs, error = self._service.obtener_notificaciones(self._usuario.usuario_id)
        if error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las notificaciones:\n{error}")
            return

        self.tablaNotificaciones.setRowCount(0)
        for notif in notifs:
            row = self.tablaNotificaciones.rowCount()
            self.tablaNotificaciones.insertRow(row)

            self.tablaNotificaciones.setItem(row, 0, QTableWidgetItem(notif.tipo or "Sistema"))
            self.tablaNotificaciones.setItem(row, 1, QTableWidgetItem(notif.titulo))
            self.tablaNotificaciones.setItem(row, 2, QTableWidgetItem(notif.mensaje or ""))
            self.tablaNotificaciones.setItem(row, 3, QTableWidgetItem(notif.fecha_creacion or ""))

            estado = "Leida" if notif.es_leida else "Sin leer"
            item_estado = QTableWidgetItem(estado)
            if not notif.es_leida:
                item_estado.setForeground(QColor(220, 53, 69))
                # Resaltar fila entera
                for col in range(5):
                    item = self.tablaNotificaciones.item(row, col)
                    if item:
                        item.setFont(item.font())
            else:
                item_estado.setForeground(QColor(100, 100, 100))
            self.tablaNotificaciones.setItem(row, 4, item_estado)

            # Guardar el ID en el item oculto (columna 0, userData)
            id_item = self.tablaNotificaciones.item(row, 0)
            if id_item:
                id_item.setData(Qt.UserRole, notif.notificacion_id)

    def _cargar_recordatorios(self):
        records, error = self._service.obtener_recordatorios(self._usuario.usuario_id)
        if error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los recordatorios:\n{error}")
            return

        self.tablaRecordatorios.setRowCount(0)
        for rec in records:
            row = self.tablaRecordatorios.rowCount()
            self.tablaRecordatorios.insertRow(row)

            self.tablaRecordatorios.setItem(row, 0, QTableWidgetItem(rec.titulo))
            self.tablaRecordatorios.setItem(row, 1, QTableWidgetItem(rec.fecha_recordatorio or ""))
            self.tablaRecordatorios.setItem(row, 2, QTableWidgetItem(rec.tipo_recurrencia or "Sin recurrencia"))

            vinculo = ""
            if rec.nombre_contacto:
                vinculo = f"Contacto: {rec.nombre_contacto}"
            elif rec.nombre_empresa:
                vinculo = f"Empresa: {rec.nombre_empresa}"
            elif rec.nombre_oportunidad:
                vinculo = f"Oportunidad: {rec.nombre_oportunidad}"
            self.tablaRecordatorios.setItem(row, 3, QTableWidgetItem(vinculo))

            if rec.es_completado:
                estado_txt = "Completado"
                color = QColor(100, 100, 100)
            else:
                estado_txt = "Pendiente"
                color = QColor(74, 144, 217)
            item_estado = QTableWidgetItem(estado_txt)
            item_estado.setForeground(color)
            self.tablaRecordatorios.setItem(row, 4, item_estado)

            id_item = self.tablaRecordatorios.item(row, 0)
            if id_item:
                id_item.setData(Qt.UserRole, rec.recordatorio_id)

    def _actualizar_contador(self):
        count = self._service.count_no_leidas(self._usuario.usuario_id)
        self.labelContadorNoLeidas.setText(f"{count} sin leer")

    # ==========================================
    # ACCIONES DE NOTIFICACIONES
    # ==========================================

    def _marcar_seleccionada_leida(self):
        row = self.tablaNotificaciones.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccion", "Selecciona una notificacion de la lista.")
            return

        id_item = self.tablaNotificaciones.item(row, 0)
        if not id_item:
            return

        notif_id = id_item.data(Qt.UserRole)
        ok, err = self._service.marcar_como_leida(notif_id)
        if err:
            QMessageBox.critical(self, "Error", err)
        else:
            self._cargar_notificaciones()
            self._actualizar_contador()

    def _marcar_todas_leidas(self):
        ok, err = self._service.marcar_todas_como_leidas(self._usuario.usuario_id)
        if err:
            QMessageBox.critical(self, "Error", err)
        else:
            self._cargar_notificaciones()
            self._actualizar_contador()

    # ==========================================
    # FORMULARIO DE RECORDATORIO
    # ==========================================

    def _mostrar_form_nuevo(self):
        self._recordatorio_editando = None
        self._abrir_formulario()

    def _editar_recordatorio(self):
        row = self.tablaRecordatorios.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccion", "Selecciona un recordatorio de la lista.")
            return

        id_item = self.tablaRecordatorios.item(row, 0)
        if not id_item:
            return

        from app.repositories.recordatorio_repository import RecordatorioRepository
        repo = RecordatorioRepository()
        rec = repo.find_by_id(id_item.data(Qt.UserRole))
        if not rec:
            return

        self._recordatorio_editando = rec
        self._abrir_formulario(rec)

    def _abrir_formulario(self, recordatorio=None):
        dialogo = _RecordatorioFormDialog(
            service=self._service,
            usuario_id=self._usuario.usuario_id,
            contacto_repo=self._contacto_repo,
            empresa_repo=self._empresa_repo,
            oportunidad_repo=self._oportunidad_repo,
            recordatorio=recordatorio,
            parent=self,
        )
        if dialogo.exec_() == QDialog.Accepted:
            self._cargar_recordatorios()

    # ==========================================
    # COMPLETAR / ELIMINAR RECORDATORIO
    # ==========================================

    def _completar_recordatorio(self):
        row = self.tablaRecordatorios.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccion", "Selecciona un recordatorio de la lista.")
            return

        id_item = self.tablaRecordatorios.item(row, 0)
        if not id_item:
            return

        resp = QMessageBox.question(
            self, "Completar Recordatorio",
            "Marcar este recordatorio como completado?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        ok, err = self._service.completar_recordatorio(id_item.data(Qt.UserRole))
        if err:
            QMessageBox.critical(self, "Error", err)
        else:
            self._cargar_recordatorios()

    def _eliminar_recordatorio(self):
        row = self.tablaRecordatorios.currentRow()
        if row < 0:
            QMessageBox.information(self, "Seleccion", "Selecciona un recordatorio de la lista.")
            return

        id_item = self.tablaRecordatorios.item(row, 0)
        if not id_item:
            return

        titulo_item = self.tablaRecordatorios.item(row, 0)
        titulo = titulo_item.text() if titulo_item else "este recordatorio"

        resp = QMessageBox.question(
            self, "Eliminar Recordatorio",
            f"Seguro que deseas eliminar el recordatorio '{titulo}'?\nEsta accion no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        ok, err = self._service.eliminar_recordatorio(id_item.data(Qt.UserRole))
        if err:
            QMessageBox.critical(self, "Error", err)
        else:
            self._cargar_recordatorios()


# ==========================================
# DIALOGO DEL FORMULARIO DE RECORDATORIO
# ==========================================

class _RecordatorioFormDialog(QDialog):
    """Dialog que envuelve el formulario .ui de recordatorio."""

    def __init__(self, service, usuario_id, contacto_repo, empresa_repo,
                 oportunidad_repo, recordatorio=None, parent=None):
        super().__init__(parent)
        self._service = service
        self._usuario_id = usuario_id
        self._contacto_repo = contacto_repo
        self._empresa_repo = empresa_repo
        self._oportunidad_repo = oportunidad_repo
        self._recordatorio = recordatorio
        self._setup_ui()
        self._cargar_combos()
        if recordatorio:
            self._poblar_form(recordatorio)

    def _setup_ui(self):
        self.setWindowTitle("Recordatorio")
        self.setMinimumWidth(650)
        self.setMinimumHeight(460)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._form_widget = QWidget()
        uic.loadUi(UI_FORM_PATH, self._form_widget)
        layout.addWidget(self._form_widget)

        # Referencias directas
        self._input_titulo = self._form_widget.inputTitulo
        self._input_desc = self._form_widget.inputDescripcion
        self._input_fecha = self._form_widget.inputFecha
        self._combo_recurrencia = self._form_widget.comboRecurrencia
        self._combo_contacto = self._form_widget.comboContacto
        self._combo_empresa = self._form_widget.comboEmpresa
        self._combo_oportunidad = self._form_widget.comboOportunidad
        self._btn_guardar = self._form_widget.btnGuardar
        self._btn_cancelar = self._form_widget.btnCancelar

        self._btn_guardar.clicked.connect(self._guardar)
        self._btn_cancelar.clicked.connect(self.reject)

        # Fecha por defecto: ahora
        self._input_fecha.setDateTime(QDateTime.currentDateTime())

    def _cargar_combos(self):
        # Recurrencia
        for tipo in self._service.tipos_recurrencia:
            self._combo_recurrencia.addItem(tipo, tipo)

        # Contactos
        self._combo_contacto.addItem("Sin vinculo", None)
        try:
            contactos = self._contacto_repo.find_all()
            for c in contactos:
                nombre = f"{c.nombre} {c.apellido_paterno}"
                self._combo_contacto.addItem(nombre, c.contacto_id)
        except Exception:
            pass

        # Empresas
        self._combo_empresa.addItem("Sin vinculo", None)
        try:
            empresas = self._empresa_repo.find_all()
            for e in empresas:
                self._combo_empresa.addItem(e.razon_social, e.empresa_id)
        except Exception:
            pass

        # Oportunidades
        self._combo_oportunidad.addItem("Sin vinculo", None)
        try:
            opors = self._oportunidad_repo.find_all()
            for o in opors:
                self._combo_oportunidad.addItem(o.nombre, o.oportunidad_id)
        except Exception:
            pass

        # Titulo y boton si es edicion
        if self._recordatorio:
            self._form_widget.formTitle.setText("Editar Recordatorio")
            self._btn_guardar.setText("Actualizar Recordatorio")

    def _poblar_form(self, rec):
        self._input_titulo.setText(rec.titulo)
        self._input_desc.setPlainText(rec.descripcion or "")

        if rec.fecha_recordatorio:
            try:
                qdt = QDateTime.fromString(rec.fecha_recordatorio, "yyyy-MM-dd HH:mm:ss")
                if not qdt.isValid():
                    qdt = QDateTime.fromString(rec.fecha_recordatorio, "yyyy-MM-dd HH:mm")
                if qdt.isValid():
                    self._input_fecha.setDateTime(qdt)
            except Exception:
                pass

        if rec.tipo_recurrencia:
            idx = self._combo_recurrencia.findData(rec.tipo_recurrencia)
            if idx >= 0:
                self._combo_recurrencia.setCurrentIndex(idx)

        if rec.contacto_id:
            idx = self._combo_contacto.findData(rec.contacto_id)
            if idx >= 0:
                self._combo_contacto.setCurrentIndex(idx)

        if rec.empresa_id:
            idx = self._combo_empresa.findData(rec.empresa_id)
            if idx >= 0:
                self._combo_empresa.setCurrentIndex(idx)

        if rec.oportunidad_id:
            idx = self._combo_oportunidad.findData(rec.oportunidad_id)
            if idx >= 0:
                self._combo_oportunidad.setCurrentIndex(idx)

    def _guardar(self):
        datos = {
            "titulo": self._input_titulo.text(),
            "descripcion": self._input_desc.toPlainText(),
            "fecha_recordatorio": self._input_fecha.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "tipo_recurrencia": self._combo_recurrencia.currentData(),
            "contacto_id": self._combo_contacto.currentData(),
            "empresa_id": self._combo_empresa.currentData(),
            "oportunidad_id": self._combo_oportunidad.currentData(),
        }

        if self._recordatorio:
            _, err = self._service.actualizar_recordatorio(self._recordatorio.recordatorio_id, datos)
        else:
            _, err = self._service.crear_recordatorio(datos, self._usuario_id)

        if err:
            QMessageBox.critical(self, "Error de Validacion", err)
        else:
            self.accept()
