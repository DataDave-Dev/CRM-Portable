# Vista de Comunicación - Plantillas, Campañas y Configuración de Correo

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QCheckBox,
    QSpinBox, QMessageBox, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5 import uic

from app.database.connection import get_connection
from app.services.campana_service import CampanaService

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "comunicacion", "comunicacion_view.ui")

_STYLE_BTN_PRIMARY = """
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
_STYLE_BTN_SECONDARY = """
    QPushButton {
        background-color: #e2e8f0;
        color: #4a5568;
        border: none;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        padding: 8px 18px;
        min-height: 34px;
    }
    QPushButton:hover { background-color: #cbd5e0; }
"""
_STYLE_BTN_DANGER = """
    QPushButton {
        background-color: transparent;
        color: #e53e3e;
        border: 1px solid #e53e3e;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        padding: 8px 18px;
        min-height: 34px;
    }
    QPushButton:hover { background-color: #fff5f5; }
"""
_STYLE_BTN_SUCCESS = """
    QPushButton {
        background-color: #38a169;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        padding: 8px 18px;
        min-height: 34px;
    }
    QPushButton:hover { background-color: #2f855a; }
"""
_STYLE_INPUT = """
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox {
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        background-color: white;
        color: #2d3748;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {
        border-color: #4a90d9;
    }
"""
_STYLE_COMBO = """
    QComboBox {
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        background-color: white;
        color: #2d3748;
        min-height: 36px;
    }
    QComboBox:focus { border-color: #4a90d9; }
    QComboBox::drop-down { border: none; width: 20px; }
"""
_STYLE_TABLE = """
    QTableWidget {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: #f0f2f5;
        font-size: 13px;
    }
    QTableWidget QHeaderView::section {
        background-color: #f7fafc;
        color: #2d3748;
        font-weight: bold;
        font-size: 13px;
        padding: 10px 8px;
        border: none;
        border-bottom: 2px solid #e2e8f0;
    }
    QTableWidget::item {
        padding: 10px 8px;
        color: #2d3748;
        border-bottom: 1px solid #f0f2f5;
    }
    QTableWidget::item:selected {
        background-color: #ebf8ff;
        color: #2c5282;
    }
    QTableWidget::item:hover { background-color: #f7fafc; }
"""
_STYLE_CARD = """
    QFrame {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
"""
_ESTADO_COLORES = {
    "Borrador":    "#718096",
    "Programada":  "#d97706",
    "En Progreso": "#2b6cb0",
    "Completada":  "#276749",
    "Cancelada":   "#c53030",
}


def _make_label(text, font_size=13, bold=False, color="#2d3748"):
    lbl = QLabel(text)
    style = f"font-size: {font_size}px; color: {color};"
    if bold:
        style += " font-weight: bold;"
    lbl.setStyleSheet(style)
    return lbl


def _make_stat_card(value_text, label_text, accent_color):
    frame = QFrame()
    frame.setMaximumHeight(80)
    frame.setStyleSheet(
        f"QFrame {{ background-color: white; border: 1px solid #e2e8f0; "
        f"border-radius: 8px; border-left: 4px solid {accent_color}; }}"
    )
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(16, 10, 16, 10)
    lay.setSpacing(3)
    val = QLabel(value_text)
    val.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {accent_color}; border: none;")
    lbl = QLabel(label_text)
    lbl.setStyleSheet("font-size: 12px; color: #718096; font-weight: 500; border: none;")
    lay.addWidget(val)
    lay.addWidget(lbl)
    return frame, val


def _setup_table(table, headers, stretch_col=1):
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionMode(QTableWidget.SingleSelection)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setStyleSheet(_STYLE_TABLE)
    h = table.horizontalHeader()
    h.setStretchLastSection(False)
    for i in range(len(headers)):
        if i == 0:
            h.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        elif i == stretch_col:
            h.setSectionResizeMode(i, QHeaderView.Stretch)
        else:
            h.setSectionResizeMode(i, QHeaderView.Interactive)
    h.setMinimumSectionSize(60)
    v = table.verticalHeader()
    v.setVisible(False)
    v.setDefaultSectionSize(42)


class ComunicacionView(QWidget):

    def __init__(self, usuario_actual, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._usuario_actual = usuario_actual
        self._service = CampanaService()

        self._plantilla_editando = None
        self._campana_editando = None
        self._campana_detalle = None
        self._config_editando = None
        self._plantillas_cargadas = []
        self._campanas_cargadas = []
        self._configs_cargadas = []

        self._build_tab_plantillas()
        self._build_tab_campanas()
        self._build_tab_config_correo()
        self._setup_tabs()

    # ==========================================
    # TABS
    # ==========================================

    def _setup_tabs(self):
        self.comunicacionTabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if index == 0:
            self._mostrar_lista_plantillas()
        elif index == 1:
            self._mostrar_lista_campanas()
        elif index == 2:
            self._mostrar_lista_configs()

    def cargar_datos(self):
        index = self.comunicacionTabs.currentIndex()
        if index == 0:
            self._cargar_tabla_plantillas()
        elif index == 1:
            self._cargar_tabla_campanas()
        elif index == 2:
            self._cargar_tabla_configs()

    # ==========================================
    # TAB PLANTILLAS - CONSTRUCCION
    # ==========================================

    def _build_tab_plantillas(self):
        # ---- LISTA ----
        self._w_plantilla_lista = QWidget()
        lay = QVBoxLayout(self._w_plantilla_lista)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)

        # header
        hdr = QHBoxLayout()
        title_lay = QVBoxLayout()
        title_lay.setSpacing(4)
        title_lay.addWidget(_make_label("Plantillas de Correo", 24, True, "#1a1a2e"))
        title_lay.addWidget(_make_label("Diseña y gestiona plantillas para tus campañas de email", 13, False, "#7f8c9b"))
        hdr.addLayout(title_lay)
        hdr.addStretch()
        self._btn_nueva_plantilla = QPushButton("+ Nueva Plantilla")
        self._btn_nueva_plantilla.setStyleSheet(_STYLE_BTN_PRIMARY)
        self._btn_nueva_plantilla.setCursor(Qt.PointingHandCursor)
        self._btn_nueva_plantilla.clicked.connect(self._mostrar_form_nueva_plantilla)
        hdr.addWidget(self._btn_nueva_plantilla)
        lay.addLayout(hdr)

        # stats
        stats_lay = QHBoxLayout()
        stats_lay.setSpacing(16)
        self._w_ptl_stat_total, self._lbl_ptl_total = _make_stat_card("0", "Total Plantillas", "#4a90d9")
        self._w_ptl_stat_activas, self._lbl_ptl_activas = _make_stat_card("0", "Activas", "#38a169")
        self._w_ptl_stat_inactivas, self._lbl_ptl_inactivas = _make_stat_card("0", "Inactivas", "#718096")
        stats_lay.addWidget(self._w_ptl_stat_total)
        stats_lay.addWidget(self._w_ptl_stat_activas)
        stats_lay.addWidget(self._w_ptl_stat_inactivas)
        lay.addLayout(stats_lay)

        # table
        self._tabla_plantillas = QTableWidget()
        _setup_table(self._tabla_plantillas, ["ID", "Nombre", "Asunto", "Categoría", "Estado", "Creado Por"], stretch_col=1)
        self._tabla_plantillas.doubleClicked.connect(self._editar_plantilla_seleccionada)
        lay.addWidget(self._tabla_plantillas)

        self.tabPlantillasLayout.addWidget(self._w_plantilla_lista)

        # ---- FORMULARIO ----
        self._w_plantilla_form = QWidget()
        flay = QVBoxLayout(self._w_plantilla_form)
        flay.setContentsMargins(0, 0, 0, 0)
        flay.setSpacing(16)

        # form header
        form_hdr = QHBoxLayout()
        form_title_lay = QVBoxLayout()
        form_title_lay.setSpacing(4)
        self._ptl_form_titulo = _make_label("Nueva Plantilla", 22, True, "#1a1a2e")
        self._ptl_form_subtitulo = _make_label("", 13, False, "#7f8c9b")
        form_title_lay.addWidget(self._ptl_form_titulo)
        form_title_lay.addWidget(self._ptl_form_subtitulo)
        form_hdr.addLayout(form_title_lay)
        form_hdr.addStretch()
        flay.addLayout(form_hdr)

        # scroll area for the form body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QVBoxLayout(body)
        body_lay.setSpacing(12)
        body_lay.setContentsMargins(0, 0, 0, 0)

        # nombre
        body_lay.addWidget(_make_label("Nombre *", 13, True))
        self._ptl_input_nombre = QLineEdit()
        self._ptl_input_nombre.setPlaceholderText("Ej. Bienvenida Nuevos Clientes")
        self._ptl_input_nombre.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._ptl_input_nombre)

        # asunto
        body_lay.addWidget(_make_label("Asunto del Correo *", 13, True))
        self._ptl_input_asunto = QLineEdit()
        self._ptl_input_asunto.setPlaceholderText("Ej. Bienvenido a nuestro servicio")
        self._ptl_input_asunto.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._ptl_input_asunto)

        # categoria
        body_lay.addWidget(_make_label("Categoría", 13, True))
        self._ptl_input_categoria = QLineEdit()
        self._ptl_input_categoria.setPlaceholderText("Ej. Marketing, Transaccional, Seguimiento")
        self._ptl_input_categoria.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._ptl_input_categoria)

        # contenido HTML
        body_lay.addWidget(_make_label("Contenido HTML *", 13, True))
        self._ptl_input_html = QTextEdit()
        self._ptl_input_html.setPlaceholderText(
            "<html>\n<body>\n  <h1>Hola {nombre},</h1>\n  <p>Bienvenido a nuestro servicio.</p>\n</body>\n</html>"
        )
        self._ptl_input_html.setMinimumHeight(200)
        self._ptl_input_html.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._ptl_input_html)

        # contenido texto plano
        body_lay.addWidget(_make_label("Contenido Texto Plano (alternativo)", 13, True))
        self._ptl_input_texto = QTextEdit()
        self._ptl_input_texto.setPlaceholderText("Versión de texto plano del correo (para clientes sin soporte HTML)")
        self._ptl_input_texto.setMinimumHeight(100)
        self._ptl_input_texto.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._ptl_input_texto)

        # activa
        self._ptl_check_activa = QCheckBox("Plantilla activa")
        self._ptl_check_activa.setChecked(True)
        self._ptl_check_activa.setStyleSheet("font-size: 13px; color: #2d3748;")
        body_lay.addWidget(self._ptl_check_activa)

        body_lay.addStretch()
        scroll.setWidget(body)
        flay.addWidget(scroll)

        # botones
        btn_row = QHBoxLayout()
        self._ptl_btn_cancelar = QPushButton("Cancelar")
        self._ptl_btn_cancelar.setStyleSheet(_STYLE_BTN_SECONDARY)
        self._ptl_btn_cancelar.setCursor(Qt.PointingHandCursor)
        self._ptl_btn_cancelar.clicked.connect(self._mostrar_lista_plantillas)
        self._ptl_btn_limpiar = QPushButton("Limpiar")
        self._ptl_btn_limpiar.setStyleSheet(_STYLE_BTN_SECONDARY)
        self._ptl_btn_limpiar.setCursor(Qt.PointingHandCursor)
        self._ptl_btn_limpiar.clicked.connect(self._limpiar_form_plantilla)
        self._ptl_btn_guardar = QPushButton("Guardar Plantilla")
        self._ptl_btn_guardar.setStyleSheet(_STYLE_BTN_PRIMARY)
        self._ptl_btn_guardar.setCursor(Qt.PointingHandCursor)
        self._ptl_btn_guardar.clicked.connect(self._guardar_plantilla)
        btn_row.addWidget(self._ptl_btn_cancelar)
        btn_row.addWidget(self._ptl_btn_limpiar)
        btn_row.addStretch()
        btn_row.addWidget(self._ptl_btn_guardar)
        flay.addLayout(btn_row)

        self._w_plantilla_form.hide()
        self.tabPlantillasLayout.addWidget(self._w_plantilla_form)

    # ==========================================
    # TAB CAMPANAS - CONSTRUCCION
    # ==========================================

    def _build_tab_campanas(self):
        # ---- LISTA ----
        self._w_campana_lista = QWidget()
        lay = QVBoxLayout(self._w_campana_lista)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)

        # header
        hdr = QHBoxLayout()
        title_lay = QVBoxLayout()
        title_lay.setSpacing(4)
        title_lay.addWidget(_make_label("Campañas de Comunicación", 24, True, "#1a1a2e"))
        title_lay.addWidget(_make_label("Gestiona campañas de email y sus destinatarios", 13, False, "#7f8c9b"))
        hdr.addLayout(title_lay)
        hdr.addStretch()
        self._btn_nueva_campana = QPushButton("+ Nueva Campaña")
        self._btn_nueva_campana.setStyleSheet(_STYLE_BTN_PRIMARY)
        self._btn_nueva_campana.setCursor(Qt.PointingHandCursor)
        self._btn_nueva_campana.clicked.connect(self._mostrar_form_nueva_campana)
        hdr.addWidget(self._btn_nueva_campana)
        lay.addLayout(hdr)

        # stats
        stats_lay = QHBoxLayout()
        stats_lay.setSpacing(16)
        self._w_camp_stat_total, self._lbl_camp_total = _make_stat_card("0", "Total Campañas", "#4a90d9")
        self._w_camp_stat_borrador, self._lbl_camp_borrador = _make_stat_card("0", "Borrador", "#718096")
        self._w_camp_stat_progreso, self._lbl_camp_progreso = _make_stat_card("0", "En Progreso", "#2b6cb0")
        self._w_camp_stat_completas, self._lbl_camp_completas = _make_stat_card("0", "Completadas", "#276749")
        stats_lay.addWidget(self._w_camp_stat_total)
        stats_lay.addWidget(self._w_camp_stat_borrador)
        stats_lay.addWidget(self._w_camp_stat_progreso)
        stats_lay.addWidget(self._w_camp_stat_completas)
        lay.addLayout(stats_lay)

        # table
        self._tabla_campanas = QTableWidget()
        _setup_table(
            self._tabla_campanas,
            ["ID", "Nombre", "Tipo", "Estado", "Destinatarios", "Enviados", "% Apertura", "Fecha"],
            stretch_col=1,
        )
        self._tabla_campanas.doubleClicked.connect(self._ver_detalle_campana)
        lay.addWidget(self._tabla_campanas)

        self.tabCampanasLayout.addWidget(self._w_campana_lista)

        # ---- FORMULARIO ----
        self._w_campana_form = QWidget()
        flay = QVBoxLayout(self._w_campana_form)
        flay.setContentsMargins(0, 0, 0, 0)
        flay.setSpacing(16)

        form_hdr = QHBoxLayout()
        form_title_lay = QVBoxLayout()
        form_title_lay.setSpacing(4)
        self._camp_form_titulo = _make_label("Nueva Campaña", 22, True, "#1a1a2e")
        self._camp_form_subtitulo = _make_label("", 13, False, "#7f8c9b")
        form_title_lay.addWidget(self._camp_form_titulo)
        form_title_lay.addWidget(self._camp_form_subtitulo)
        form_hdr.addLayout(form_title_lay)
        form_hdr.addStretch()
        flay.addLayout(form_hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QVBoxLayout(body)
        body_lay.setSpacing(12)
        body_lay.setContentsMargins(0, 0, 0, 0)

        # nombre
        body_lay.addWidget(_make_label("Nombre *", 13, True))
        self._camp_input_nombre = QLineEdit()
        self._camp_input_nombre.setPlaceholderText("Ej. Campaña Q1 Enero 2026")
        self._camp_input_nombre.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._camp_input_nombre)

        # descripcion
        body_lay.addWidget(_make_label("Descripción", 13, True))
        self._camp_input_descripcion = QTextEdit()
        self._camp_input_descripcion.setPlaceholderText("Describe el objetivo y alcance de esta campaña")
        self._camp_input_descripcion.setMaximumHeight(80)
        self._camp_input_descripcion.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._camp_input_descripcion)

        # tipo y estado en fila
        tipo_est_row = QHBoxLayout()
        tipo_col = QVBoxLayout()
        tipo_col.setSpacing(6)
        tipo_col.addWidget(_make_label("Tipo", 13, True))
        self._camp_combo_tipo = QComboBox()
        self._camp_combo_tipo.setStyleSheet(_STYLE_COMBO)
        self._camp_combo_tipo.addItem("-- Sin tipo --", None)
        for t in self._service.tipos_campana:
            self._camp_combo_tipo.addItem(t, t)
        tipo_col.addWidget(self._camp_combo_tipo)
        tipo_est_row.addLayout(tipo_col)

        estado_col = QVBoxLayout()
        estado_col.setSpacing(6)
        estado_col.addWidget(_make_label("Estado", 13, True))
        self._camp_combo_estado = QComboBox()
        self._camp_combo_estado.setStyleSheet(_STYLE_COMBO)
        for e in self._service.estados_campana:
            self._camp_combo_estado.addItem(e, e)
        estado_col.addWidget(self._camp_combo_estado)
        tipo_est_row.addLayout(estado_col)
        body_lay.addLayout(tipo_est_row)

        # plantilla
        body_lay.addWidget(_make_label("Plantilla de Correo", 13, True))
        self._camp_combo_plantilla = QComboBox()
        self._camp_combo_plantilla.setStyleSheet(_STYLE_COMBO)
        body_lay.addWidget(self._camp_combo_plantilla)

        # segmento
        body_lay.addWidget(_make_label("Segmento de Contactos (para carga masiva)", 13, True))
        self._camp_combo_segmento = QComboBox()
        self._camp_combo_segmento.setStyleSheet(_STYLE_COMBO)
        body_lay.addWidget(self._camp_combo_segmento)

        # fecha programada
        body_lay.addWidget(_make_label("Fecha Programada", 13, True))
        self._camp_input_fecha = QLineEdit()
        self._camp_input_fecha.setPlaceholderText("YYYY-MM-DD HH:MM")
        self._camp_input_fecha.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._camp_input_fecha)

        # presupuesto
        body_lay.addWidget(_make_label("Presupuesto (opcional)", 13, True))
        self._camp_input_presupuesto = QLineEdit()
        self._camp_input_presupuesto.setPlaceholderText("0.00")
        self._camp_input_presupuesto.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._camp_input_presupuesto)

        body_lay.addStretch()
        scroll.setWidget(body)
        flay.addWidget(scroll)

        btn_row = QHBoxLayout()
        self._camp_btn_cancelar = QPushButton("Cancelar")
        self._camp_btn_cancelar.setStyleSheet(_STYLE_BTN_SECONDARY)
        self._camp_btn_cancelar.setCursor(Qt.PointingHandCursor)
        self._camp_btn_cancelar.clicked.connect(self._mostrar_lista_campanas)
        self._camp_btn_limpiar = QPushButton("Limpiar")
        self._camp_btn_limpiar.setStyleSheet(_STYLE_BTN_SECONDARY)
        self._camp_btn_limpiar.setCursor(Qt.PointingHandCursor)
        self._camp_btn_limpiar.clicked.connect(self._limpiar_form_campana)
        self._camp_btn_guardar = QPushButton("Guardar Campaña")
        self._camp_btn_guardar.setStyleSheet(_STYLE_BTN_PRIMARY)
        self._camp_btn_guardar.setCursor(Qt.PointingHandCursor)
        self._camp_btn_guardar.clicked.connect(self._guardar_campana)
        btn_row.addWidget(self._camp_btn_cancelar)
        btn_row.addWidget(self._camp_btn_limpiar)
        btn_row.addStretch()
        btn_row.addWidget(self._camp_btn_guardar)
        flay.addLayout(btn_row)

        self._w_campana_form.hide()
        self.tabCampanasLayout.addWidget(self._w_campana_form)

        # ---- DETALLE DE CAMPANA ----
        self._w_campana_detalle = QWidget()
        dlay = QVBoxLayout(self._w_campana_detalle)
        dlay.setContentsMargins(0, 0, 0, 0)
        dlay.setSpacing(16)

        # header detalle
        det_hdr = QHBoxLayout()
        det_title_lay = QVBoxLayout()
        det_title_lay.setSpacing(4)
        self._det_titulo = _make_label("Campaña", 22, True, "#1a1a2e")
        self._det_estado_lbl = _make_label("Borrador", 13)
        det_title_lay.addWidget(self._det_titulo)
        det_title_lay.addWidget(self._det_estado_lbl)
        det_hdr.addLayout(det_title_lay)
        det_hdr.addStretch()
        self._det_btn_editar = QPushButton("Editar")
        self._det_btn_editar.setStyleSheet(_STYLE_BTN_SECONDARY)
        self._det_btn_editar.setCursor(Qt.PointingHandCursor)
        self._det_btn_editar.clicked.connect(self._editar_campana_desde_detalle)
        self._det_btn_eliminar = QPushButton("Eliminar")
        self._det_btn_eliminar.setStyleSheet(_STYLE_BTN_DANGER)
        self._det_btn_eliminar.setCursor(Qt.PointingHandCursor)
        self._det_btn_eliminar.clicked.connect(self._eliminar_campana_desde_detalle)
        self._det_btn_volver = QPushButton("Volver")
        self._det_btn_volver.setStyleSheet(_STYLE_BTN_SECONDARY)
        self._det_btn_volver.setCursor(Qt.PointingHandCursor)
        self._det_btn_volver.clicked.connect(self._mostrar_lista_campanas)
        det_hdr.addWidget(self._det_btn_volver)
        det_hdr.addWidget(self._det_btn_editar)
        det_hdr.addWidget(self._det_btn_eliminar)
        dlay.addLayout(det_hdr)

        # metricas
        met_lay = QHBoxLayout()
        met_lay.setSpacing(12)
        self._w_met_dest, self._lbl_met_dest = _make_stat_card("0", "Destinatarios", "#4a90d9")
        self._w_met_env, self._lbl_met_env = _make_stat_card("0", "Enviados", "#38a169")
        self._w_met_ab, self._lbl_met_ab = _make_stat_card("0%", "% Apertura", "#d97706")
        self._w_met_clic, self._lbl_met_clic = _make_stat_card("0%", "% Clics", "#9f7aea")
        self._w_met_reb, self._lbl_met_reb = _make_stat_card("0", "Rebotados", "#e53e3e")
        met_lay.addWidget(self._w_met_dest)
        met_lay.addWidget(self._w_met_env)
        met_lay.addWidget(self._w_met_ab)
        met_lay.addWidget(self._w_met_clic)
        met_lay.addWidget(self._w_met_reb)
        dlay.addLayout(met_lay)

        # destinatarios header
        dest_hdr = QHBoxLayout()
        dest_hdr.addWidget(_make_label("Destinatarios", 16, True, "#1a1a2e"))
        dest_hdr.addStretch()

        # agregar destinatario individual
        self._det_combo_contacto = QComboBox()
        self._det_combo_contacto.setStyleSheet(_STYLE_COMBO)
        self._det_combo_contacto.setMinimumWidth(240)
        dest_hdr.addWidget(self._det_combo_contacto)

        self._det_btn_add_dest = QPushButton("+ Agregar")
        self._det_btn_add_dest.setStyleSheet(_STYLE_BTN_PRIMARY)
        self._det_btn_add_dest.setCursor(Qt.PointingHandCursor)
        self._det_btn_add_dest.clicked.connect(self._agregar_destinatario)
        dest_hdr.addWidget(self._det_btn_add_dest)

        self._det_btn_cargar_segmento = QPushButton("Cargar desde Segmento")
        self._det_btn_cargar_segmento.setStyleSheet(_STYLE_BTN_SUCCESS)
        self._det_btn_cargar_segmento.setCursor(Qt.PointingHandCursor)
        self._det_btn_cargar_segmento.clicked.connect(self._cargar_desde_segmento)
        dest_hdr.addWidget(self._det_btn_cargar_segmento)

        self._det_btn_quitar_dest = QPushButton("Quitar")
        self._det_btn_quitar_dest.setStyleSheet(_STYLE_BTN_DANGER)
        self._det_btn_quitar_dest.setCursor(Qt.PointingHandCursor)
        self._det_btn_quitar_dest.clicked.connect(self._quitar_destinatario)
        dest_hdr.addWidget(self._det_btn_quitar_dest)
        dlay.addLayout(dest_hdr)

        # tabla destinatarios
        self._tabla_destinatarios = QTableWidget()
        _setup_table(
            self._tabla_destinatarios,
            ["ID", "Contacto", "Email Destino", "Estado Envio", "Fecha Envio"],
            stretch_col=1,
        )
        dlay.addWidget(self._tabla_destinatarios)

        self._w_campana_detalle.hide()
        self.tabCampanasLayout.addWidget(self._w_campana_detalle)

    # ==========================================
    # TAB CONFIG CORREO - CONSTRUCCION
    # ==========================================

    def _build_tab_config_correo(self):
        # ---- LISTA ----
        self._w_config_lista = QWidget()
        lay = QVBoxLayout(self._w_config_lista)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)

        hdr = QHBoxLayout()
        title_lay = QVBoxLayout()
        title_lay.setSpacing(4)
        title_lay.addWidget(_make_label("Configuración de Correo", 24, True, "#1a1a2e"))
        title_lay.addWidget(_make_label(
            "Administra las cuentas de correo para envío masivo (Gmail, SMTP, SendGrid, etc.)",
            13, False, "#7f8c9b"
        ))
        hdr.addLayout(title_lay)
        hdr.addStretch()
        self._btn_nueva_config = QPushButton("+ Nueva Configuración")
        self._btn_nueva_config.setStyleSheet(_STYLE_BTN_PRIMARY)
        self._btn_nueva_config.setCursor(Qt.PointingHandCursor)
        self._btn_nueva_config.clicked.connect(self._mostrar_form_nueva_config)
        hdr.addWidget(self._btn_nueva_config)
        lay.addLayout(hdr)

        # stats
        stats_lay = QHBoxLayout()
        stats_lay.setSpacing(16)
        self._w_cfg_stat_total, self._lbl_cfg_total = _make_stat_card("0", "Configuraciones", "#4a90d9")
        self._w_cfg_stat_activa, self._lbl_cfg_activa = _make_stat_card("-", "Activa", "#38a169")
        stats_lay.addWidget(self._w_cfg_stat_total)
        stats_lay.addWidget(self._w_cfg_stat_activa)
        stats_lay.addStretch()
        lay.addLayout(stats_lay)

        # tabla
        self._tabla_configs = QTableWidget()
        _setup_table(
            self._tabla_configs,
            ["ID", "Nombre", "Proveedor", "Email Remitente", "Host", "Puerto", "TLS", "Activa"],
            stretch_col=1,
        )
        self._tabla_configs.doubleClicked.connect(self._editar_config_seleccionada)
        lay.addWidget(self._tabla_configs)

        # botones de accion debajo de la tabla
        action_row = QHBoxLayout()
        self._cfg_btn_activar = QPushButton("Activar Seleccionada")
        self._cfg_btn_activar.setStyleSheet(_STYLE_BTN_SUCCESS)
        self._cfg_btn_activar.setCursor(Qt.PointingHandCursor)
        self._cfg_btn_activar.clicked.connect(self._activar_config_seleccionada)
        self._cfg_btn_eliminar = QPushButton("Eliminar Seleccionada")
        self._cfg_btn_eliminar.setStyleSheet(_STYLE_BTN_DANGER)
        self._cfg_btn_eliminar.setCursor(Qt.PointingHandCursor)
        self._cfg_btn_eliminar.clicked.connect(self._eliminar_config_seleccionada)
        action_row.addWidget(self._cfg_btn_activar)
        action_row.addWidget(self._cfg_btn_eliminar)
        action_row.addStretch()
        lay.addLayout(action_row)

        self.tabConfigCorreoLayout.addWidget(self._w_config_lista)

        # ---- FORMULARIO ----
        self._w_config_form = QWidget()
        flay = QVBoxLayout(self._w_config_form)
        flay.setContentsMargins(0, 0, 0, 0)
        flay.setSpacing(16)

        form_hdr = QHBoxLayout()
        form_title_lay = QVBoxLayout()
        form_title_lay.setSpacing(4)
        self._cfg_form_titulo = _make_label("Nueva Configuración de Correo", 22, True, "#1a1a2e")
        self._cfg_form_subtitulo = _make_label("", 13, False, "#7f8c9b")
        form_title_lay.addWidget(self._cfg_form_titulo)
        form_title_lay.addWidget(self._cfg_form_subtitulo)
        form_hdr.addLayout(form_title_lay)
        form_hdr.addStretch()
        flay.addLayout(form_hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QVBoxLayout(body)
        body_lay.setSpacing(12)
        body_lay.setContentsMargins(0, 0, 0, 0)

        # nombre
        body_lay.addWidget(_make_label("Nombre de la Configuración *", 13, True))
        self._cfg_input_nombre = QLineEdit()
        self._cfg_input_nombre.setPlaceholderText("Ej. Gmail Corporativo, SMTP Empresa")
        self._cfg_input_nombre.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._cfg_input_nombre)

        # proveedor
        body_lay.addWidget(_make_label("Proveedor *", 13, True))
        self._cfg_combo_proveedor = QComboBox()
        self._cfg_combo_proveedor.setStyleSheet(_STYLE_COMBO)
        for prov in self._service.proveedores_correo:
            self._cfg_combo_proveedor.addItem(prov, prov)
        self._cfg_combo_proveedor.currentTextChanged.connect(self._on_proveedor_changed)
        body_lay.addWidget(self._cfg_combo_proveedor)

        # host y puerto en fila
        host_puerto_row = QHBoxLayout()
        host_col = QVBoxLayout()
        host_col.setSpacing(6)
        host_col.addWidget(_make_label("Host SMTP", 13, True))
        self._cfg_input_host = QLineEdit()
        self._cfg_input_host.setPlaceholderText("Ej. smtp.gmail.com")
        self._cfg_input_host.setStyleSheet(_STYLE_INPUT)
        host_col.addWidget(self._cfg_input_host)
        host_puerto_row.addLayout(host_col, 3)

        puerto_col = QVBoxLayout()
        puerto_col.setSpacing(6)
        puerto_col.addWidget(_make_label("Puerto", 13, True))
        self._cfg_input_puerto = QSpinBox()
        self._cfg_input_puerto.setRange(1, 65535)
        self._cfg_input_puerto.setValue(587)
        self._cfg_input_puerto.setStyleSheet(_STYLE_INPUT)
        puerto_col.addWidget(self._cfg_input_puerto)
        host_puerto_row.addLayout(puerto_col, 1)
        body_lay.addLayout(host_puerto_row)

        # TLS y SSL
        ssl_row = QHBoxLayout()
        self._cfg_check_tls = QCheckBox("Usar TLS (recomendado)")
        self._cfg_check_tls.setChecked(True)
        self._cfg_check_tls.setStyleSheet("font-size: 13px; color: #2d3748;")
        self._cfg_check_ssl = QCheckBox("Usar SSL")
        self._cfg_check_ssl.setChecked(False)
        self._cfg_check_ssl.setStyleSheet("font-size: 13px; color: #2d3748;")
        ssl_row.addWidget(self._cfg_check_tls)
        ssl_row.addWidget(self._cfg_check_ssl)
        ssl_row.addStretch()
        body_lay.addLayout(ssl_row)

        # email remitente y nombre
        email_nombre_row = QHBoxLayout()
        email_col = QVBoxLayout()
        email_col.setSpacing(6)
        email_col.addWidget(_make_label("Email Remitente *", 13, True))
        self._cfg_input_email = QLineEdit()
        self._cfg_input_email.setPlaceholderText("correo@empresa.com")
        self._cfg_input_email.setStyleSheet(_STYLE_INPUT)
        email_col.addWidget(self._cfg_input_email)
        email_nombre_row.addLayout(email_col, 2)

        nombre_col = QVBoxLayout()
        nombre_col.setSpacing(6)
        nombre_col.addWidget(_make_label("Nombre Remitente (visible)", 13, True))
        self._cfg_input_nombre_rem = QLineEdit()
        self._cfg_input_nombre_rem.setPlaceholderText("Ej. CRM Empresa SA de CV")
        self._cfg_input_nombre_rem.setStyleSheet(_STYLE_INPUT)
        nombre_col.addWidget(self._cfg_input_nombre_rem)
        email_nombre_row.addLayout(nombre_col, 2)
        body_lay.addLayout(email_nombre_row)

        # usuario y contraseña (SMTP)
        body_lay.addWidget(_make_label("Usuario SMTP (generalmente el mismo email)", 13, True))
        self._cfg_input_usuario = QLineEdit()
        self._cfg_input_usuario.setPlaceholderText("correo@empresa.com")
        self._cfg_input_usuario.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._cfg_input_usuario)

        body_lay.addWidget(_make_label("Contraseña / App Password", 13, True))
        pwd_row = QHBoxLayout()
        self._cfg_input_password = QLineEdit()
        self._cfg_input_password.setEchoMode(QLineEdit.Password)
        self._cfg_input_password.setPlaceholderText("Contraseña de la cuenta o App Password")
        self._cfg_input_password.setStyleSheet(_STYLE_INPUT)
        self._cfg_btn_show_pwd = QPushButton("Ver")
        self._cfg_btn_show_pwd.setStyleSheet(_STYLE_BTN_SECONDARY)
        self._cfg_btn_show_pwd.setMaximumWidth(60)
        self._cfg_btn_show_pwd.setCursor(Qt.PointingHandCursor)
        self._cfg_btn_show_pwd.clicked.connect(self._toggle_password)
        pwd_row.addWidget(self._cfg_input_password)
        pwd_row.addWidget(self._cfg_btn_show_pwd)
        body_lay.addLayout(pwd_row)

        # API Key (para SendGrid/Mailgun)
        self._cfg_lbl_api = _make_label("API Key (SendGrid / Mailgun)", 13, True)
        body_lay.addWidget(self._cfg_lbl_api)
        self._cfg_input_api_key = QLineEdit()
        self._cfg_input_api_key.setPlaceholderText("SG.xxxxx o key-xxxxx")
        self._cfg_input_api_key.setEchoMode(QLineEdit.Password)
        self._cfg_input_api_key.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._cfg_input_api_key)

        # notas
        body_lay.addWidget(_make_label("Notas adicionales", 13, True))
        self._cfg_input_notas = QTextEdit()
        self._cfg_input_notas.setPlaceholderText("Cualquier información adicional sobre esta configuración")
        self._cfg_input_notas.setMaximumHeight(80)
        self._cfg_input_notas.setStyleSheet(_STYLE_INPUT)
        body_lay.addWidget(self._cfg_input_notas)

        # activa
        self._cfg_check_activa = QCheckBox("Establecer como configuración activa")
        self._cfg_check_activa.setChecked(False)
        self._cfg_check_activa.setStyleSheet("font-size: 13px; color: #2d3748;")
        body_lay.addWidget(self._cfg_check_activa)

        body_lay.addStretch()
        scroll.setWidget(body)
        flay.addWidget(scroll)

        btn_row = QHBoxLayout()
        self._cfg_btn_cancelar = QPushButton("Cancelar")
        self._cfg_btn_cancelar.setStyleSheet(_STYLE_BTN_SECONDARY)
        self._cfg_btn_cancelar.setCursor(Qt.PointingHandCursor)
        self._cfg_btn_cancelar.clicked.connect(self._mostrar_lista_configs)
        self._cfg_btn_limpiar = QPushButton("Limpiar")
        self._cfg_btn_limpiar.setStyleSheet(_STYLE_BTN_SECONDARY)
        self._cfg_btn_limpiar.setCursor(Qt.PointingHandCursor)
        self._cfg_btn_limpiar.clicked.connect(self._limpiar_form_config)
        self._cfg_btn_guardar = QPushButton("Guardar Configuración")
        self._cfg_btn_guardar.setStyleSheet(_STYLE_BTN_PRIMARY)
        self._cfg_btn_guardar.setCursor(Qt.PointingHandCursor)
        self._cfg_btn_guardar.clicked.connect(self._guardar_config_correo)
        btn_row.addWidget(self._cfg_btn_cancelar)
        btn_row.addWidget(self._cfg_btn_limpiar)
        btn_row.addStretch()
        btn_row.addWidget(self._cfg_btn_guardar)
        flay.addLayout(btn_row)

        self._w_config_form.hide()
        self.tabConfigCorreoLayout.addWidget(self._w_config_form)

    # ==========================================
    # PLANTILLAS - LOGICA
    # ==========================================

    def _mostrar_lista_plantillas(self):
        self._w_plantilla_form.hide()
        self._w_plantilla_lista.show()
        self._cargar_tabla_plantillas()

    def _cargar_tabla_plantillas(self):
        plantillas, error = self._service.obtener_plantillas()
        if error:
            QMessageBox.critical(self, "Error", error)
            return

        self._plantillas_cargadas = plantillas or []
        total = len(self._plantillas_cargadas)
        activas = sum(1 for p in self._plantillas_cargadas if p.activa)
        inactivas = total - activas

        self._lbl_ptl_total.setText(str(total))
        self._lbl_ptl_activas.setText(str(activas))
        self._lbl_ptl_inactivas.setText(str(inactivas))

        self._tabla_plantillas.setRowCount(0)
        for p in self._plantillas_cargadas:
            r = self._tabla_plantillas.rowCount()
            self._tabla_plantillas.insertRow(r)
            self._tabla_plantillas.setItem(r, 0, QTableWidgetItem(str(p.plantilla_id)))
            self._tabla_plantillas.setItem(r, 1, QTableWidgetItem(p.nombre))
            self._tabla_plantillas.setItem(r, 2, QTableWidgetItem(p.asunto))
            self._tabla_plantillas.setItem(r, 3, QTableWidgetItem(p.categoria or ""))
            estado_item = QTableWidgetItem("Activa" if p.activa else "Inactiva")
            estado_item.setForeground(QColor("#276749" if p.activa else "#718096"))
            self._tabla_plantillas.setItem(r, 4, estado_item)
            self._tabla_plantillas.setItem(r, 5, QTableWidgetItem(p.nombre_creador or ""))

    def _mostrar_form_nueva_plantilla(self):
        self._plantilla_editando = None
        self._limpiar_form_plantilla()
        self._ptl_form_titulo.setText("Nueva Plantilla de Correo")
        self._ptl_form_subtitulo.setText("Completa la información de la nueva plantilla. Los campos con * son obligatorios.")
        self._ptl_btn_guardar.setText("Guardar Plantilla")
        self._w_plantilla_lista.hide()
        self._w_plantilla_form.show()

    def _editar_plantilla_seleccionada(self, index):
        row = index.row()
        id_item = self._tabla_plantillas.item(row, 0)
        if not id_item:
            return
        pid = int(id_item.text())
        plantilla = next((p for p in self._plantillas_cargadas if p.plantilla_id == pid), None)
        if not plantilla:
            return

        self._plantilla_editando = plantilla
        self._limpiar_form_plantilla()
        self._ptl_form_titulo.setText("Editar Plantilla")
        self._ptl_form_subtitulo.setText(f"Editando: {plantilla.nombre}")
        self._ptl_btn_guardar.setText("Actualizar Plantilla")

        self._ptl_input_nombre.setText(plantilla.nombre)
        self._ptl_input_asunto.setText(plantilla.asunto)
        self._ptl_input_categoria.setText(plantilla.categoria or "")
        self._ptl_input_html.setPlainText(plantilla.contenido_html or "")
        self._ptl_input_texto.setPlainText(plantilla.contenido_texto or "")
        self._ptl_check_activa.setChecked(bool(plantilla.activa))

        self._w_plantilla_lista.hide()
        self._w_plantilla_form.show()

    def _guardar_plantilla(self):
        datos = {
            "nombre": self._ptl_input_nombre.text().strip(),
            "asunto": self._ptl_input_asunto.text().strip(),
            "categoria": self._ptl_input_categoria.text().strip(),
            "contenido_html": self._ptl_input_html.toPlainText().strip(),
            "contenido_texto": self._ptl_input_texto.toPlainText().strip(),
            "activa": self._ptl_check_activa.isChecked(),
        }

        if self._plantilla_editando:
            plantilla, error = self._service.actualizar_plantilla(
                self._plantilla_editando.plantilla_id, datos
            )
            titulo_ok = "Plantilla Actualizada"
            msg_ok = "ha sido actualizada exitosamente."
        else:
            plantilla, error = self._service.crear_plantilla(datos, self._usuario_actual.usuario_id)
            titulo_ok = "Plantilla Creada"
            msg_ok = "ha sido creada exitosamente."

        if error:
            QMessageBox.critical(self, "Error", error)
        elif plantilla:
            QMessageBox.information(self, titulo_ok, f"La plantilla '{plantilla.nombre}' {msg_ok}")
            self._mostrar_lista_plantillas()

    def _limpiar_form_plantilla(self):
        self._ptl_input_nombre.clear()
        self._ptl_input_asunto.clear()
        self._ptl_input_categoria.clear()
        self._ptl_input_html.clear()
        self._ptl_input_texto.clear()
        self._ptl_check_activa.setChecked(True)
        self._ptl_input_nombre.setFocus()

    # ==========================================
    # CAMPANAS - LOGICA
    # ==========================================

    def _mostrar_lista_campanas(self):
        self._w_campana_form.hide()
        self._w_campana_detalle.hide()
        self._w_campana_lista.show()
        self._cargar_tabla_campanas()

    def _cargar_tabla_campanas(self):
        campanas, error = self._service.obtener_campanas()
        if error:
            QMessageBox.critical(self, "Error", error)
            return

        self._campanas_cargadas = campanas or []
        total = len(self._campanas_cargadas)
        borrador = sum(1 for c in self._campanas_cargadas if c.estado == "Borrador")
        progreso = sum(1 for c in self._campanas_cargadas if c.estado == "En Progreso")
        completas = sum(1 for c in self._campanas_cargadas if c.estado == "Completada")

        self._lbl_camp_total.setText(str(total))
        self._lbl_camp_borrador.setText(str(borrador))
        self._lbl_camp_progreso.setText(str(progreso))
        self._lbl_camp_completas.setText(str(completas))

        self._tabla_campanas.setRowCount(0)
        for c in self._campanas_cargadas:
            r = self._tabla_campanas.rowCount()
            self._tabla_campanas.insertRow(r)
            self._tabla_campanas.setItem(r, 0, QTableWidgetItem(str(c.campana_id)))
            self._tabla_campanas.setItem(r, 1, QTableWidgetItem(c.nombre))
            self._tabla_campanas.setItem(r, 2, QTableWidgetItem(c.tipo or ""))
            estado_item = QTableWidgetItem(c.estado or "")
            color = _ESTADO_COLORES.get(c.estado, "#718096")
            estado_item.setForeground(QColor(color))
            self._tabla_campanas.setItem(r, 3, estado_item)
            self._tabla_campanas.setItem(r, 4, QTableWidgetItem(str(c.total_destinatarios)))
            self._tabla_campanas.setItem(r, 5, QTableWidgetItem(str(c.total_enviados)))
            self._tabla_campanas.setItem(r, 6, QTableWidgetItem(f"{c.porcentaje_apertura}%"))
            self._tabla_campanas.setItem(r, 7, QTableWidgetItem(c.fecha_creacion or ""))

    def _mostrar_form_nueva_campana(self):
        self._campana_editando = None
        self._limpiar_form_campana()
        self._cargar_combos_campana()
        self._camp_form_titulo.setText("Nueva Campaña de Comunicación")
        self._camp_form_subtitulo.setText("Completa la información. El nombre es obligatorio.")
        self._camp_btn_guardar.setText("Guardar Campaña")
        self._w_campana_lista.hide()
        self._w_campana_detalle.hide()
        self._w_campana_form.show()

    def _cargar_combos_campana(self):
        # plantillas activas
        self._camp_combo_plantilla.clear()
        self._camp_combo_plantilla.addItem("-- Sin plantilla --", None)
        plantillas, _ = self._service.obtener_plantillas_activas()
        for p in (plantillas or []):
            self._camp_combo_plantilla.addItem(p.nombre, p.plantilla_id)

        # segmentos de tipo Contactos
        conn = get_connection()
        self._camp_combo_segmento.clear()
        self._camp_combo_segmento.addItem("-- Sin segmento --", None)
        cursor = conn.execute(
            "SELECT SegmentoID, Nombre FROM Segmentos WHERE TipoEntidad = 'Contactos' ORDER BY Nombre"
        )
        for row in cursor.fetchall():
            self._camp_combo_segmento.addItem(row["Nombre"], row["SegmentoID"])

    def _ver_detalle_campana(self, index):
        row = index.row()
        id_item = self._tabla_campanas.item(row, 0)
        if not id_item:
            return
        cid = int(id_item.text())
        campana = next((c for c in self._campanas_cargadas if c.campana_id == cid), None)
        if not campana:
            return

        self._campana_detalle = campana
        self._cargar_detalle_campana(campana)
        self._w_campana_lista.hide()
        self._w_campana_form.hide()
        self._w_campana_detalle.show()

    def _cargar_detalle_campana(self, campana):
        self._det_titulo.setText(campana.nombre)
        color = _ESTADO_COLORES.get(campana.estado, "#718096")
        self._det_estado_lbl.setText(campana.estado or "")
        self._det_estado_lbl.setStyleSheet(
            f"font-size: 13px; color: {color}; font-weight: 600;"
        )

        self._lbl_met_dest.setText(str(campana.total_destinatarios))
        self._lbl_met_env.setText(str(campana.total_enviados))
        self._lbl_met_ab.setText(f"{campana.porcentaje_apertura}%")
        self._lbl_met_clic.setText(f"{campana.porcentaje_clics}%")
        self._lbl_met_reb.setText(str(campana.total_rebotados))

        # combo de contactos para agregar destinatario
        conn = get_connection()
        self._det_combo_contacto.clear()
        self._det_combo_contacto.addItem("-- Seleccionar contacto --", None)
        cursor = conn.execute(
            "SELECT ContactoID, (Nombre || ' ' || ApellidoPaterno) AS NC, Email "
            "FROM Contactos WHERE Activo = 1 AND Email IS NOT NULL AND Email != '' ORDER BY Nombre"
        )
        for row in cursor.fetchall():
            label = f"{row['NC']} <{row['Email']}>"
            self._det_combo_contacto.addItem(label, (row["ContactoID"], row["Email"]))

        self._cargar_tabla_destinatarios(campana.campana_id)

    def _cargar_tabla_destinatarios(self, campana_id):
        destinatarios, error = self._service.get_destinatarios(campana_id)
        if error:
            QMessageBox.critical(self, "Error", error)
            return

        self._tabla_destinatarios.setRowCount(0)
        for d in (destinatarios or []):
            r = self._tabla_destinatarios.rowCount()
            self._tabla_destinatarios.insertRow(r)
            self._tabla_destinatarios.setItem(r, 0, QTableWidgetItem(str(d["DestinatarioID"])))
            nombre = d.get("NombreContacto") or ""
            self._tabla_destinatarios.setItem(r, 1, QTableWidgetItem(nombre))
            self._tabla_destinatarios.setItem(r, 2, QTableWidgetItem(d.get("EmailDestino") or ""))
            self._tabla_destinatarios.setItem(r, 3, QTableWidgetItem(d.get("EstadoEnvio") or "Pendiente"))
            self._tabla_destinatarios.setItem(r, 4, QTableWidgetItem(d.get("FechaEnvio") or ""))

    def _agregar_destinatario(self):
        if not self._campana_detalle:
            return
        data = self._det_combo_contacto.currentData()
        if not data:
            QMessageBox.warning(self, "Aviso", "Selecciona un contacto para agregar.")
            return
        contacto_id, email = data
        ok, error = self._service.agregar_destinatario(
            self._campana_detalle.campana_id, contacto_id, email
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_tabla_destinatarios(self._campana_detalle.campana_id)
            campana_act, _ = self._service.obtener_campana(self._campana_detalle.campana_id)
            if campana_act:
                self._campana_detalle = campana_act
                self._lbl_met_dest.setText(str(campana_act.total_destinatarios))

    def _cargar_desde_segmento(self):
        if not self._campana_detalle or not self._campana_detalle.segmento_id:
            QMessageBox.warning(
                self, "Aviso",
                "Esta campaña no tiene un segmento asignado.\n"
                "Edita la campaña y asigna un segmento de contactos primero."
            )
            return
        resp = QMessageBox.question(
            self, "Cargar Destinatarios",
            f"Se cargarán todos los contactos del segmento '{self._campana_detalle.nombre_segmento}' "
            "como destinatarios (solo los que tengan email).\n\n¿Deseas continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return
        n, error = self._service.cargar_desde_segmento(
            self._campana_detalle.campana_id, self._campana_detalle.segmento_id
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            QMessageBox.information(self, "Carga Completada", f"Se agregaron {n} destinatarios.")
            self._cargar_tabla_destinatarios(self._campana_detalle.campana_id)
            campana_act, _ = self._service.obtener_campana(self._campana_detalle.campana_id)
            if campana_act:
                self._campana_detalle = campana_act
                self._lbl_met_dest.setText(str(campana_act.total_destinatarios))

    def _quitar_destinatario(self):
        if not self._campana_detalle:
            return
        selected = self._tabla_destinatarios.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecciona una fila para quitar.")
            return
        row = self._tabla_destinatarios.currentRow()
        id_item = self._tabla_destinatarios.item(row, 0)
        if not id_item:
            return
        destinatario_id = int(id_item.text())
        ok, error = self._service.eliminar_destinatario(
            destinatario_id, self._campana_detalle.campana_id
        )
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            self._cargar_tabla_destinatarios(self._campana_detalle.campana_id)
            campana_act, _ = self._service.obtener_campana(self._campana_detalle.campana_id)
            if campana_act:
                self._campana_detalle = campana_act
                self._lbl_met_dest.setText(str(campana_act.total_destinatarios))

    def _editar_campana_desde_detalle(self):
        if not self._campana_detalle:
            return
        campana = self._campana_detalle
        self._campana_editando = campana
        self._limpiar_form_campana()
        self._cargar_combos_campana()

        self._camp_form_titulo.setText("Editar Campaña")
        self._camp_form_subtitulo.setText(f"Editando: {campana.nombre}")
        self._camp_btn_guardar.setText("Actualizar Campaña")

        self._camp_input_nombre.setText(campana.nombre)
        self._camp_input_descripcion.setPlainText(campana.descripcion or "")
        self._camp_input_fecha.setText(campana.fecha_programada or "")

        presupuesto = str(campana.presupuesto) if campana.presupuesto else ""
        self._camp_input_presupuesto.setText(presupuesto)

        for i in range(self._camp_combo_tipo.count()):
            if self._camp_combo_tipo.itemData(i) == campana.tipo:
                self._camp_combo_tipo.setCurrentIndex(i)
                break

        for i in range(self._camp_combo_estado.count()):
            if self._camp_combo_estado.itemData(i) == campana.estado:
                self._camp_combo_estado.setCurrentIndex(i)
                break

        for i in range(self._camp_combo_plantilla.count()):
            if self._camp_combo_plantilla.itemData(i) == campana.plantilla_id:
                self._camp_combo_plantilla.setCurrentIndex(i)
                break

        for i in range(self._camp_combo_segmento.count()):
            if self._camp_combo_segmento.itemData(i) == campana.segmento_id:
                self._camp_combo_segmento.setCurrentIndex(i)
                break

        self._w_campana_detalle.hide()
        self._w_campana_form.show()

    def _eliminar_campana_desde_detalle(self):
        if not self._campana_detalle:
            return
        campana = self._campana_detalle
        resp = QMessageBox.question(
            self, "Eliminar Campaña",
            f"¿Seguro que deseas eliminar la campaña '{campana.nombre}'?\n"
            "Se eliminarán todos sus destinatarios.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            ok, error = self._service.eliminar_campana(campana.campana_id)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                self._campana_detalle = None
                self._mostrar_lista_campanas()

    def _guardar_campana(self):
        presupuesto = None
        pres_text = self._camp_input_presupuesto.text().strip()
        if pres_text:
            try:
                presupuesto = float(pres_text)
            except ValueError:
                QMessageBox.warning(self, "Error", "El presupuesto debe ser un número válido.")
                return

        datos = {
            "nombre": self._camp_input_nombre.text().strip(),
            "descripcion": self._camp_input_descripcion.toPlainText().strip(),
            "tipo": self._camp_combo_tipo.currentData(),
            "estado": self._camp_combo_estado.currentData(),
            "plantilla_id": self._camp_combo_plantilla.currentData(),
            "segmento_id": self._camp_combo_segmento.currentData(),
            "fecha_programada": self._camp_input_fecha.text().strip() or None,
            "presupuesto": presupuesto,
        }

        if self._campana_editando:
            campana, error = self._service.actualizar_campana(
                self._campana_editando.campana_id, datos
            )
            titulo_ok = "Campaña Actualizada"
            msg_ok = "ha sido actualizada exitosamente."
        else:
            campana, error = self._service.crear_campana(datos, self._usuario_actual.usuario_id)
            titulo_ok = "Campaña Creada"
            msg_ok = "ha sido creada exitosamente."

        if error:
            QMessageBox.critical(self, "Error", error)
        elif campana:
            QMessageBox.information(self, titulo_ok, f"La campaña '{campana.nombre}' {msg_ok}")
            self._mostrar_lista_campanas()

    def _limpiar_form_campana(self):
        self._camp_input_nombre.clear()
        self._camp_input_descripcion.clear()
        self._camp_input_fecha.clear()
        self._camp_input_presupuesto.clear()
        self._camp_combo_tipo.setCurrentIndex(0)
        self._camp_combo_estado.setCurrentIndex(0)
        self._camp_combo_plantilla.setCurrentIndex(0)
        self._camp_combo_segmento.setCurrentIndex(0)
        self._camp_input_nombre.setFocus()

    # ==========================================
    # CONFIG CORREO - LOGICA
    # ==========================================

    def _mostrar_lista_configs(self):
        self._w_config_form.hide()
        self._w_config_lista.show()
        self._cargar_tabla_configs()

    def _cargar_tabla_configs(self):
        configs, error = self._service.obtener_configs_correo()
        if error:
            QMessageBox.critical(self, "Error", error)
            return

        self._configs_cargadas = configs or []
        total = len(self._configs_cargadas)
        activa = next((c for c in self._configs_cargadas if c.activa), None)

        self._lbl_cfg_total.setText(str(total))
        self._lbl_cfg_activa.setText(activa.nombre if activa else "-")

        self._tabla_configs.setRowCount(0)
        for cfg in self._configs_cargadas:
            r = self._tabla_configs.rowCount()
            self._tabla_configs.insertRow(r)
            self._tabla_configs.setItem(r, 0, QTableWidgetItem(str(cfg.config_id)))
            self._tabla_configs.setItem(r, 1, QTableWidgetItem(cfg.nombre))
            self._tabla_configs.setItem(r, 2, QTableWidgetItem(cfg.proveedor))
            self._tabla_configs.setItem(r, 3, QTableWidgetItem(cfg.email_remitente))
            self._tabla_configs.setItem(r, 4, QTableWidgetItem(cfg.host or ""))
            self._tabla_configs.setItem(r, 5, QTableWidgetItem(str(cfg.puerto or "")))
            self._tabla_configs.setItem(r, 6, QTableWidgetItem("Sí" if cfg.usar_tls else "No"))
            activa_item = QTableWidgetItem("ACTIVA" if cfg.activa else "")
            if cfg.activa:
                activa_item.setForeground(QColor("#276749"))
                activa_item.setBackground(QColor("#f0fff4"))
            self._tabla_configs.setItem(r, 7, activa_item)

    def _mostrar_form_nueva_config(self):
        self._config_editando = None
        self._limpiar_form_config()
        self._cfg_form_titulo.setText("Nueva Configuración de Correo")
        self._cfg_form_subtitulo.setText(
            "Configura una cuenta de correo para el envío masivo de campañas."
        )
        self._cfg_btn_guardar.setText("Guardar Configuración")
        self._on_proveedor_changed(self._cfg_combo_proveedor.currentText())
        self._w_config_lista.hide()
        self._w_config_form.show()

    def _editar_config_seleccionada(self, index):
        row = index.row()
        id_item = self._tabla_configs.item(row, 0)
        if not id_item:
            return
        cid = int(id_item.text())
        config = next((c for c in self._configs_cargadas if c.config_id == cid), None)
        if not config:
            return

        self._config_editando = config
        self._limpiar_form_config()
        self._cfg_form_titulo.setText("Editar Configuración de Correo")
        self._cfg_form_subtitulo.setText(f"Editando: {config.nombre}")
        self._cfg_btn_guardar.setText("Actualizar Configuración")

        self._cfg_input_nombre.setText(config.nombre)

        for i in range(self._cfg_combo_proveedor.count()):
            if self._cfg_combo_proveedor.itemData(i) == config.proveedor:
                self._cfg_combo_proveedor.setCurrentIndex(i)
                break

        self._cfg_input_host.setText(config.host or "")
        self._cfg_input_puerto.setValue(config.puerto or 587)
        self._cfg_check_tls.setChecked(bool(config.usar_tls))
        self._cfg_check_ssl.setChecked(bool(config.usar_ssl))
        self._cfg_input_email.setText(config.email_remitente)
        self._cfg_input_nombre_rem.setText(config.nombre_remitente or "")
        self._cfg_input_usuario.setText(config.usuario or "")
        self._cfg_input_password.setText(config.contrasena or "")
        self._cfg_input_api_key.setText(config.api_key or "")
        self._cfg_input_notas.setPlainText(config.notas or "")
        self._cfg_check_activa.setChecked(bool(config.activa))

        self._on_proveedor_changed(config.proveedor)
        self._w_config_lista.hide()
        self._w_config_form.show()

    def _activar_config_seleccionada(self):
        row = self._tabla_configs.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona una configuración de la tabla.")
            return
        id_item = self._tabla_configs.item(row, 0)
        if not id_item:
            return
        cid = int(id_item.text())
        config = next((c for c in self._configs_cargadas if c.config_id == cid), None)
        if not config:
            return

        ok, error = self._service.activar_config_correo(cid)
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            QMessageBox.information(
                self, "Configuración Activada",
                f"La configuración '{config.nombre}' es ahora la activa para envíos."
            )
            self._cargar_tabla_configs()

    def _eliminar_config_seleccionada(self):
        row = self._tabla_configs.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona una configuración de la tabla.")
            return
        id_item = self._tabla_configs.item(row, 0)
        if not id_item:
            return
        cid = int(id_item.text())
        config = next((c for c in self._configs_cargadas if c.config_id == cid), None)
        if not config:
            return

        resp = QMessageBox.question(
            self, "Eliminar Configuración",
            f"¿Seguro que deseas eliminar la configuración '{config.nombre}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            ok, error = self._service.eliminar_config_correo(cid)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                self._cargar_tabla_configs()

    def _guardar_config_correo(self):
        datos = {
            "nombre": self._cfg_input_nombre.text().strip(),
            "proveedor": self._cfg_combo_proveedor.currentData(),
            "host": self._cfg_input_host.text().strip(),
            "puerto": self._cfg_input_puerto.value(),
            "usar_tls": self._cfg_check_tls.isChecked(),
            "usar_ssl": self._cfg_check_ssl.isChecked(),
            "email_remitente": self._cfg_input_email.text().strip(),
            "nombre_remitente": self._cfg_input_nombre_rem.text().strip(),
            "usuario": self._cfg_input_usuario.text().strip(),
            "contrasena": self._cfg_input_password.text().strip(),
            "api_key": self._cfg_input_api_key.text().strip(),
            "notas": self._cfg_input_notas.toPlainText().strip(),
            "activa": self._cfg_check_activa.isChecked(),
        }

        if self._config_editando:
            config, error = self._service.actualizar_config_correo(
                self._config_editando.config_id, datos
            )
            titulo_ok = "Configuración Actualizada"
            msg_ok = "ha sido actualizada exitosamente."
        else:
            config, error = self._service.crear_config_correo(datos)
            titulo_ok = "Configuración Guardada"
            msg_ok = "ha sido guardada exitosamente."

        if error:
            QMessageBox.critical(self, "Error", error)
        elif config:
            QMessageBox.information(self, titulo_ok, f"La configuración '{config.nombre}' {msg_ok}")
            self._mostrar_lista_configs()

    def _limpiar_form_config(self):
        self._cfg_input_nombre.clear()
        self._cfg_combo_proveedor.setCurrentIndex(0)
        self._cfg_input_host.clear()
        self._cfg_input_puerto.setValue(587)
        self._cfg_check_tls.setChecked(True)
        self._cfg_check_ssl.setChecked(False)
        self._cfg_input_email.clear()
        self._cfg_input_nombre_rem.clear()
        self._cfg_input_usuario.clear()
        self._cfg_input_password.clear()
        self._cfg_input_api_key.clear()
        self._cfg_input_notas.clear()
        self._cfg_check_activa.setChecked(False)
        self._cfg_input_nombre.setFocus()

    def _toggle_password(self):
        if self._cfg_input_password.echoMode() == QLineEdit.Password:
            self._cfg_input_password.setEchoMode(QLineEdit.Normal)
            self._cfg_btn_show_pwd.setText("Ocultar")
        else:
            self._cfg_input_password.setEchoMode(QLineEdit.Password)
            self._cfg_btn_show_pwd.setText("Ver")

    def _on_proveedor_changed(self, proveedor):
        es_api = proveedor in ("SendGrid", "Mailgun")
        self._cfg_lbl_api.setVisible(es_api)
        self._cfg_input_api_key.setVisible(es_api)

        presets = {
            "Gmail":   ("smtp.gmail.com", 587, True, False),
            "Outlook": ("smtp.office365.com", 587, True, False),
            "Yahoo":   ("smtp.mail.yahoo.com", 587, True, False),
            "SendGrid": ("smtp.sendgrid.net", 587, True, False),
            "Mailgun": ("smtp.mailgun.org", 587, True, False),
        }
        if proveedor in presets and not self._config_editando:
            host, port, tls, ssl = presets[proveedor]
            self._cfg_input_host.setText(host)
            self._cfg_input_puerto.setValue(port)
            self._cfg_check_tls.setChecked(tls)
            self._cfg_check_ssl.setChecked(ssl)
