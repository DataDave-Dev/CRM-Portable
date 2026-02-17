# Widget para gestionar notas de contacto

import os
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QHeaderView, QLineEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5 import uic
from app.services.nota_contacto_service import NotaContactoService
from app.utils.sanitizer import Sanitizer

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "clientes", "notas_contacto_widget.ui")


class NotasContactoWidget(QWidget):

    def __init__(self, contacto_id, usuario_actual_id, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._contacto_id = contacto_id
        self._usuario_actual_id = usuario_actual_id
        self._nota_service = NotaContactoService()
        self._nota_editando = None
        self._notas_cargadas = []
        self._filtro_texto = ""

        self._setup_ui()
        self._setup_signals()
        self._mostrar_lista_notas()

    def _setup_ui(self):
        # ocultar formulario inicialmente
        self.formNotaContainer.hide()

        # configurar headers de tabla
        h_header = self.tabla_notas.horizontalHeader()
        if h_header:
            h_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
            h_header.setSectionResizeMode(1, QHeaderView.Stretch)  # Titulo
            h_header.setSectionResizeMode(2, QHeaderView.Stretch)  # Contenido
            h_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Privada
            h_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Creado Por
            h_header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Fecha
            # habilitar ordenamiento por columna
            self.tabla_notas.setSortingEnabled(True)

        v_header = self.tabla_notas.verticalHeader()
        if v_header:
            v_header.setVisible(False)
            v_header.setDefaultSectionSize(42)

        # ocultar columna ID
        self.tabla_notas.setColumnHidden(0, True)

        # configurar limites de caracteres
        self.input_titulo.setMaxLength(Sanitizer.MAX_TITULO_LENGTH)

        # agregar campo de busqueda si existe el contenedor adecuado
        try:
            if hasattr(self, 'tablaContainer'):
                # crear campo de busqueda
                search_layout = QHBoxLayout()
                search_label = QLabel("Buscar:")
                self.search_input = QLineEdit()
                self.search_input.setPlaceholderText("Buscar en notas...")
                self.search_input.setClearButtonEnabled(True)
                search_layout.addWidget(search_label)
                search_layout.addWidget(self.search_input)

                # insertar al inicio del layout de la tabla
                self.tablaContainer.layout().insertLayout(0, search_layout)
        except:
            pass

        # agregar contadores de caracteres para el formulario
        try:
            if hasattr(self, 'formNotaContainer'):
                # crear labels para contadores
                self.label_contador_titulo = QLabel(f"0/{Sanitizer.MAX_TITULO_LENGTH}")
                self.label_contador_contenido = QLabel(f"0/{Sanitizer.MAX_CONTENIDO_LENGTH}")

                # intentar agregar los contadores cerca de los campos
                if hasattr(self, 'input_titulo') and self.input_titulo.parent():
                    parent_layout = self.input_titulo.parent().layout()
                    if parent_layout:
                        for i in range(parent_layout.count()):
                            if parent_layout.itemAt(i).widget() == self.input_titulo:
                                parent_layout.insertWidget(i + 1, self.label_contador_titulo)
                                break
        except:
            pass

    def _setup_signals(self):
        self.btn_nueva_nota.clicked.connect(self._mostrar_form_nueva_nota)
        self.btn_editar_nota.clicked.connect(self._editar_nota_seleccionada)
        self.btn_eliminar_nota.clicked.connect(self._eliminar_nota_seleccionada)
        self.btn_guardar_nota.clicked.connect(self._guardar_nota)
        self.btn_cancelar_nota.clicked.connect(self._cancelar_form_nota)
        self.tabla_notas.doubleClicked.connect(self._editar_nota_desde_tabla)

        # conectar busqueda
        if hasattr(self, 'search_input'):
            self.search_input.textChanged.connect(self._filtrar_notas)

        # conectar contadores de caracteres
        if hasattr(self, 'label_contador_titulo'):
            self.input_titulo.textChanged.connect(self._actualizar_contador_titulo)
        if hasattr(self, 'label_contador_contenido'):
            self.input_contenido.textChanged.connect(self._actualizar_contador_contenido)

    def _filtrar_notas(self, texto):
        # filtra las notas segun el texto de busqueda
        self._filtro_texto = texto.lower()
        self._actualizar_tabla_filtrada()

    def _actualizar_tabla_filtrada(self):
        # actualiza la tabla aplicando el filtro
        self.tabla_notas.setSortingEnabled(False)
        self.tabla_notas.setRowCount(0)

        for nota in self._notas_cargadas:
            # aplicar filtro
            if self._filtro_texto:
                titulo = (nota.titulo or "").lower()
                contenido = (nota.contenido or "").lower()
                if self._filtro_texto not in titulo and self._filtro_texto not in contenido:
                    continue

            # agregar fila
            row = self.tabla_notas.rowCount()
            self.tabla_notas.insertRow(row)

            self.tabla_notas.setItem(row, 0, QTableWidgetItem(str(nota.nota_id)))
            self.tabla_notas.setItem(row, 1, QTableWidgetItem(nota.titulo or ""))
            self.tabla_notas.setItem(row, 2, QTableWidgetItem(nota.contenido or ""))
            self.tabla_notas.setItem(row, 3, QTableWidgetItem("Si" if nota.es_privada else "No"))
            self.tabla_notas.setItem(row, 4, QTableWidgetItem(nota.nombre_creador or ""))
            self.tabla_notas.setItem(row, 5, QTableWidgetItem(nota.fecha_creacion or ""))

        self.tabla_notas.setSortingEnabled(True)

    def _actualizar_contador_titulo(self, texto):
        # actualiza el contador de caracteres del titulo
        if hasattr(self, 'label_contador_titulo'):
            longitud = len(texto)
            self.label_contador_titulo.setText(f"{longitud}/{Sanitizer.MAX_TITULO_LENGTH}")
            if longitud > Sanitizer.MAX_TITULO_LENGTH * 0.9:
                self.label_contador_titulo.setStyleSheet("color: red;")
            else:
                self.label_contador_titulo.setStyleSheet("")

    def _actualizar_contador_contenido(self):
        # actualiza el contador de caracteres del contenido
        if hasattr(self, 'label_contador_contenido'):
            longitud = len(self.input_contenido.toPlainText())
            self.label_contador_contenido.setText(f"{longitud}/{Sanitizer.MAX_CONTENIDO_LENGTH}")
            if longitud > Sanitizer.MAX_CONTENIDO_LENGTH * 0.9:
                self.label_contador_contenido.setStyleSheet("color: red;")
            else:
                self.label_contador_contenido.setStyleSheet("")

    def cargar_notas(self):
        # metodo publico para recargar notas desde el exterior
        self._cargar_tabla_notas()

    def _cargar_tabla_notas(self):
        if not self._contacto_id:
            return

        try:
            notas, error = self._nota_service.obtener_por_contacto(self._contacto_id)
            if error:
                QMessageBox.critical(self, "Error", error)
                return

            self._notas_cargadas = notas or []
            self._actualizar_tabla_filtrada()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las notas: {str(e)}")

    def _mostrar_lista_notas(self):
        self.formNotaContainer.hide()
        self.listaNotasContainer.show()
        self._cargar_tabla_notas()

    def _mostrar_form_nueva_nota(self):
        self._nota_editando = None
        self.listaNotasContainer.hide()
        self.formNotaContainer.show()
        self.form_titulo_label.setText("Nueva Nota")
        self.btn_guardar_nota.setText("Guardar Nota")
        self._limpiar_formulario_nota()

    def _editar_nota_seleccionada(self):
        selected_rows = self.tabla_notas.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Atencion", "Por favor, selecciona una nota para editar.")
            return

        row = selected_rows[0].row()
        self._editar_nota_desde_fila(row)

    def _editar_nota_desde_tabla(self, index):
        row = index.row()
        self._editar_nota_desde_fila(row)

    def _editar_nota_desde_fila(self, row):
        id_item = self.tabla_notas.item(row, 0)
        if not id_item:
            return

        nota_id = int(id_item.text())
        nota = next((n for n in self._notas_cargadas if n.nota_id == nota_id), None)
        if not nota:
            return

        self._nota_editando = nota
        self.listaNotasContainer.hide()
        self.formNotaContainer.show()
        self.form_titulo_label.setText("Editar Nota")
        self.btn_guardar_nota.setText("Actualizar Nota")

        # cargar datos en formulario
        self.input_titulo.setText(nota.titulo or "")
        self.input_contenido.setPlainText(nota.contenido or "")
        self.check_privada.setChecked(nota.es_privada == 1)

    def _guardar_nota(self):
        titulo = self.input_titulo.text().strip()
        contenido = self.input_contenido.toPlainText().strip()
        es_privada = 1 if self.check_privada.isChecked() else 0

        if not contenido:
            QMessageBox.warning(self, "Atencion", "El contenido de la nota es requerido.")
            return

        # validar longitudes
        if len(contenido) > Sanitizer.MAX_CONTENIDO_LENGTH:
            QMessageBox.warning(self, "Atencion", f"El contenido no puede exceder {Sanitizer.MAX_CONTENIDO_LENGTH} caracteres. Actualmente: {len(contenido)}")
            return

        if titulo and len(titulo) > Sanitizer.MAX_TITULO_LENGTH:
            QMessageBox.warning(self, "Atencion", f"El titulo no puede exceder {Sanitizer.MAX_TITULO_LENGTH} caracteres. Actualmente: {len(titulo)}")
            return

        datos = {
            "contacto_id": self._contacto_id,
            "titulo": titulo,
            "contenido": contenido,
            "es_privada": es_privada,
        }

        try:
            if self._nota_editando:
                # actualizar nota existente
                _, error = self._nota_service.actualizar_nota(self._nota_editando.nota_id, datos, self._usuario_actual_id)
                if error:
                    QMessageBox.critical(self, "Error", error)
                    return
                QMessageBox.information(self, "Exito", "Nota actualizada correctamente")
            else:
                # crear nueva nota
                _, error = self._nota_service.crear_nota(datos, self._usuario_actual_id)
                if error:
                    QMessageBox.critical(self, "Error", error)
                    return
                QMessageBox.information(self, "Exito", "Nota creada correctamente")

            self._mostrar_lista_notas()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar la nota: {str(e)}")

    def _eliminar_nota_seleccionada(self):
        selected_rows = self.tabla_notas.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Atencion", "Por favor, selecciona una nota para eliminar.")
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminacion",
            "Estas seguro de eliminar esta nota? Esta accion no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if respuesta != QMessageBox.Yes:
            return

        row = selected_rows[0].row()
        id_item = self.tabla_notas.item(row, 0)
        if not id_item:
            return

        nota_id = int(id_item.text())

        try:
            _, error = self._nota_service.eliminar_nota(nota_id, self._usuario_actual_id)
            if error:
                QMessageBox.critical(self, "Error", error)
                return

            QMessageBox.information(self, "Exito", "Nota eliminada correctamente")
            self._cargar_tabla_notas()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar la nota: {str(e)}")

    def _cancelar_form_nota(self):
        self._mostrar_lista_notas()

    def _limpiar_formulario_nota(self):
        self.input_titulo.clear()
        self.input_contenido.clear()
        self.check_privada.setChecked(False)
