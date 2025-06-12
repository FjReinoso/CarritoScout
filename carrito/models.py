from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    
    class Meta:
        db_table = 'Carritos'
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        
    def __str__(self):
        return f"Carrito #{self.id_carrito} - {self.usuario.username}"
    
    @property
    def nombre_display(self):
        """Retorna el nombre del carrito o un nombre por defecto"""
        if self.nombre and self.nombre.strip():
            return self.nombre
        return f"Carrito #{self.id_carrito}"
    
    @property
    def total_productos(self):
        """Calcula el total de productos en el carrito"""
        return sum(item.cantidad for item in self.items.all())
    
    @property
    def precio_total(self):
        """Calcula el precio total del carrito"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def items_count(self):
        """Retorna el número de items diferentes en el carrito"""
        return self.items.count()

class CarritoProducto(models.Model):
    """Modelo intermedio para productos en carritos"""
    id = models.AutoField(primary_key=True)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    supermercado = models.ForeignKey('productos.Supermercado', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Supermercado')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Precio unitario')
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'Carrito_Productos'
        unique_together = ['carrito', 'producto', 'supermercado']  # Un producto por supermercado por carrito
        verbose_name = 'Producto en Carrito'
        verbose_name_plural = 'Productos en Carrito'
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} ({self.supermercado.nombre if self.supermercado else 'Sin supermercado'})"
    
    @property
    def subtotal(self):
        """Calcula el subtotal de este item"""
        precio = self.precio_unitario if self.precio_unitario is not None else (self.producto.precio or 0)
        return precio * self.cantidad

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
    
    class Meta:
        db_table = 'Invitaciones_Carrito'
        unique_together = ['carrito', 'usuario']
        verbose_name = 'Invitación a Carrito'
        verbose_name_plural = 'Invitaciones a Carrito'
        
    def __str__(self):
        return f"{self.usuario.username} - Carrito #{self.carrito.id_carrito} ({self.estado})"

class HistorialCarrito(models.Model):
    """Historial de carritos finalizados"""
    id_historial_carrito = models.AutoField(primary_key=True)
    carrito = models.OneToOneField(Carrito, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historial_carritos')
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_finalizacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'Historial_Carritos'
        verbose_name = 'Historial de Carrito'
        verbose_name_plural = 'Historial de Carritos'
        
    def __str__(self):
        return f"Historial #{self.id_historial_carrito} - {self.usuario.username}"