from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario
from django.db import connection, ProgrammingError, IntegrityError
from django.conf import settings
import sys

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Señal que se activa cuando se guarda un usuario.
    Crea un perfil para el usuario y lo registra en la tabla SQL personalizada Usuarios
    usando el modelo UsuarioLegacy de Django.
    """
    print("\n--- INICIO SEÑAL crear_perfil_usuario ---")
    print(f"Usuario: {instance.username}, Creado: {created}")
    
    if created:
        # Solo crear el perfil del usuario si es un nuevo usuario
        try:
            PerfilUsuario.objects.get_or_create(usuario=instance)
            print(f"Perfil creado para el usuario: {instance.username}")
        except Exception as e:
            print(f"Error al crear perfil para {instance.username}: {e}")
        
        # Verificar si estamos en un entorno de prueba
        is_test = 'test' in sys.argv or connection.settings_dict['NAME'].startswith('test_')
        
        # En entorno de prueba, omitir operaciones con Usuarios Legacy
        if is_test:
            print("Omitiendo operaciones con Usuarios Legacy en entorno de prueba")
            print("--- FIN SEÑAL crear_perfil_usuario ---\n")
            return
        
        # Importamos aquí para evitar problemas de importación circular
        from .models import UsuarioLegacy
        
        # Insertar usuario en la tabla Usuarios personalizada usando el ORM de Django
        print("\n--- INICIO INSERCIÓN EN TABLA USUARIOS CON ORM ---")
        print(f"Intento de inserción para usuario: {instance.username} ({instance.email})")
        try:
            # Verificar si el usuario ya existe en la tabla
            if UsuarioLegacy.objects.filter(email=instance.email).exists():
                print(f"El usuario {instance.email} ya existe en la tabla Usuarios")
                print("--- FIN INSERCIÓN EN TABLA USUARIOS CON ORM ---\n")
                return
              # Crear el nuevo usuario en la tabla Usuarios legacy
            usuario_legacy = UsuarioLegacy(
                nombre=instance.username,
                email=instance.email,
                contraseña='[CONTRASEÑA HASHEADA]',
                first_name=instance.first_name if instance.first_name else None,
                last_name=instance.last_name if instance.last_name else None
            )
            usuario_legacy.save()
            print(f"¡ÉXITO! Usuario {instance.username} insertado en tabla Usuarios con ORM")
        except Exception as e:
            print(f"Error al insertar usuario en tabla Usuarios con ORM: {e}")
            print("--- FIN INSERCIÓN EN TABLA USUARIOS CON ORM ---\n")
            return
        
        print("--- FIN INSERCIÓN EN TABLA USUARIOS CON ORM ---\n")
    
    print("--- FIN SEÑAL crear_perfil_usuario ---\n")

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    # Verificar si existe el perfil antes de guardar
    try:
        if hasattr(instance, 'perfilusuario'):
            instance.perfilusuario.save()
            print(f"Guardado perfil de usuario: {instance.username}")
    except Exception as e:
        print(f"Error al guardar perfil de usuario: {e}")