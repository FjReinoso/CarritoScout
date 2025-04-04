# CarritoScout

Aplicación para la comparación de precios de supermercados y productos frescos, con historial de precios, opciones para hacer tu carrito y previsión del coste, y un historial para la inflación de precios.

## 1. Arquitectura del Proyecto

### **Arquitectura MVC (Modelo-Vista-Controlador)**


El proyecto sigue la arquitectura MVC (Modelo-Vista-Controlador), que es compatible con Django. Esta arquitectura organiza la aplicación en tres componentes interconectados:

Modelo: Representa los datos y la lógica de negocio de la aplicación. En Django, esto se implementa en el archivo models.py de cada aplicación.
Vista: Maneja la capa de presentación y la interfaz de usuario. En Django, las vistas se implementan en el archivo views.py y pueden renderizar plantillas o devolver respuestas JSON para APIs.
Controlador: Gestiona la interacción entre el modelo y la vista. En Django, el controlador está implícitamente manejado por el framework a través del enrutamiento de URLs (urls.py) y las funciones de vista.
Esta arquitectura asegura una clara separación de responsabilidades, lo que facilita el mantenimiento y la extensión de la aplicación.

### **Despliegue con Docker**

El proyecto estará montado en Docker para facilitar su despliegue y portabilidad. Las razones para esta decisión son:

1. **Entorno Consistente**: Docker asegura que el proyecto se ejecute de manera idéntica en cualquier entorno, eliminando problemas de configuración entre desarrollo, pruebas y producción.
2. **Facilidad de Despliegue**: Con Docker, podemos empaquetar todas las dependencias del proyecto en contenedores, simplificando el proceso de despliegue.
3. **Escalabilidad**: Docker permite escalar los servicios del proyecto de manera eficiente, ya sea en un entorno local o en la nube.
4. **Integración Continua**: Facilita la integración con pipelines de CI/CD, asegurando un flujo de desarrollo y despliegue más ágil.

Se incluirá un archivo `docker-compose.yml` para orquestar los diferentes servicios necesarios, como la base de datos, el backend y cualquier otro componente adicional. Esto permitirá levantar todo el entorno con un solo comando, mejorando la experiencia de desarrollo y despliegue.
---
## 2. **Funcionalidades Principales**

### **Registro y Autenticación de Usuarios**
- Registro de nuevos usuarios.
- Inicio de sesión y autenticación.
- Recuperación de contraseñas.

### **Gestión de Productos**
- Base de datos de productos frescos y de supermercado.
- CRUD (Crear, Leer, Actualizar, Eliminar) de productos.
- Categorías de productos (frutas, verduras, lácteos, etc.).

### **Comparación de Precios**
- Comparación de precios de productos entre diferentes supermercados.
- Visualización de precios actuales y históricos.
- Filtros por categoría, supermercado y rango de precios.

### **Carrito de Compras**
- Creación y gestión de carritos de compras.
- Añadir y eliminar productos del carrito.
- Cálculo del coste total del carrito según el supermercado seleccionado.

### **Historial de Precios**
- Registro de precios históricos de productos.
- Gráficas de evolución de precios.
- Análisis de tendencias de precios.

### **Previsión de Costes**
- Algoritmo para prever el coste de productos en base a datos históricos (opcional, ya que puede ser algo complicado).
- Sugerencias de compra según previsiones de inflación.

### **Alertas y Notificaciones**
- Notificaciones de cambios significativos en los precios.
- Alertas de ofertas y descuentos en productos seleccionados.

### **Panel de Administración**
- Gestión de usuarios y permisos.
- Administración de productos y precios.
- Visualización de estadísticas de uso de la aplicación.

---

## **Funcionalidades Extra para Añadir Profundidad**
- Integrar API de supermercados para actualizaciones automáticas.
- Rankings de calidad y sistema de valoraciones.
- Recomendaciones de productos según tus compras habituales.
- Historial de compras y análisis de gastos.
- Carritos compartidos entre varias cuentas.
- Sección de ofertas y promociones.
- Comparación de precios por kilo/litro.
- Geolocalización de supermercados cercanos.
- Modo offline.
- Alertas de disponibilidad de productos.

---

### **Nota**
Estas funcionalidades extra están pensadas para añadir más profundidad y complejidad al proyecto en caso de que sea necesario. Algunas de ellas pueden ser un poco irreales o complejas, ya que implican tecnologías o algoritmos avanzados (como geolocalización o previsión de costes), pero son propuestas para explorar.

CarritoScout/
├── backend/
│   ├── carritoscout/  # Proyecto principal de Django
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── templates/  # Plantillas HTML globales
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   └── ...
│   │   ├── static/  # Archivos estáticos globales
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── images/
│   │   └── media/  # Archivos multimedia subidos por los usuarios
│   ├── APIrest/  # Aplicación principal para la API y funcionalidad central
│   │   ├── __init__.py
│   │   ├── admin.py  # Registro de modelos en el panel de administración
│   │   ├── apps.py
│   │   ├── models.py  # Modelos de la base de datos
│   │   ├── views.py  # Vistas para manejar las solicitudes
│   │   ├── urls.py  # Enrutamiento de URLs para la app
│   │   ├── serializers.py  # Serializadores para las respuestas de la API
│   │   ├── forms.py  # Formularios para la entrada de usuario (si es necesario)
│   │   ├── templates/  # Plantillas específicas de la app
│   │   │   ├── APIrest/
│   │   │       ├── product_list.html
│   │   │       ├── product_detail.html
│   │   │       └── ...
│   │   ├── static/  # Archivos estáticos específicos de la app
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── images/
│   │   ├── migrations/  # Migraciones de la base de datos
│   │   │   ├── __init__.py
│   │   │   └── ...
│   │   └── tests.py  # Pruebas unitarias para la app
│   ├── manage.py  # Script de gestión de Django
│   ├── requirements.txt  # Dependencias de Python
│   └── .env  # Variables de entorno
├── docker-compose.yml  # Configuración de Docker
├── README.md  # Documentación del proyecto
└── Documentacion/  # Documentación adicional
    ├── DescripcionProyecto.md
    └── documentacionBDD.md