from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario
#Este archivo existe con el proposito de sincronizar el modelo PerfilUsuario con el modelo User de Django.
# Cuando se crea un usuario, se crea un perfil asociado automáticamente.
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Señal que se activa cuando se guarda un usuario.
    Crea un perfil para el usuario cuando se crea un nuevo usuario.
    """
    if created:
        try:
            PerfilUsuario.objects.get_or_create(usuario=instance)
            print(f"Perfil creado para el usuario: {instance.username}")
        except Exception as e:
            print(f"Error al crear perfil para {instance.username}: {e}")

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Señal que se activa cuando se guarda un usuario.
    Guarda el perfil asociado si existe.
    """
    try:
        if hasattr(instance, 'perfilusuario'):
            instance.perfilusuario.save()
            print(f"Guardado perfil de usuario: {instance.username}")
    except Exception as e:
        print(f"Error al guardar perfil de usuario: {e}")