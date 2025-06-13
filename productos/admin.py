from django.contrib import admin
from .models import Supermercado, Producto, Precio

@admin.register(Supermercado)
class SupermercadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'geolocalizacion')
    search_fields = ('nombre', 'direccion')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'unidad_medida', 'precio')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria',)

@admin.register(Precio)
class PrecioAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'id_supermercado', 'precio', 'fecha_actualizacion')
    search_fields = ('id_producto__nombre', 'id_supermercado__nombre')
    list_filter = ('id_supermercado',)
