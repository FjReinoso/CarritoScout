from django.contrib import admin
from .models import PerfilUsuario

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'direccion', 'telefono', 'fecha_nacimiento')
    search_fields = ('usuario__username', 'usuario__email', 'direccion', 'telefono')
