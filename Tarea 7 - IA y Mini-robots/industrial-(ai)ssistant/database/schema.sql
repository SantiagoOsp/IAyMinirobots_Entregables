-- Activa la validación de relaciones en esta conexión.
PRAGMA foreign_keys = ON;


-- 1. Equipos registrados en la planta.
CREATE TABLE IF NOT EXISTS equipos (
    codigo TEXT PRIMARY KEY NOT NULL,
    nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
    ubicacion TEXT,
    estado TEXT NOT NULL DEFAULT 'OPERATIVO'
        CHECK (estado IN (
            'OPERATIVO',
            'EN_MANTENIMIENTO',
            'FUERA_DE_SERVICIO'
        ))
);


-- 2. Catálogo de repuestos.
CREATE TABLE IF NOT EXISTS repuestos (
    codigo TEXT PRIMARY KEY NOT NULL,
    descripcion TEXT NOT NULL
        CHECK (length(trim(descripcion)) > 0),
    fabricante TEXT
);


-- 3. Compatibilidad entre equipos y repuestos.
CREATE TABLE IF NOT EXISTS equipos_repuestos (
    equipo_codigo TEXT NOT NULL,
    repuesto_codigo TEXT NOT NULL,

    PRIMARY KEY (equipo_codigo, repuesto_codigo),

    FOREIGN KEY (equipo_codigo)
        REFERENCES equipos(codigo),

    FOREIGN KEY (repuesto_codigo)
        REFERENCES repuestos(codigo)
);


-- 4. Existencias: una ubicación por repuesto en esta versión.
CREATE TABLE IF NOT EXISTS inventario (
    codigo_repuesto TEXT PRIMARY KEY NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 0
        CHECK (
            typeof(cantidad) = 'integer'
            AND cantidad >= 0
        ),
    ubicacion TEXT,

    FOREIGN KEY (codigo_repuesto)
        REFERENCES repuestos(codigo)
);


-- 5. Órdenes de trabajo.
CREATE TABLE IF NOT EXISTS ordenes_trabajo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo_codigo TEXT NOT NULL,
    falla TEXT NOT NULL CHECK (length(trim(falla)) > 0),

    prioridad TEXT NOT NULL DEFAULT 'MEDIA'
        CHECK (prioridad IN ('BAJA', 'MEDIA', 'ALTA', 'CRITICA')),

    estado TEXT NOT NULL DEFAULT 'ABIERTA'
        CHECK (estado IN (
            'ABIERTA',
            'EN_PROCESO',
            'CERRADA',
            'CANCELADA'
        )),

    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Permite validar conjuntamente equipo y orden en el historial.
    UNIQUE (id, equipo_codigo),

    FOREIGN KEY (equipo_codigo)
        REFERENCES equipos(codigo)
);


-- 6. Registro de fallas, con o sin orden asociada.
CREATE TABLE IF NOT EXISTS historial_fallas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo_codigo TEXT NOT NULL,
    falla TEXT NOT NULL CHECK (length(trim(falla)) > 0),
    orden_trabajo INTEGER,
    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (equipo_codigo)
        REFERENCES equipos(codigo),

    FOREIGN KEY (orden_trabajo, equipo_codigo)
        REFERENCES ordenes_trabajo(id, equipo_codigo)
);


-- Facilitan las consultas por equipo.
CREATE INDEX IF NOT EXISTS idx_ordenes_equipo
    ON ordenes_trabajo(equipo_codigo);

CREATE INDEX IF NOT EXISTS idx_historial_equipo
    ON historial_fallas(equipo_codigo);

    CREATE TABLE IF NOT EXISTS solicitudes_orden (
    solicitud_id TEXT PRIMARY KEY NOT NULL
        CHECK (length(trim(solicitud_id)) > 0),

    orden_id INTEGER NOT NULL UNIQUE,

    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (orden_id)
        REFERENCES ordenes_trabajo(id)
);