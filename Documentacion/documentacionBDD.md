# Documentación de la Base de Datos

## 1. Diagrama Entidad-Relación (ER) y/o Grafo de la Base de Datos

Este es el diseño final de la base de datos. He decidido representar las tablas intermedias, aunque por claridad para entenderlo quizás sería mejor no representarlas.

*(Quizás la versión que tengo en papel es más fea pero se entiende mejor)*

---

## 2. Esquema de Base de Datos y Normalización

### **Entidades y Atributos**

- **Usuarios**: `id_usuario` (Primaria), `nombre`, `email`, `contraseña`, `fecha_registro`.
- **Supermercados**: `id_supermercado` (Primaria), `nombre`, `direccion`, `geolocalizacion`.
- **Productos**: `id_producto` (Primaria), `nombre`, `categoria`, `unidad_medida`, `precio`, `descripcion`.
- **Precios**: `id_precio` (Primaria), `id_producto` (Clave Ajena), `id_supermercado` (Clave Ajena), `precio`, `fecha_actualizacion`.
- **Carritos**: `id_carrito` (Primaria), `id_usuario` (Clave Ajena), `fecha_creacion`.
- **Carrito_Productos**: `id_carrito` (Clave Ajena, Primaria), `id_producto` (Clave Ajena, Primaria), `cantidad`.
- **Historial_Carritos**: `id_historial_carrito` (Primaria), `id_carrito` (Clave Ajena), `id_usuario` (Clave Ajena), `costo_total`, `fecha_finalizacion`.
- **Historial_Carrito_Productos**: `id_historial_carrito` (Clave Ajena, Primaria), `id_producto` (Clave Ajena, Primaria), `cantidad`.
- **Historial_Precios**: `id_historial` (Primaria), `id_producto` (Clave Ajena), `id_supermercado` (Clave Ajena), `precio`, `fecha_registro`.
- **Valoraciones**: `id_valoracion` (Primaria), `id_producto` (Clave Ajena), `id_usuario` (Clave Ajena), `puntuacion`, `comentario`, `fecha_valoracion`.
- **Ofertas**: `id_oferta` (Primaria), `id_producto` (Clave Ajena), `id_supermercado` (Clave Ajena), `precio_oferta`, `fecha_inicio`, `fecha_fin`.

### **Normalización**

- **1NF**: Todas las columnas tienen valores atómicos y no hay grupos repetidos. *(Ejemplo: Tabla de Usuarios)*
- **2NF**: Todos los atributos no clave dependen completamente de la clave primaria. *(Ejemplo: `Carrito_Productos` tiene clave primaria compuesta, y `cantidad` depende completamente de estas dos claves, sin dependencias parciales)*
- **3NF**: No hay dependencias transitivas. *(Ningún atributo no clave depende de otro atributo no clave)*
- **BCNF**: Todas las dependencias funcionales tienen determinantes como claves. *(Ejemplo: En `Precios`, tanto `id_precio` como `id_producto` + `id_supermercado` son claves candidatas)*
- **4NF**: No hay dependencias multivaluadas ni triviales. *(Ejemplo: En `Carrito_Productos`, cada combinación de `id_carrito` e `id_producto` tiene un único valor para `cantidad`)*

---

## 3. Scripts de Creación o Definiciones

### **Relacional: Scripts SQL para la creación de la base de datos**

```sql
-- Tabla de Usuarios
CREATE TABLE Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Supermercados
CREATE TABLE Supermercados (
    id_supermercado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    geolocalizacion VARCHAR(100) -- Coordenadas GPS (se incluye pero no se usará en la v1)
);

-- Tabla de Productos
CREATE TABLE Productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50), -- Ejemplo: frutas, verduras, lácteos
    unidad_medida VARCHAR(20), -- Ejemplo: kg, litro, unidad
    precio DECIMAL(10, 2),
    descripcion TEXT
);

-- Tabla de Precios
CREATE TABLE Precios (
    id_precio INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_supermercado INT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    FOREIGN KEY (id_supermercado) REFERENCES Supermercados(id_supermercado)
);

-- Tabla de Carritos
CREATE TABLE Carritos (
    id_carrito INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

-- Tabla de Carrito_Productos (Relación entre Carritos y Productos)
CREATE TABLE Carrito_Productos (
    id_carrito INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_carrito, id_producto),
    FOREIGN KEY (id_carrito) REFERENCES Carritos(id_carrito),
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
);

-- Tabla de Historial de Precios
CREATE TABLE Historial_Precios (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_supermercado INT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    FOREIGN KEY (id_supermercado) REFERENCES Supermercados(id_supermercado)
);

-- Tabla de Valoraciones
CREATE TABLE Valoraciones (
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
CREATE TABLE Ofertas (
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
CREATE TABLE Historial_Carritos (
    id_historial_carrito INT AUTO_INCREMENT PRIMARY KEY,
    id_carrito INT NOT NULL,
    id_usuario INT NOT NULL,
    costo_total DECIMAL(10, 2) NOT NULL,
    fecha_finalizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_carrito) REFERENCES Carritos(id_carrito),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

-- Tabla de Historial_Carrito_Productos (Relación entre Historial_Carritos y Productos)
CREATE TABLE Historial_Carrito_Productos (
    id_historial_carrito INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_historial_carrito, id_producto),
    FOREIGN KEY (id_historial_carrito) REFERENCES Historial_Carritos(id_historial_carrito),
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
);
```

*(Esto es en teoría todo, no he probado todavía a montar la base de datos, así que puede que en alguno de los datos o referencias me haya equivocado, por lo que podría necesitar edición)*

---

## 4. Documentación Adicional

### **Justificación de las decisiones de diseño**

Aunque inicialmente pensé en hacerlo en una base de datos no relacional, creo que esta aplicación es bastante intensa con los datos, ya que todo lo que implique un historial de varias cosas (sobre todo de precios de supermercados, los cuales varían y hay muchísimos productos) es bastante complejo.

En este caso, las relaciones nos vienen genial, y creo que tiene mucho más sentido hacerlo relacional. Los datos serán mucho más íntegros y las automatizaciones más sencillas si se quieren refrescar los datos a través de una API.

Si bien es cierto que es mucho más complejo montarla, probablemente en alguna parte del diseño esté regular o haya que retocarla. Algunas partes, como las ofertas, no están pensadas para desarrollarse en el producto mínimo viable. Aun así, merece la pena a la hora de poner la aplicación a funcionar y como experiencia didáctica, ya que no he trabajado mucho con la creación de bases de datos SQL.

También esta decisión limita el proyecto a tener que usar Django, ya que tiene integración con bases SQL de forma fácil, pero no es algo crítico.

Por último, hay algunas tablas que pueden ser innecesarias, como los historiales, y se podrían sacar quizás de otras tablas añadiendo campos de fecha o demás. Sin embargo, creo que es más cómodo y eficiente aislarlas como tablas para no tener que tocar en varias tablas muchos registros consecutivos. *(Esto es mi opinión y puede que sea errónea, así que queda pendiente de revisión)*.

---




