# Widget especializado para gestionar la jerarquia Pais > Estado > Ciudad

import os
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import uic
from app.services.catalogo_service import CatalogoService
from app.config.catalogos import GEOGRAFIA_CONFIGS
from app.views.catalogo_form_dialog import CatalogoFormDialog

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "geografia", "geografia_view.ui")


class GeografiaWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)

        self._pais_service = CatalogoService(GEOGRAFIA_CONFIGS['paises'])
        self._estado_service = CatalogoService(GEOGRAFIA_CONFIGS['estados'])
        self._ciudad_service = CatalogoService(GEOGRAFIA_CONFIGS['ciudades'])

        self._selected_pais_id = None
        self._selected_estado_id = None

        self._setup_ui()

    def _setup_ui(self):
        # configurar headers de tablas
        self._setup_table_headers()

        # conectar senales de seleccion
        self.tablaPaises.clicked.connect(self._on_pais_selected)
        self.tablaEstados.clicked.connect(self._on_estado_selected)

        # conectar botones CRUD para paises
        self.btnNuevoPais.clicked.connect(self._on_nuevo_pais)
        self.btnEditarPais.clicked.connect(self._on_editar_pais)
        self.btnEliminarPais.clicked.connect(self._on_eliminar_pais)

        # conectar botones CRUD para estados
        self.btnNuevoEstado.clicked.connect(self._on_nuevo_estado)
        self.btnEditarEstado.clicked.connect(self._on_editar_estado)
        self.btnEliminarEstado.clicked.connect(self._on_eliminar_estado)

        # conectar botones CRUD para ciudades
        self.btnNuevaCiudad.clicked.connect(self._on_nueva_ciudad)
        self.btnEditarCiudad.clicked.connect(self._on_editar_ciudad)
        self.btnEliminarCiudad.clicked.connect(self._on_eliminar_ciudad)

    def _setup_table_headers(self):
        for tabla in [self.tablaPaises, self.tablaEstados, self.tablaCiudades]:
            h_header = tabla.horizontalHeader()
            h_header.setSectionResizeMode(QHeaderView.Stretch)
            h_header.setSectionResizeMode(0, QHeaderView.Fixed)
            tabla.setColumnWidth(0, 50)
            v_header = tabla.verticalHeader()
            v_header.setVisible(False)
            v_header.setDefaultSectionSize(36)

    def cargar_datos(self):
        self._cargar_paises()

    def _cargar_paises(self):
        items, error = self._pais_service.obtener_todos()
        if error:
            QMessageBox.critical(self, "Error", error)
            return

        self.tablaPaises.setRowCount(0)
        for item in items:
            row = self.tablaPaises.rowCount()
            self.tablaPaises.insertRow(row)
            self.tablaPaises.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.tablaPaises.setItem(row, 1, QTableWidgetItem(getattr(item, 'Nombre', '')))
            self.tablaPaises.setItem(row, 2, QTableWidgetItem(getattr(item, 'CodigoISO', '') or ''))

        self._selected_pais_id = None
        self._selected_estado_id = None
        self.tablaEstados.setRowCount(0)
        self.tablaCiudades.setRowCount(0)

    def _cargar_estados(self, pais_id):
        items, error = self._estado_service.obtener_todos(filters={'PaisID': pais_id})
        if error:
            QMessageBox.critical(self, "Error", error)
            return

        self.tablaEstados.setRowCount(0)
        for item in items:
            row = self.tablaEstados.rowCount()
            self.tablaEstados.insertRow(row)
            self.tablaEstados.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.tablaEstados.setItem(row, 1, QTableWidgetItem(getattr(item, 'Nombre', '')))

        self._selected_estado_id = None
        self.tablaCiudades.setRowCount(0)

    def _cargar_ciudades(self, estado_id):
        items, error = self._ciudad_service.obtener_todos(filters={'EstadoID': estado_id})
        if error:
            QMessageBox.critical(self, "Error", error)
            return

        self.tablaCiudades.setRowCount(0)
        for item in items:
            row = self.tablaCiudades.rowCount()
            self.tablaCiudades.insertRow(row)
            self.tablaCiudades.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.tablaCiudades.setItem(row, 1, QTableWidgetItem(getattr(item, 'Nombre', '')))

    # --- SELECCION ---

    def _on_pais_selected(self, index):
        row = index.row()
        id_item = self.tablaPaises.item(row, 0)
        nombre_item = self.tablaPaises.item(row, 1)
        if not id_item:
            return
        self._selected_pais_id = int(id_item.text())
        self.estadoSubtitle.setText(f"Estados de {nombre_item.text()}")
        self._cargar_estados(self._selected_pais_id)

    def _on_estado_selected(self, index):
        row = index.row()
        id_item = self.tablaEstados.item(row, 0)
        nombre_item = self.tablaEstados.item(row, 1)
        if not id_item:
            return
        self._selected_estado_id = int(id_item.text())
        self.ciudadSubtitle.setText(f"Ciudades de {nombre_item.text()}")
        self._cargar_ciudades(self._selected_estado_id)

    # --- CRUD PAISES ---

    def _on_nuevo_pais(self):
        config = GEOGRAFIA_CONFIGS['paises']
        dialog = CatalogoFormDialog(config, parent=self)
        if dialog.exec_() == CatalogoFormDialog.Accepted:
            datos = dialog.get_datos()
            result, error = self._pais_service.crear(datos)
            if error:
                QMessageBox.warning(self, "Error", error)
            else:
                self._cargar_paises()

    def _on_editar_pais(self):
        row = self.tablaPaises.currentRow()
        if row < 0:
            QMessageBox.information(self, "Aviso", "Selecciona un pais para editar")
            return
        pais_id = int(self.tablaPaises.item(row, 0).text())
        item, error = self._pais_service.obtener_por_id(pais_id)
        if error:
            QMessageBox.warning(self, "Error", error)
            return

        config = GEOGRAFIA_CONFIGS['paises']
        dialog = CatalogoFormDialog(config, datos_edicion=item, parent=self)
        if dialog.exec_() == CatalogoFormDialog.Accepted:
            datos = dialog.get_datos()
            result, error = self._pais_service.actualizar(pais_id, datos)
            if error:
                QMessageBox.warning(self, "Error", error)
            else:
                self._cargar_paises()

    def _on_eliminar_pais(self):
        row = self.tablaPaises.currentRow()
        if row < 0:
            QMessageBox.information(self, "Aviso", "Selecciona un pais para eliminar")
            return
        pais_id = int(self.tablaPaises.item(row, 0).text())
        respuesta = QMessageBox.question(
            self, "Confirmar", "Estas seguro de eliminar este pais?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            result, error = self._pais_service.eliminar(pais_id)
            if error:
                QMessageBox.warning(self, "No se puede eliminar", error)
            else:
                self._cargar_paises()

    # --- CRUD ESTADOS ---

    def _on_nuevo_estado(self):
        if not self._selected_pais_id:
            QMessageBox.information(self, "Aviso", "Selecciona un pais primero")
            return
        config = GEOGRAFIA_CONFIGS['estados']
        dialog = CatalogoFormDialog(config, parent=self)
        if dialog.exec_() == CatalogoFormDialog.Accepted:
            datos = dialog.get_datos()
            datos['PaisID'] = self._selected_pais_id
            result, error = self._estado_service.crear(datos)
            if error:
                QMessageBox.warning(self, "Error", error)
            else:
                self._cargar_estados(self._selected_pais_id)

    def _on_editar_estado(self):
        row = self.tablaEstados.currentRow()
        if row < 0:
            QMessageBox.information(self, "Aviso", "Selecciona un estado para editar")
            return
        estado_id = int(self.tablaEstados.item(row, 0).text())
        item, error = self._estado_service.obtener_por_id(estado_id)
        if error:
            QMessageBox.warning(self, "Error", error)
            return

        config = GEOGRAFIA_CONFIGS['estados']
        dialog = CatalogoFormDialog(config, datos_edicion=item, parent=self)
        if dialog.exec_() == CatalogoFormDialog.Accepted:
            datos = dialog.get_datos()
            datos['PaisID'] = self._selected_pais_id
            result, error = self._estado_service.actualizar(estado_id, datos)
            if error:
                QMessageBox.warning(self, "Error", error)
            else:
                self._cargar_estados(self._selected_pais_id)

    def _on_eliminar_estado(self):
        row = self.tablaEstados.currentRow()
        if row < 0:
            QMessageBox.information(self, "Aviso", "Selecciona un estado para eliminar")
            return
        estado_id = int(self.tablaEstados.item(row, 0).text())
        respuesta = QMessageBox.question(
            self, "Confirmar", "Estas seguro de eliminar este estado?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            result, error = self._estado_service.eliminar(estado_id)
            if error:
                QMessageBox.warning(self, "No se puede eliminar", error)
            else:
                self._cargar_estados(self._selected_pais_id)

    # --- CRUD CIUDADES ---

    def _on_nueva_ciudad(self):
        if not self._selected_estado_id:
            QMessageBox.information(self, "Aviso", "Selecciona un estado primero")
            return
        config = GEOGRAFIA_CONFIGS['ciudades']
        dialog = CatalogoFormDialog(config, parent=self)
        if dialog.exec_() == CatalogoFormDialog.Accepted:
            datos = dialog.get_datos()
            datos['EstadoID'] = self._selected_estado_id
            result, error = self._ciudad_service.crear(datos)
            if error:
                QMessageBox.warning(self, "Error", error)
            else:
                self._cargar_ciudades(self._selected_estado_id)

    def _on_editar_ciudad(self):
        row = self.tablaCiudades.currentRow()
        if row < 0:
            QMessageBox.information(self, "Aviso", "Selecciona una ciudad para editar")
            return
        ciudad_id = int(self.tablaCiudades.item(row, 0).text())
        item, error = self._ciudad_service.obtener_por_id(ciudad_id)
        if error:
            QMessageBox.warning(self, "Error", error)
            return

        config = GEOGRAFIA_CONFIGS['ciudades']
        dialog = CatalogoFormDialog(config, datos_edicion=item, parent=self)
        if dialog.exec_() == CatalogoFormDialog.Accepted:
            datos = dialog.get_datos()
            datos['EstadoID'] = self._selected_estado_id
            result, error = self._ciudad_service.actualizar(ciudad_id, datos)
            if error:
                QMessageBox.warning(self, "Error", error)
            else:
                self._cargar_ciudades(self._selected_estado_id)

    def _on_eliminar_ciudad(self):
        row = self.tablaCiudades.currentRow()
        if row < 0:
            QMessageBox.information(self, "Aviso", "Selecciona una ciudad para eliminar")
            return
        ciudad_id = int(self.tablaCiudades.item(row, 0).text())
        respuesta = QMessageBox.question(
            self, "Confirmar", "Estas seguro de eliminar esta ciudad?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            result, error = self._ciudad_service.eliminar(ciudad_id)
            if error:
                QMessageBox.warning(self, "No se puede eliminar", error)
            else:
                self._cargar_ciudades(self._selected_estado_id)
