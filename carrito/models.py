from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto
from django.utils import timezone

class Carrito(models.Model):
    """Modelo para el carrito de compras de un usuario"""
    id_carrito = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carritos')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Carritos'
        verbose_name = 'Carrito de Compras'
        verbose_name_plural = 'Carritos de Compras'
        
    def __str__(self):
        return f"Carrito de {self.usuario.username} - {self.fecha_creacion.strftime('%d/%m/%Y')}"
    
    @property
    def total_productos(self):
        """Retorna el número total de productos en el carrito"""
        return sum(item.cantidad for item in self.items.all())
    
    @property
    def precio_total(self):
        """Retorna el precio total del carrito"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def items_count(self):
        """Retorna el número de items distintos en el carrito"""
        return self.items.count()

class CarritoProducto(models.Model):
    """Relación entre carritos y productos (items del carrito)"""
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Carrito_Productos'
        unique_together = ['carrito', 'producto']  # Un producto por carrito
        verbose_name = 'Producto en Carrito'
        verbose_name_plural = 'Productos en Carrito'
        
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    @property
    def subtotal(self):
        """Calcula el subtotal de este item"""
        precio_unitario = self.producto.precio or 0
        return precio_unitario * self.cantidad

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
        return f"Historial de carrito de {self.usuario.username} - {self.fecha_finalizacion.strftime('%d/%m/%Y')}"
