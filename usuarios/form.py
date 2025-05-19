from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario

class PerfilUsuarioForm(forms.ModelForm):
    direccion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Vacío', 'class': 'form-control'}),
        label="Dirección"
    )
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Vacío', 'class': 'form-control'}),
        label="Teléfono"
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Vacío', 'class': 'form-control'}),
        label="Fecha de Nacimiento"
    )
    
    def __init__(self, *args, **kwargs):
        super(PerfilUsuarioForm, self).__init__(*args, **kwargs)
        # Si hay un valor de fecha_nacimiento, asegurar que se muestre en el formato correcto
        if self.instance and self.instance.fecha_nacimiento:
            # Convertir a string con formato YYYY-MM-DD para el widget de fecha
            self.initial['fecha_nacimiento'] = self.instance.fecha_nacimiento.strftime('%Y-%m-%d')

    class Meta:
        model = PerfilUsuario
        fields = ['direccion', 'telefono', 'fecha_nacimiento']

class PerfilUsuarioCorreoForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        label="Correo Electrónico"
    )

    class Meta:
        model = User
        fields = ['email']
        
class DatosPersonalesForm(forms.ModelForm):
    first_name = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nombre"
    )
    last_name = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Apellidos"
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class RegistroBasicoForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, label="Nombre")
    last_name = forms.CharField(max_length=30, required=False, label="Apellidos")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class RegistroOpcionalForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['direccion', 'telefono', 'fecha_nacimiento']