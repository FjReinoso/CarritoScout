from django.contrib import admin
from .models import Carrito, CarritoProducto, HistorialCarrito

class CarritoProductoInline(admin.TabularInline):
    model = CarritoProducto
    extra = 1

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id_carrito', 'usuario', 'fecha_creacion', 'activo', 'total_productos', 'precio_total')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('usuario__username',)
    inlines = [CarritoProductoInline]

@admin.register(CarritoProducto)
class CarritoProductoAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'producto', 'cantidad', 'fecha_agregado', 'subtotal')
    list_filter = ('fecha_agregado',)
    search_fields = ('producto__nombre',)

@admin.register(HistorialCarrito)
class HistorialCarritoAdmin(admin.ModelAdmin):
    list_display = ('id_historial_carrito', 'usuario', 'costo_total', 'fecha_finalizacion')
    list_filter = ('fecha_finalizacion',)
    search_fields = ('usuario__username',)
