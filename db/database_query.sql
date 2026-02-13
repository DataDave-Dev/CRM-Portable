-- QUERY PARA LA BASE DE DATOS --

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

--- TABLAS DE CATÁLOGOS / CONFIGURACIÓN ---

-- Roles del sistema (Roles para negar accesos a ciertos usuarios)
CREATE TABLE IF NOT EXISTS Roles (
    RolID           INTEGER PRIMARY KEY AUTOINCREMENT,
    NombreRol       TEXT NOT NULL UNIQUE,
    Descripcion     TEXT,
    FechaCreacion   TEXT DEFAULT (datetime('now', 'localtime'))
);
-- Usuarios del sistema (equipo de ventas, admins, etc.)
CREATE TABLE IF NOT EXISTS Usuarios (
    UsuarioID       INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL,
    ApellidoPaterno TEXT NOT NULL,
    ApellidoMaterno TEXT,
    Email           TEXT NOT NULL UNIQUE,
    Telefono        TEXT,
    ContrasenaHash  TEXT NOT NULL,
    RolID           INTEGER NOT NULL,
    Activo          INTEGER DEFAULT 1,
    FotoPerfil      TEXT,
    FechaCreacion   TEXT DEFAULT (datetime('now', 'localtime')),
    UltimoAcceso    TEXT,
    FOREIGN KEY (RolID) REFERENCES Roles(RolID)
);
-- Catálogo de industrias
CREATE TABLE IF NOT EXISTS Industrias (
    IndustriaID     INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL UNIQUE,
    Descripcion     TEXT
);
-- Catálogo de tamaños de empresa
CREATE TABLE IF NOT EXISTS TamanosEmpresa (
    TamanoID        INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL UNIQUE,
    RangoEmpleados  TEXT,
    Descripcion     TEXT
);
-- Catálogo de orígenes de contacto (lead source)
CREATE TABLE IF NOT EXISTS OrigenesContacto (
    OrigenID        INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL UNIQUE,
    Descripcion     TEXT
);
-- Catálogo de países
CREATE TABLE IF NOT EXISTS Paises (
    PaisID          INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL UNIQUE,
    CodigoISO       TEXT
);
-- Catálogo de estados
CREATE TABLE IF NOT EXISTS Estados (
    EstadoID        INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL,
    PaisID          INTEGER NOT NULL,
    FOREIGN KEY (PaisID) REFERENCES Paises(PaisID)
);
-- Catálogo de ciudades
CREATE TABLE IF NOT EXISTS Ciudades (
    CiudadID        INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL,
    EstadoID        INTEGER NOT NULL,
    FOREIGN KEY (EstadoID) REFERENCES Estados(EstadoID)
);
-- Catálogo de monedas
CREATE TABLE IF NOT EXISTS Monedas (
    MonedaID        INTEGER PRIMARY KEY AUTOINCREMENT,
    Codigo          TEXT NOT NULL UNIQUE,
    Nombre          TEXT NOT NULL,
    Simbolo         TEXT
);
-- Catálogo de etapas del pipeline de ventas
CREATE TABLE IF NOT EXISTS EtapasVenta (
    EtapaID         INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL UNIQUE,
    Orden           INTEGER NOT NULL,
    Probabilidad    REAL DEFAULT 0,
    Color           TEXT,
    Descripcion     TEXT
);
-- Catálogo de motivos de pérdida
CREATE TABLE IF NOT EXISTS MotivosPerdida (
    MotivoID        INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL UNIQUE,
    Descripcion     TEXT
);
-- Catálogo de tipos de actividad
CREATE TABLE IF NOT EXISTS TiposActividad (
    TipoActividadID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL UNIQUE,
    Icono           TEXT,
    Color           TEXT
);
-- Catálogo de prioridades
CREATE TABLE IF NOT EXISTS Prioridades (
    PrioridadID     INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre          TEXT NOT NULL UNIQUE,
    Nivel           INTEGER NOT NULL,
    Color           TEXT
);
-- Catálogo de estados de actividad
CREATE TABLE IF NOT EXISTS EstadosActividad (
    EstadoActividadID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre            TEXT NOT NULL UNIQUE
);

--- MÓDULO 1: GESTIÓN DE CONTACTOS ---

-- Empresas / Cuentas
CREATE TABLE IF NOT EXISTS Empresas (
    EmpresaID            INTEGER PRIMARY KEY AUTOINCREMENT,
    RazonSocial          TEXT NOT NULL,
    NombreComercial      TEXT,
    RFC                  TEXT,
    IndustriaID          INTEGER,
    TamanoID             INTEGER,
    SitioWeb             TEXT,
    Telefono             TEXT,
    Email                TEXT,
    Direccion            TEXT,
    CiudadID             INTEGER,
    CodigoPostal         TEXT,
    IngresoAnualEstimado REAL,
    MonedaID             INTEGER,
    NumEmpleados         INTEGER,
    Descripcion          TEXT,
    LogoURL              TEXT,
    OrigenID             INTEGER,
    PropietarioID        INTEGER,
    Activo               INTEGER DEFAULT 1,
    FechaCreacion        TEXT DEFAULT (datetime('now', 'localtime')),
    FechaModificacion    TEXT DEFAULT (datetime('now', 'localtime')),
    CreadoPor            INTEGER,
    ModificadoPor        INTEGER,
    FOREIGN KEY (IndustriaID) REFERENCES Industrias(IndustriaID),
    FOREIGN KEY (TamanoID) REFERENCES TamanosEmpresa(TamanoID),
    FOREIGN KEY (CiudadID) REFERENCES Ciudades(CiudadID),
    FOREIGN KEY (MonedaID) REFERENCES Monedas(MonedaID),
    FOREIGN KEY (OrigenID) REFERENCES OrigenesContacto(OrigenID),
    FOREIGN KEY (PropietarioID) REFERENCES Usuarios(UsuarioID),
    FOREIGN KEY (CreadoPor) REFERENCES Usuarios(UsuarioID),
    FOREIGN KEY (ModificadoPor) REFERENCES Usuarios(UsuarioID)
);

-- Contactos (personas dentro de las empresas)
CREATE TABLE IF NOT EXISTS Contactos (
    ContactoID          INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre              TEXT NOT NULL,
    ApellidoPaterno     TEXT NOT NULL,
    ApellidoMaterno     TEXT,
    Email               TEXT,
    EmailSecundario     TEXT,
    TelefonoOficina     TEXT,
    TelefonoCelular     TEXT,
    Puesto              TEXT,
    Departamento        TEXT,
    EmpresaID           INTEGER,
    Direccion           TEXT,
    CiudadID            INTEGER,
    CodigoPostal        TEXT,
    FechaNacimiento     TEXT,
    LinkedInURL         TEXT,
    OrigenID            INTEGER,
    PropietarioID       INTEGER,
    EsContactoPrincipal INTEGER DEFAULT 0,
    NoContactar         INTEGER DEFAULT 0,
    Activo              INTEGER DEFAULT 1,
    FotoURL             TEXT,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FechaModificacion   TEXT DEFAULT (datetime('now', 'localtime')),
    CreadoPor           INTEGER,
    ModificadoPor       INTEGER,
    FOREIGN KEY (EmpresaID) REFERENCES Empresas(EmpresaID),
    FOREIGN KEY (CiudadID) REFERENCES Ciudades(CiudadID),
    FOREIGN KEY (OrigenID) REFERENCES OrigenesContacto(OrigenID),
    FOREIGN KEY (PropietarioID) REFERENCES Usuarios(UsuarioID),
    FOREIGN KEY (CreadoPor) REFERENCES Usuarios(UsuarioID),
    FOREIGN KEY (ModificadoPor) REFERENCES Usuarios(UsuarioID)
);

-- Notas de contactos
CREATE TABLE IF NOT EXISTS NotasContacto (
    NotaID              INTEGER PRIMARY KEY AUTOINCREMENT,
    ContactoID          INTEGER NOT NULL,
    Titulo              TEXT,
    Contenido           TEXT NOT NULL,
    EsPrivada           INTEGER DEFAULT 0,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    CreadoPor           INTEGER NOT NULL,
    FOREIGN KEY (ContactoID) REFERENCES Contactos(ContactoID),
    FOREIGN KEY (CreadoPor) REFERENCES Usuarios(UsuarioID)
);

-- Notas de empresas
CREATE TABLE IF NOT EXISTS NotasEmpresa (
    NotaID              INTEGER PRIMARY KEY AUTOINCREMENT,
    EmpresaID           INTEGER NOT NULL,
    Titulo              TEXT,
    Contenido           TEXT NOT NULL,
    EsPrivada           INTEGER DEFAULT 0,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    CreadoPor           INTEGER NOT NULL,
    FOREIGN KEY (EmpresaID) REFERENCES Empresas(EmpresaID),
    FOREIGN KEY (CreadoPor) REFERENCES Usuarios(UsuarioID)
);

--- MÓDULO 2: OPORTUNIDADES DE VENTA (PIPELINE) ---

-- Productos / Servicios del catálogo
CREATE TABLE IF NOT EXISTS Productos (
    ProductoID          INTEGER PRIMARY KEY AUTOINCREMENT,
    Codigo              TEXT UNIQUE,
    Nombre              TEXT NOT NULL,
    Descripcion         TEXT,
    Categoria           TEXT,
    PrecioUnitario      REAL,
    MonedaID            INTEGER,
    UnidadMedida        TEXT,
    Activo              INTEGER DEFAULT 1,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (MonedaID) REFERENCES Monedas(MonedaID)
);

-- Oportunidades de venta
CREATE TABLE IF NOT EXISTS Oportunidades (
    OportunidadID       INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre              TEXT NOT NULL,
    EmpresaID           INTEGER,
    ContactoID          INTEGER,
    EtapaID             INTEGER NOT NULL,
    MontoEstimado       REAL,
    MonedaID            INTEGER,
    ProbabilidadCierre  REAL,
    FechaCierreEstimada TEXT,
    FechaCierreReal     TEXT,
    OrigenID            INTEGER,
    PropietarioID       INTEGER NOT NULL,
    MotivosPerdidaID    INTEGER,
    NotasPerdida        TEXT,
    Descripcion         TEXT,
    EsGanada            INTEGER,  -- NULL=abierta, 1=ganada, 0=perdida
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FechaModificacion   TEXT DEFAULT (datetime('now', 'localtime')),
    CreadoPor           INTEGER,
    ModificadoPor       INTEGER,
    FOREIGN KEY (EmpresaID) REFERENCES Empresas(EmpresaID),
    FOREIGN KEY (ContactoID) REFERENCES Contactos(ContactoID),
    FOREIGN KEY (EtapaID) REFERENCES EtapasVenta(EtapaID),
    FOREIGN KEY (MonedaID) REFERENCES Monedas(MonedaID),
    FOREIGN KEY (OrigenID) REFERENCES OrigenesContacto(OrigenID),
    FOREIGN KEY (PropietarioID) REFERENCES Usuarios(UsuarioID),
    FOREIGN KEY (MotivosPerdidaID) REFERENCES MotivosPerdida(MotivoID),
    FOREIGN KEY (CreadoPor) REFERENCES Usuarios(UsuarioID),
    FOREIGN KEY (ModificadoPor) REFERENCES Usuarios(UsuarioID)
);

-- Detalle de productos en cada oportunidad
CREATE TABLE IF NOT EXISTS OportunidadProductos (
    OportunidadProductoID INTEGER PRIMARY KEY AUTOINCREMENT,
    OportunidadID         INTEGER NOT NULL,
    ProductoID            INTEGER NOT NULL,
    Cantidad              REAL NOT NULL DEFAULT 1,
    PrecioUnitario        REAL NOT NULL,
    Descuento             REAL DEFAULT 0,
    Notas                 TEXT,
    FOREIGN KEY (OportunidadID) REFERENCES Oportunidades(OportunidadID),
    FOREIGN KEY (ProductoID) REFERENCES Productos(ProductoID)
);

-- Historial de cambios de etapa en oportunidades
CREATE TABLE IF NOT EXISTS HistorialEtapas (
    HistorialID         INTEGER PRIMARY KEY AUTOINCREMENT,
    OportunidadID       INTEGER NOT NULL,
    EtapaAnteriorID     INTEGER,
    EtapaNuevaID        INTEGER NOT NULL,
    FechaCambio         TEXT DEFAULT (datetime('now', 'localtime')),
    UsuarioID           INTEGER NOT NULL,
    Comentario          TEXT,
    FOREIGN KEY (OportunidadID) REFERENCES Oportunidades(OportunidadID),
    FOREIGN KEY (EtapaAnteriorID) REFERENCES EtapasVenta(EtapaID),
    FOREIGN KEY (EtapaNuevaID) REFERENCES EtapasVenta(EtapaID),
    FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID)
);

-- Cotizaciones vinculadas a oportunidades
CREATE TABLE IF NOT EXISTS Cotizaciones (
    CotizacionID        INTEGER PRIMARY KEY AUTOINCREMENT,
    NumeroCotizacion    TEXT NOT NULL UNIQUE,
    OportunidadID       INTEGER NOT NULL,
    ContactoID          INTEGER,
    FechaEmision        TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    FechaVigencia       TEXT,
    Subtotal            REAL,
    IVA                 REAL,
    Total               REAL,
    MonedaID            INTEGER,
    Estado              TEXT DEFAULT 'Borrador',
    Notas               TEXT,
    TerminosCondiciones TEXT,
    CreadoPor           INTEGER NOT NULL,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (OportunidadID) REFERENCES Oportunidades(OportunidadID),
    FOREIGN KEY (ContactoID) REFERENCES Contactos(ContactoID),
    FOREIGN KEY (MonedaID) REFERENCES Monedas(MonedaID),
    FOREIGN KEY (CreadoPor) REFERENCES Usuarios(UsuarioID)
);

-- Detalle de cotizaciones
CREATE TABLE IF NOT EXISTS CotizacionDetalle (
    DetalleID           INTEGER PRIMARY KEY AUTOINCREMENT,
    CotizacionID        INTEGER NOT NULL,
    ProductoID          INTEGER NOT NULL,
    Descripcion         TEXT,
    Cantidad            REAL NOT NULL DEFAULT 1,
    PrecioUnitario      REAL NOT NULL,
    Descuento           REAL DEFAULT 0,
    FOREIGN KEY (CotizacionID) REFERENCES Cotizaciones(CotizacionID),
    FOREIGN KEY (ProductoID) REFERENCES Productos(ProductoID)
);

--- MÓDULO 3: ACTIVIDADES ---

-- Actividades (llamadas, reuniones, correos, tareas, visitas)
CREATE TABLE IF NOT EXISTS Actividades (
    ActividadID         INTEGER PRIMARY KEY AUTOINCREMENT,
    TipoActividadID     INTEGER NOT NULL,
    Asunto              TEXT NOT NULL,
    Descripcion         TEXT,
    ContactoID          INTEGER,
    EmpresaID           INTEGER,
    OportunidadID       INTEGER,
    PropietarioID       INTEGER NOT NULL,
    PrioridadID         INTEGER,
    EstadoActividadID   INTEGER NOT NULL,
    FechaInicio         TEXT,
    FechaFin            TEXT,
    FechaVencimiento    TEXT,
    DuracionMinutos     INTEGER,
    Ubicacion           TEXT,
    Resultado           TEXT,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FechaModificacion   TEXT DEFAULT (datetime('now', 'localtime')),
    CreadoPor           INTEGER,
    ModificadoPor       INTEGER,
    FOREIGN KEY (TipoActividadID) REFERENCES TiposActividad(TipoActividadID),
    FOREIGN KEY (ContactoID) REFERENCES Contactos(ContactoID),
    FOREIGN KEY (EmpresaID) REFERENCES Empresas(EmpresaID),
    FOREIGN KEY (OportunidadID) REFERENCES Oportunidades(OportunidadID),
    FOREIGN KEY (PropietarioID) REFERENCES Usuarios(UsuarioID),
    FOREIGN KEY (PrioridadID) REFERENCES Prioridades(PrioridadID),
    FOREIGN KEY (EstadoActividadID) REFERENCES EstadosActividad(EstadoActividadID),
    FOREIGN KEY (CreadoPor) REFERENCES Usuarios(UsuarioID),
    FOREIGN KEY (ModificadoPor) REFERENCES Usuarios(UsuarioID)
);

-- Participantes de actividades
CREATE TABLE IF NOT EXISTS ActividadParticipantes (
    ParticipanteID      INTEGER PRIMARY KEY AUTOINCREMENT,
    ActividadID         INTEGER NOT NULL,
    ContactoID          INTEGER,
    UsuarioID           INTEGER,
    Confirmado          INTEGER DEFAULT 0,
    FOREIGN KEY (ActividadID) REFERENCES Actividades(ActividadID),
    FOREIGN KEY (ContactoID) REFERENCES Contactos(ContactoID),
    FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID)
);