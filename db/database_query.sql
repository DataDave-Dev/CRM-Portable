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
-- Catálogo de orígenes de contacto
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

--- MÓDULO 4: SEGMENTACIÓN ---

-- Etiquetas/Tags para segmentación flexible
CREATE TABLE IF NOT EXISTS Etiquetas (
    EtiquetaID          INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre              TEXT NOT NULL UNIQUE,
    Color               TEXT,
    Categoria           TEXT,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime'))
);

-- Relación muchos a muchos: Contactos <-> Etiquetas
CREATE TABLE IF NOT EXISTS ContactoEtiquetas (
    ContactoEtiquetaID  INTEGER PRIMARY KEY AUTOINCREMENT,
    ContactoID          INTEGER NOT NULL,
    EtiquetaID          INTEGER NOT NULL,
    FechaAsignacion     TEXT DEFAULT (datetime('now', 'localtime')),
    AsignadoPor         INTEGER,
    FOREIGN KEY (ContactoID) REFERENCES Contactos(ContactoID),
    FOREIGN KEY (EtiquetaID) REFERENCES Etiquetas(EtiquetaID),
    FOREIGN KEY (AsignadoPor) REFERENCES Usuarios(UsuarioID),
    UNIQUE (ContactoID, EtiquetaID)
);

-- Relación muchos a muchos: Empresas <-> Etiquetas
CREATE TABLE IF NOT EXISTS EmpresaEtiquetas (
    EmpresaEtiquetaID   INTEGER PRIMARY KEY AUTOINCREMENT,
    EmpresaID           INTEGER NOT NULL,
    EtiquetaID          INTEGER NOT NULL,
    FechaAsignacion     TEXT DEFAULT (datetime('now', 'localtime')),
    AsignadoPor         INTEGER,
    FOREIGN KEY (EmpresaID) REFERENCES Empresas(EmpresaID),
    FOREIGN KEY (EtiquetaID) REFERENCES Etiquetas(EtiquetaID),
    FOREIGN KEY (AsignadoPor) REFERENCES Usuarios(UsuarioID),
    UNIQUE (EmpresaID, EtiquetaID)
);

-- Segmentos (grupos de contactos o empresas con asignacion manual)
CREATE TABLE IF NOT EXISTS Segmentos (
    SegmentoID          INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre              TEXT NOT NULL,
    Descripcion         TEXT,
    TipoEntidad         TEXT NOT NULL,
    CantidadRegistros   INTEGER DEFAULT 0,
    CreadoPor           INTEGER NOT NULL,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FechaModificacion   TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (CreadoPor) REFERENCES Usuarios(UsuarioID)
);

-- Miembros contactos de cada segmento (asignacion manual)
CREATE TABLE IF NOT EXISTS SegmentoContactos (
    SegmentoContactoID  INTEGER PRIMARY KEY AUTOINCREMENT,
    SegmentoID          INTEGER NOT NULL,
    ContactoID          INTEGER NOT NULL,
    FechaAsignacion     TEXT DEFAULT (datetime('now', 'localtime')),
    AsignadoPor         INTEGER,
    FOREIGN KEY (SegmentoID) REFERENCES Segmentos(SegmentoID) ON DELETE CASCADE,
    FOREIGN KEY (ContactoID) REFERENCES Contactos(ContactoID) ON DELETE CASCADE,
    FOREIGN KEY (AsignadoPor) REFERENCES Usuarios(UsuarioID),
    UNIQUE (SegmentoID, ContactoID)
);

-- Miembros empresas de cada segmento (asignacion manual)
CREATE TABLE IF NOT EXISTS SegmentoEmpresas (
    SegmentoEmpresaID   INTEGER PRIMARY KEY AUTOINCREMENT,
    SegmentoID          INTEGER NOT NULL,
    EmpresaID           INTEGER NOT NULL,
    FechaAsignacion     TEXT DEFAULT (datetime('now', 'localtime')),
    AsignadoPor         INTEGER,
    FOREIGN KEY (SegmentoID) REFERENCES Segmentos(SegmentoID) ON DELETE CASCADE,
    FOREIGN KEY (EmpresaID) REFERENCES Empresas(EmpresaID) ON DELETE CASCADE,
    FOREIGN KEY (AsignadoPor) REFERENCES Usuarios(UsuarioID),
    UNIQUE (SegmentoID, EmpresaID)
);

--- MÓDULO 5: COMUNICACIÓN / CAMPAÑAS ---

-- Plantillas de correo
CREATE TABLE IF NOT EXISTS PlantillasCorreo (
    PlantillaID         INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre              TEXT NOT NULL,
    Asunto              TEXT NOT NULL,
    ContenidoHTML       TEXT NOT NULL,
    ContenidoTexto      TEXT,
    Categoria           TEXT,
    Activa              INTEGER DEFAULT 1,
    CreadoPor           INTEGER NOT NULL,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FechaModificacion   TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (CreadoPor) REFERENCES Usuarios(UsuarioID)
);

-- Campañas de comunicación
CREATE TABLE IF NOT EXISTS Campanas (
    CampanaID           INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre              TEXT NOT NULL,
    Descripcion         TEXT,
    Tipo                TEXT,
    Estado              TEXT DEFAULT 'Borrador',
    PlantillaID         INTEGER,
    SegmentoID          INTEGER,
    FechaProgramada     TEXT,
    FechaEnvio          TEXT,
    FechaFinalizacion   TEXT,
    TotalDestinatarios  INTEGER DEFAULT 0,
    TotalEnviados       INTEGER DEFAULT 0,
    TotalEntregados     INTEGER DEFAULT 0,
    TotalAbiertos       INTEGER DEFAULT 0,
    TotalClics          INTEGER DEFAULT 0,
    TotalRebotados      INTEGER DEFAULT 0,
    TotalDesuscripciones INTEGER DEFAULT 0,
    Presupuesto         REAL,
    MonedaID            INTEGER,
    PropietarioID       INTEGER NOT NULL,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FechaModificacion   TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (PlantillaID) REFERENCES PlantillasCorreo(PlantillaID),
    FOREIGN KEY (SegmentoID) REFERENCES Segmentos(SegmentoID),
    FOREIGN KEY (MonedaID) REFERENCES Monedas(MonedaID),
    FOREIGN KEY (PropietarioID) REFERENCES Usuarios(UsuarioID)
);

-- Destinatarios de campañas
CREATE TABLE IF NOT EXISTS CampanaDestinatarios (
    DestinatarioID      INTEGER PRIMARY KEY AUTOINCREMENT,
    CampanaID           INTEGER NOT NULL,
    ContactoID          INTEGER NOT NULL,
    EmailDestino        TEXT,
    EstadoEnvio         TEXT DEFAULT 'Pendiente',
    FechaEnvio          TEXT,
    FechaApertura       TEXT,
    CantidadAperturas   INTEGER DEFAULT 0,
    FechaPrimerClic     TEXT,
    CantidadClics       INTEGER DEFAULT 0,
    SeDesuscribio       INTEGER DEFAULT 0,
    FOREIGN KEY (CampanaID) REFERENCES Campanas(CampanaID),
    FOREIGN KEY (ContactoID) REFERENCES Contactos(ContactoID)
);

-- Registro de clics en campañas
CREATE TABLE IF NOT EXISTS CampanaClics (
    ClicID              INTEGER PRIMARY KEY AUTOINCREMENT,
    DestinatarioID      INTEGER NOT NULL,
    URLClickeada        TEXT NOT NULL,
    FechaClic           TEXT DEFAULT (datetime('now', 'localtime')),
    IPOrigen            TEXT,
    UserAgent           TEXT,
    FOREIGN KEY (DestinatarioID) REFERENCES CampanaDestinatarios(DestinatarioID)
);

-- Configuracion de cuentas de correo saliente
CREATE TABLE IF NOT EXISTS ConfiguracionCorreo (
    ConfigID            INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre              TEXT NOT NULL,
    Proveedor           TEXT NOT NULL DEFAULT 'SMTP',
    Host                TEXT,
    Puerto              INTEGER DEFAULT 587,
    UsarTLS             INTEGER DEFAULT 1,
    UsarSSL             INTEGER DEFAULT 0,
    EmailRemitente      TEXT NOT NULL,
    NombreRemitente     TEXT,
    Usuario             TEXT,
    Contrasena          TEXT,
    ApiKey              TEXT,
    Activa              INTEGER DEFAULT 0,
    Notas               TEXT,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FechaModificacion   TEXT DEFAULT (datetime('now', 'localtime'))
);

--- MÓDULO 6: REPORTES (Vistas para análisis) ---

-- Vista: Pipeline de ventas actual
CREATE VIEW IF NOT EXISTS vw_PipelineVentas AS
SELECT 
    o.OportunidadID,
    o.Nombre AS NombreOportunidad,
    e.RazonSocial AS Empresa,
    (c.Nombre || ' ' || c.ApellidoPaterno) AS Contacto,
    ev.Nombre AS Etapa,
    ev.Orden AS OrdenEtapa,
    o.MontoEstimado,
    o.ProbabilidadCierre,
    ROUND(o.MontoEstimado * o.ProbabilidadCierre / 100, 2) AS ValorPonderado,
    o.FechaCierreEstimada,
    (u.Nombre || ' ' || u.ApellidoPaterno) AS Vendedor,
    o.FechaCreacion,
    CAST(julianday('now', 'localtime') - julianday(o.FechaCreacion) AS INTEGER) AS DiasEnPipeline
FROM Oportunidades o
    LEFT JOIN Empresas e ON o.EmpresaID = e.EmpresaID
    LEFT JOIN Contactos c ON o.ContactoID = c.ContactoID
    INNER JOIN EtapasVenta ev ON o.EtapaID = ev.EtapaID
    INNER JOIN Usuarios u ON o.PropietarioID = u.UsuarioID
WHERE o.EsGanada IS NULL;

-- Vista: Rendimiento del equipo de ventas
CREATE VIEW IF NOT EXISTS vw_RendimientoVendedores AS
SELECT 
    u.UsuarioID,
    (u.Nombre || ' ' || u.ApellidoPaterno) AS Vendedor,
    COUNT(CASE WHEN o.EsGanada IS NULL THEN 1 END) AS OportunidadesAbiertas,
    COUNT(CASE WHEN o.EsGanada = 1 THEN 1 END) AS OportunidadesGanadas,
    COUNT(CASE WHEN o.EsGanada = 0 THEN 1 END) AS OportunidadesPerdidas,
    IFNULL(SUM(CASE WHEN o.EsGanada = 1 THEN o.MontoEstimado ELSE 0 END), 0) AS MontoGanado,
    IFNULL(SUM(CASE WHEN o.EsGanada IS NULL THEN o.MontoEstimado ELSE 0 END), 0) AS MontoPendiente,
    CASE 
        WHEN COUNT(CASE WHEN o.EsGanada IS NOT NULL THEN 1 END) > 0
        THEN ROUND(
            CAST(COUNT(CASE WHEN o.EsGanada = 1 THEN 1 END) AS REAL) / 
            COUNT(CASE WHEN o.EsGanada IS NOT NULL THEN 1 END) * 100, 2)
        ELSE 0
    END AS TasaConversion,
    CAST(AVG(CASE 
        WHEN o.EsGanada = 1 
        THEN julianday(o.FechaCierreReal) - julianday(o.FechaCreacion) 
    END) AS INTEGER) AS PromedioDiasCierre
FROM Usuarios u
    LEFT JOIN Oportunidades o ON u.UsuarioID = o.PropietarioID
WHERE u.RolID IN (SELECT RolID FROM Roles WHERE NombreRol IN ('Vendedor', 'Gerente de Ventas'))
GROUP BY u.UsuarioID, u.Nombre, u.ApellidoPaterno;

-- Vista: Análisis de conversión por etapa
CREATE VIEW IF NOT EXISTS vw_ConversionPorEtapa AS
SELECT 
    ev.EtapaID,
    ev.Nombre AS Etapa,
    ev.Orden,
    COUNT(o.OportunidadID) AS TotalOportunidades,
    IFNULL(SUM(o.MontoEstimado), 0) AS MontoTotal,
    ROUND(AVG(o.MontoEstimado), 2) AS TicketPromedio,
    ev.Probabilidad AS ProbabilidadEtapa
FROM EtapasVenta ev
    LEFT JOIN Oportunidades o ON ev.EtapaID = o.EtapaID
GROUP BY ev.EtapaID, ev.Nombre, ev.Orden, ev.Probabilidad;

-- Vista: Análisis de campañas
CREATE VIEW IF NOT EXISTS vw_AnalisisCampanas AS
SELECT 
    c.CampanaID,
    c.Nombre,
    c.Tipo,
    c.Estado,
    c.FechaEnvio,
    c.TotalDestinatarios,
    c.TotalEnviados,
    c.TotalEntregados,
    c.TotalAbiertos,
    c.TotalClics,
    c.TotalRebotados,
    c.TotalDesuscripciones,
    CASE WHEN c.TotalEnviados > 0 
         THEN ROUND(CAST(c.TotalEntregados AS REAL) / c.TotalEnviados * 100, 2)
         ELSE 0 END AS TasaEntrega,
    CASE WHEN c.TotalEntregados > 0 
         THEN ROUND(CAST(c.TotalAbiertos AS REAL) / c.TotalEntregados * 100, 2)
         ELSE 0 END AS TasaApertura,
    CASE WHEN c.TotalAbiertos > 0 
         THEN ROUND(CAST(c.TotalClics AS REAL) / c.TotalAbiertos * 100, 2)
         ELSE 0 END AS TasaClics,
    (u.Nombre || ' ' || u.ApellidoPaterno) AS Propietario
FROM Campanas c
    INNER JOIN Usuarios u ON c.PropietarioID = u.UsuarioID;

-- Vista: Actividad reciente por contacto
CREATE VIEW IF NOT EXISTS vw_ActividadRecienteContacto AS
SELECT 
    co.ContactoID,
    (co.Nombre || ' ' || co.ApellidoPaterno) AS NombreContacto,
    e.RazonSocial AS Empresa,
    COUNT(a.ActividadID) AS TotalActividades,
    MAX(a.FechaCreacion) AS UltimaActividad,
    CAST(julianday('now', 'localtime') - julianday(MAX(a.FechaCreacion)) AS INTEGER) AS DiasSinContacto,
    SUM(CASE WHEN ta.Nombre = 'Llamada' THEN 1 ELSE 0 END) AS TotalLlamadas,
    SUM(CASE WHEN ta.Nombre = 'Reunión' THEN 1 ELSE 0 END) AS TotalReuniones,
    SUM(CASE WHEN ta.Nombre = 'Correo' THEN 1 ELSE 0 END) AS TotalCorreos
FROM Contactos co
    LEFT JOIN Empresas e ON co.EmpresaID = e.EmpresaID
    LEFT JOIN Actividades a ON co.ContactoID = a.ContactoID
    LEFT JOIN TiposActividad ta ON a.TipoActividadID = ta.TipoActividadID
WHERE co.Activo = 1
GROUP BY co.ContactoID, co.Nombre, co.ApellidoPaterno, e.RazonSocial;

-- Vista: Subtotal calculado de productos en oportunidad
CREATE VIEW IF NOT EXISTS vw_OportunidadProductosDetalle AS
SELECT 
    op.OportunidadProductoID,
    op.OportunidadID,
    p.Nombre AS Producto,
    p.Codigo AS CodigoProducto,
    op.Cantidad,
    op.PrecioUnitario,
    op.Descuento,
    ROUND(op.Cantidad * op.PrecioUnitario * (1 - op.Descuento / 100), 2) AS Subtotal,
    op.Notas
FROM OportunidadProductos op
    INNER JOIN Productos p ON op.ProductoID = p.ProductoID;

-- Vista: Subtotal calculado de detalle de cotizaciones
CREATE VIEW IF NOT EXISTS vw_CotizacionDetalleCalc AS
SELECT 
    cd.DetalleID,
    cd.CotizacionID,
    p.Nombre AS Producto,
    cd.Descripcion,
    cd.Cantidad,
    cd.PrecioUnitario,
    cd.Descuento,
    ROUND(cd.Cantidad * cd.PrecioUnitario * (1 - cd.Descuento / 100), 2) AS Subtotal
FROM CotizacionDetalle cd
    INNER JOIN Productos p ON cd.ProductoID = p.ProductoID;

--- MÓDULO 7: RECORDATORIOS / NOTIFICACIONES ---

-- Recordatorios
CREATE TABLE IF NOT EXISTS Recordatorios (
    RecordatorioID      INTEGER PRIMARY KEY AUTOINCREMENT,
    UsuarioID           INTEGER NOT NULL,
    Titulo              TEXT NOT NULL,
    Descripcion         TEXT,
    FechaRecordatorio   TEXT NOT NULL,
    ContactoID          INTEGER,
    EmpresaID           INTEGER,
    OportunidadID       INTEGER,
    ActividadID         INTEGER,
    TipoRecurrencia     TEXT,
    EsLeido             INTEGER DEFAULT 0,
    EsCompletado        INTEGER DEFAULT 0,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID),
    FOREIGN KEY (ContactoID) REFERENCES Contactos(ContactoID),
    FOREIGN KEY (EmpresaID) REFERENCES Empresas(EmpresaID),
    FOREIGN KEY (OportunidadID) REFERENCES Oportunidades(OportunidadID),
    FOREIGN KEY (ActividadID) REFERENCES Actividades(ActividadID)
);

-- Notificaciones del sistema
CREATE TABLE IF NOT EXISTS Notificaciones (
    NotificacionID      INTEGER PRIMARY KEY AUTOINCREMENT,
    UsuarioID           INTEGER NOT NULL,
    Tipo                TEXT NOT NULL,
    Titulo              TEXT NOT NULL,
    Mensaje             TEXT,
    EntidadTipo         TEXT,
    EntidadID           INTEGER,
    URL                 TEXT,
    EsLeida             INTEGER DEFAULT 0,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FechaLectura        TEXT,
    FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID)
);

--- MÓDULOS ADICIONALES ---

-- Documentos / Archivos adjuntos
CREATE TABLE IF NOT EXISTS Documentos (
    DocumentoID         INTEGER PRIMARY KEY AUTOINCREMENT,
    NombreArchivo       TEXT NOT NULL,
    Extension           TEXT,
    TamanoBytes         INTEGER,
    RutaArchivo         TEXT NOT NULL,
    EntidadTipo         TEXT NOT NULL,
    EntidadID           INTEGER NOT NULL,
    Descripcion         TEXT,
    SubidoPor           INTEGER NOT NULL,
    FechaSubida         TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (SubidoPor) REFERENCES Usuarios(UsuarioID)
);

-- Registro de auditoría
CREATE TABLE IF NOT EXISTS LogAuditoria (
    LogID               INTEGER PRIMARY KEY AUTOINCREMENT,
    UsuarioID           INTEGER,
    Accion              TEXT NOT NULL,
    EntidadTipo         TEXT,
    EntidadID           INTEGER,
    ValoresAnteriores   TEXT,
    ValoresNuevos       TEXT,
    IPOrigen            TEXT,
    FechaAccion         TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID)
);

-- Metas de ventas
CREATE TABLE IF NOT EXISTS MetasVentas (
    MetaID              INTEGER PRIMARY KEY AUTOINCREMENT,
    UsuarioID           INTEGER NOT NULL,
    Periodo             TEXT NOT NULL,
    TipoPeriodo         TEXT NOT NULL,
    MetaMonto           REAL NOT NULL,
    MonedaID            INTEGER,
    MetaOportunidades   INTEGER,
    MontoAlcanzado      REAL DEFAULT 0,
    OportunidadesCerradas INTEGER DEFAULT 0,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID),
    FOREIGN KEY (MonedaID) REFERENCES Monedas(MonedaID)
);

--- TRIGGERS ---

-- Actualizar FechaModificacion en Empresas
CREATE TRIGGER IF NOT EXISTS trg_Empresas_UpdateFecha
AFTER UPDATE ON Empresas
BEGIN
    UPDATE Empresas 
    SET FechaModificacion = datetime('now', 'localtime') 
    WHERE EmpresaID = NEW.EmpresaID;
END;

-- Actualizar FechaModificacion en Contactos
CREATE TRIGGER IF NOT EXISTS trg_Contactos_UpdateFecha
AFTER UPDATE ON Contactos
BEGIN
    UPDATE Contactos 
    SET FechaModificacion = datetime('now', 'localtime') 
    WHERE ContactoID = NEW.ContactoID;
END;

-- Actualizar FechaModificacion en Oportunidades
CREATE TRIGGER IF NOT EXISTS trg_Oportunidades_UpdateFecha
AFTER UPDATE ON Oportunidades
BEGIN
    UPDATE Oportunidades 
    SET FechaModificacion = datetime('now', 'localtime') 
    WHERE OportunidadID = NEW.OportunidadID;
END;

-- Registrar cambio de etapa en HistorialEtapas automáticamente
CREATE TRIGGER IF NOT EXISTS trg_Oportunidades_HistorialEtapa
AFTER UPDATE OF EtapaID ON Oportunidades
WHEN OLD.EtapaID != NEW.EtapaID
BEGIN
    INSERT INTO HistorialEtapas (OportunidadID, EtapaAnteriorID, EtapaNuevaID, UsuarioID, Comentario)
    VALUES (
        NEW.OportunidadID,
        OLD.EtapaID,
        NEW.EtapaID,
        IFNULL(NEW.ModificadoPor, NEW.PropietarioID),
        'Cambio automático de etapa'
    );
END;

-- Crear notificación cuando se asigna nueva oportunidad
CREATE TRIGGER IF NOT EXISTS trg_Oportunidades_NotificacionNueva
AFTER INSERT ON Oportunidades
BEGIN
    INSERT INTO Notificaciones (UsuarioID, Tipo, Titulo, Mensaje, EntidadTipo, EntidadID)
    VALUES (
        NEW.PropietarioID,
        'NuevaOportunidad',
        'Nueva oportunidad asignada: ' || NEW.Nombre,
        'Se te ha asignado la oportunidad "' || NEW.Nombre || '" con un monto estimado de $' || IFNULL(NEW.MontoEstimado, 0),
        'Oportunidad',
        NEW.OportunidadID
    );
END;

-- Crear notificación cuando una cotización es aceptada
CREATE TRIGGER IF NOT EXISTS trg_Cotizaciones_Aceptada
AFTER UPDATE OF Estado ON Cotizaciones
WHEN NEW.Estado = 'Aceptada' AND OLD.Estado != 'Aceptada'
BEGIN
    INSERT INTO Notificaciones (UsuarioID, Tipo, Titulo, Mensaje, EntidadTipo, EntidadID)
    VALUES (
        NEW.CreadoPor,
        'CotizacionAceptada',
        'Cotización aceptada: ' || NEW.NumeroCotizacion,
        'La cotización ' || NEW.NumeroCotizacion || ' ha sido aceptada por el cliente.',
        'Cotizacion',
        NEW.CotizacionID
    );
END;

-- Auditoría en eliminación de contactos
CREATE TRIGGER IF NOT EXISTS trg_Contactos_AuditoriaDelete
BEFORE DELETE ON Contactos
BEGIN
    INSERT INTO LogAuditoria (UsuarioID, Accion, EntidadTipo, EntidadID, ValoresAnteriores)
    VALUES (
        NULL,
        'DELETE',
        'Contacto',
        OLD.ContactoID,
        '{"Nombre":"' || OLD.Nombre || '","Apellido":"' || OLD.ApellidoPaterno || '","Email":"' || IFNULL(OLD.Email, '') || '","EmpresaID":' || IFNULL(OLD.EmpresaID, 'null') || '}'
    );
END;

-- Auditoría en eliminación de empresas
CREATE TRIGGER IF NOT EXISTS trg_Empresas_AuditoriaDelete
BEFORE DELETE ON Empresas
BEGIN
    INSERT INTO LogAuditoria (UsuarioID, Accion, EntidadTipo, EntidadID, ValoresAnteriores)
    VALUES (
        NULL,
        'DELETE',
        'Empresa',
        OLD.EmpresaID,
        '{"RazonSocial":"' || OLD.RazonSocial || '","RFC":"' || IFNULL(OLD.RFC, '') || '"}'
    );
END;

-- DATOS INICIALES ---

-- Roles
INSERT INTO Roles (NombreRol, Descripcion) VALUES
('Administrador', 'Acceso total al sistema'),
('Gerente de Ventas', 'Gestión del equipo de ventas y reportes'),
('Vendedor', 'Gestión de contactos, oportunidades y actividades'),
('Marketing', 'Gestión de campañas y comunicaciones');

-- Usuarios de prueba (contraseña de todos: Test1234)
INSERT INTO Usuarios (UsuarioID, Nombre, ApellidoPaterno, ApellidoMaterno, Email, Telefono, ContrasenaHash, RolID, Activo) VALUES
(2, 'María',  'González',  'Soto',   'mgonzalez@crm.com',  '8181110001', '$2b$12$CHdRzEA79sLCImEidhdGSObYTEzSQFmoEo8FQefSf5dRGD9R6XSmW', 3, 1),
(3, 'Carlos', 'Ramírez',   'Torres', 'cramirez@crm.com',   '8182220002', '$2b$12$CHdRzEA79sLCImEidhdGSObYTEzSQFmoEo8FQefSf5dRGD9R6XSmW', 3, 1),
(4, 'Lucía',  'Hernández', 'Garza',  'lhernandez@crm.com', '8183330003', '$2b$12$CHdRzEA79sLCImEidhdGSObYTEzSQFmoEo8FQefSf5dRGD9R6XSmW', 2, 1),
(5, 'Pedro',  'Sánchez',   'Medina', 'psanchez@crm.com',   '8184440004', '$2b$12$CHdRzEA79sLCImEidhdGSObYTEzSQFmoEo8FQefSf5dRGD9R6XSmW', 4, 1);

-- Etapas de venta
INSERT INTO EtapasVenta (Nombre, Orden, Probabilidad, Color, Descripcion) VALUES
('Prospecto', 1, 10.00, '#3498DB', 'Contacto inicial identificado'),
('Calificación', 2, 20.00, '#2ECC71', 'Evaluando si es un prospecto viable'),
('Presentación', 3, 40.00, '#F39C12', 'Presentación de producto/servicio realizada'),
('Propuesta', 4, 60.00, '#E67E22', 'Cotización o propuesta enviada'),
('Negociación', 5, 80.00, '#E74C3C', 'En proceso de negociación de términos'),
('Cierre Ganado', 6, 100.00, '#27AE60', 'Oportunidad ganada exitosamente'),
('Cierre Perdido', 7, 0.00, '#95A5A6', 'Oportunidad perdida');

-- Tipos de actividad
INSERT INTO TiposActividad (Nombre, Icono, Color) VALUES
('Llamada', 'phone', '#3498DB'),
('Reunión', 'users', '#2ECC71'),
('Correo', 'mail', '#F39C12'),
('Tarea', 'check-square', '#E74C3C'),
('Visita', 'map-pin', '#9B59B6'),
('WhatsApp', 'message-circle', '#25D366');

-- Prioridades
INSERT INTO Prioridades (Nombre, Nivel, Color) VALUES
('Baja', 1, '#95A5A6'),
('Media', 2, '#F39C12'),
('Alta', 3, '#E67E22'),
('Urgente', 4, '#E74C3C');

-- Estados de actividad
INSERT INTO EstadosActividad (Nombre) VALUES
('Pendiente'),
('En Progreso'),
('Completada'),
('Cancelada'),
('Reprogramada');

-- Motivos de pérdida
INSERT INTO MotivosPerdida (Nombre, Descripcion) VALUES
('Precio', 'El precio fue demasiado alto para el cliente'),
('Competencia', 'El cliente eligió a un competidor'),
('Presupuesto', 'El cliente no tiene presupuesto disponible'),
('Timing', 'No es el momento adecuado para el cliente'),
('Funcionalidad', 'El producto no cumple con los requerimientos'),
('Sin respuesta', 'El cliente dejó de responder'),
('Cancelación interna', 'Se canceló internamente el seguimiento');

-- Orígenes de contacto
INSERT INTO OrigenesContacto (Nombre, Descripcion) VALUES
('Sitio Web', 'Formulario de contacto en el sitio web'),
('Referido', 'Referencia de un cliente existente'),
('Redes Sociales', 'Facebook, Instagram, LinkedIn, etc.'),
('Llamada Entrante', 'El cliente llamó directamente'),
('Feria/Exposición', 'Contacto en evento o feria comercial'),
('Email Marketing', 'Respuesta a campaña de email'),
('Google Ads', 'Campaña de publicidad en Google'),
('Directorio', 'Contacto de directorio empresarial'),
('Visita en frío', 'Prospección directa sin cita');

-- Industrias
INSERT INTO Industrias (Nombre) VALUES
('Aviación'), ('Automotriz'), ('Manufactura'), ('Construcción'),
('Minería'), ('Energía'), ('Transporte'), ('Agricultura'),
('Alimentos y Bebidas'), ('Tecnología'), ('Salud'), ('Educación'),
('Gobierno'), ('Retail'), ('Servicios Financieros'), ('Petroquímica');

-- Tamaños de empresa
INSERT INTO TamanosEmpresa (Nombre, RangoEmpleados) VALUES
('Micro', '1-10'),
('Pequeña', '11-50'),
('Mediana', '51-250'),
('Grande', '251-1000'),
('Corporativo', '1000+');

-- Monedas
INSERT INTO Monedas (Codigo, Nombre, Simbolo) VALUES
('MXN', 'Peso Mexicano', '$'),
('USD', 'Dólar Estadounidense', 'US$'),
('EUR', 'Euro', '€');

-- Países y estados de México
INSERT INTO Paises (Nombre, CodigoISO) VALUES ('México', 'MEX'), ('Estados Unidos', 'USA');

INSERT INTO Estados (Nombre, PaisID) VALUES
('Nuevo León', 1), ('Ciudad de México', 1), ('Jalisco', 1),
('Estado de México', 1), ('Coahuila', 1), ('Tamaulipas', 1),
('Chihuahua', 1), ('Sonora', 1), ('Puebla', 1), ('Guanajuato', 1),
('Querétaro', 1), ('Veracruz', 1), ('Baja California', 1);

INSERT INTO Ciudades (Nombre, EstadoID) VALUES
('Monterrey', 1), ('San Pedro Garza García', 1), ('Guadalupe', 1),
('Apodaca', 1), ('San Nicolás de los Garza', 1), ('Santa Catarina', 1),
('Ciudad de México', 2), ('Guadalajara', 3), ('Zapopan', 3),
('Toluca', 4), ('Saltillo', 5), ('Reynosa', 6),
('Chihuahua', 7), ('Hermosillo', 8), ('Puebla', 9),
('León', 10), ('Querétaro', 11), ('Veracruz', 12), ('Tijuana', 13);

-- Empresas / Clientes
INSERT INTO Empresas (RazonSocial, NombreComercial, RFC, IndustriaID, TamanoID, SitioWeb, Telefono, Email, Direccion, CiudadID, CodigoPostal, MonedaID, OrigenID, PropietarioID, Activo) VALUES
('PINTURAS INDUSTRIALES Y AUTOMOTRICES GARCIA', 'PIAGA',        'PIA980324BT2', 2,  3, 'https://piaga.com.mx/',          '8181570333', 'ventas@piaga.com.mx',           'GENERAL NICOLAS BRAVO ORIENTE 502', 1,  '67100', 1, 9, 2, 1),
('GRUPO INDUSTRIAL MONTERREY SA DE CV',         'GIM',          'GIM910512KL4', 3,  4, 'https://gim.com.mx',             '8183450000', 'contacto@gim.com.mx',           'AV. FUNDIDORA 501',                 1,  '64010', 1, 2, 4, 1),
('TECHSOLUTIONS NORTE SA DE CV',                'TechSolutions', 'TSN010830AB3', 10, 3, 'https://techsolutions.mx',       '8180010200', 'hola@techsolutions.mx',         'AV. LAZARO CARDENAS 2400 L-12',     2,  '66267', 1, 1, 2, 1),
('CONSTRUCTORA VANGUARDIA SA DE CV',            'Vanguardia',   'CVG860214PQ9', 4,  4, 'https://vanguardiaconstruye.mx', '3311234567', 'ventas@vanguardiaconstruye.mx', 'AV. AMERICAS 1800 PISO 4',          8,  '44630', 1, 5, 4, 1),
('DISTRIBUIDORA DEL NORTE SA DE CV',            'DistNorte',    'DNO990710WR1', 14, 3, 'https://distnorte.mx',           '8442340010', 'compras@distnorte.mx',          'BLVD. V. CARRANZA 2709',            11, '25070', 1, 8, 3, 1),
('MINERA SAN PEDRO SA DE CV',                   'MinSanPedro',  'MSP750324XT5', 5,  5, 'https://minerasanpedro.mx',      '6141234567', 'operaciones@minerasanpedro.mx', 'KM 14.5 CARRETERA CHIHUAHUA-DEL',   13, '31010', 1, 9, 2, 1),
('TRANSPORTES REYES SA DE CV',                  'TransReyes',   'TRE880620VN8', 7,  2, NULL,                             '5550001234', 'logistica@transreyes.mx',       'CALZ. DE LA VIGA 1820',             7,  '09440', 1, 4, 3, 1),
('AGRO EXPORTACIONES SA DE CV',                 'AgroExport',   'AEX030418JM2', 8,  3, 'https://agroexport.mx',          '6621009988', 'export@agroexport.mx',          'BLVD. SOLIDARIDAD 3000',            14, '83180', 1, 5, 4, 1);

-- Contactos
INSERT INTO Contactos (Nombre, ApellidoPaterno, ApellidoMaterno, Email, TelefonoCelular, Puesto, Departamento, EmpresaID, EsContactoPrincipal, PropietarioID, Activo) VALUES
('Alonso David', 'De León',   'Rodarte',   'soporte@expertgroup.mx',     '8120222986', 'Auxiliar de Sistemas',     'Sistemas',      1, 1, 2, 1),
('Roberto',      'García',    'Ávila',     'rgarcia@piaga.com.mx',       '8181000002', 'Director General',         'Dirección',     1, 0, 2, 1),
('Daniela',      'Flores',    'Ríos',      'dflores@piaga.com.mx',       '8189900003', 'Jefa de Compras',          'Compras',       1, 0, 2, 1),
('Enrique',      'Torres',    'Mendoza',   'etorres@gim.com.mx',         '8183450001', 'Gerente de Operaciones',   'Operaciones',   2, 1, 4, 1),
('Sofía',        'Martínez',  'Salinas',   'smartinez@gim.com.mx',       '8183450002', 'Directora de Finanzas',    'Finanzas',      2, 0, 4, 1),
('Diego',        'López',     'Vega',      'dlopez@techsolutions.mx',    '8180010204', 'CTO',                      'Tecnología',    3, 1, 2, 1),
('Patricia',     'Morales',   'Castillo',  'pmorales@vanguardia.mx',     '3311234568', 'Directora de Proyectos',   'Proyectos',     4, 1, 4, 1),
('Héctor',       'Jiménez',   'Ruiz',      'hjimenez@vanguardia.mx',     '3311234569', 'Jefe de Compras',          'Compras',       4, 0, 4, 1),
('Laura',        'Reyes',     'Domínguez', 'lreyes@distnorte.mx',        '8442340012', 'Gerente Comercial',        'Ventas',        5, 1, 3, 1),
('Arturo',       'Chávez',    'Peña',      'achavez@minerasp.mx',        '6141234568', 'Director de Operaciones',  'Operaciones',   6, 1, 2, 1),
('Gabriela',     'Núñez',     'Vargas',    'gnunez@transreyes.mx',       '5550001235', 'Coordinadora Logística',   'Logística',     7, 1, 3, 1),
('Fernando',     'Ramos',     'Ortega',    'framos@agroexport.mx',       '6621009989', 'Gerente de Exportaciones', 'Exportaciones', 8, 1, 4, 1),
('Valentina',    'Cruz',      'León',      'vcruz@agroexport.mx',        '6621009990', 'Asistente Ejecutiva',      'Dirección',     8, 0, 4, 1);

-- Etiquetas
INSERT INTO Etiquetas (EtiquetaID, Nombre, Color, Categoria) VALUES
(1, 'Cliente Premium',    '#D3AF37', 'Clientes'),
(2, 'Prospecto Caliente', '#E74C3C', 'Ventas'),
(3, 'Industria Grande',   '#3498DB', 'Segmentación');

-- Oportunidades
INSERT INTO Oportunidades (Nombre, EmpresaID, ContactoID, EtapaID, MontoEstimado, MonedaID, ProbabilidadCierre, FechaCierreEstimada, PropietarioID, FechaCreacion) VALUES
('Contrato mantenimiento pintura 2026',   1,  3, 4,   85000, 1, 60, '2026-03-31', 2, '2026-01-10'),
('Implementación ERP módulos industria',  2,  4, 3,  350000, 1, 40, '2026-04-30', 3, '2026-01-20'),
('Consultoría infraestructura TI',        3,  6, 2,  120000, 1, 20, '2026-05-15', 2, '2026-02-01'),
('Equipos construcción pesada Q1 2026',   4,  7, 5,  450000, 1, 80, '2026-03-15', 4, '2026-01-15'),
('Software gestión de inventario',        5,  9, 4,   95000, 1, 60, '2026-04-01', 3, '2026-02-10'),
('Equipos de seguridad industrial',       6, 10, 1,  200000, 1, 10, '2026-06-30', 2, '2026-02-05');

INSERT INTO Oportunidades (Nombre, EmpresaID, ContactoID, EtapaID, MontoEstimado, MonedaID, ProbabilidadCierre, FechaCierreEstimada, PropietarioID, FechaCreacion) VALUES
('Sistema GPS flotilla transporte',      7, 11, 3,   45000, 1, 40, '2026-04-30', 3, '2025-11-20'),
('Plataforma gestión agrícola integral', 8, 12, 2,  180000, 1, 20, '2026-06-01', 4, '2025-12-01');

INSERT INTO Oportunidades (Nombre, EmpresaID, ContactoID, EtapaID, MontoEstimado, MonedaID, ProbabilidadCierre, FechaCierreEstimada, FechaCierreReal, PropietarioID, EsGanada, FechaCreacion) VALUES
('Pintura base industrial 2025',         1,  2, 6,  320000, 1, 100, '2025-06-30', '2025-06-01', 2, 1, '2025-03-15'),
('Automatización línea de producción',   2,  5, 6,  850000, 1, 100, '2025-10-31', '2025-09-30', 4, 1, '2025-05-10'),
('Migración y virtualización servidores',3,  6, 6,  240000, 1, 100, '2025-11-30', '2025-10-15', 3, 1, '2025-08-20'),
('Grúas y equipo pesado 2025',           4,  8, 6, 1200000, 1, 100, '2025-08-31', '2025-07-30', 4, 1, '2025-02-01');

INSERT INTO Oportunidades (Nombre, EmpresaID, ContactoID, EtapaID, MontoEstimado, MonedaID, ProbabilidadCierre, FechaCierreEstimada, FechaCierreReal, PropietarioID, EsGanada, MotivosPerdidaID, FechaCreacion) VALUES
('Licencias software gestión retail',    5,  9, 7,   75000, 1, 0, '2025-08-31', '2025-08-01', 3, 0, 1, '2025-06-15'),
('Equipamiento explosivo minero Q2',     6, 10, 7,  550000, 1, 0, '2025-07-31', '2025-06-30', 2, 0, 2, '2025-04-20'),
('Flotilla GPS completa 30 unidades',    7, 11, 7,  180000, 1, 0, '2025-12-31', '2025-11-20', 3, 0, 1, '2025-09-10');

-- Actividades
INSERT INTO Actividades (TipoActividadID, Asunto, ContactoID, EmpresaID, OportunidadID, PropietarioID, PrioridadID, EstadoActividadID, FechaInicio, FechaFin, FechaCreacion) VALUES
(1, 'Llamada inicial prospección PIAGA',           1,  1,  1, 2, 2, 3, '2026-01-08', '2026-01-08', '2026-01-08'),
(2, 'Reunión presentación solución PIAGA',         3,  1,  1, 2, 3, 3, '2026-01-12', '2026-01-12', '2026-01-12'),
(3, 'Envío propuesta comercial PIAGA',             3,  1,  1, 2, 2, 3, '2026-01-15', '2026-01-15', '2026-01-15'),
(1, 'Follow-up oportunidad ERP GIM',              4,  2,  2, 3, 3, 3, '2026-01-22', '2026-01-22', '2026-01-22'),
(2, 'Demo sistema ERP módulos',                   4,  2,  2, 3, 3, 3, '2026-01-28', '2026-01-28', '2026-01-28'),
(3, 'Envío especificaciones técnicas GIM',        5,  2,  2, 3, 2, 3, '2026-02-02', '2026-02-02', '2026-02-02'),
(1, 'Llamada calificación TechSolutions',         6,  3,  3, 2, 2, 3, '2026-02-03', '2026-02-03', '2026-02-03'),
(4, 'Preparar análisis de requerimientos TI',     6,  3,  3, 2, 2, 1, '2026-02-20', NULL,         '2026-02-03'),
(5, 'Visita instalaciones Vanguardia',            7,  4,  4, 4, 3, 3, '2026-01-20', '2026-01-20', '2026-01-20'),
(2, 'Negociación contrato equipos pesados',       7,  4,  4, 4, 4, 3, '2026-01-25', '2026-01-25', '2026-01-25'),
(3, 'Envío contrato borrador Vanguardia',         7,  4,  4, 4, 3, 3, '2026-02-05', '2026-02-05', '2026-02-05'),
(1, 'Seguimiento propuesta DistNorte',            9,  5,  5, 3, 2, 3, '2026-02-12', '2026-02-12', '2026-02-12'),
(3, 'Propuesta formal software inventario',       9,  5,  5, 3, 2, 3, '2026-02-15', '2026-02-15', '2026-02-15'),
(1, 'Llamada prospección MinSanPedro',           10,  6,  6, 2, 1, 3, '2026-02-06', '2026-02-06', '2026-02-06'),
(3, 'Envío catálogo equipos de seguridad',       10,  6,  6, 2, 1, 3, '2026-02-18', '2026-02-18', '2026-02-18'),
(5, 'Visita instalaciones TransReyes',           11,  7,  7, 3, 2, 3, '2025-11-25', '2025-11-25', '2025-11-25'),
(1, 'Seguimiento sistema GPS flotilla',          11,  7,  7, 3, 2, 3, '2025-12-05', '2025-12-05', '2025-12-05'),
(3, 'Envío cotización plataforma agrícola',      12,  8,  8, 4, 2, 3, '2025-12-05', '2025-12-05', '2025-12-05'),
(2, 'Reunión presentación AgroExport',           12,  8,  8, 4, 3, 3, '2025-12-15', '2025-12-15', '2025-12-15'),
(1, 'Llamada cierre PIAGA pintura 2025',          2,  1,  9, 2, 4, 3, '2025-05-28', '2025-05-28', '2025-05-28'),
(2, 'Reunión firma contrato GIM automatización',  4,  2, 10, 4, 4, 3, '2025-09-28', '2025-09-28', '2025-09-28'),
(6, 'WhatsApp confirmación cierre TechSolutions', 6,  3, 11, 3, 3, 3, '2025-10-12', '2025-10-12', '2025-10-12'),
(2, 'Reunión firma grúas Vanguardia',             7,  4, 12, 4, 4, 3, '2025-07-25', '2025-07-25', '2025-07-25'),
(4, 'Análisis pérdida DistNorte licencias',       9,  5, 13, 3, 2, 3, '2025-08-03', '2025-08-03', '2025-08-03'),
(4, 'Análisis pérdida TransReyes GPS',           11,  7, 15, 3, 2, 3, '2025-11-22', '2025-11-22', '2025-11-22');

-- Plantillas de correo electrónico
INSERT INTO PlantillasCorreo (Nombre, Asunto, ContenidoHTML, ContenidoTexto, Categoria, Activa, CreadoPor) VALUES
('Bienvenida Cliente Nuevo',
 'Bienvenido a nuestros servicios — CRM',
 '<h1>¡Bienvenido!</h1><p>Gracias por confiar en nosotros. Estamos a tus órdenes.</p>',
 'Gracias por confiar en nosotros. Estamos a tus órdenes.',
 'Onboarding', 1, 2),
('Seguimiento de Propuesta',
 '¿Tuviste oportunidad de revisar nuestra propuesta?',
 '<h2>Seguimiento</h2><p>Nos gustaría saber si pudiste revisar la propuesta que te enviamos.</p>',
 'Nos gustaría saber si pudiste revisar nuestra propuesta.',
 'Ventas', 1, 2),
('Newsletter Mensual Novedades',
 'Novedades del mes — CRM',
 '<h1>Novedades del mes</h1><p>Conoce las últimas noticias, lanzamientos y promociones.</p>',
 'Conoce las últimas noticias de nuestra empresa.',
 'Marketing', 1, 5);

-- Segmentos y sus miembros
INSERT INTO Segmentos (Nombre, Descripcion, TipoEntidad, CantidadRegistros, CreadoPor) VALUES
('Industria Manufactura y Construcción', 'Empresas del sector industrial con oportunidades activas', 'contacto', 5, 4),
('Tomadores de Decisión TI',            'Directores y gerentes del sector tecnología',               'contacto', 2, 4);

INSERT INTO SegmentoContactos (SegmentoID, ContactoID, AsignadoPor) VALUES
(1, 2, 4), (1, 4, 4), (1, 7, 4), (1, 8, 4), (1, 12, 4),
(2, 6, 4), (2, 10, 4);

-- Campañas de comunicación
INSERT INTO Campanas (Nombre, Descripcion, Tipo, Estado, PlantillaID, SegmentoID, FechaEnvio, TotalDestinatarios, TotalEnviados, TotalEntregados, TotalAbiertos, TotalClics, TotalRebotados, TotalDesuscripciones, PropietarioID) VALUES
('Bienvenida Prospectos Enero 2026',      'Correo de bienvenida a prospectos captados en enero',     'Email', 'Enviada',  1, 1, '2026-01-15', 45,  45,  43, 28, 12, 2, 1, 5),
('Promo Manufactura Febrero 2026',        'Descuentos especiales en soluciones para manufactura',    'Email', 'Enviada',  2, 1, '2026-02-01', 38,  38,  36, 20,  8, 2, 0, 5),
('Newsletter Q4 2025',                    'Resumen de novedades del cuarto trimestre 2025',          'Email', 'Enviada',  3, NULL,'2025-10-15',120, 120, 115, 62, 25, 5, 3, 5),
('Lanzamiento Módulo Reportes Marzo 2026','Presentación del nuevo módulo de reportes avanzados',     'Email', 'Borrador', 2, 2, NULL,          0,   0,   0,  0,  0, 0, 0, 5);

-- Etiquetas asignadas a contactos
INSERT INTO ContactoEtiquetas (ContactoID, EtiquetaID, AsignadoPor) VALUES
(2, 1, 4), (4, 1, 4), (7, 1, 4),
(6, 2, 2), (10, 2, 2),
(4, 3, 4), (7, 3, 4), (10, 3, 4);

--- ÍNDICES ---

-- Indices en foreign keys de Empresas
CREATE INDEX IF NOT EXISTS idx_empresas_industria ON Empresas(IndustriaID);
CREATE INDEX IF NOT EXISTS idx_empresas_tamano ON Empresas(TamanoID);
CREATE INDEX IF NOT EXISTS idx_empresas_ciudad ON Empresas(CiudadID);
CREATE INDEX IF NOT EXISTS idx_empresas_moneda ON Empresas(MonedaID);
CREATE INDEX IF NOT EXISTS idx_empresas_origen ON Empresas(OrigenID);
CREATE INDEX IF NOT EXISTS idx_empresas_propietario ON Empresas(PropietarioID);

-- Indices en foreign keys de Contactos
CREATE INDEX IF NOT EXISTS idx_contactos_empresa ON Contactos(EmpresaID);
CREATE INDEX IF NOT EXISTS idx_contactos_ciudad ON Contactos(CiudadID);
CREATE INDEX IF NOT EXISTS idx_contactos_origen ON Contactos(OrigenID);
CREATE INDEX IF NOT EXISTS idx_contactos_propietario ON Contactos(PropietarioID);

-- Indices en foreign keys de Oportunidades
CREATE INDEX IF NOT EXISTS idx_oportunidades_etapa ON Oportunidades(EtapaID);
CREATE INDEX IF NOT EXISTS idx_oportunidades_propietario ON Oportunidades(PropietarioID);
CREATE INDEX IF NOT EXISTS idx_oportunidades_empresa ON Oportunidades(EmpresaID);
CREATE INDEX IF NOT EXISTS idx_oportunidades_contacto ON Oportunidades(ContactoID);
CREATE INDEX IF NOT EXISTS idx_oportunidades_moneda ON Oportunidades(MonedaID);
CREATE INDEX IF NOT EXISTS idx_oportunidades_motivo_perdida ON Oportunidades(MotivosPerdidaID);

-- Indices en foreign keys de Actividades
CREATE INDEX IF NOT EXISTS idx_actividades_contacto ON Actividades(ContactoID);
CREATE INDEX IF NOT EXISTS idx_actividades_oportunidad ON Actividades(OportunidadID);
CREATE INDEX IF NOT EXISTS idx_actividades_propietario ON Actividades(PropietarioID);
CREATE INDEX IF NOT EXISTS idx_actividades_tipo ON Actividades(TipoActividadID);
CREATE INDEX IF NOT EXISTS idx_actividades_estado ON Actividades(EstadoActividadID);

-- Indices en foreign keys de Recordatorios y Notificaciones
CREATE INDEX IF NOT EXISTS idx_recordatorios_usuario ON Recordatorios(UsuarioID);
CREATE INDEX IF NOT EXISTS idx_recordatorios_actividad ON Recordatorios(ActividadID);
CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON Notificaciones(UsuarioID);

-- Indices en foreign keys de Campanas
CREATE INDEX IF NOT EXISTS idx_campana_dest_campana ON CampanaDestinatarios(CampanaID);
CREATE INDEX IF NOT EXISTS idx_campana_dest_contacto ON CampanaDestinatarios(ContactoID);

-- Indices para geografia (jerarquia)
CREATE INDEX IF NOT EXISTS idx_estados_pais ON Estados(PaisID);
CREATE INDEX IF NOT EXISTS idx_ciudades_estado ON Ciudades(EstadoID);

-- Indices compuestos para filtros frecuentes
CREATE INDEX IF NOT EXISTS idx_empresas_activo_fecha ON Empresas(Activo, FechaCreacion DESC);
CREATE INDEX IF NOT EXISTS idx_contactos_activo_fecha ON Contactos(Activo, FechaCreacion DESC);
CREATE INDEX IF NOT EXISTS idx_oportunidades_activo_fecha ON Oportunidades(FechaCreacion DESC);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo_rol ON Usuarios(Activo, RolID);

-- Indices para busquedas por email y RFC
CREATE INDEX IF NOT EXISTS idx_empresas_email ON Empresas(Email);
CREATE INDEX IF NOT EXISTS idx_empresas_rfc ON Empresas(RFC);
CREATE INDEX IF NOT EXISTS idx_contactos_email ON Contactos(Email);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON Usuarios(Email);

-- Indices para busquedas por nombre
CREATE INDEX IF NOT EXISTS idx_empresas_razon_social ON Empresas(RazonSocial);
CREATE INDEX IF NOT EXISTS idx_contactos_nombre_completo ON Contactos(Nombre, ApellidoPaterno);
CREATE INDEX IF NOT EXISTS idx_contactos_apellidos ON Contactos(ApellidoPaterno, ApellidoMaterno);
CREATE INDEX IF NOT EXISTS idx_usuarios_nombre ON Usuarios(Nombre, ApellidoPaterno);

-- Indices para ordenamiento y filtrado por fechas
CREATE INDEX IF NOT EXISTS idx_oportunidades_fecha_cierre ON Oportunidades(FechaCierreEstimada);
CREATE INDEX IF NOT EXISTS idx_oportunidades_es_ganada ON Oportunidades(EsGanada);
CREATE INDEX IF NOT EXISTS idx_actividades_fecha_vencimiento ON Actividades(FechaVencimiento);
CREATE INDEX IF NOT EXISTS idx_recordatorios_fecha ON Recordatorios(FechaRecordatorio);

-- Indices compuestos para notificaciones (filtro frecuente)
CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_leida ON Notificaciones(UsuarioID, EsLeida);

-- Indices para auditoria
CREATE INDEX IF NOT EXISTS idx_log_auditoria_fecha ON LogAuditoria(FechaAccion);
CREATE INDEX IF NOT EXISTS idx_log_auditoria_entidad ON LogAuditoria(EntidadTipo, EntidadID);
