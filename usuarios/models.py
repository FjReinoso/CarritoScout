from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfilusuario')
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class UsuarioLegacy(models.Model):
    """
    Modelo que representa la tabla personalizada 'Usuarios'.
    Este modelo es principalmente para referencia y no debe usarse directamente.
    Se mantiene sincronizado automáticamente con User a través de señales.
    """
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    contraseña = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100, null=True, blank=True)  # Campo opcional
    last_name = models.CharField(max_length=100, null=True, blank=True)   # Campo opcional
    fecha_registro = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Usuarios'  # Nombre explícito de la tabla en la base de datos
        managed = False  # Django no debe gestionar esta tabla (no crear migraciones para ella)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.nombre})"
        return f"Usuario Legacy: {self.nombre}"
