from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario
from django.db import connection

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        # Crear el perfil del usuario
        PerfilUsuario.objects.create(usuario=instance)

        # Insertar el usuario en la tabla SQL personalizada "Usuarios"
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Usuarios (nombre, email, contraseña, fecha_registro)
                VALUES (%s, %s, %s, NOW())
                """,
                [instance.username, instance.email, instance.password]
            )

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    instance.perfil.save()