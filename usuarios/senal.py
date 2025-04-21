from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario
from django.db import connection, ProgrammingError, IntegrityError

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Señal que se activa cuando se guarda un usuario.
    Crea un perfil para el usuario y lo registra en la tabla SQL personalizada.
    """
    if created:
        # Crear el perfil del usuario en Django
        try:
            PerfilUsuario.objects.create(usuario=instance)
        except IntegrityError:
            # Si el perfil ya existe, no necesitamos crear uno nuevo
            pass
        
        # En lugar de cambiar el modo autocommit (que no funciona en pruebas),
        # simplemente ejecutamos las consultas SQL dentro del contexto actual
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Usuarios (nombre, email, contraseña, fecha_registro)
                    VALUES (%s, %s, %s, NOW())
                    """,
                    [instance.username, instance.email, instance.password]
                )
        except ProgrammingError:
            # La tabla Usuarios no existe, intentamos crearla primero
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS Usuarios (
                            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                            nombre VARCHAR(100) NOT NULL,
                            email VARCHAR(100) UNIQUE NOT NULL,
                            contraseña VARCHAR(255) NOT NULL,
                            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                    # Ahora intentamos la inserción nuevamente
                    cursor.execute(
                        """
                        INSERT INTO Usuarios (nombre, email, contraseña, fecha_registro)
                        VALUES (%s, %s, %s, NOW())
                        """,
                        [instance.username, instance.email, instance.password]
                    )
            except Exception as e:
                print(f"Error al crear la tabla Usuarios en el entorno de prueba: {e}")
        except Exception as e:
            # Capturar cualquier otra excepción
            print(f"Error al insertar usuario en la tabla Usuarios: {e}")