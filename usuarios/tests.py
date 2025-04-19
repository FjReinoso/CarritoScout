
from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario

class UsuarioTests(TestCase):
    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.username = "testuser"
        self.password = "securepassword123"
        self.email = "testuser@example.com"

    def test_creacion_usuario(self):
        """
        Prueba la creación de un usuario y verifica que se guarde en ambas bases de datos.
        """
        # Crear usuario en la base de datos de Django
        user = User.objects.create_user(username=self.username, password=self.password, email=self.email)

        # Verificar que el usuario se creó correctamente en la base de datos de Django
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, self.username)

        # Verificar que el usuario se duplicó automáticamente en la base de datos personalizada
        usuario_personalizado = PerfilUsuario.objects.get(username=self.username)
        self.assertEqual(usuario_personalizado.username, self.username)
        self.assertEqual(usuario_personalizado.email, self.email)

    def test_login_usuario(self):
        """
        Prueba el inicio de sesión de un usuario.
        """
        # Crear usuario
        User.objects.create_user(username=self.username, password=self.password)

        # Intentar iniciar sesión
        login = self.client.login(username=self.username, password=self.password)

        # Verificar que el inicio de sesión fue exitoso
        self.assertTrue(login)

    def test_usuario_no_duplicado(self):
        """
        Verifica que no se creen duplicados en la base de datos personalizada.
        """
        # Crear usuario
        User.objects.create_user(username=self.username, password=self.password, email=self.email)

        # Intentar crear el mismo usuario nuevamente
        with self.assertRaises(Exception):
            PerfilUsuario.objects.create(username=self.username, email=self.email)
