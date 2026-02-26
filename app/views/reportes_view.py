# Vista de Reportes — Módulo 6
# Reportes con exportación a Excel y PDF

import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QSizePolicy, QFileDialog,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5 import uic

from app.services.reporte_service import ReporteService, REPORTES

# Reportes que admiten filtro de fecha.
# vendedores y etapas son agregados sin columna de fecha directa.
_REPORTES_CON_FECHA = {"pipeline", "campanas", "actividad"}

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "reportes", "reportes_view.ui")

# ------------------------------------------------------------------ #
# Estilos de botones (hover/pressed/disabled requieren Python)        #
# ------------------------------------------------------------------ #

_STYLE_BTN_EXCEL = """
    QPushButton {
        background-color: #276749;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 600;
        padding: 10px 24px;
        min-height: 38px;
    }
    QPushButton:hover { background-color: #22543d; }
    QPushButton:pressed { background-color: #1c4532; }
    QPushButton:disabled { background-color: #9ae6b4; color: #f0fff4; }
"""
_STYLE_BTN_PDF = """
    QPushButton {
        background-color: #c53030;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 600;
        padding: 10px 24px;
        min-height: 38px;
    }
    QPushButton:hover { background-color: #9b2c2c; }
    QPushButton:pressed { background-color: #742a2a; }
    QPushButton:disabled { background-color: #fc8181; color: #fff5f5; }
"""
_STYLE_BTN_REFRESH = """
    QPushButton {
        background-color: #4a90d9;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 600;
        padding: 10px 24px;
        min-height: 38px;
    }
    QPushButton:hover { background-color: #3a7bc8; }
    QPushButton:pressed { background-color: #2a6bb8; }
"""
# Paleta semántica de acento para tarjetas (misma que las list widgets)
_CARD_ACCENTS = {
    "total":          "#4a90d9",  # azul — totales / conteos
    "monto_total":    "#48bb78",  # verde — dinero positivo
    "valor_ponderado":"#48bb78",
    "monto_ganado":   "#48bb78",
    "ticket_prom":    "#48bb78",
    "dias_promedio":  "#718096",  # gris — tiempo
    "dias_prom":      "#718096",
    "conv_promedio":  "#ed8936",  # naranja — porcentajes de conversión
    "apertura_prom":  "#ed8936",
    "clics_prom":     "#ed8936",
    "entrega_prom":   "#4a90d9",
    "ganadas":        "#48bb78",
    "total_opps":     "#4a90d9",
    "total_etapas":   "#4a90d9",
    "total_acts":     "#4a90d9",
    "sin_actividad":  "#f56565",  # rojo — contactos sin actividad
    "total_campanas": "#4a90d9",
}
_DEFAULT_ACCENT = "#4a90d9"


# ------------------------------------------------------------------ #
# Helpers de widgets dinámicos                                        #
# ------------------------------------------------------------------ #

def _make_stat_card(label_text, value="—", accent=_DEFAULT_ACCENT):
    """Tarjeta de resumen — mismo estilo que las list widgets del sistema."""
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            border-left: 4px solid {accent};
        }}
    """)
    frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    frame.setMaximumHeight(80)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 12, 16, 12)
    layout.setSpacing(4)

    lbl_val = QLabel(str(value))
    lbl_val.setStyleSheet(
        f"font-size: 28px; font-weight: bold; color: {accent}; border: none;"
    )
    lbl_val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    lbl_name = QLabel(label_text)
    lbl_name.setStyleSheet("font-size: 12px; color: #718096; font-weight: 500; border: none;")
    lbl_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    layout.addWidget(lbl_val)
    layout.addWidget(lbl_name)
    return frame, lbl_val


def _make_table(cabeceras):
    tabla = QTableWidget()
    tabla.setColumnCount(len(cabeceras))
    tabla.setHorizontalHeaderLabels(cabeceras)
    tabla.setEditTriggers(QTableWidget.NoEditTriggers)
    tabla.setSelectionBehavior(QTableWidget.SelectRows)
    tabla.setAlternatingRowColors(True)
    tabla.horizontalHeader().setStretchLastSection(True)
    tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    tabla.verticalHeader().setVisible(False)
    tabla.verticalHeader().setDefaultSectionSize(36)
    tabla.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    return tabla


def _llenar_tabla(tabla, datos, columnas):
    tabla.setRowCount(0)
    for fila in datos:
        row = tabla.rowCount()
        tabla.insertRow(row)
        for col_idx, col_key in enumerate(columnas):
            valor = fila.get(col_key, "")
            if valor is None:
                valor = ""
            item = QTableWidgetItem(str(valor))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            tabla.setItem(row, col_idx, item)
    tabla.resizeColumnsToContents()


# ------------------------------------------------------------------ #
# ReportesView                                                        #
# ------------------------------------------------------------------ #

class ReportesView(QWidget):

    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self._usuario = usuario
        self._service = ReporteService()
        self._datos_cache = {k: [] for k in REPORTES}
        self._cargados = set()   # claves de reportes ya consultados al menos una vez

        uic.loadUi(UI_PATH, self)
        self._init_filtro_fecha()
        self._populate_tabs()

    # ---------------------------------------------------------------- #
    # Filtro de período                                                #
    # ---------------------------------------------------------------- #

    def _init_filtro_fecha(self):
        """Inicializa las fechas por defecto y conecta las señales."""
        hoy = QDate.currentDate()
        self.dtDesde.setDate(QDate(hoy.year(), 1, 1))  # 1 ene del año en curso
        self.dtHasta.setDate(hoy)
        self.dtDesde.dateChanged.connect(self._on_fecha_changed)
        self.dtHasta.dateChanged.connect(self._on_fecha_changed)

    def _on_fecha_changed(self):
        """Recarga el tab activo desde la BD cuando cambia el rango de fechas."""
        tab_idx = self.reportesTabs.currentIndex()
        claves = list(REPORTES.keys())
        if 0 <= tab_idx < len(claves):
            clave = claves[tab_idx]
            # Solo recargar si el reporte fue cargado antes y admite filtro de fecha
            if clave in _REPORTES_CON_FECHA and clave in self._cargados:
                self._cargar_reporte(clave)

    # ---------------------------------------------------------------- #
    # Población de tabs desde el .ui                                   #
    # ---------------------------------------------------------------- #

    def _populate_tabs(self):
        """Agrega contenido dinámico a los layouts de cada tab definidos en el .ui."""
        tab_layouts = {
            "pipeline":   self.tabPipelineLayout,
            "vendedores": self.tabVendedoresLayout,
            "etapas":     self.tabEtapasLayout,
            "campanas":   self.tabCampanasLayout,
            "actividad":  self.tabActividadLayout,
        }

        self._tab_data = {}
        for clave, layout in tab_layouts.items():
            self._tab_data[clave] = self._populate_tab_layout(clave, layout)

        self.reportesTabs.currentChanged.connect(self._on_tab_changed)

    def _populate_tab_layout(self, clave, layout):
        """Rellena un layout de tab con botones, tarjetas de resumen y tabla."""
        cfg = REPORTES[clave]

        # fila superior: título del reporte + botones de acción
        top_row = QHBoxLayout()

        lbl = QLabel(cfg["titulo"])
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a1a2e;")
        top_row.addWidget(lbl)
        top_row.addStretch()

        btn_refresh = QPushButton("Actualizar")
        btn_refresh.setStyleSheet(_STYLE_BTN_REFRESH)
        btn_refresh.setFixedWidth(120)

        btn_excel = QPushButton("Exportar Excel")
        btn_excel.setStyleSheet(_STYLE_BTN_EXCEL)
        btn_excel.setFixedWidth(150)

        btn_pdf = QPushButton("Exportar PDF")
        btn_pdf.setStyleSheet(_STYLE_BTN_PDF)
        btn_pdf.setFixedWidth(140)

        top_row.addWidget(btn_refresh)
        top_row.addWidget(btn_excel)
        top_row.addWidget(btn_pdf)
        layout.addLayout(top_row)

        # tarjetas de resumen
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        stat_cards = {}
        for stat_key, stat_label in self._stat_defs(clave):
            accent = _CARD_ACCENTS.get(stat_key, _DEFAULT_ACCENT)
            frame, lbl_val = _make_stat_card(stat_label, accent=accent)
            cards_row.addWidget(frame)
            stat_cards[stat_key] = lbl_val
        layout.addLayout(cards_row)

        # tabla de datos
        tabla = _make_table(cfg["cabeceras"])
        layout.addWidget(tabla)

        # mensaje de estado vacío
        lbl_vacio = QLabel("Sin datos disponibles. Haz clic en Actualizar.")
        lbl_vacio.setAlignment(Qt.AlignCenter)
        lbl_vacio.setStyleSheet("color: #a0aec0; font-size: 14px; padding: 40px;")
        lbl_vacio.hide()
        layout.addWidget(lbl_vacio)

        # conectar botones
        btn_refresh.clicked.connect(lambda _, c=clave: self._cargar_reporte(c))
        btn_excel.clicked.connect(lambda _, c=clave: self._exportar(c, "excel"))
        btn_pdf.clicked.connect(lambda _, c=clave: self._exportar(c, "pdf"))

        return {
            "tabla":       tabla,
            "btn_refresh": btn_refresh,
            "btn_excel":   btn_excel,
            "btn_pdf":     btn_pdf,
            "stat_cards":  stat_cards,
            "lbl_vacio":   lbl_vacio,
        }

    def _stat_defs(self, clave):
        """Retorna lista de (stat_key, label) para las tarjetas de resumen."""
        if clave == "pipeline":
            return [
                ("total",           "Oportunidades"),
                ("monto_total",     "Monto Total"),
                ("valor_ponderado", "Valor Ponderado"),
                ("dias_promedio",   "Días Prom. Pipeline"),
            ]
        if clave == "vendedores":
            return [
                ("total",          "Vendedores"),
                ("ganadas",        "Oportunidades Ganadas"),
                ("monto_ganado",   "Monto Total Ganado"),
                ("conv_promedio",  "Conv. Promedio %"),
            ]
        if clave == "etapas":
            return [
                ("total_etapas", "Etapas"),
                ("total_opps",   "Total Oportunidades"),
                ("monto_total",  "Monto Total"),
                ("ticket_prom",  "Ticket Promedio"),
            ]
        if clave == "campanas":
            return [
                ("total",         "Campañas"),
                ("apertura_prom", "Apertura Promedio %"),
                ("clics_prom",    "Clics Promedio %"),
                ("entrega_prom",  "Entrega Promedio %"),
            ]
        if clave == "actividad":
            return [
                ("total",         "Contactos"),
                ("sin_actividad", "Sin Actividad Reciente"),
                ("total_acts",    "Total Actividades"),
                ("dias_prom",     "Días Prom. sin Contacto"),
            ]
        return []

    # ---------------------------------------------------------------- #
    # Carga de datos                                                    #
    # ---------------------------------------------------------------- #

    def cargar_datos(self):
        """Llamado desde main_view al mostrar este módulo."""
        tab_idx = self.reportesTabs.currentIndex()
        claves = list(REPORTES.keys())
        if 0 <= tab_idx < len(claves):
            self._cargar_reporte(claves[tab_idx])

    def _on_tab_changed(self, idx):
        claves = list(REPORTES.keys())
        if 0 <= idx < len(claves):
            clave = claves[idx]
            if clave not in self._cargados:
                self._cargar_reporte(clave)

    def _cargar_reporte(self, clave):
        metodos = {
            "pipeline":   self._service.obtener_pipeline_ventas,
            "vendedores": self._service.obtener_rendimiento_vendedores,
            "etapas":     self._service.obtener_conversion_etapas,
            "campanas":   self._service.obtener_analisis_campanas,
            "actividad":  self._service.obtener_actividad_contactos,
        }

        # Pasar fechas a los reportes que admiten filtro temporal
        kwargs = {}
        if clave in _REPORTES_CON_FECHA:
            kwargs["fecha_desde"] = self.dtDesde.date().toPyDate()
            kwargs["fecha_hasta"] = self.dtHasta.date().toPyDate()

        datos, error = metodos[clave](**kwargs)
        tab = self._tab_data[clave]

        if error:
            QMessageBox.warning(self, "Error al cargar reporte", error)
            return

        self._datos_cache[clave] = datos or []
        self._cargados.add(clave)
        self._mostrar_datos(clave)

    def _mostrar_datos(self, clave):
        """Actualiza la tabla y las tarjetas con los datos en caché."""
        tab = self._tab_data[clave]
        cfg = REPORTES[clave]
        datos = self._datos_cache[clave]

        _llenar_tabla(tab["tabla"], datos, cfg["columnas"])

        vacio = len(datos) == 0
        tab["lbl_vacio"].setVisible(vacio)
        tab["tabla"].setVisible(not vacio)

        self._actualizar_stats(clave, datos, tab["stat_cards"])

    def _actualizar_stats(self, clave, datos, stat_cards):
        n = len(datos)

        def fmt_dinero(v):
            try:
                return f"${float(v):,.0f}"
            except Exception:
                return str(v)

        def prom(key):
            vals = [float(d.get(key) or 0) for d in datos]
            return round(sum(vals) / len(vals), 1) if vals else 0

        if clave == "pipeline":
            monto = sum(float(d.get("MontoEstimado") or 0) for d in datos)
            pond  = sum(float(d.get("ValorPonderado") or 0) for d in datos)
            dias  = prom("DiasEnPipeline")
            stat_cards.get("total",           QLabel()).setText(str(n))
            stat_cards.get("monto_total",     QLabel()).setText(fmt_dinero(monto))
            stat_cards.get("valor_ponderado", QLabel()).setText(fmt_dinero(pond))
            stat_cards.get("dias_promedio",   QLabel()).setText(str(int(dias)))

        elif clave == "vendedores":
            ganadas = sum(int(d.get("OportunidadesGanadas") or 0) for d in datos)
            monto   = sum(float(d.get("MontoGanado") or 0) for d in datos)
            conv    = prom("TasaConversion")
            stat_cards.get("total",         QLabel()).setText(str(n))
            stat_cards.get("ganadas",       QLabel()).setText(str(ganadas))
            stat_cards.get("monto_ganado",  QLabel()).setText(fmt_dinero(monto))
            stat_cards.get("conv_promedio", QLabel()).setText(f"{conv}%")

        elif clave == "etapas":
            total_opps = sum(int(d.get("TotalOportunidades") or 0) for d in datos)
            monto      = sum(float(d.get("MontoTotal") or 0) for d in datos)
            ticket     = prom("TicketPromedio")
            stat_cards.get("total_etapas", QLabel()).setText(str(n))
            stat_cards.get("total_opps",   QLabel()).setText(str(total_opps))
            stat_cards.get("monto_total",  QLabel()).setText(fmt_dinero(monto))
            stat_cards.get("ticket_prom",  QLabel()).setText(fmt_dinero(ticket))

        elif clave == "campanas":
            apertura = prom("TasaApertura")
            clics    = prom("TasaClics")
            entrega  = prom("TasaEntrega")
            stat_cards.get("total",          QLabel()).setText(str(n))
            stat_cards.get("apertura_prom",  QLabel()).setText(f"{apertura}%")
            stat_cards.get("clics_prom",     QLabel()).setText(f"{clics}%")
            stat_cards.get("entrega_prom",   QLabel()).setText(f"{entrega}%")

        elif clave == "actividad":
            sin_act    = sum(1 for d in datos if (d.get("TotalActividades") or 0) == 0)
            total_acts = sum(int(d.get("TotalActividades") or 0) for d in datos)
            dias       = prom("DiasSinContacto")
            stat_cards.get("total",          QLabel()).setText(str(n))
            stat_cards.get("sin_actividad",  QLabel()).setText(str(sin_act))
            stat_cards.get("total_acts",     QLabel()).setText(str(total_acts))
            stat_cards.get("dias_prom",      QLabel()).setText(str(int(dias)))

    # ---------------------------------------------------------------- #
    # Exportar                                                          #
    # ---------------------------------------------------------------- #

    def _exportar(self, clave, formato):
        # exportar exactamente lo que está visible (datos del rango activo)
        datos = self._datos_cache.get(clave, [])
        if not datos:
            QMessageBox.information(
                self, "Sin datos",
                "No hay datos para exportar. Haz clic en Actualizar primero."
            )
            return

        cfg    = REPORTES[clave]
        titulo = cfg["titulo"]

        if formato == "excel":
            ruta, _ = QFileDialog.getSaveFileName(
                self,
                f"Exportar {titulo} a Excel",
                os.path.expanduser(f"~/Reporte_{clave}.xlsx"),
                "Excel (*.xlsx)",
            )
            if not ruta:
                return
            ok, error = self._service.exportar_excel(clave, datos, ruta)
        else:
            ruta, _ = QFileDialog.getSaveFileName(
                self,
                f"Exportar {titulo} a PDF",
                os.path.expanduser(f"~/Reporte_{clave}.pdf"),
                "PDF (*.pdf)",
            )
            if not ruta:
                return
            ok, error = self._service.exportar_pdf(clave, datos, ruta)

        if error:
            QMessageBox.critical(self, "Error al exportar", error)
        else:
            QMessageBox.information(
                self,
                "Exportación exitosa",
                f"Reporte exportado correctamente.\n\nArchivo guardado en:\n{ruta}"
            )
