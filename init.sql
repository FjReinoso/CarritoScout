-- Seleccionar la base de datos (asegúrate de que exista)
USE carrito_db;

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Supermercados
CREATE TABLE IF NOT EXISTS Supermercados (
    id_supermercado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    geolocalizacion VARCHAR(100) -- Coordenadas GPS (se incluye pero no se usará en la v1)
);

-- Tabla de Productos
CREATE TABLE IF NOT EXISTS Productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50), -- Ejemplo: frutas, verduras, lácteos
    unidad_medida VARCHAR(20), -- Ejemplo: kg, litro, unidad
    precio DECIMAL(10, 2),
    descripcion TEXT
);

-- Tabla de Precios
CREATE TABLE IF NOT EXISTS Precios (
    id_precio INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_supermercado INT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    FOREIGN KEY (id_supermercado) REFERENCES Supermercados(id_supermercado)
);

-- Tabla de Carritos
CREATE TABLE IF NOT EXISTS Carritos (
    id_carrito INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

-- Tabla de Carrito_Productos (Relación entre Carritos y Productos)
CREATE TABLE IF NOT EXISTS Carrito_Productos (
    id_carrito INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_carrito, id_producto),
    FOREIGN KEY (id_carrito) REFERENCES Carritos(id_carrito),
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
);

-- Tabla de Historial de Precios
CREATE TABLE IF NOT EXISTS Historial_Precios (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_supermercado INT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    FOREIGN KEY (id_supermercado) REFERENCES Supermercados(id_supermercado)
);

-- Tabla de Valoraciones
CREATE TABLE IF NOT EXISTS Valoraciones (
    id_valoracion INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_usuario INT NOT NULL,
    puntuacion INT CHECK (puntuacion BETWEEN 1 AND 5), -- Escala de 1 a 5
    comentario TEXT,
    fecha_valoracion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

-- Tabla de Ofertas
CREATE TABLE IF NOT EXISTS Ofertas (
    id_oferta INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_supermercado INT NOT NULL,
    precio_oferta DECIMAL(10, 2) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    FOREIGN KEY (id_supermercado) REFERENCES Supermercados(id_supermercado)
);

-- Tabla de Historial de Carritos
CREATE TABLE IF NOT EXISTS Historial_Carritos (
    id_historial_carrito INT AUTO_INCREMENT PRIMARY KEY,
    id_carrito INT NOT NULL,
    id_usuario INT NOT NULL,
    costo_total DECIMAL(10, 2) NOT NULL,
    fecha_finalizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_carrito) REFERENCES Carritos(id_carrito),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

-- Tabla de Historial_Carrito_Productos (Relación entre Historial_Carritos y Productos)
CREATE TABLE IF NOT EXISTS Historial_Carrito_Productos (
    id_historial_carrito INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_historial_carrito, id_producto),
    FOREIGN KEY (id_historial_carrito) REFERENCES Historial_Carritos(id_historial_carrito),
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
);