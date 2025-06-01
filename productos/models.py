

from django.db import models

class Supermercado(models.Model):
    id_supermercado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    geolocalizacion = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        db_table = 'Supermercados'
        managed = False  # Usamos la nuestra

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, null=True, blank=True)
    unidad_medida = models.CharField(max_length=20, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'Productos'
        managed = False  # Usamos la nuestra

    def __str__(self):
        return self.nombre
    
class Precio(models.Model):
    id_precio = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')
    id_supermercado = models.ForeignKey(Supermercado, on_delete=models.CASCADE, db_column='id_supermercado')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Precios'
        managed = False  # Usamos la nuestra