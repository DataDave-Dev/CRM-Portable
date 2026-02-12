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