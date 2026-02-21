# Vista de Actividades - gestiona llamadas, reuniones, correos y tareas

import os
import datetime
from PyQt5.QtWidgets import (
    QWidget, QMessageBox, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QDate
from PyQt5 import uic

# Fecha centinela que representa "sin fecha" en QDateEdit (specialValueText)
_FECHA_NULA = QDate(2000, 1, 1)


def _get_fecha(widget) -> str:
    """Lee un QDateEdit y retorna 'yyyy-MM-dd' o '' si no se seleccionó fecha."""
    d = widget.date()
    return "" if d == _FECHA_NULA else d.toString("yyyy-MM-dd")


def _set_fecha(widget, valor: str):
    """Escribe una fecha 'yyyy-MM-dd' en un QDateEdit; si es vacío pone la fecha nula."""
    if valor:
        d = QDate.fromString(valor, "yyyy-MM-dd")
        widget.setDate(d if d.isValid() else _FECHA_NULA)
    else:
        widget.setDate(_FECHA_NULA)
from app.database.connection import get_connection
from app.services.actividad_service import ActividadService
from app.utils.catalog_cache import CatalogCache

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "actividades", "actividades_view.ui")


class ActividadesView(QWidget):

    def __init__(self, usuario_actual, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._usuario_actual = usuario_actual
        self._actividad_service = ActividadService()

        self._actividad_editando = None
        self._actividades_cargadas = []

        self._create_actividad_list()
        self._create_actividad_form()

    # ==========================================
    # LISTA DE ACTIVIDADES
    # ==========================================

    def _create_actividad_list(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "actividades", "actividad_list.ui")
        self.lista_actividades_widget = QWidget()
        uic.loadUi(ui_path, self.lista_actividades_widget)

        self.btn_nueva_actividad = self.lista_actividades_widget.btn_nueva_actividad
        self.tabla_actividades = self.lista_actividades_widget.tabla_actividades
        self.stat_act_total = self.lista_actividades_widget.statValueTotal
        self.stat_act_pendientes = self.lista_actividades_widget.statValuePendientes
        self.stat_act_completadas = self.lista_actividades_widget.statValueCompletadas
        self.stat_act_vencidas = self.lista_actividades_widget.statValueVencidas

        self.btn_nueva_actividad.clicked.connect(self._mostrar_form_nueva_actividad)
        self.tabla_actividades.doubleClicked.connect(self._editar_actividad_seleccionada)

        h = self.tabla_actividades.horizontalHeader()
        if h:
            h.setStretchLastSection(False)
            h.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
            h.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Tipo
            h.setSectionResizeMode(2, QHeaderView.Stretch)           # Asunto
            h.setSectionResizeMode(3, QHeaderView.Interactive)       # Contacto
            h.setSectionResizeMode(4, QHeaderView.Interactive)       # Empresa
            h.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Vencimiento
            h.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Prioridad
            h.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Estado
            h.setMinimumSectionSize(60)
        v = self.tabla_actividades.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(42)

        self.tabActividadesLayout.addWidget(self.lista_actividades_widget)

    def _cargar_tabla_actividades(self):
        try:
            actividades, error = self._actividad_service.obtener_todas(limit=200)
            if error:
                QMessageBox.critical(self, "Error", error)
                return

            self._actividades_cargadas = actividades or []
            hoy = datetime.date.today().isoformat()
            total = len(self._actividades_cargadas)
            pendientes = sum(
                1 for a in self._actividades_cargadas
                if a.nombre_estado_actividad and a.nombre_estado_actividad.lower() in ("pendiente", "en progreso")
            )
            completadas = sum(
                1 for a in self._actividades_cargadas
                if a.nombre_estado_actividad and a.nombre_estado_actividad.lower() == "completada"
            )
            vencidas = sum(
                1 for a in self._actividades_cargadas
                if a.fecha_vencimiento and a.fecha_vencimiento < hoy
                and a.nombre_estado_actividad and a.nombre_estado_actividad.lower() not in ("completada", "cancelada")
            )

            self.stat_act_total.setText(str(total))
            self.stat_act_pendientes.setText(str(pendientes))
            self.stat_act_completadas.setText(str(completadas))
            self.stat_act_vencidas.setText(str(vencidas))

            self.tabla_actividades.setRowCount(0)
            for act in self._actividades_cargadas:
                r = self.tabla_actividades.rowCount()
                self.tabla_actividades.insertRow(r)
                self.tabla_actividades.setItem(r, 0, QTableWidgetItem(str(act.actividad_id)))
                self.tabla_actividades.setItem(r, 1, QTableWidgetItem(act.nombre_tipo_actividad or "N/A"))
                self.tabla_actividades.setItem(r, 2, QTableWidgetItem(act.asunto or ""))
                self.tabla_actividades.setItem(r, 3, QTableWidgetItem(act.nombre_contacto or "N/A"))
                self.tabla_actividades.setItem(r, 4, QTableWidgetItem(act.nombre_empresa or "N/A"))
                self.tabla_actividades.setItem(r, 5, QTableWidgetItem(act.fecha_vencimiento or "N/A"))
                self.tabla_actividades.setItem(r, 6, QTableWidgetItem(act.nombre_prioridad or "N/A"))

                estado_str = act.nombre_estado_actividad or "N/A"
                item_estado = QTableWidgetItem(estado_str)
                estado_lower = estado_str.lower()
                if estado_lower == "completada":
                    item_estado.setForeground(QColor(34, 139, 34))
                elif estado_lower == "cancelada":
                    item_estado.setForeground(QColor(150, 150, 150))
                elif estado_lower == "pendiente":
                    item_estado.setForeground(QColor(237, 137, 54))
                elif act.fecha_vencimiento and act.fecha_vencimiento < hoy:
                    item_estado.setForeground(QColor(220, 53, 69))
                self.tabla_actividades.setItem(r, 7, item_estado)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las actividades: {str(e)}")

    def _mostrar_lista_actividades(self):
        self.form_actividades_widget.hide()
        self.lista_actividades_widget.show()
        self._cargar_tabla_actividades()

    # ==========================================
    # FORMULARIO DE ACTIVIDADES
    # ==========================================

    def _create_actividad_form(self):
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "actividades", "actividad_form.ui")
        self.form_actividades_widget = QWidget()
        uic.loadUi(ui_path, self.form_actividades_widget)

        # referencias directas
        self.act_form_titulo = self.form_actividades_widget.form_titulo
        self.act_form_subtitulo = self.form_actividades_widget.form_subtitulo
        self.act_combo_tipo = self.form_actividades_widget.combo_tipo_actividad
        self.act_combo_estado = self.form_actividades_widget.combo_estado_actividad
        self.act_input_asunto = self.form_actividades_widget.input_asunto
        self.act_combo_prioridad = self.form_actividades_widget.combo_prioridad
        self.act_combo_propietario = self.form_actividades_widget.combo_propietario
        self.act_input_descripcion = self.form_actividades_widget.input_descripcion
        self.act_input_fecha_inicio = self.form_actividades_widget.input_fecha_inicio
        self.act_input_fecha_fin = self.form_actividades_widget.input_fecha_fin
        self.act_input_fecha_vencimiento = self.form_actividades_widget.input_fecha_vencimiento
        self.act_input_duracion = self.form_actividades_widget.input_duracion_minutos
        self.act_input_ubicacion = self.form_actividades_widget.input_ubicacion
        self.act_combo_contacto = self.form_actividades_widget.combo_contacto
        self.act_combo_empresa = self.form_actividades_widget.combo_empresa
        self.act_combo_oportunidad = self.form_actividades_widget.combo_oportunidad
        self.act_input_resultado = self.form_actividades_widget.input_resultado
        self.act_btn_guardar = self.form_actividades_widget.btn_guardar
        self.act_btn_limpiar = self.form_actividades_widget.btn_limpiar
        self.act_btn_cancelar = self.form_actividades_widget.btn_cancelar

        self.act_btn_guardar.clicked.connect(self._guardar_actividad)
        self.act_btn_limpiar.clicked.connect(self._limpiar_formulario_actividad)
        self.act_btn_cancelar.clicked.connect(self._mostrar_lista_actividades)

        self._cargar_combos_actividad()
        self.form_actividades_widget.hide()
        self.tabActividadesLayout.addWidget(self.form_actividades_widget)

    def _cargar_combos_actividad(self):
        conn = get_connection()

        self.act_combo_tipo.clear()
        self.act_combo_tipo.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_tipos_actividad():
            self.act_combo_tipo.addItem(nombre, id_val)

        self.act_combo_estado.clear()
        self.act_combo_estado.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_estados_actividad():
            self.act_combo_estado.addItem(nombre, id_val)

        self.act_combo_prioridad.clear()
        self.act_combo_prioridad.addItem("-- Sin prioridad --", None)
        for id_val, nombre in CatalogCache.get_prioridades():
            self.act_combo_prioridad.addItem(nombre, id_val)

        self.act_combo_propietario.clear()
        self.act_combo_propietario.addItem("-- Seleccionar --", None)
        for id_val, nombre in CatalogCache.get_usuarios():
            self.act_combo_propietario.addItem(nombre, id_val)

        self.act_combo_contacto.clear()
        self.act_combo_contacto.addItem("-- Sin contacto --", None)
        cursor = conn.execute(
            "SELECT ContactoID, (Nombre || ' ' || ApellidoPaterno) AS NombreCompleto "
            "FROM Contactos WHERE Activo = 1 ORDER BY Nombre"
        )
        for row in cursor.fetchall():
            self.act_combo_contacto.addItem(row["NombreCompleto"], row["ContactoID"])

        self.act_combo_empresa.clear()
        self.act_combo_empresa.addItem("-- Sin empresa --", None)
        cursor = conn.execute(
            "SELECT EmpresaID, RazonSocial FROM Empresas WHERE Activo = 1 ORDER BY RazonSocial"
        )
        for row in cursor.fetchall():
            self.act_combo_empresa.addItem(row["RazonSocial"], row["EmpresaID"])

        self.act_combo_oportunidad.clear()
        self.act_combo_oportunidad.addItem("-- Sin oportunidad --", None)
        cursor = conn.execute(
            "SELECT OportunidadID, Nombre FROM Oportunidades WHERE EsGanada IS NULL ORDER BY Nombre"
        )
        for row in cursor.fetchall():
            self.act_combo_oportunidad.addItem(row["Nombre"], row["OportunidadID"])

        # seleccionar usuario actual como propietario por defecto
        for i in range(self.act_combo_propietario.count()):
            if self.act_combo_propietario.itemData(i) == self._usuario_actual.usuario_id:
                self.act_combo_propietario.setCurrentIndex(i)
                break

    def _mostrar_form_nueva_actividad(self):
        self._actividad_editando = None
        self._limpiar_formulario_actividad()
        self.act_form_titulo.setText("Nueva Actividad")
        self.act_form_subtitulo.setText(
            "Completa la informacion de la nueva actividad. "
            "Los campos marcados con * son obligatorios."
        )
        self.act_btn_guardar.setText("Guardar Actividad")
        self.lista_actividades_widget.hide()
        self.form_actividades_widget.show()

    def _editar_actividad_seleccionada(self, index):
        row = index.row()
        item_id = self.tabla_actividades.item(row, 0)
        if not item_id:
            return

        actividad_id = int(item_id.text())
        actividad = next(
            (a for a in self._actividades_cargadas if a.actividad_id == actividad_id), None
        )
        if not actividad:
            return

        self._actividad_editando = actividad
        self._limpiar_formulario_actividad()

        self.act_form_titulo.setText("Editar Actividad")
        self.act_form_subtitulo.setText(
            f"Editando: {actividad.asunto}"
        )
        self.act_btn_guardar.setText("Actualizar Actividad")

        # poblar campos
        self.act_input_asunto.setText(actividad.asunto or "")
        self.act_input_descripcion.setPlainText(actividad.descripcion or "")
        _set_fecha(self.act_input_fecha_inicio, actividad.fecha_inicio)
        _set_fecha(self.act_input_fecha_fin, actividad.fecha_fin)
        _set_fecha(self.act_input_fecha_vencimiento, actividad.fecha_vencimiento)
        self.act_input_duracion.setText(str(actividad.duracion_minutos) if actividad.duracion_minutos is not None else "")
        self.act_input_ubicacion.setText(actividad.ubicacion or "")
        self.act_input_resultado.setPlainText(actividad.resultado or "")

        self._set_combo_by_data(self.act_combo_tipo, actividad.tipo_actividad_id)
        self._set_combo_by_data(self.act_combo_estado, actividad.estado_actividad_id)
        self._set_combo_by_data(self.act_combo_prioridad, actividad.prioridad_id)
        self._set_combo_by_data(self.act_combo_propietario, actividad.propietario_id)
        self._set_combo_by_data(self.act_combo_contacto, actividad.contacto_id)
        self._set_combo_by_data(self.act_combo_empresa, actividad.empresa_id)
        self._set_combo_by_data(self.act_combo_oportunidad, actividad.oportunidad_id)

        self.lista_actividades_widget.hide()
        self.form_actividades_widget.show()

    def _guardar_actividad(self):
        datos = {
            "tipo_actividad_id": self.act_combo_tipo.currentData(),
            "asunto": self.act_input_asunto.text().strip(),
            "descripcion": self.act_input_descripcion.toPlainText().strip(),
            "propietario_id": self.act_combo_propietario.currentData(),
            "prioridad_id": self.act_combo_prioridad.currentData(),
            "estado_actividad_id": self.act_combo_estado.currentData(),
            "fecha_inicio": _get_fecha(self.act_input_fecha_inicio),
            "fecha_fin": _get_fecha(self.act_input_fecha_fin),
            "fecha_vencimiento": _get_fecha(self.act_input_fecha_vencimiento),
            "duracion_minutos": self.act_input_duracion.text().strip(),
            "ubicacion": self.act_input_ubicacion.text().strip(),
            "contacto_id": self.act_combo_contacto.currentData(),
            "empresa_id": self.act_combo_empresa.currentData(),
            "oportunidad_id": self.act_combo_oportunidad.currentData(),
            "resultado": self.act_input_resultado.toPlainText().strip(),
        }

        if self._actividad_editando:
            actividad, error = self._actividad_service.actualizar_actividad(
                self._actividad_editando.actividad_id, datos, self._usuario_actual.usuario_id
            )
            titulo_error = "Error al Actualizar Actividad"
            titulo_exito = "Actividad Actualizada"
            msg_exito = "ha sido actualizada exitosamente."
        else:
            actividad, error = self._actividad_service.crear_actividad(
                datos, self._usuario_actual.usuario_id
            )
            titulo_error = "Error al Crear Actividad"
            titulo_exito = "Actividad Creada"
            msg_exito = "ha sido creada exitosamente."

        if error:
            QMessageBox.critical(self, titulo_error, error)
        elif actividad:
            QMessageBox.information(
                self,
                titulo_exito,
                f"La actividad '{actividad.asunto}' {msg_exito}"
            )
            self._mostrar_lista_actividades()

    def _limpiar_formulario_actividad(self):
        self.act_input_asunto.clear()
        self.act_input_descripcion.clear()
        self.act_input_fecha_inicio.setDate(_FECHA_NULA)
        self.act_input_fecha_fin.setDate(_FECHA_NULA)
        self.act_input_fecha_vencimiento.setDate(_FECHA_NULA)
        self.act_input_duracion.clear()
        self.act_input_ubicacion.clear()
        self.act_input_resultado.clear()
        self.act_combo_tipo.setCurrentIndex(0)
        self.act_combo_estado.setCurrentIndex(0)
        self.act_combo_prioridad.setCurrentIndex(0)
        self.act_combo_contacto.setCurrentIndex(0)
        self.act_combo_empresa.setCurrentIndex(0)
        self.act_combo_oportunidad.setCurrentIndex(0)
        # restablecer propietario al usuario actual
        for i in range(self.act_combo_propietario.count()):
            if self.act_combo_propietario.itemData(i) == self._usuario_actual.usuario_id:
                self.act_combo_propietario.setCurrentIndex(i)
                break
        self.act_input_asunto.setFocus()

    def cargar_datos(self):
        self._cargar_tabla_actividades()

    # ==========================================
    # HELPERS
    # ==========================================

    @staticmethod
    def _set_combo_by_data(combo, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return
