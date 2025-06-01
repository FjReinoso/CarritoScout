from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PerfilUsuario(models.Model):
    """Extensión del User de Django con todos los campos necesarios"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfilusuario')
    
    
    # Extendemos los campos del modelo user de django
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    
    # extra
    fecha_registro = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'Perfiles_Usuario'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    @property
    def nombre_completo(self):
        
        if self.usuario.first_name and self.usuario.last_name:
            return f"{self.usuario.first_name} {self.usuario.last_name}"
        return self.usuario.username