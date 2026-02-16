# Vista principal del CRM - carga el .ui y muestra datos del usuario

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLineEdit, QMessageBox,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import QSize
from PyQt5 import uic
from app.services.usuario_service import UsuarioService
from app.repositories.rol_repository import RolRepository
from app.views.configuracion_view import ConfiguracionView
from app.views.clientes_view import ClientesView

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "main", "main_view.ui")
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")


class MainView(QMainWindow):

    def __init__(self, usuario):
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self._usuario_actual = usuario
        self._usuario_service = UsuarioService()
        self._rol_repository = RolRepository()
        self._usuario_editando = None  # None = modo crear, Usuario = modo editar
        self._setup_icons()
        self._set_user_data(usuario)
        self._setup_navigation()
        self._create_lista_usuarios()
        self._create_form_usuarios()
        self._create_clientes()
        self._create_configuracion()

    def _setup_icons(self):
        logout_icon = QIcon(os.path.join(ASSETS_PATH, "logout.svg"))
        self.btnCerrarSesion.setIcon(logout_icon)
        self.btnCerrarSesion.setIconSize(QSize(20, 20))

    def _set_user_data(self, usuario):
        nombre_completo = f"{usuario.nombre} {usuario.apellido_paterno}"
        self.headerUserName.setText(nombre_completo)
        self.welcomeTitle.setText(f"Bienvenido, {usuario.nombre}")

    def _setup_navigation(self):
        # conectar los botones de navegación del sidebar
        self.sidebar_buttons = []

        # lista de todos los botones de navegación para poder cambiar estilos
        if hasattr(self, 'btnDashboard'):
            self.sidebar_buttons.append(self.btnDashboard)
        if hasattr(self, 'btnClientes'):
            self.sidebar_buttons.append(self.btnClientes)
        if hasattr(self, 'btnProductos'):
            self.sidebar_buttons.append(self.btnProductos)
        if hasattr(self, 'btnVentas'):
            self.sidebar_buttons.append(self.btnVentas)
        if hasattr(self, 'btnReportes'):
            self.sidebar_buttons.append(self.btnReportes)
        if hasattr(self, 'btnUsuarios'):
            self.sidebar_buttons.append(self.btnUsuarios)
            # conectar el botón de Usuarios para mostrar la lista
            self.btnUsuarios.clicked.connect(self._mostrar_seccion_usuarios)
        if hasattr(self, 'btnClientes'):
            self.sidebar_buttons.append(self.btnClientes)
            self.btnClientes.clicked.connect(self._mostrar_seccion_clientes)
        if hasattr(self, 'btnConfiguracion'):
            self.sidebar_buttons.append(self.btnConfiguracion)
            self.btnConfiguracion.clicked.connect(self._mostrar_seccion_configuracion)

    def _resaltar_boton_activo(self, boton_activo):
        # resetear el estilo de todos los botones del sidebar
        estilo_normal = """
            background-color: transparent;
            color: #a0aec0;
            font-size: 15px;
            font-weight: 500;
            text-align: left;
            padding: 14px 20px;
            border: none;
            border-radius: 8px;
            margin: 2px 12px;
        """

        estilo_activo = """
            background-color: #4a90d9;
            color: #ffffff;
            font-size: 15px;
            font-weight: 600;
            text-align: left;
            padding: 14px 20px;
            border: none;
            border-radius: 8px;
            margin: 2px 12px;
        """

        # aplicar estilo normal a todos los botones
        for boton in self.sidebar_buttons:
            boton.setStyleSheet(estilo_normal)

        # aplicar estilo activo al botón seleccionado
        if boton_activo:
            boton_activo.setStyleSheet(estilo_activo)

    def _create_lista_usuarios(self):
        # cargar la lista de usuarios desde el archivo .ui (editable con Qt Designer)
        ui_list_path = os.path.join(os.path.dirname(__file__), "ui", "users", "user_list.ui")
        self.lista_usuarios_widget = QWidget()
        uic.loadUi(ui_list_path, self.lista_usuarios_widget)

        # crear referencias directas
        self.btn_nuevo_usuario = self.lista_usuarios_widget.btn_nuevo_usuario
        self.tabla_usuarios = self.lista_usuarios_widget.tabla_usuarios
        self.stat_value_total = self.lista_usuarios_widget.statValueTotal
        self.stat_value_activos = self.lista_usuarios_widget.statValueActivos
        self.stat_value_inactivos = self.lista_usuarios_widget.statValueInactivos

        # conectar señales
        self.btn_nuevo_usuario.clicked.connect(self._mostrar_form_nuevo_usuario)
        self.tabla_usuarios.doubleClicked.connect(self._editar_usuario_seleccionado)

        # configurar headers de la tabla para ocupar todo el ancho
        h_header = self.tabla_usuarios.horizontalHeader()
        if h_header:
            h_header.setSectionResizeMode(QHeaderView.Stretch)

        v_header = self.tabla_usuarios.verticalHeader()
        if v_header:
            v_header.setVisible(False)
            v_header.setDefaultSectionSize(42)

        # ocultar el widget inicialmente
        self.lista_usuarios_widget.hide()

    def _cargar_tabla_usuarios(self):
        # cargar todos los usuarios desde la BD y mostrarlos en la tabla
        try:
            usuarios = self._usuario_service._repo.find_all()

            # actualizar estadísticas
            total_usuarios = len(usuarios)
            usuarios_activos = sum(1 for u in usuarios if u.activo == 1)
            usuarios_inactivos = total_usuarios - usuarios_activos

            self.stat_value_total.setText(str(total_usuarios))
            self.stat_value_activos.setText(str(usuarios_activos))
            self.stat_value_inactivos.setText(str(usuarios_inactivos))

            # limpiar la tabla antes de llenarla
            self.tabla_usuarios.setRowCount(0)

            # agregar cada usuario como una fila en la tabla
            for usuario in usuarios:
                row_position = self.tabla_usuarios.rowCount()
                self.tabla_usuarios.insertRow(row_position)

                # columna ID
                self.tabla_usuarios.setItem(row_position, 0, QTableWidgetItem(str(usuario.usuario_id)))

                # columna Nombre Completo
                nombre_completo = f"{usuario.nombre} {usuario.apellido_paterno}"
                if usuario.apellido_materno:
                    nombre_completo += f" {usuario.apellido_materno}"
                self.tabla_usuarios.setItem(row_position, 1, QTableWidgetItem(nombre_completo))

                # columna Email
                self.tabla_usuarios.setItem(row_position, 2, QTableWidgetItem(usuario.email))

                # columna Teléfono
                telefono = usuario.telefono if usuario.telefono else "N/A"
                self.tabla_usuarios.setItem(row_position, 3, QTableWidgetItem(telefono))

                # columna Rol
                self.tabla_usuarios.setItem(row_position, 4, QTableWidgetItem(usuario.nombre_rol))

                # columna Estado
                estado = "Activo" if usuario.activo == 1 else "Inactivo"
                item_estado = QTableWidgetItem(estado)
                # colorear según el estado
                if usuario.activo == 1:
                    item_estado.setForeground(QColor(34, 139, 34))  # verde oscuro
                else:
                    item_estado.setForeground(QColor(220, 53, 69))  # rojo
                self.tabla_usuarios.setItem(row_position, 5, item_estado)

                # columna Fecha Registro
                fecha = usuario.fecha_creacion if usuario.fecha_creacion else "N/A"
                self.tabla_usuarios.setItem(row_position, 6, QTableWidgetItem(fecha))


        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar los usuarios: {str(e)}"
            )

    def _mostrar_seccion_usuarios(self):
        # mostrar la lista de usuarios y ocultar otras vistas
        self._ocultar_contenido_actual()

        # agregar y mostrar la lista de usuarios
        if self.lista_usuarios_widget.parent() != self.contentArea:
            self.contentLayout.addWidget(self.lista_usuarios_widget)

        self.lista_usuarios_widget.show()
        self.headerPageTitle.setText("Usuarios")

        # cargar los datos de la tabla
        self._cargar_tabla_usuarios()

        # resaltar el botón de Usuarios en el sidebar
        if hasattr(self, 'btnUsuarios'):
            self._resaltar_boton_activo(self.btnUsuarios)

    def _mostrar_form_nuevo_usuario(self):
        # resetear modo edición
        self._usuario_editando = None
        self._ocultar_contenido_actual()

        if self.form_usuarios_widget.parent() != self.contentArea:
            self.contentLayout.addWidget(self.form_usuarios_widget)

        self.form_usuarios_widget.show()
        self.headerPageTitle.setText("Usuarios - Nuevo")
        self.form_titulo.setText("Nuevo Usuario")
        self.form_subtitulo.setText(
            "Completa la información del nuevo usuario del sistema. "
            "Los campos marcados con * son obligatorios."
        )
        self.btn_guardar.setText("Guardar Usuario")
        self.label_password.setText("Contraseña *")
        self.label_confirm_password.setText("Confirmar Contraseña *")
        self._limpiar_formulario()

    def _editar_usuario_seleccionado(self, index):
        # obtener el ID del usuario desde la fila seleccionada
        row = index.row()
        usuario_id_item = self.tabla_usuarios.item(row, 0)
        if not usuario_id_item:
            return

        usuario_id = int(usuario_id_item.text())

        # buscar el usuario completo en la lista cargada
        try:
            usuarios = self._usuario_service._repo.find_all()
            usuario = next((u for u in usuarios if u.usuario_id == usuario_id), None)
            if not usuario:
                return
        except Exception:
            return

        self._usuario_editando = usuario
        self._ocultar_contenido_actual()

        if self.form_usuarios_widget.parent() != self.contentArea:
            self.contentLayout.addWidget(self.form_usuarios_widget)

        self.form_usuarios_widget.show()
        self.headerPageTitle.setText("Usuarios - Editar")
        self.form_titulo.setText("Editar Usuario")
        self.form_subtitulo.setText(
            f"Editando usuario: {usuario.nombre} {usuario.apellido_paterno}. "
            "Deja los campos de contraseña vacíos para mantener la actual."
        )
        self.btn_guardar.setText("Actualizar Usuario")
        self.label_password.setText("Nueva Contraseña")
        self.label_confirm_password.setText("Confirmar Nueva Contraseña")

        # poblar el formulario con los datos del usuario
        self.input_nombre.setText(usuario.nombre)
        self.input_apellido_paterno.setText(usuario.apellido_paterno)
        self.input_apellido_materno.setText(usuario.apellido_materno or "")
        self.input_email.setText(usuario.email)
        self.input_telefono.setText(usuario.telefono or "")
        self.input_password.clear()
        self.input_confirm_password.clear()
        self.check_activo.setChecked(usuario.activo == 1)

        # seleccionar el rol correcto en el combo
        for i in range(self.combo_rol.count()):
            if self.combo_rol.itemData(i) == usuario.rol_id:
                self.combo_rol.setCurrentIndex(i)
                break

    def _ocultar_contenido_actual(self):
        # ocultar todos los widgets y spacers del área de contenido
        for i in range(self.contentLayout.count()):
            item = self.contentLayout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.hide()
            elif item.spacerItem():
                item.spacerItem().changeSize(0, 0)
            elif item.layout():
                # ocultar widgets dentro de sub-layouts (ej: cardsRow)
                for j in range(item.layout().count()):
                    sub_widget = item.layout().itemAt(j).widget()
                    if sub_widget:
                        sub_widget.hide()
        self.contentLayout.invalidate()

    def _create_form_usuarios(self):
        # cargar el formulario desde el archivo .ui (editable con Qt Designer)
        ui_form_path = os.path.join(os.path.dirname(__file__), "ui", "users", "user_form.ui")
        self.form_usuarios_widget = QWidget()
        uic.loadUi(ui_form_path, self.form_usuarios_widget)

        # conectar señales de los botones
        self.form_usuarios_widget.btn_guardar.clicked.connect(self._guardar_usuario)
        self.form_usuarios_widget.btn_limpiar.clicked.connect(self._limpiar_formulario)
        self.form_usuarios_widget.btn_cancelar.clicked.connect(self._mostrar_seccion_usuarios)
        self.form_usuarios_widget.btn_toggle_password.clicked.connect(self._toggle_password_visibility)
        self.form_usuarios_widget.btn_toggle_confirm.clicked.connect(self._toggle_confirm_visibility)

        # crear referencias directas para acceso rapido desde el resto de la clase
        self.form_titulo = self.form_usuarios_widget.form_titulo
        self.form_subtitulo = self.form_usuarios_widget.form_subtitulo
        self.input_nombre = self.form_usuarios_widget.input_nombre
        self.input_apellido_paterno = self.form_usuarios_widget.input_apellido_paterno
        self.input_apellido_materno = self.form_usuarios_widget.input_apellido_materno
        self.input_telefono = self.form_usuarios_widget.input_telefono
        self.input_email = self.form_usuarios_widget.input_email
        self.input_password = self.form_usuarios_widget.input_password
        self.input_confirm_password = self.form_usuarios_widget.input_confirm_password
        self.btn_toggle_password = self.form_usuarios_widget.btn_toggle_password
        self.btn_toggle_confirm = self.form_usuarios_widget.btn_toggle_confirm
        self.btn_guardar = self.form_usuarios_widget.btn_guardar
        self.combo_rol = self.form_usuarios_widget.combo_rol
        self.check_activo = self.form_usuarios_widget.check_activo
        self.label_password = self.form_usuarios_widget.label_password
        self.label_confirm_password = self.form_usuarios_widget.label_confirm_password

        # cargar los roles en el combobox
        self._cargar_roles()

        # ocultar el formulario inicialmente
        self.form_usuarios_widget.hide()

    def _cargar_roles(self):
        # cargar los roles desde la base de datos y llenar el combobox
        try:
            roles = self._rol_repository.find_all()
            for rol in roles:
                self.combo_rol.addItem(rol.nombre_rol, rol.rol_id)
        except Exception as e:
            # si hay error al cargar roles, mostrar mensaje
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudieron cargar los roles: {str(e)}"
            )

    def _toggle_password_visibility(self):
        # alternar entre mostrar y ocultar la contraseña
        if self.input_password.echoMode() == QLineEdit.Password:
            self.input_password.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_password.setText("Ocultar")
        else:
            self.input_password.setEchoMode(QLineEdit.Password)
            self.btn_toggle_password.setText("Ver")

    def _toggle_confirm_visibility(self):
        # alternar entre mostrar y ocultar la confirmación de contraseña
        if self.input_confirm_password.echoMode() == QLineEdit.Password:
            self.input_confirm_password.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_confirm.setText("Ocultar")
        else:
            self.input_confirm_password.setEchoMode(QLineEdit.Password)
            self.btn_toggle_confirm.setText("Ver")

    def _validar_formulario(self):
        # validar que todos los campos requeridos estén completos
        if not self.input_nombre.text().strip():
            return False, "El nombre es requerido"

        if not self.input_apellido_paterno.text().strip():
            return False, "El apellido paterno es requerido"

        if not self.input_email.text().strip():
            return False, "El email es requerido"

        # en modo crear, la contraseña es obligatoria
        # en modo editar, solo se valida si se escribió algo
        contrasena = self.input_password.text()
        confirmar = self.input_confirm_password.text()
        es_edicion = self._usuario_editando is not None

        if not es_edicion:
            if not contrasena:
                return False, "La contraseña es requerida"
            if not confirmar:
                return False, "Debes confirmar la contraseña"

        if contrasena or confirmar:
            if contrasena != confirmar:
                return False, "Las contraseñas no coinciden"
            if len(contrasena) < 8:
                return False, "La contraseña debe tener al menos 8 caracteres"

        # validar formato de teléfono si se proporciona
        telefono = self.input_telefono.text().strip()
        if telefono and (not telefono.isdigit() or len(telefono) != 10):
            return False, "El teléfono debe contener exactamente 10 dígitos"

        return True, None

    def _guardar_usuario(self):
        # validar el formulario antes de guardar
        valido, mensaje_error = self._validar_formulario()
        if not valido:
            QMessageBox.warning(self, "Error de Validación", mensaje_error)
            return

        # recopilar los datos del formulario
        datos_usuario = {
            "nombre": self.input_nombre.text().strip(),
            "apellido_paterno": self.input_apellido_paterno.text().strip(),
            "apellido_materno": self.input_apellido_materno.text().strip(),
            "email": self.input_email.text().strip(),
            "telefono": self.input_telefono.text().strip(),
            "contrasena": self.input_password.text(),
            "rol_id": self.combo_rol.currentData(),
            "activo": 1 if self.check_activo.isChecked() else 0,
        }

        if self._usuario_editando:
            # modo edición
            usuario, error = self._usuario_service.actualizar_usuario(
                self._usuario_editando.usuario_id, datos_usuario
            )
            titulo_error = "Error al Actualizar Usuario"
            titulo_exito = "Usuario Actualizado"
            msg_exito = "ha sido actualizado exitosamente."
        else:
            # modo creación
            usuario, error = self._usuario_service.crear_usuario(datos_usuario)
            titulo_error = "Error al Crear Usuario"
            titulo_exito = "Usuario Creado"
            msg_exito = "ha sido creado exitosamente."

        if error:
            QMessageBox.critical(self, titulo_error, error)
        elif usuario:
            nombre_completo = f"{usuario.nombre} {usuario.apellido_paterno}"
            QMessageBox.information(
                self,
                titulo_exito,
                f"El usuario {nombre_completo} {msg_exito}"
            )
            self._mostrar_seccion_usuarios()

    def _limpiar_formulario(self):
        # limpiar todos los campos del formulario
        self.input_nombre.clear()
        self.input_apellido_paterno.clear()
        self.input_apellido_materno.clear()
        self.input_email.clear()
        self.input_telefono.clear()
        self.input_password.clear()
        self.input_confirm_password.clear()
        self.combo_rol.setCurrentIndex(0)
        self.check_activo.setChecked(True)
        # enfocar el primer campo
        self.input_nombre.setFocus()

    def _create_clientes(self):
        self.clientes_widget = ClientesView(self._usuario_actual)
        self.clientes_widget.hide()

    def _mostrar_seccion_clientes(self):
        self._ocultar_contenido_actual()

        if self.clientes_widget.parent() != self.contentArea:
            self.contentLayout.addWidget(self.clientes_widget)

        self.clientes_widget.show()
        self.clientes_widget.cargar_datos()
        self.headerPageTitle.setText("Clientes")

        if hasattr(self, 'btnClientes'):
            self._resaltar_boton_activo(self.btnClientes)

    def _create_configuracion(self):
        self.configuracion_widget = ConfiguracionView()
        self.configuracion_widget.hide()

    def _mostrar_seccion_configuracion(self):
        self._ocultar_contenido_actual()

        if self.configuracion_widget.parent() != self.contentArea:
            self.contentLayout.addWidget(self.configuracion_widget)

        self.configuracion_widget.show()
        self.headerPageTitle.setText("Configuracion")

        if hasattr(self, 'btnConfiguracion'):
            self._resaltar_boton_activo(self.btnConfiguracion)
