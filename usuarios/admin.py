from django.contrib import admin
from .models import PerfilUsuario
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'direccion', 'telefono', 'fecha_nacimiento')
    search_fields = ('usuario__username', 'usuario__email', 'direccion', 'telefono')

# Registrar el modelo User para manipulación directa desde el admin
admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
