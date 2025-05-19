from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .form import RegistroBasicoForm, RegistroOpcionalForm, PerfilUsuarioForm, PerfilUsuarioCorreoForm, DatosPersonalesForm
from .models import PerfilUsuario, UsuarioLegacy

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
    perfil = user.perfilusuario
    
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
                
                # Sincronizar cambios con la tabla Usuarios legacy
                try:
                    # Buscar el usuario en la tabla Usuarios legacy
                    usuario_legacy = UsuarioLegacy.objects.filter(email=user.email).first()
                    if usuario_legacy:
                        usuario_legacy.first_name = user.first_name
                        usuario_legacy.last_name = user.last_name
                        usuario_legacy.save()
                        print(f"Datos personales actualizados en tabla legacy para {user.email}")
                    else:
                        print(f"No se encontró el usuario {user.email} en la tabla Usuarios legacy")
                except Exception as e:
                    print(f"Error al actualizar datos en tabla legacy: {e}")
                
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
                
                # Sincronizar cambios con la tabla Usuarios legacy para la información adicional
                try:
                    # Buscar el usuario en la tabla Usuarios legacy
                    usuario_legacy = UsuarioLegacy.objects.filter(email=user.email).first()
                    if usuario_legacy:
                        # Actualizar los campos en la tabla Usuarios
                        usuario_legacy.direccion = perfil.direccion
                        usuario_legacy.telefono = perfil.telefono
                        usuario_legacy.fecha_nacimiento = perfil.fecha_nacimiento
                        usuario_legacy.save()
                        print(f"Información adicional actualizada en tabla legacy para {user.email}")
                    else:
                        print(f"No se encontró el usuario {user.email} en la tabla Usuarios legacy")
                except Exception as e:
                    print(f"Error al actualizar información adicional en tabla legacy: {e}")
                
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
        'user': user,  # Pasamos el usuario para acceder a su información en la plantilla
    })
