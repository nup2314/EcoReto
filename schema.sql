-- Ejecuta esto en el SQL Editor de Neon
CREATE TABLE IF NOT EXISTS acciones (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(80) NOT NULL,
    categoria VARCHAR(40) NOT NULL,
    descripcion TEXT NOT NULL,
    propuesto_por VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    impacto VARCHAR(40) NOT NULL DEFAULT ''
);

INSERT INTO acciones (titulo, categoria, descripcion, propuesto_por, impacto)
VALUES
 ('Cuida cada gota', 'Agua', 'Cerrar la llave al cepillarse', 'Equipo Verde', '10 litros'),
 ('Dale otra vida', 'Reutilización', 'Usar hojas por ambos lados', 'Equipo Azul', '20 hojas');

-- Tabla para las cuentas que se crean con "Regístrate"
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(30) UNIQUE NOT NULL,
    clave_hash TEXT NOT NULL
);
