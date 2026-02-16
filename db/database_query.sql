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

-- Segmentos guardados (filtros predefinidos)
CREATE TABLE IF NOT EXISTS Segmentos (
    SegmentoID          INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre              TEXT NOT NULL,
    Descripcion         TEXT,
    TipoEntidad         TEXT NOT NULL,
    CriteriosJSON       TEXT,
    CantidadRegistros   INTEGER,
    EsDinamico          INTEGER DEFAULT 1,
    CreadoPor           INTEGER NOT NULL,
    FechaCreacion       TEXT DEFAULT (datetime('now', 'localtime')),
    FechaModificacion   TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (CreadoPor) REFERENCES Usuarios(UsuarioID)
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
('Marketing', 'Gestión de campañas y comunicaciones')

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
