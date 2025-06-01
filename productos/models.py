# productos/models.py
from django.db import models

class Supermercado(models.Model):
    id_supermercado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    geolocalizacion = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'Supermercados'
        
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    unidad_medida = models.CharField(max_length=20, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Campo individual (puede ser precio promedio)
    descripcion = models.TextField(blank=True, null=True)
    #imagen = models.ImageField(upload_to='productos/', blank=True, null=True)  # Campo adicional para imágenes usar pillow
    
    class Meta:
        db_table = 'Productos'
        
    def __str__(self):
        return self.nombre

class Precio(models.Model):
    id_precio = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE,
        db_column='id_producto',
        related_name='precios'
    )
    id_supermercado = models.ForeignKey(
        Supermercado,
        on_delete=models.CASCADE,
        db_column='id_supermercado'
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Precios'
        unique_together = ['id_producto', 'id_supermercado']  # Un precio por producto por supermercado
        
    def __str__(self):
        return f"{self.id_producto.nombre} - {self.id_supermercado.nombre}: €{self.precio}"