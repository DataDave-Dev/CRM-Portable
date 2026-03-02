# Vista del Dashboard - carga dashboard_view.ui y puebla los KPIs y tablas

import os
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5 import uic

from app.repositories.dashboard_repository import DashboardRepository

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "dashboard", "dashboard_view.ui")

# Colores por estado de actividad
_COLORES_ESTADO = {
    "Pendiente":    QColor(230, 126, 34),
    "En Progreso":  QColor(52, 152, 219),
    "Completada":   QColor(39, 174, 96),
    "Cancelada":    QColor(149, 165, 166),
    "Reprogramada": QColor(155, 89, 182),
}


class DashboardView(QWidget):

    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._usuario = usuario
        self._repo = DashboardRepository()
        self._configurar_tablas()
        self.btnRefresh.clicked.connect(self.cargar_datos)

    def _configurar_tablas(self):
        # Tabla actividades recientes
        h = self.tablaActividadesRecientes.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Tipo
        h.setSectionResizeMode(1, QHeaderView.Stretch)           # Asunto
        h.setSectionResizeMode(2, QHeaderView.Interactive)       # Contacto
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Estado
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Fecha
        h.setMinimumSectionSize(70)
        self.tablaActividadesRecientes.verticalHeader().setVisible(False)
        self.tablaActividadesRecientes.verticalHeader().setDefaultSectionSize(36)

        # Tabla recordatorios proximos
        h2 = self.tablaRecordatoriosProximos.horizontalHeader()
        h2.setSectionResizeMode(0, QHeaderView.Stretch)           # Titulo
        h2.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Fecha
        h2.setSectionResizeMode(2, QHeaderView.Interactive)       # Vinculado
        h2.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Recurrencia
        h2.setMinimumSectionSize(70)
        self.tablaRecordatoriosProximos.verticalHeader().setVisible(False)
        self.tablaRecordatoriosProximos.verticalHeader().setDefaultSectionSize(36)

    def cargar_datos(self):
        self._cargar_kpis()
        self._cargar_actividades_recientes()
        self._cargar_recordatorios_proximos()

    # ------------------------------------------------------------------
    # KPI cards
    # ------------------------------------------------------------------

    def _cargar_kpis(self):
        try:
            kpis = self._repo.get_kpis()
        except Exception:
            return

        self.lblContactosValue.setText(str(kpis.get("ContactosActivos", 0)))
        self.lblEmpresasValue.setText(str(kpis.get("EmpresasActivas", 0)))
        self.lblOportunidadesValue.setText(str(kpis.get("OportunidadesAbiertas", 0)))

        valor_pipeline = kpis.get("ValorPipeline", 0) or 0
        self.lblPipelineValue.setText(self._fmt_monto(valor_pipeline))

        tasa = kpis.get("TasaConversionGlobal", 0) or 0
        self.lblConversionValue.setText(f"{tasa:.1f}%")

        self.lblActividadesValue.setText(str(kpis.get("ActividadesPendientes", 0)))

        # Colorear la tasa segun su valor
        if tasa >= 60:
            color = "#27ae60"
        elif tasa >= 30:
            color = "#f39c12"
        else:
            color = "#e74c3c"
        self.lblConversionValue.setStyleSheet(
            f"color: {color}; font-size: 30px; font-weight: bold;"
        )

    def _fmt_monto(self, valor):
        if valor >= 1_000_000:
            return f"${valor / 1_000_000:.1f}M"
        if valor >= 1_000:
            return f"${valor / 1_000:.0f}K"
        return f"${valor:.0f}"

    # ------------------------------------------------------------------
    # Tabla: Actividades recientes
    # ------------------------------------------------------------------

    def _cargar_actividades_recientes(self):
        try:
            rows = self._repo.get_actividades_recientes()
        except Exception:
            return

        tabla = self.tablaActividadesRecientes
        tabla.setRowCount(0)

        for row in rows:
            pos = tabla.rowCount()
            tabla.insertRow(pos)

            tipo    = str(row["Tipo"])
            asunto  = str(row["Asunto"])
            contacto = str(row["Contacto"])
            estado  = str(row["Estado"])
            fecha   = str(row["Fecha"] or "—")[:10]

            tabla.setItem(pos, 0, QTableWidgetItem(tipo))
            tabla.setItem(pos, 1, QTableWidgetItem(asunto))
            tabla.setItem(pos, 2, QTableWidgetItem(contacto))

            item_estado = QTableWidgetItem(estado)
            color = _COLORES_ESTADO.get(estado)
            if color:
                item_estado.setForeground(color)
            tabla.setItem(pos, 3, item_estado)

            tabla.setItem(pos, 4, QTableWidgetItem(fecha))

    # ------------------------------------------------------------------
    # Tabla: Recordatorios proximos
    # ------------------------------------------------------------------

    def _cargar_recordatorios_proximos(self):
        try:
            rows = self._repo.get_recordatorios_proximos(self._usuario.usuario_id)
        except Exception:
            return

        tabla = self.tablaRecordatoriosProximos
        tabla.setRowCount(0)

        from datetime import datetime
        ahora = datetime.now()

        for row in rows:
            pos = tabla.rowCount()
            tabla.insertRow(pos)

            titulo      = str(row["Titulo"])
            fecha_str   = str(row["FechaRecordatorio"] or "")
            vinculado   = str(row["Vinculado"])
            recurrencia = str(row["Recurrencia"])

            # Formatear fecha
            fecha_display = fecha_str[:16] if fecha_str else "—"

            tabla.setItem(pos, 0, QTableWidgetItem(titulo))

            item_fecha = QTableWidgetItem(fecha_display)
            # Colorear en rojo si ya vencio
            try:
                fecha_dt = datetime.fromisoformat(fecha_str)
                if fecha_dt < ahora:
                    item_fecha.setForeground(QColor(231, 76, 60))
            except Exception:
                pass
            tabla.setItem(pos, 1, item_fecha)

            tabla.setItem(pos, 2, QTableWidgetItem(vinculado))
            tabla.setItem(pos, 3, QTableWidgetItem(recurrencia))
