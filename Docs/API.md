# API de Servicios - CRM Sistema

Esta documentación describe la API pública de todos los servicios del sistema CRM.

## Tabla de Contenidos

1. [Convenciones](#convenciones)
2. [AuthService](#authservice)
3. [UsuarioService](#usuarioservice)
4. [EmpresaService](#empresaservice)
5. [ContactoService](#contactoservice)
6. [NotaContactoService](#notacontactoservice)
7. [NotaEmpresaService](#notaempresaservice)
8. [CatalogoService](#catalogoservice)

---

## Convenciones

### Patrón de retorno

Todos los métodos de servicios retornan una tupla `(resultado, error)`:

```python
resultado, error = service.metodo(parametros)

# Si es exitoso:
# resultado = objeto o valor retornado
# error = None

# Si falla:
# resultado = None
# error = mensaje de error descriptivo para el usuario
```

### Uso recomendado

```python
# Siempre verificar error primero
usuario, error = usuario_service.obtener_por_id(5)
if error:
    QMessageBox.warning(self, "Error", error)
    return
# Usar usuario solo si error es None
print(f"Usuario: {usuario.nombre}")
```

---

## AuthService

**Ubicación**: `app/services/auth_service.py`

**Propósito**: Autenticación y gestión de sesión.

### Métodos

#### `login(email, password)`

Autentica un usuario con email y contraseña.

**Parámetros**:
- `email` (str): Correo electrónico del usuario
- `password` (str): Contraseña en texto plano

**Retorna**:
- `(Usuario, None)` si autenticación exitosa
- `(None, error_msg)` si falla

**Ejemplo**:
```python
from app.services.auth_service import AuthService

service = AuthService()
usuario, error = service.login("admin@example.com", "password123")

if error:
    print(f"Error: {error}")
else:
    print(f"Bienvenido {usuario.nombre}")
    print(f"Rol: {usuario.rol_id}")
    print(f"Último acceso: {usuario.ultimo_acceso}")
```

**Validaciones**:
- Email debe existir en la base de datos
- Contraseña debe coincidir con hash almacenado
- Usuario debe estar activo

**Efectos secundarios**:
- Actualiza `ultimo_acceso` del usuario
- Registra intento de login en logs

---

## UsuarioService

**Ubicación**: `app/services/usuario_service.py`

**Propósito**: Gestión de usuarios del sistema.

### Métodos

#### `crear_usuario(datos_usuario)`

Crea un nuevo usuario en el sistema.

**Parámetros**:
- `datos_usuario` (dict): Datos del usuario
  - `nombre` (str, requerido): Nombre del usuario
  - `apellido_paterno` (str, requerido): Apellido paterno
  - `apellido_materno` (str, opcional): Apellido materno
  - `email` (str, requerido): Correo electrónico único
  - `telefono` (str, opcional): Teléfono de 10 dígitos
  - `contrasena` (str, requerido): Contraseña mínimo 8 caracteres
  - `rol_id` (int, requerido): ID del rol asignado
  - `activo` (int, opcional): 1=activo, 0=inactivo (default: 1)
  - `foto_perfil` (str, opcional): Ruta a imagen de perfil

**Retorna**:
- `(Usuario, None)` si creación exitosa
- `(None, error_msg)` si falla

**Ejemplo**:
```python
from app.services.usuario_service import UsuarioService

service = UsuarioService()
datos = {
    "nombre": "Juan",
    "apellido_paterno": "Perez",
    "apellido_materno": "Garcia",
    "email": "juan.perez@example.com",
    "telefono": "8123456789",
    "contrasena": "SecurePass123",
    "rol_id": 2
}

usuario, error = service.crear_usuario(datos)
if error:
    print(f"Error: {error}")
else:
    print(f"Usuario creado con ID: {usuario.usuario_id}")
```

**Validaciones**:
- Campos requeridos presentes y no vacíos
- Email con formato válido (regex)
- Email único en el sistema
- Contraseña mínimo 8 caracteres
- Teléfono: 10 dígitos numéricos (si se proporciona)

**Seguridad**:
- Contraseña se hashea con bcrypt antes de guardar
- NUNCA se loguea la contraseña en texto plano

#### `actualizar_usuario(usuario_id, datos_usuario)`

Actualiza un usuario existente.

**Parámetros**:
- `usuario_id` (int): ID del usuario a actualizar
- `datos_usuario` (dict): Datos a actualizar (mismos campos que `crear_usuario`, pero `contrasena` es opcional)

**Retorna**:
- `(Usuario, None)` si actualización exitosa
- `(None, error_msg)` si falla

**Ejemplo**:
```python
datos = {
    "nombre": "Juan Carlos",
    "apellido_paterno": "Perez",
    "email": "juan.perez@example.com",
    "rol_id": 3,
    "contrasena": "NewPassword456"  # Opcional
}

usuario, error = service.actualizar_usuario(5, datos)
```

**Nota**: Si no se proporciona `contrasena`, la contraseña anterior se mantiene.

---

## EmpresaService

**Ubicación**: `app/services/empresa_service.py`

**Propósito**: Gestión de empresas (cuentas).

### Métodos

#### `obtener_todas(limit=None, offset=0)`

Obtiene todas las empresas con paginación opcional.

**Parámetros**:
- `limit` (int, opcional): Número máximo de registros a retornar
- `offset` (int, opcional): Número de registros a saltar (default: 0)

**Retorna**:
- `(list[Empresa], None)` si exitoso
- `(None, error_msg)` si falla

**Ejemplo**:
```python
from app.services.empresa_service import EmpresaService

service = EmpresaService()

# Obtener primeras 50 empresas
empresas, error = service.obtener_todas(limit=50, offset=0)
if error is None:
    for empresa in empresas:
        print(f"{empresa.empresa_id}: {empresa.razon_social}")

# Obtener siguiente página
empresas_pagina2, error = service.obtener_todas(limit=50, offset=50)
```

#### `contar_total()`

Cuenta el total de empresas (útil para paginación).

**Retorna**:
- `(int, None)` si exitoso
- `(None, error_msg)` si falla

#### `obtener_por_id(empresa_id)`

Obtiene una empresa por su ID.

**Parámetros**:
- `empresa_id` (int): ID de la empresa

**Retorna**:
- `(Empresa, None)` si exitoso
- `(None, error_msg)` si falla

#### `crear_empresa(datos, usuario_actual_id)`

Crea una nueva empresa.

**Parámetros**:
- `datos` (dict): Datos de la empresa
  - `razon_social` (str, requerido): Razón social
  - `nombre_comercial` (str, opcional): Nombre comercial
  - `rfc` (str, opcional): RFC de 12-13 caracteres, único
  - `industria_id` (int, opcional): ID de la industria
  - `tamano_id` (int, opcional): ID del tamaño
  - `sitio_web` (str, opcional): URL del sitio web
  - `telefono` (str, opcional): Teléfono de 10 dígitos
  - `email` (str, opcional): Email con formato válido
  - `direccion` (str, opcional): Dirección física
  - `ciudad_id` (int, opcional): ID de la ciudad
  - `codigo_postal` (str, opcional): Código postal de 5 dígitos
  - `ingreso_anual_estimado` (float, opcional): Ingreso anual positivo
  - `moneda_id` (int, opcional): ID de la moneda
  - `num_empleados` (int, opcional): Número de empleados positivo
  - `descripcion` (str, opcional): Descripción
  - `origen_id` (int, opcional): ID del origen del lead
  - `propietario_id` (int, opcional): ID del usuario propietario
  - `activo` (int, opcional): 1=activo, 0=inactivo (default: 1)
- `usuario_actual_id` (int): ID del usuario que crea la empresa

**Retorna**:
- `(Empresa, None)` si creación exitosa
- `(None, error_msg)` si falla

**Ejemplo**:
```python
datos = {
    "razon_social": "Acme Corp S.A. de C.V.",
    "nombre_comercial": "Acme",
    "rfc": "ACM010101ABC",
    "industria_id": 1,
    "tamano_id": 2,
    "email": "contacto@acme.com",
    "telefono": "8187654321",
    "ingreso_anual_estimado": 5000000.00,
    "moneda_id": 1,
    "num_empleados": 150
}

empresa, error = service.crear_empresa(datos, usuario_actual_id=1)
```

**Validaciones**:
- Razón social requerida
- RFC: 12-13 caracteres alfanuméricos, único
- Email: formato válido
- Teléfono: 10 dígitos
- Código postal: 5 dígitos
- Ingreso anual: número positivo
- Número de empleados: entero positivo

**Nota**: El RFC es dato sensible y se filtra automáticamente en logs.

#### `actualizar_empresa(empresa_id, datos, usuario_actual_id)`

Actualiza una empresa existente.

**Parámetros**:
- `empresa_id` (int): ID de la empresa a actualizar
- `datos` (dict): Datos a actualizar (mismos campos que `crear_empresa`)
- `usuario_actual_id` (int): ID del usuario que actualiza

**Retorna**:
- `(Empresa, None)` si actualización exitosa
- `(None, error_msg)` si falla

---

## ContactoService

**Ubicación**: `app/services/contacto_service.py`

**Propósito**: Gestión de contactos (personas).

### Métodos

API similar a `EmpresaService`, con los siguientes métodos:

- `obtener_todos(limit=None, offset=0)`
- `contar_total()`
- `obtener_por_id(contacto_id)`
- `crear_contacto(datos, usuario_actual_id)`
- `actualizar_contacto(contacto_id, datos, usuario_actual_id)`

#### Campos de Contacto

**Campos del dict `datos`**:
- `nombre` (str, requerido): Nombre del contacto
- `apellido_paterno` (str, requerido): Apellido paterno
- `apellido_materno` (str, opcional): Apellido materno
- `email` (str, opcional): Email primario
- `email_secundario` (str, opcional): Email secundario
- `telefono_oficina` (str, opcional): Teléfono de oficina (10 dígitos)
- `telefono_celular` (str, opcional): Teléfono celular (10 dígitos)
- `puesto` (str, opcional): Puesto en la empresa
- `departamento` (str, opcional): Departamento
- `empresa_id` (int, opcional): ID de la empresa asociada
- `direccion` (str, opcional): Dirección física
- `ciudad_id` (int, opcional): ID de la ciudad
- `codigo_postal` (str, opcional): Código postal (5 dígitos)
- `fecha_nacimiento` (str, opcional): Fecha en formato AAAA-MM-DD
- `linkedin_url` (str, opcional): URL de perfil LinkedIn
- `origen_id` (int, opcional): ID del origen del lead
- `propietario_id` (int, opcional): ID del usuario propietario
- `es_contacto_principal` (int, opcional): 1=principal, 0=no
- `no_contactar` (int, opcional): 1=no contactar, 0=si
- `activo` (int, opcional): 1=activo, 0=inactivo

**Ejemplo**:
```python
from app.services.contacto_service import ContactoService

service = ContactoService()
datos = {
    "nombre": "Maria",
    "apellido_paterno": "Lopez",
    "email": "maria.lopez@empresa.com",
    "telefono_celular": "8123456789",
    "puesto": "Gerente de Compras",
    "empresa_id": 10,
    "es_contacto_principal": 1
}

contacto, error = service.crear_contacto(datos, usuario_actual_id=1)
```

---

## NotaContactoService

**Ubicación**: `app/services/nota_contacto_service.py`

**Propósito**: Gestión de notas asociadas a contactos.

### Métodos

#### `obtener_por_contacto(contacto_id)`

Obtiene todas las notas de un contacto específico.

**Parámetros**:
- `contacto_id` (int): ID del contacto

**Retorna**:
- `(list[NotaContacto], None)` si exitoso
- `(None, error_msg)` si falla

#### `obtener_por_id(nota_id)`

Obtiene una nota específica por su ID.

**Parámetros**:
- `nota_id` (int): ID de la nota

**Retorna**:
- `(NotaContacto, None)` si exitoso
- `(None, error_msg)` si falla

#### `crear_nota(datos, usuario_actual_id)`

Crea una nueva nota asociada a un contacto.

**Parámetros**:
- `datos` (dict): Datos de la nota
  - `contacto_id` (int, requerido): ID del contacto
  - `contenido` (str, requerido): Contenido de 1-5000 caracteres
  - `titulo` (str, opcional): Título de hasta 200 caracteres
  - `es_privada` (int, opcional): 1=privada, 0=pública (default: 0)
- `usuario_actual_id` (int): ID del usuario que crea la nota

**Retorna**:
- `(NotaContacto, None)` si creación exitosa
- `(None, error_msg)` si falla

**Ejemplo**:
```python
from app.services.nota_contacto_service import NotaContactoService

service = NotaContactoService()
datos = {
    "contacto_id": 15,
    "titulo": "Llamada de seguimiento",
    "contenido": "Se contactó al cliente para dar seguimiento a la propuesta. Muestra interés en continuar.",
    "es_privada": 0
}

nota, error = service.crear_nota(datos, usuario_actual_id=3)
if error is None:
    print(f"Nota {nota.nota_id} creada")
```

**Validaciones**:
- Contenido requerido
- Contenido: 1-5000 caracteres
- Título: máximo 200 caracteres (si se proporciona)

**Seguridad**:
- Contenido sanitizado contra XSS (HTML escapado)
- Operación registrada en auditoría

#### `actualizar_nota(nota_id, datos, usuario_actual_id=None)`

Actualiza una nota existente.

**Parámetros**:
- `nota_id` (int): ID de la nota a actualizar
- `datos` (dict): Datos a actualizar (titulo, contenido, es_privada)
- `usuario_actual_id` (int, opcional): ID del usuario que actualiza

**Retorna**:
- `(NotaContacto, None)` si actualización exitosa
- `(None, error_msg)` si falla

**Nota**: Se registra en auditoría con valores anteriores y nuevos.

#### `eliminar_nota(nota_id, usuario_actual_id=None)`

Elimina una nota del sistema.

**Parámetros**:
- `nota_id` (int): ID de la nota a eliminar
- `usuario_actual_id` (int, opcional): ID del usuario que elimina

**Retorna**:
- `(True, None)` si eliminación exitosa
- `(False, error_msg)` si falla

**Nota**: Se registra en auditoría con valores anteriores antes de eliminar.

---

## NotaEmpresaService

**Ubicación**: `app/services/nota_empresa_service.py`

**Propósito**: Gestión de notas asociadas a empresas.

### Métodos

API idéntica a `NotaContactoService`, pero para empresas:

- `obtener_por_empresa(empresa_id)`: Obtiene notas de una empresa
- `obtener_por_id(nota_id)`
- `crear_nota(datos, usuario_actual_id)`: Campo `empresa_id` en vez de `contacto_id`
- `actualizar_nota(nota_id, datos, usuario_actual_id=None)`
- `eliminar_nota(nota_id, usuario_actual_id=None)`

**Ejemplo**:
```python
from app.services.nota_empresa_service import NotaEmpresaService

service = NotaEmpresaService()

# Crear nota de empresa
datos = {
    "empresa_id": 25,
    "titulo": "Visita a instalaciones",
    "contenido": "Se realizó visita a las instalaciones de la empresa. Instalaciones en buen estado.",
    "es_privada": 0
}

nota, error = service.crear_nota(datos, usuario_actual_id=2)
```

---

## CatalogoService

**Ubicación**: `app/services/catalogo_service.py`

**Propósito**: Gestión genérica de catálogos (Industrias, Monedas, Países, etc.).

### Constructor

```python
from app.config.catalogos import CATALOGO_CONFIG
from app.services.catalogo_service import CatalogoService

# Crear servicio para un catálogo específico
config = CATALOGO_CONFIG['industrias']
service = CatalogoService(config)
```

### Métodos

#### `obtener_todos(filters=None)`

Obtiene todos los registros del catálogo con filtros opcionales.

**Parámetros**:
- `filters` (dict, opcional): Filtros a aplicar (ej: `{"activo": 1}`)

**Retorna**:
- `(list[dict], None)` si exitoso
- `(None, error_msg)` si falla

**Ejemplo**:
```python
# Obtener todas las industrias activas
config = CATALOGO_CONFIG['industrias']
service = CatalogoService(config)
items, error = service.obtener_todos(filters={"activo": 1})

for item in items:
    print(f"{item['industria_id']}: {item['nombre']}")
```

#### `obtener_por_id(id_value)`

Obtiene un registro específico por su ID.

**Parámetros**:
- `id_value` (int): ID del registro

**Retorna**:
- `(dict, None)` si exitoso
- `(None, error_msg)` si falla o no existe

#### `crear(datos)`

Crea un nuevo registro en el catálogo.

**Parámetros**:
- `datos` (dict): Datos del registro según configuración de columnas

**Retorna**:
- `(int, None)` - ID del registro creado
- `(None, error_msg)` si falla

**Validaciones**:
- Campos requeridos según configuración
- Unicidad en `unique_column` si está configurado

**Ejemplo**:
```python
# Crear nueva industria
config = CATALOGO_CONFIG['industrias']
service = CatalogoService(config)
datos = {"nombre": "Tecnología"}

nueva_id, error = service.crear(datos)
if error is None:
    print(f"Industria creada con ID: {nueva_id}")
```

**Nota**: Invalida caché automáticamente.

#### `actualizar(id_value, datos)`

Actualiza un registro existente.

**Parámetros**:
- `id_value` (int): ID del registro a actualizar
- `datos` (dict): Datos a actualizar

**Retorna**:
- `(True, None)` si actualización exitosa
- `(None, error_msg)` si falla

**Nota**: Valida unicidad excluyendo el registro actual.

#### `eliminar(id_value)`

Elimina un registro del catálogo.

**Parámetros**:
- `id_value` (int): ID del registro a eliminar

**Retorna**:
- `(True, None)` si eliminación exitosa
- `(None, error_msg)` si falla

**IMPORTANTE**: Verifica referencias antes de eliminar. Si existen registros que referencian este ID, la eliminación falla con un mensaje descriptivo.

**Ejemplo**:
```python
# Intentar eliminar industria
ok, error = service.eliminar(5)
if error:
    print(error)
    # Posible mensaje: "No se puede eliminar. Este registro es utilizado por 12 registro(s) en el sistema."
```

---

## Resumen de validaciones por servicio

| Servicio | Validaciones principales |
|----------|-------------------------|
| **AuthService** | Email existe, contraseña correcta, usuario activo |
| **UsuarioService** | Email único y válido, contraseña ≥8 chars, teléfono 10 dígitos |
| **EmpresaService** | Razón social requerida, RFC único 12-13 chars, email válido, teléfono 10 dígitos, CP 5 dígitos |
| **ContactoService** | Nombre y apellido requeridos, emails válidos, teléfonos 10 dígitos, CP 5 dígitos, fecha formato AAAA-MM-DD |
| **NotaContactoService** | Contenido requerido 1-5000 chars, título ≤200 chars, sanitización XSS |
| **NotaEmpresaService** | Igual que NotaContactoService |
| **CatalogoService** | Campos requeridos según config, unicidad en unique_column, protección contra eliminación con referencias |

---

## Códigos de error comunes

| Error | Significado |
|-------|-------------|
| `"El campo X es requerido"` | Campo obligatorio faltante o vacío |
| `"El formato del email no es válido"` | Email no cumple patrón regex |
| `"Este email ya está registrado"` | Email duplicado |
| `"Este RFC ya esta registrado"` | RFC duplicado |
| `"El teléfono debe contener exactamente 10 dígitos"` | Teléfono inválido |
| `"El codigo postal debe contener exactamente 5 dígitos"` | CP inválido |
| `"No se puede eliminar. Este registro es utilizado por N registro(s)"` | Violación de integridad referencial |
| `"Registro no encontrado"` | ID no existe en BD |
| `"Correo electrónico no encontrado"` | Usuario no existe |
| `"Contraseña incorrecta"` | Contraseña no coincide |
| Otros mensajes genéricos | Errores de BD sanitizados |

---

## Notas de seguridad

1. **Contraseñas**: NUNCA se retornan, loguean o almacenan en texto plano
2. **Datos sensibles**: RFC, tokens, etc. se filtran automáticamente en logs
3. **SQL Injection**: Todas las queries son parametrizadas
4. **XSS**: Contenido de notas se sanitiza con HTML escaping
5. **Auditoría**: Operaciones CREATE/UPDATE/DELETE se registran en LogAuditoria

---

## Ejemplo de uso completo

```python
from app.services.empresa_service import EmpresaService
from app.services.contacto_service import ContactoService
from app.services.nota_contacto_service import NotaContactoService

# 1. Crear empresa
empresa_service = EmpresaService()
datos_empresa = {
    "razon_social": "Tech Solutions S.A.",
    "rfc": "TSO010101ABC",
    "email": "contacto@techsolutions.com",
    "industria_id": 1
}
empresa, error = empresa_service.crear_empresa(datos_empresa, usuario_actual_id=1)
if error:
    print(f"Error al crear empresa: {error}")
    return

# 2. Crear contacto en esa empresa
contacto_service = ContactoService()
datos_contacto = {
    "nombre": "Ana",
    "apellido_paterno": "Martinez",
    "email": "ana@techsolutions.com",
    "empresa_id": empresa.empresa_id,
    "puesto": "CTO",
    "es_contacto_principal": 1
}
contacto, error = contacto_service.crear_contacto(datos_contacto, usuario_actual_id=1)
if error:
    print(f"Error al crear contacto: {error}")
    return

# 3. Agregar nota al contacto
nota_service = NotaContactoService()
datos_nota = {
    "contacto_id": contacto.contacto_id,
    "titulo": "Primera reunión",
    "contenido": "Reunión inicial exitosa. Muestra interés en nuestra propuesta.",
    "es_privada": 0
}
nota, error = nota_service.crear_nota(datos_nota, usuario_actual_id=1)
if error:
    print(f"Error al crear nota: {error}")
    return

print(f"✓ Empresa {empresa.empresa_id} creada")
print(f"✓ Contacto {contacto.contacto_id} creado")
print(f"✓ Nota {nota.nota_id} creada")
```
