# Dialogo popup de notificaciones y recordatorios - se muestra automaticamente al iniciar sesion

from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal


class NotificacionCard(QFrame):
    """Tarjeta individual para mostrar una notificacion del sistema."""

    def __init__(self, notificacion, parent=None):
        super().__init__(parent)
        self._notificacion = notificacion
        self._setup_ui()

    def _setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin: 2px 0px;
            }
            QFrame:hover {
                border: 1px solid #4a90d9;
                background-color: #ebf4ff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        # Fila superior: tipo + fecha
        fila_top = QHBoxLayout()
        tipo_label = QLabel(self._notificacion.tipo or "Sistema")
        tipo_label.setStyleSheet(
            "background-color: #4a90d9; color: #fff; border-radius: 4px; "
            "padding: 2px 8px; font-size: 11px; font-weight: 600; border: none;"
        )
        tipo_label.setFixedHeight(22)

        fecha_label = QLabel(self._notificacion.fecha_creacion or "")
        fecha_label.setStyleSheet("color: #7f8c9b; font-size: 11px; border: none; background: transparent;")
        fecha_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        fila_top.addWidget(tipo_label)
        fila_top.addStretch()
        fila_top.addWidget(fecha_label)
        layout.addLayout(fila_top)

        titulo_label = QLabel(self._notificacion.titulo)
        titulo_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1a1a2e; border: none; background: transparent;")
        titulo_label.setWordWrap(True)
        layout.addWidget(titulo_label)

        if self._notificacion.mensaje:
            msg_label = QLabel(self._notificacion.mensaje)
            msg_label.setStyleSheet("font-size: 12px; color: #4a5568; border: none; background: transparent;")
            msg_label.setWordWrap(True)
            layout.addWidget(msg_label)


class RecordatorioCard(QFrame):
    """Tarjeta individual para mostrar un recordatorio pendiente."""

    def __init__(self, recordatorio, parent=None):
        super().__init__(parent)
        self._recordatorio = recordatorio
        self._es_vencido = self._calcular_vencido()
        self._setup_ui()

    def _calcular_vencido(self):
        if not self._recordatorio.fecha_recordatorio:
            return False
        try:
            fecha = datetime.strptime(self._recordatorio.fecha_recordatorio, "%Y-%m-%d %H:%M:%S")
            return fecha < datetime.now()
        except ValueError:
            try:
                fecha = datetime.strptime(self._recordatorio.fecha_recordatorio, "%Y-%m-%d %H:%mm")
                return fecha < datetime.now()
            except Exception:
                return False

    def _setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        if self._es_vencido:
            self.setStyleSheet("""
                QFrame {
                    background-color: #fff5f5;
                    border: 1px solid #feb2b2;
                    border-radius: 8px;
                    margin: 2px 0px;
                }
                QFrame:hover {
                    border: 1px solid #fc8181;
                    background-color: #fed7d7;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #fffaf0;
                    border: 1px solid #fbd38d;
                    border-radius: 8px;
                    margin: 2px 0px;
                }
                QFrame:hover {
                    border: 1px solid #ed8936;
                    background-color: #fefcbf;
                }
            """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        # Fila superior: badge de estado + fecha
        fila_top = QHBoxLayout()
        badge_txt = "Vencido" if self._es_vencido else "Recordatorio"
        badge_color = "#fc8181" if self._es_vencido else "#ed8936"
        badge_label = QLabel(badge_txt)
        badge_label.setStyleSheet(
            f"background-color: {badge_color}; color: #fff; border-radius: 4px; "
            "padding: 2px 8px; font-size: 11px; font-weight: 600; border: none;"
        )
        badge_label.setFixedHeight(22)

        fecha_label = QLabel(self._recordatorio.fecha_recordatorio or "")
        fecha_label.setStyleSheet("color: #7f8c9b; font-size: 11px; border: none; background: transparent;")
        fecha_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        fila_top.addWidget(badge_label)
        fila_top.addStretch()
        fila_top.addWidget(fecha_label)
        layout.addLayout(fila_top)

        titulo_label = QLabel(self._recordatorio.titulo)
        titulo_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #1a1a2e; border: none; background: transparent;")
        titulo_label.setWordWrap(True)
        layout.addWidget(titulo_label)

        if self._recordatorio.descripcion:
            desc_label = QLabel(self._recordatorio.descripcion)
            desc_label.setStyleSheet("font-size: 12px; color: #4a5568; border: none; background: transparent;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        vinculo = ""
        if self._recordatorio.nombre_contacto:
            vinculo = f"Contacto: {self._recordatorio.nombre_contacto}"
        elif self._recordatorio.nombre_empresa:
            vinculo = f"Empresa: {self._recordatorio.nombre_empresa}"
        elif self._recordatorio.nombre_oportunidad:
            vinculo = f"Oportunidad: {self._recordatorio.nombre_oportunidad}"

        if vinculo:
            link_label = QLabel(vinculo)
            link_label.setStyleSheet("font-size: 11px; color: #718096; border: none; background: transparent;")
            layout.addWidget(link_label)


def _hacer_separador_seccion(texto):
    """Crea un widget separador con el titulo de la seccion."""
    frame = QFrame()
    frame.setStyleSheet("background: transparent; border: none;")
    row = QHBoxLayout(frame)
    row.setContentsMargins(0, 6, 0, 2)
    row.setSpacing(8)

    linea_izq = QFrame()
    linea_izq.setFrameShape(QFrame.HLine)
    linea_izq.setStyleSheet("background-color: #e2e8f0; max-height: 1px; border: none;")

    lbl = QLabel(texto)
    lbl.setStyleSheet(
        "color: #718096; font-size: 11px; font-weight: 600; "
        "background: transparent; border: none; padding: 0 4px;"
    )
    lbl.setSizePolicy(lbl.sizePolicy().horizontalPolicy(), lbl.sizePolicy().verticalPolicy())
    lbl.setFixedWidth(lbl.fontMetrics().horizontalAdvance(texto) + 12)

    linea_der = QFrame()
    linea_der.setFrameShape(QFrame.HLine)
    linea_der.setStyleSheet("background-color: #e2e8f0; max-height: 1px; border: none;")

    row.addWidget(linea_izq, 1)
    row.addWidget(lbl)
    row.addWidget(linea_der, 1)
    return frame


class NotificacionPopup(QDialog):
    """
    Dialog popup que muestra las notificaciones no leidas y los recordatorios
    pendientes del usuario al iniciar sesion.
    """

    cerrado = pyqtSignal()

    def __init__(self, notificaciones, recordatorios, service, usuario_id, parent=None):
        super().__init__(parent)
        self._notificaciones = notificaciones
        self._recordatorios = recordatorios
        self._service = service
        self._usuario_id = usuario_id
        self._setup_ui()
        self._poblar_contenido()

    def _setup_ui(self):
        total = len(self._notificaciones) + len(self._recordatorios)

        self.setWindowTitle("Notificaciones y Recordatorios")
        self.setMinimumWidth(520)
        self.setMaximumWidth(640)
        self.setMinimumHeight(320)
        self.setMaximumHeight(600)
        self.setModal(False)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5;
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        # Header
        header = QHBoxLayout()
        titulo = QLabel("Resumen pendiente")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a1a2e;")

        cantidad = QLabel(f"{total} pendientes")
        cantidad.setStyleSheet(
            "background-color: #fc8181; color: #fff; border-radius: 10px; "
            "padding: 2px 10px; font-size: 12px; font-weight: 600;"
        )
        header.addWidget(titulo)
        header.addStretch()
        header.addWidget(cantidad)
        outer.addLayout(header)

        # Scroll area con las tarjetas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        self._scroll_contenido = QWidget()
        self._scroll_contenido.setStyleSheet("background-color: transparent;")
        self._scroll_layout = QVBoxLayout(self._scroll_contenido)
        self._scroll_layout.setContentsMargins(0, 0, 4, 0)
        self._scroll_layout.setSpacing(6)
        self._scroll_layout.addStretch()

        scroll.setWidget(self._scroll_contenido)
        outer.addWidget(scroll)

        # Botones de accion
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_marcar_todas = QPushButton("Marcar notificaciones como leidas")
        btn_marcar_todas.setCursor(Qt.PointingHandCursor)
        btn_marcar_todas.setStyleSheet("""
            QPushButton {
                background-color: #4a90d9;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 9px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #357abd; }
            QPushButton:disabled { background-color: #a0aec0; }
        """)
        btn_marcar_todas.setEnabled(bool(self._notificaciones))
        btn_marcar_todas.clicked.connect(self._marcar_notificaciones_leidas)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #e2e8f0;
                color: #4a5568;
                border: none;
                border-radius: 6px;
                padding: 9px 20px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #cbd5e0; }
        """)
        btn_cerrar.clicked.connect(self.accept)

        btn_row.addWidget(btn_marcar_todas)
        btn_row.addStretch()
        btn_row.addWidget(btn_cerrar)
        outer.addLayout(btn_row)

    def _poblar_contenido(self):
        # Limpiar antes de poblar
        while self._scroll_layout.count() > 1:
            item = self._scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        mostrar_encabezados = bool(self._notificaciones) and bool(self._recordatorios)
        insert_pos = 0

        # Seccion de notificaciones
        if self._notificaciones:
            if mostrar_encabezados:
                sep = _hacer_separador_seccion(f"Notificaciones ({len(self._notificaciones)})")
                self._scroll_layout.insertWidget(insert_pos, sep)
                insert_pos += 1

            for notif in self._notificaciones:
                card = NotificacionCard(notif)
                self._scroll_layout.insertWidget(insert_pos, card)
                insert_pos += 1

        # Seccion de recordatorios
        if self._recordatorios:
            if mostrar_encabezados:
                sep = _hacer_separador_seccion(f"Recordatorios ({len(self._recordatorios)})")
                self._scroll_layout.insertWidget(insert_pos, sep)
                insert_pos += 1

            for rec in self._recordatorios:
                card = RecordatorioCard(rec)
                self._scroll_layout.insertWidget(insert_pos, card)
                insert_pos += 1

    def _marcar_notificaciones_leidas(self):
        self._service.marcar_todas_como_leidas(self._usuario_id)
        self.accept()
        self.cerrado.emit()
