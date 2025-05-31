from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from .models import PerfilUsuario

class CambioPasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'required': 'Debes introducir tu contraseña actual'}
    )
    new_password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        min_length=8,
        error_messages={
            'required': 'Debes introducir una nueva contraseña',
            'min_length': 'La contraseña debe tener al menos 8 caracteres'
        }
    )
    confirm_password = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'required': 'Debes confirmar tu nueva contraseña'}
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError(
                "Las contraseñas no coinciden."
            )
        return cleaned_data

class PerfilUsuarioForm(forms.ModelForm):
    direccion = forms.CharField(
        max_length=24, 
        required=True,
        error_messages={
            'required': 'La dirección es obligatoria',
            'max_length': 'La dirección no puede exceder los 24 caracteres'
        }
    )
    
    # Validador para teléfono: solo 9 dígitos
    telefono = forms.CharField(
        max_length=9,
        min_length=9,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',
                message='El teléfono debe tener exactamente 9 dígitos numéricos',
                code='invalid_phone'
            )
        ],
        error_messages={
            'required': 'El teléfono es obligatorio',
            'max_length': 'El teléfono debe tener 9 dígitos',
            'min_length': 'El teléfono debe tener 9 dígitos'
        }
    )
    
    class Meta:
        model = PerfilUsuario
        fields = ['direccion', 'telefono', 'fecha_nacimiento']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
        }

class PerfilUsuarioCorreoForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=24, 
        required=True,
        error_messages={
            'required': 'El correo electrónico es obligatorio',
            'max_length': 'El correo no puede exceder los 24 caracteres',
            'invalid': 'Por favor, introduce un correo electrónico válido'
        }
    )

    class Meta:
        model = User
        fields = ['email']
        
class DatosPersonalesForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=24,
        required=True,
        error_messages={
            'required': 'El nombre es obligatorio',
            'max_length': 'El nombre no puede exceder los 24 caracteres'
        }
    )
    
    last_name = forms.CharField(
        max_length=24,
        required=True, 
        error_messages={
            'required': 'Los apellidos son obligatorios',
            'max_length': 'Los apellidos no pueden exceder los 24 caracteres'
        }
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