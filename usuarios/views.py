from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from .form import RegistroBasicoForm, RegistroOpcionalForm, PerfilUsuarioForm, PerfilUsuarioCorreoForm, DatosPersonalesForm, CambioPasswordForm
from .models import PerfilUsuario

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('usuarios:pagina_principal')
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})

def registro_view(request):
    if request.method == 'POST':
        form = RegistroBasicoForm(request.POST)
        if form.is_valid():
            # Crear el usuario y guardarlo en la base de datos
            user = form.save(commit=True)
            
            # Iniciar sesión automáticamente
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Verificar que se haya creado el perfil
                try:
                    perfil = user.perfilusuario
                except:
                    perfil = PerfilUsuario.objects.create(usuario=user)
                    
                return redirect('usuarios:pagina_principal')
            else:
                # Si hay problemas con la autenticación, añadimos un error al formulario
                form.add_error(None, "Error de autenticación. Por favor intenta nuevamente.")
    else:
        form = RegistroBasicoForm()
    
    # Aquí añadimos print para depuración
    if form.errors:
        print(f"Errores del formulario: {form.errors}")
        
    return render(request, 'usuarios/registro.html', {'form': form})

def registro_basico(request):
    if request.method == 'POST':
        form = RegistroBasicoForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('usuarios:registro_opcional')
    else:
        form = RegistroBasicoForm()
    return render(request, 'usuarios/registro_basico.html', {'form': form})

def registro_opcional(request):
    if request.method == 'POST':
        form = RegistroOpcionalForm(request.POST)
        if form.is_valid():
            # Buscar o crear el perfil del usuario
            try:
                perfil = request.user.perfilusuario
            except:
                perfil = PerfilUsuario(usuario=request.user)
            
            # Actualizar los campos del perfil con los datos del formulario
            perfil.direccion = form.cleaned_data['direccion']
            perfil.telefono = form.cleaned_data['telefono']
            perfil.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
            perfil.save()
            
            return redirect('usuarios:pagina_principal')
    else:
        form = RegistroOpcionalForm()
    return render(request, 'usuarios/registro_opcional.html', {'form': form})

@login_required
def pagina_principal(request):
    return render(request, 'usuarios/pagina_principal.html')

@login_required
def perfil_view(request):
    user = request.user
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=user)
    
    # Identificamos qué formulario se está enviando comprobando los botones y procesamos el cambio de contraseña
    if request.method == 'POST' and 'cambiar_password' in request.POST:
        password_form = CambioPasswordForm(request.POST)
        datos_personales_form = DatosPersonalesForm(instance=user)
        correo_form = PerfilUsuarioCorreoForm(instance=user)
        perfil_form = PerfilUsuarioForm(instance=perfil)
        
        if password_form.is_valid():
            current_password = password_form.cleaned_data['current_password']
            new_password = password_form.cleaned_data['new_password']
            
            # Verificar la contraseña actual
            if check_password(current_password, user.password):
                # Cambiar la contraseña
                user.set_password(new_password)
                user.save()
                
                # Actualizar la sesión para evitar cerrar sesión
                update_session_auth_hash(request, user)
                
                messages.success(request, "¡Tu contraseña ha sido actualizada correctamente!")
                return redirect('usuarios:perfil')
            else:
                messages.error(request, "La contraseña actual no es correcta.")
                return redirect('usuarios:perfil')
    else:
        password_form = CambioPasswordForm()
    
    # Identificamos qué formulario se está enviando comprobando los botones
    if request.method == 'POST':
        # Comprobamos si existe el formulario personal (first_name, last_name)
        if 'datos_personales' in request.POST:
            datos_personales_form = DatosPersonalesForm(request.POST, instance=user)
            correo_form = PerfilUsuarioCorreoForm(instance=user)
            perfil_form = PerfilUsuarioForm(instance=perfil)
            
            if datos_personales_form.is_valid():
                # Guardar cambios en el modelo User
                user_updated = datos_personales_form.save()
                
                # Añadir mensaje de éxito
                messages.success(request, "¡Los datos personales se han actualizado correctamente!")
                return redirect('usuarios:perfil')
        
        # Comprobamos si existe el formulario de información adicional (dirección, teléfono, etc.)
        elif 'info_adicional' in request.POST:
            perfil_form = PerfilUsuarioForm(request.POST, instance=perfil)
            datos_personales_form = DatosPersonalesForm(instance=user)
            correo_form = PerfilUsuarioCorreoForm(instance=user)
            if perfil_form.is_valid():
                # Guardar el formulario para actualizar el perfil
                perfil_actualizado = perfil_form.save()
                
                # Obtener el perfil actualizado nuevamente para tener los datos más recientes
                perfil = perfil_actualizado
                
                # Añadir mensaje de éxito
                messages.success(request, "¡La información adicional se ha actualizado correctamente!")
                return redirect('usuarios:perfil')
        
        # Si no reconocemos el formulario, asumimos que es el correo
        else:
            correo_form = PerfilUsuarioCorreoForm(request.POST, instance=user)
            datos_personales_form = DatosPersonalesForm(instance=user)
            perfil_form = PerfilUsuarioForm(instance=perfil)
            
            if correo_form.is_valid():
                correo_form.save()
                messages.success(request, "¡El correo electrónico se ha actualizado correctamente!")
                return redirect('usuarios:perfil')
    else:
        # Inicializar todos los formularios
        datos_personales_form = DatosPersonalesForm(instance=user)
        correo_form = PerfilUsuarioCorreoForm(instance=user)
        # El formato de fecha se maneja en el __init__ del PerfilUsuarioForm
        perfil_form = PerfilUsuarioForm(instance=perfil)

    return render(request, 'usuarios/perfil.html', {
        'datos_personales_form': datos_personales_form,
        'perfil_form': perfil_form,
        'correo_form': correo_form,
        'password_form': password_form,
        'user': user,  # Pasamos el usuario para acceder a su información en la plantilla
    })