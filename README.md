# Comparador de Precios de Supermercados

## Descripción del Proyecto

Este proyecto es una **aplicación web** diseñada para comparar precios de productos frescos y de supermercado entre diferentes establecimientos. Ofrece funcionalidades avanzadas como la gestión de carritos de compra, historial de precios, previsión de costes y alertas de ofertas. Además, incluye herramientas para analizar tendencias de precios y realizar recomendaciones personalizadas.

El objetivo principal es proporcionar a los usuarios una experiencia completa para optimizar sus compras, mientras se sigue una arquitectura moderna y escalable.

---

## Funcionalidades Principales

- **Registro y Autenticación de Usuarios**:
  - Registro de nuevos usuarios.
  - Inicio de sesión y autenticación segura.
  - Recuperación de contraseñas.

- **Gestión de Productos**:
  - CRUD (Crear, Leer, Actualizar, Eliminar) de productos.
  - Clasificación por categorías (frutas, verduras, lácteos, etc.).
  - Clasificación por supermercado.
  - Busqueda de productos por información específica.

- **Comparación de Precios**:
  - Comparación de precios entre diferentes supermercados.
  - Visualización de precios actuales e históricos.
  - Filtros por categoría, supermercado y rango de precios.

- **Carrito de Compras**:
  - Creación y gestión de carritos de compras.
  - Cálculo del coste total según el supermercado seleccionado.
  - Uso compartido de carritos con desglose por persona.

- **Historial de Precios**:
  - Registro de precios históricos.
  - Gráficas de evolución de precios.

- **Alertas y Notificaciones**: (previsto despues de la v1)
  - Notificaciones de cambios significativos en los precios.
  - Alertas de ofertas y descuentos.

- **Panel de Administración**:
  - Gestión de usuarios y permisos.
  - Administración de productos y precios.
  - Visualización de estadísticas de uso.
  - Moderación en comentarios y valoraciones.

---

## Funcionalidades Extra/Opcionales

- Análisis de tendencias de precios.
- Creación de API propia para extraer los precios de los supermercados periódicamente.
- Integración con APIs de supermercados para actualizaciones automáticas.
- Sistema de rankings y valoraciones de productos.
- Recomendaciones basadas en compras habituales.
- Historial de compras y análisis de gastos.
- Carritos compartidos entre varias cuentas.
- Comparación de precios por kilo/litro.
- Geolocalización de supermercados cercanos.
- Modo offline.
- Alertas de disponibilidad de productos.
- **Previsión de Costes**:
  - Algoritmo para prever costes basados en datos históricos.
  - Sugerencias de compra según previsiones de inflación.

---

## Tecnologías Utilizadas

### **Frontend**:
- **HTML**, **CSS**, **JavaScript**.

### **Backend**:
- **Python** con **Django**.

### **Base de Datos**:
- **MariaDB**.

### **Herramientas de Desarrollo**:
- **GitHub** para control de versiones.
- **Docker** para contenedores y despliegue.
- **Postman** para pruebas durante el desarrollo.

---

## Arquitectura del Proyecto y elección de diseño

El proyecto sigue la arquitectura MVC (Modelo-Vista-Controlador), que es compatible con Django. Esta arquitectura organiza la aplicación en tres componentes interconectados:

Modelo: Representa los datos y la lógica de negocio de la aplicación.
Vista: Maneja la capa de presentación y la interfaz de usuario.
Controlador: Gestiona la interacción entre el modelo y la vista.

Esta arquitectura asegura una clara separación de responsabilidades, lo que facilita el mantenimiento y la extensión de la aplicación.



---

## Instalación y Configuración

### Requisitos Previos
- Docker y Docker Compose instalados.
- Python 3.9+.
- MariaDB configurado.

### Pasos
1. Clona el repositorio:
   ```bash
   [Propenso a cambios de nombre, puede estar desactualizado]
   git clone https://github.com/FjReinoso/CarritoScout
   cd CarritoScout
2. Construye los contenedores con Docker:
    ```bash
     docker-compose up --build
3. Accede a la aplicación en tu navegador en http://localhost:8000
