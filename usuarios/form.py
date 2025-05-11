from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario

class PerfilUsuarioForm(forms.ModelForm):
    direccion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Vacío'}),
        label="Dirección"
    )
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Vacío'}),
        label="Teléfono"
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Vacío'}),
        label="Fecha de Nacimiento"
    )

    class Meta:
        model = PerfilUsuario
        fields = ['direccion', 'telefono', 'fecha_nacimiento']

class PerfilUsuarioCorreoForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'readonly': 'readonly'}),
        label="Correo Electrónico"
    )

    class Meta:
        model = User
        fields = ['email']

class RegistroBasicoForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellidos")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class RegistroOpcionalForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['direccion', 'telefono', 'fecha_nacimiento']