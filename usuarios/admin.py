from django.contrib import admin
from .models import PerfilUsuario, UsuarioLegacy

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'direccion', 'telefono', 'fecha_nacimiento')
    search_fields = ('usuario__username', 'usuario__email', 'direccion', 'telefono')

@admin.register(UsuarioLegacy)
class UsuarioLegacyAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'nombre', 'email', 'first_name', 'last_name', 'fecha_registro')
    search_fields = ('nombre', 'email', 'first_name', 'last_name')
    readonly_fields = ('id_usuario', 'nombre', 'email', 'contraseña', 'first_name', 'last_name', 'fecha_registro')
    
    def has_add_permission(self, request):
        return False  # Desactiva la capacidad de agregar nuevos registros desde el admin
    
    def has_change_permission(self, request, obj=None):
        return False  # Desactiva la capacidad de editar registros desde el admin