# Manual Técnico de CarritoScout

## Índice

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
   - [Patrón MVC en Django](#patrón-mvc-en-django)
   - [Estructura de Carpetas](#estructura-de-carpetas)
   - [Aplicaciones principales](#aplicaciones-principales)
3. [Modelos de Datos](#modelos-de-datos)
   - [Modelos de Carrito](#modelos-de-carrito)
   - [Modelos de Productos](#modelos-de-productos)
   - [Modelos de Usuarios](#modelos-de-usuarios)
   - [Relaciones entre Modelos](#relaciones-entre-modelos)
4. [Flujos Principales](#flujos-principales)
   - [Gestión de Carritos](#gestión-de-carritos)
   - [Productos y Precios](#productos-y-precios)
   - [Sistema de Compartición](#sistema-de-compartición)
   - [Historial de Compras](#historial-de-compras)
5. [Componentes Frontend](#componentes-frontend)
   - [Plantillas y Vistas](#plantillas-y-vistas)
   - [JavaScript: CarritoManager](#javascript-carritomanager)
   - [Interacción AJAX](#interacción-ajax)
6. [Componentes Backend](#componentes-backend)
   - [Vistas y Controladores](#vistas-y-controladores)
   - [Seguridad y Autenticación](#seguridad-y-autenticación)
7. [Guía de Despliegue](#guía-de-despliegue)
   - [Entorno de Desarrollo](#entorno-de-desarrollo)
   - [Configuración de Producción](#configuración-de-producción)
8. [App Usuarios en profundidad](app-usuarios-en-profundidad)
10. [Ampliaciones y Mejoras](#ampliaciones-y-mejoras)

## Introducción

CarritoScout es una aplicación web desarrollada en Django que permite a los usuarios gestionar listas de compra (carritos), comparar precios de productos entre diferentes supermercados, compartir carritos con otros usuarios y mantener un historial de compras. Este manual técnico está orientado a desarrolladores web que necesiten comprender la estructura y funcionamiento del proyecto para su mantenimiento o mejora.

## Arquitectura del Sistema

### Patrón MVC en Django

CarritoScout sigue el patrón arquitectónico MVC (Modelo-Vista-Controlador), que en Django se traduce como MTV (Models-Templates-Views):

- **Modelos**: Definen la estructura de la base de datos y la lógica de negocio asociada a los datos (`models.py`).
- **Plantillas**: Archivos HTML con el código de presentación (`templates/`).
- **Vistas**: Controlan la lógica de la aplicación y procesan las peticiones del usuario (`views.py`).

### Estructura de Carpetas

El proyecto sigue la estructura estándar de un proyecto Django:

```
carritoScout/                    # Carpeta raíz del proyecto
│
├── carritoScout/                # Configuración principal del proyecto
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py              # Configuración global
│   ├── urls.py                  # URLs principales
│   └── wsgi.py
│
├── carrito/                     # Aplicación de gestión de carritos
│   ├── migrations/              # Migraciones de base de datos
│   ├── templates/carrito/       # Plantillas específicas
│   ├── __init__.py
│   ├── admin.py                 # Configuración del admin
│   ├── models.py                # Modelos de la app
│   ├── tests.py                 # Tests unitarios
│   ├── urls.py                  # URLs específicas
│   └── views.py                 # Vistas/Controladores
│
├── productos/                   # Aplicación de gestión de productos
│   ├── [...]                    # Estructura similar a carrito/
│
├── usuarios/                    # Aplicación de gestión de usuarios
│   ├── [...]                    # Estructura similar a carrito/
│
├── analytics/                   # Aplicación de análisis de datos
│   ├── [...]                    # Estructura similar a carrito/
│
├── static/                      # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
│
└── manage.py                    # Script de administración
```

### Aplicaciones Principales

El proyecto se divide en varias aplicaciones Django:

1. **carrito**: Gestiona los carritos de compras, sus productos y la compartición.
2. **productos**: Administra el catálogo de productos y precios.
3. **usuarios**: Controla la autenticación, perfiles y preferencias de usuarios.
4. **analytics**: Maneja la recopilación y visualización de datos analíticos.

## Modelos de Datos

### Modelos de Carrito

Los carritos son el núcleo del sistema. El modelo principal es `Carrito` y tiene varios modelos relacionados:

```python
class Carrito(models.Model):
    """Modelo para representar un carrito de compras"""
    id_carrito = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carritos')
    usuarios_compartidos = models.ManyToManyField(
        User, 
        through='InvitacionCarrito', 
        related_name='carritos_compartidos',
        blank=True
    )
    nombre = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)
    
    @property
    def nombre_display(self):
        """Retorna el nombre del carrito o un nombre por defecto"""
        if self.nombre and self.nombre.strip():
            return self.nombre
        return f"Carrito #{self.id_carrito}"
    
    # Otros métodos y propiedades...
```

#### CarritoProducto

Este modelo conecta los productos con los carritos y contiene la información de cantidad y precio.

```python
class CarritoProducto(models.Model):
    """Modelo intermedio para productos en carritos"""
    id = models.AutoField(primary_key=True)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    supermercado = models.ForeignKey('productos.Supermercado', on_delete=models.CASCADE, null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(default=timezone.now)
    
    @property
    def subtotal(self):
        """Calcula el subtotal de este item"""
        precio = self.precio_unitario if self.precio_unitario is not None else (self.producto.precio or 0)
        return precio * self.cantidad
```

#### InvitacionCarrito

Gestiona las invitaciones a carritos compartidos entre usuarios:

```python
class InvitacionCarrito(models.Model):
    """Modelo intermedio para invitaciones a carritos compartidos"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='invitaciones')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitaciones_carrito')
    fecha_invitacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
```

#### HistorialCarrito

Almacena la información de los carritos finalizados:

```python
class HistorialCarrito(models.Model):
    """Historial de carritos finalizados"""
    id_historial_carrito = models.AutoField(primary_key=True)
    carrito = models.OneToOneField(Carrito, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historial_carritos')
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_finalizacion = models.DateTimeField(default=timezone.now)
```

#### CarritoActivoUsuario

Relaciona a cada usuario con su carrito activo actual:

```python
class CarritoActivoUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito_activo')
    carrito = models.ForeignKey('Carrito', on_delete=models.CASCADE, related_name='activos_por_usuario')
    fecha_activacion = models.DateTimeField(default=timezone.now)
```

### Modelos de Productos

Los productos representan los artículos que los usuarios pueden agregar a sus carritos:

```python
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    unidad_medida = models.CharField(max_length=20, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    
    @property
    def precio_minimo(self):
        """Retorna el precio mínimo de este producto"""
        precio_min = self.precios.aggregate(models.Min('precio'))['precio__min']
        return precio_min
    
    @property
    def precio_maximo(self):
        """Retorna el precio máximo de este producto"""
        precio_max = self.precios.aggregate(models.Max('precio'))['precio__max']
        return precio_max
```

#### Precio y Supermercado

Estos modelos gestionan los precios de productos por supermercado:

```python
class Supermercado(models.Model):
    id_supermercado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    geolocalizacion = models.CharField(max_length=100, blank=True, null=True)

class Precio(models.Model):
    id_precio = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios')
    id_supermercado = models.ForeignKey(Supermercado, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_actualizacion = models.DateTimeField()
```

### Relaciones entre Modelos

El sistema utiliza varias relaciones complejas:

- **One-to-Many**: Un usuario puede tener múltiples carritos (Carrito.usuario).
- **Many-to-Many**: Un carrito puede ser compartido con múltiples usuarios (Carrito.usuarios_compartidos).
- **Through Models**: Se utiliza InvitacionCarrito como modelo intermedio para las invitaciones.
- **One-to-One**: Cada usuario tiene un único carrito activo (CarritoActivoUsuario).

## Flujos Principales

### Gestión de Carritos

#### Crear un Nuevo Carrito

```python
@login_required
@require_POST
def crear_carrito(request):
    """Vista para crear un nuevo carrito vía AJAX desde el modal"""
    try:
        nombre = request.POST.get('nombre', '').strip()
        activo = request.POST.get('activo') == 'true'
        
        # Si el usuario quiere establecer este carrito como activo,
        # desactivar todos los demás carritos del usuario
        if activo:
            Carrito.objects.filter(usuario=request.user, activo=True).update(activo=False)
        
        # Crear el nuevo carrito
        carrito = Carrito.objects.create(
            usuario=request.user,
            nombre=nombre if nombre else None,
            activo=activo,
            fecha_creacion=timezone.now()
        )

        # Si el usuario quiere este carrito como activo, actualizar la relación
        if activo:
            CarritoActivoUsuario.objects.update_or_create(
                usuario=request.user,
                defaults={'carrito': carrito, 'fecha_activacion': timezone.now()}
            )
        
        # Preparar la respuesta JSON
        return JsonResponse({
            'status': 'success',
            'message': f"Carrito {carrito.nombre_display} creado exitosamente",
            'carrito_id': carrito.id_carrito,
            'cart_name': carrito.nombre_display
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al crear el carrito. Inténtalo de nuevo.'
        })
```

#### Ver Carrito Activo

```python
@login_required
def ver_carrito(request):
    """Vista principal del carrito"""
    # Buscar el carrito activo del usuario (propio o compartido)
    carrito_activo_obj = CarritoActivoUsuario.objects.filter(usuario=request.user).select_related('carrito').first()
    carrito = carrito_activo_obj.carrito if carrito_activo_obj else None
    
    # Obtener todos los carritos del usuario (propios y compartidos)
    todos_carritos = Carrito.objects.filter(
        Q(usuario=request.user) | Q(usuarios_compartidos=request.user)
    ).distinct().order_by('-fecha_creacion')
    
    # Invitaciones pendientes para el usuario
    invitaciones_pendientes = InvitacionCarrito.objects.filter(usuario=request.user, estado='pendiente')
    
    # Preparar el contexto para la plantilla
    context = {
        'carrito': carrito,
        'items': CarritoProducto.objects.filter(carrito=carrito).select_related('producto') if carrito else [],
        'todos_carritos': todos_carritos,
        'total_carritos': todos_carritos.count(),
        'invitaciones_pendientes': invitaciones_pendientes,
    }
    
    return render(request, 'carrito/carrito.html', context)
```

### Gestión de Productos

#### Agregar un Producto al Carrito

```python
@login_required
@require_POST
def agregar_al_carrito(request):
    """Vista para agregar productos al carrito activo del usuario"""
    try:
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))
        supermercado_id = request.POST.get('supermercado_id')
        precio_unitario = request.POST.get('precio_unitario')
        
        # Verificar datos y obtener objetos
        producto = get_object_or_404(Producto, id_producto=producto_id)
        supermercado = get_object_or_404(Supermercado, id_supermercado=supermercado_id) if supermercado_id else None
        
        # Buscar o crear carrito activo
        carrito_activo_obj = CarritoActivoUsuario.objects.filter(usuario=request.user).select_related('carrito').first()
        
        # Si no hay carrito activo, crear uno automáticamente
        if not carrito_activo_obj:
            carrito = Carrito.objects.create(
                usuario=request.user,
                nombre=f"Carrito de {request.user.username}",
                activo=True,
                fecha_creacion=timezone.now()
            )
            
            CarritoActivoUsuario.objects.update_or_create(
                usuario=request.user,
                defaults={'carrito': carrito, 'fecha_activacion': timezone.now()}
            )
        else:
            carrito = carrito_activo_obj.carrito
        
        # Buscar si ya existe ese producto en el carrito
        carrito_producto, created = CarritoProducto.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            supermercado=supermercado,
            defaults={'cantidad': cantidad, 'precio_unitario': precio_unitario}
        )
        
        # Si ya existía, incrementar la cantidad
        if not created:
            carrito_producto.cantidad = F('cantidad') + cantidad
            carrito_producto.precio_unitario = precio_unitario
            carrito_producto.save()
            carrito_producto.refresh_from_db()
        
        # Respuesta JSON con actualizaciones
        return JsonResponse({
            'status': 'success',
            'message': f'{producto.nombre} añadido al carrito',
            'cart_count': carrito.total_productos,
            'cart_name': carrito.nombre_display
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al agregar el producto. Inténtalo de nuevo.'
        })
```

### Sistema de Compartición

#### Invitar Usuario al Carrito

El sistema implementa un mecanismo de invitaciones que permite a varios usuarios compartir un mismo carrito:

```python
@login_required
@require_POST
def invitar_usuario(request):
    """Vista para invitar a otro usuario a compartir el carrito activo"""
    try:
        email = request.POST.get('email', '').strip()
        
        # Validar email
        if not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Por favor, proporciona un email válido.'
            })
        
        # Buscar usuario por email
        usuario_invitado = User.objects.filter(email=email).first()
        if not usuario_invitado:
            return JsonResponse({
                'status': 'error',
                'message': 'No se encontró ningún usuario con ese email.'
            })
        
        # No permitir auto-invitaciones
        if usuario_invitado == request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'No puedes invitarte a ti mismo.'
            })
        
        # Obtener carrito activo
        carrito_activo_obj = CarritoActivoUsuario.objects.filter(usuario=request.user).select_related('carrito').first()
        if not carrito_activo_obj:
            return JsonResponse({
                'status': 'error',
                'message': 'No tienes un carrito activo para compartir.'
            })
        
        carrito = carrito_activo_obj.carrito
        
        # Verificar que el usuario tenga permisos para invitar
        if carrito.usuario != request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'Solo el propietario del carrito puede enviar invitaciones.'
            })
        
        # Verificar si el usuario ya está invitado o compartido
        if InvitacionCarrito.objects.filter(carrito=carrito, usuario=usuario_invitado).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Este usuario ya ha sido invitado o ya tiene acceso al carrito.'
            })
        
        # Crear la invitación
        InvitacionCarrito.objects.create(
            carrito=carrito,
            usuario=usuario_invitado,
            estado='pendiente',
            fecha_invitacion=timezone.now()
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Invitación enviada a {usuario_invitado.username} correctamente.'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al enviar la invitación. Inténtalo de nuevo.'
        })
```

#### Finalizar un Carrito

Cuando un usuario completa una lista de compra, puede finalizar el carrito, lo que lo guarda en el historial:

```python
@login_required
@require_POST
def finalizar_carrito(request):
    """Vista para finalizar un carrito y guardarlo en historial"""
    try:
        carrito_id = request.POST.get('carrito_id')
        
        # Obtener el carrito que se quiere finalizar
        carrito = get_object_or_404(Carrito, id_carrito=carrito_id)
        
        # Verificar permisos
        if carrito.usuario != request.user and not carrito.usuarios_compartidos.filter(id=request.user.id).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'No tienes permisos para finalizar este carrito.'
            })
        
        # Verificar productos
        if not carrito.items.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'No puedes finalizar un carrito vacío.'
            })
        
        # Calcular costo total
        costo_total = carrito.precio_total
        
        # Crear entrada en historial
        HistorialCarrito.objects.create(
            carrito=carrito,
            usuario=request.user,
            costo_total=costo_total,
            fecha_finalizacion=timezone.now()
        )
        
        # Desactivar carrito finalizado
        carrito.activo = False
        carrito.save()
        
        # Si este era el carrito activo del usuario, buscar otro carrito para activar
        carrito_activo_obj = CarritoActivoUsuario.objects.filter(usuario=request.user, carrito=carrito).first()
        if carrito_activo_obj:
            # Buscar otro carrito del usuario
            otro_carrito = Carrito.objects.filter(
                Q(usuario=request.user) | Q(usuarios_compartidos=request.user)
            ).exclude(id_carrito=carrito_id).order_by('-fecha_creacion').first()
            
            if otro_carrito:
                carrito_activo_obj.carrito = otro_carrito
                carrito_activo_obj.fecha_activacion = timezone.now()
                carrito_activo_obj.save()
            else:
                carrito_activo_obj.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Carrito finalizado correctamente. ¡Gracias por tu compra!',
            'redirect_url': reverse('carrito:historial')
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al finalizar el carrito. Inténtalo de nuevo.'
        })
```

## Componentes Frontend

### Plantillas y Vistas

Las plantillas principales del sistema son:

- **carrito/carrito.html**: Vista principal del carrito activo
- **carrito/historial.html**: Lista del historial de carritos finalizados
- **productos/lista_productos.html**: Catálogo de productos disponibles
- **usuarios/login.html** y **usuarios/registro.html**: Formularios de autenticación

### JavaScript: CarritoManager

La interacción del usuario con la interfaz se maneja principalmente a través de la clase `CarritoManager` implementada en `static/js/carrito.js`:

```javascript
class CarritoManager {
    constructor() {
        this.djangoData = null;
        this.currentCartIdToDelete = null;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.loadDjangoData();
            this.setupEventListeners();
        });
    }

    // Métodos para manejar la interacción con el carrito
    updateQuantity(itemId, newQuantity) {
        const csrftoken = this.getCSRFToken();
        
        fetch('/carrito/actualizar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `item_id=${itemId}&cantidad=${newQuantity}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Actualizar total del carrito
                document.getElementById('cartTotal').textContent = `${data.cart_total.toFixed(2)}€`;
                document.getElementById('cartCount').textContent = data.cart_count;
                
                // Actualizar subtotal del item
                const subtotalElement = document.querySelector(`.subtotal[data-item-id="${itemId}"]`);
                if (subtotalElement) {
                    subtotalElement.textContent = `${data.item_subtotal.toFixed(2)}€`;
                }
                
                // Mostrar mensaje de éxito
                this.showToast('success', data.message);
            } else {
                this.showToast('error', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showToast('error', 'Error de conexión. Inténtalo de nuevo.');
        });
    }
    
    // Otros métodos...
}
```

### Interacción AJAX

El sistema utiliza AJAX para manejar interacciones sin recargar la página. Ejemplos:

- Agregar/eliminar productos del carrito
- Actualizar cantidades
- Invitar usuarios
- Responder a invitaciones
- Finalizar compras

## Componentes Backend

### Vistas y Controladores

Las vistas principales están organizadas por funcionalidad:

- **carrito/views.py**: Gestión de carritos, productos y compartición
- **productos/views.py**: Catálogo y detalles de productos
- **usuarios/views.py**: Autenticación, registro y perfil de usuario

### Seguridad y Autenticación

El sistema utiliza el sistema de autenticación de Django con algunas personalizaciones:

- Protección CSRF en todas las solicitudes POST
- Decoradores `@login_required` para asegurar las vistas
- Verificación de permisos en operaciones sobre carritos compartidos

## Guía de Despliegue

### Entorno de Desarrollo

Para configurar el entorno de desarrollo:

1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno: `source venv/bin/activate` (Linux/Mac) o `venv\Scripts\activate` (Windows)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar variables de entorno en `.env`
6. Ejecutar migraciones: `python manage.py migrate`
7. Crear superusuario: `python manage.py createsuperuser`
8. Iniciar servidor: `python manage.py runserver`

### Configuración de Producción

Para el despliegue en producción se utiliza Fly.io:

1. Configurar las variables de entorno de producción
2. Asegurar `DEBUG = False`
3. Configurar el servidor web (Gunicorn)
4. Implementar la estrategia de base de datos (PostgreSQL)
5. Configurar Whitenoise para archivos estáticos
6. Desplegar con el comando `flyctl deploy`
## App Usuarios en profundidad


## Ampliaciones y Mejoras

Posibles mejoras para el proyecto:

1. Implementación de API REST para interacción con apps móviles
2. Mejora del sistema de análisis de precios
3. Integración con APIs de supermercados reales
4. Implementación de escáner de códigos de barras
5. Ampliación del sistema de notificaciones
6. Mejoras en la interfaz de usuario y experiencia móvil
