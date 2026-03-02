# Vista del Dashboard - carga dashboard_view.ui y puebla KPIs, graficas y tablas

import os
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QVBoxLayout
from PyQt5.QtGui import QColor
from PyQt5 import uic

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from app.repositories.dashboard_repository import DashboardRepository

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "dashboard", "dashboard_view.ui")

# Paleta de colores del CRM
_AZUL      = "#4a90d9"
_VERDE     = "#27ae60"
_ROJO      = "#e74c3c"
_NARANJA   = "#f39c12"
_MORADO    = "#9b59b6"
_GRIS      = "#95a5a6"
_FONDO     = "#ffffff"
_TEXTO     = "#1a1a2e"

# Pipeline: un color por etapa (hasta 7 etapas)
_COLORES_PIPELINE = [
    "#3498db", "#2ecc71", "#f39c12",
    "#e67e22", "#e74c3c", "#27ae60", "#95a5a6",
]

# Colores por estado de actividad (para la tabla)
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
        self._canvas_pipeline = None
        self._canvas_oportunidades = None
        self._configurar_tablas()
        self._init_graficas()
        self.btnRefresh.clicked.connect(self.cargar_datos)

    # ------------------------------------------------------------------
    # Configuracion inicial de tablas y canvases vacios
    # ------------------------------------------------------------------

    def _configurar_tablas(self):
        h = self.tablaActividadesRecientes.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(2, QHeaderView.Interactive)
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        h.setMinimumSectionSize(70)
        self.tablaActividadesRecientes.verticalHeader().setVisible(False)
        self.tablaActividadesRecientes.verticalHeader().setDefaultSectionSize(36)

        h2 = self.tablaRecordatoriosProximos.horizontalHeader()
        h2.setSectionResizeMode(0, QHeaderView.Stretch)
        h2.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h2.setSectionResizeMode(2, QHeaderView.Interactive)
        h2.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        h2.setMinimumSectionSize(70)
        self.tablaRecordatoriosProximos.verticalHeader().setVisible(False)
        self.tablaRecordatoriosProximos.verticalHeader().setDefaultSectionSize(36)

    def _init_graficas(self):
        # Crear canvases vacios y anclarlos a los contenedores del .ui
        self._canvas_pipeline = self._crear_canvas(self.chartPipelineContainer)
        self._canvas_oportunidades = self._crear_canvas(self.chartOportunidadesContainer)

    def _crear_canvas(self, contenedor):
        fig = Figure(facecolor=_FONDO, tight_layout=True)
        canvas = FigureCanvasQTAgg(fig)
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(canvas)
        return canvas

    # ------------------------------------------------------------------
    # Punto de entrada principal
    # ------------------------------------------------------------------

    def cargar_datos(self):
        self._cargar_kpis()
        self._cargar_grafica_pipeline()
        self._cargar_grafica_oportunidades()
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
        self.lblPipelineValue.setText(self._fmt_monto(kpis.get("ValorPipeline", 0) or 0))
        self.lblActividadesValue.setText(str(kpis.get("ActividadesPendientes", 0)))

        tasa = kpis.get("TasaConversionGlobal", 0) or 0
        self.lblConversionValue.setText(f"{tasa:.1f}%")
        color = _VERDE if tasa >= 60 else (_NARANJA if tasa >= 30 else _ROJO)
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
    # Grafica 1: Pipeline por etapa (barras horizontales)
    # ------------------------------------------------------------------

    def _cargar_grafica_pipeline(self):
        try:
            rows = self._repo.get_pipeline_por_etapa()
        except Exception:
            return

        canvas = self._canvas_pipeline
        fig = canvas.figure
        fig.clear()

        if not rows:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "Sin oportunidades abiertas",
                    ha="center", va="center", color=_GRIS, fontsize=11)
            ax.axis("off")
            canvas.draw()
            return

        etapas  = [r["Etapa"] for r in rows]
        montos  = [r["MontoTotal"] / 1000 for r in rows]   # en miles MXN
        colores = [_COLORES_PIPELINE[i % len(_COLORES_PIPELINE)] for i in range(len(etapas))]

        ax = fig.add_subplot(111)
        ax.set_facecolor(_FONDO)
        fig.patch.set_facecolor(_FONDO)

        bars = ax.barh(etapas, montos, color=colores, height=0.55, zorder=2)

        # Etiquetas de valor al final de cada barra
        for bar, monto in zip(bars, montos):
            ax.text(
                bar.get_width() + max(montos) * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"${monto:.0f}K",
                va="center", ha="left",
                fontsize=9, color=_TEXTO,
            )

        ax.set_xlabel("Monto estimado (miles MXN)", fontsize=9, color=_GRIS)
        ax.tick_params(colors=_TEXTO, labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#e2e8f0")
        ax.spines["bottom"].set_color("#e2e8f0")
        ax.xaxis.grid(True, color="#f0f2f5", zorder=0)
        ax.set_axisbelow(True)
        # Ampliar limite derecho para que quepan las etiquetas
        ax.set_xlim(0, max(montos) * 1.30 if montos else 1)

        fig.tight_layout(pad=1.2)
        canvas.draw()

    # ------------------------------------------------------------------
    # Grafica 2: Estado de oportunidades (donut)
    # ------------------------------------------------------------------

    def _cargar_grafica_oportunidades(self):
        try:
            row = self._repo.get_oportunidades_estado()
        except Exception:
            return

        canvas = self._canvas_oportunidades
        fig = canvas.figure
        fig.clear()

        abiertas = int(row["Abiertas"] or 0) if row else 0
        ganadas  = int(row["Ganadas"]  or 0) if row else 0
        perdidas = int(row["Perdidas"] or 0) if row else 0
        total    = abiertas + ganadas + perdidas

        ax = fig.add_subplot(111)
        ax.set_facecolor(_FONDO)
        fig.patch.set_facecolor(_FONDO)

        if total == 0:
            ax.text(0.5, 0.5, "Sin datos de oportunidades",
                    ha="center", va="center", color=_GRIS, fontsize=11)
            ax.axis("off")
            canvas.draw()
            return

        valores = [abiertas, ganadas, perdidas]
        etiquetas = [
            f"Abiertas\n{abiertas}",
            f"Ganadas\n{ganadas}",
            f"Perdidas\n{perdidas}",
        ]
        colores_donut = [_AZUL, _VERDE, _ROJO]

        # Filtrar segmentos con valor 0 para no mostrar etiquetas vacías
        datos = [(v, l, c) for v, l, c in zip(valores, etiquetas, colores_donut) if v > 0]
        valores_f, etiquetas_f, colores_f = zip(*datos) if datos else ([], [], [])

        wedges, texts, autotexts = ax.pie(
            valores_f,
            labels=etiquetas_f,
            colors=colores_f,
            autopct="%1.0f%%",
            startangle=90,
            wedgeprops={"width": 0.55, "edgecolor": _FONDO, "linewidth": 2},
            textprops={"fontsize": 9, "color": _TEXTO},
            pctdistance=0.75,
        )

        for at in autotexts:
            at.set_fontsize(9)
            at.set_color(_FONDO)
            at.set_fontweight("bold")

        # Texto central: total
        ax.text(0, 0, f"{total}\ntotal", ha="center", va="center",
                fontsize=11, fontweight="bold", color=_TEXTO)

        fig.tight_layout(pad=1.2)
        canvas.draw()

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

            tabla.setItem(pos, 0, QTableWidgetItem(str(row["Tipo"])))
            tabla.setItem(pos, 1, QTableWidgetItem(str(row["Asunto"])))
            tabla.setItem(pos, 2, QTableWidgetItem(str(row["Contacto"])))

            item_estado = QTableWidgetItem(str(row["Estado"]))
            color = _COLORES_ESTADO.get(str(row["Estado"]))
            if color:
                item_estado.setForeground(color)
            tabla.setItem(pos, 3, item_estado)

            fecha = str(row["Fecha"] or "—")[:10]
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

            fecha_str = str(row["FechaRecordatorio"] or "")
            tabla.setItem(pos, 0, QTableWidgetItem(str(row["Titulo"])))

            item_fecha = QTableWidgetItem(fecha_str[:16] if fecha_str else "—")
            try:
                if datetime.fromisoformat(fecha_str) < ahora:
                    item_fecha.setForeground(QColor(231, 76, 60))
            except Exception:
                pass
            tabla.setItem(pos, 1, item_fecha)

            tabla.setItem(pos, 2, QTableWidgetItem(str(row["Vinculado"])))
            tabla.setItem(pos, 3, QTableWidgetItem(str(row["Recurrencia"])))
