# Widget de solo lectura para mostrar el historial de etapas de una oportunidad

import os
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5 import uic
from app.repositories.historial_etapas_repository import HistorialEtapasRepository

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "ventas", "historial_etapas_widget.ui")


class HistorialEtapasWidget(QWidget):

    def __init__(self, oportunidad_id, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._oportunidad_id = oportunidad_id
        self._repo = HistorialEtapasRepository()

        self._setup_tabla()
        self._cargar_historial()

    def _setup_tabla(self):
        h = self.tabla_historial.horizontalHeader()
        if h:
            h.setSectionResizeMode(QHeaderView.Stretch)
        v = self.tabla_historial.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(36)

    def _cargar_historial(self):
        try:
            registros = self._repo.find_by_oportunidad(self._oportunidad_id)
            self.tabla_historial.setRowCount(0)
            for reg in registros:
                r = self.tabla_historial.rowCount()
                self.tabla_historial.insertRow(r)
                # formatear fecha (solo fecha, sin hora)
                fecha = reg["fecha_cambio"] or ""
                if " " in fecha:
                    fecha = fecha.split(" ")[0]
                self.tabla_historial.setItem(r, 0, QTableWidgetItem(fecha))
                self.tabla_historial.setItem(r, 1, QTableWidgetItem(reg["etapa_anterior"]))
                self.tabla_historial.setItem(r, 2, QTableWidgetItem(reg["etapa_nueva"]))
                self.tabla_historial.setItem(r, 3, QTableWidgetItem(reg["nombre_usuario"]))
                self.tabla_historial.setItem(r, 4, QTableWidgetItem(reg["comentario"]))
        except Exception as e:
            QMessageBox.warning(self, "Advertencia", f"No se pudo cargar el historial de etapas: {str(e)}")
