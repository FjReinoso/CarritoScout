from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .form import RegistroBasicoForm, RegistroOpcionalForm, PerfilUsuarioForm, PerfilUsuarioCorreoForm
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
    perfil = user.perfilusuario

    if request.method == 'POST':
        perfil_form = PerfilUsuarioForm(request.POST, instance=perfil)
        correo_form = PerfilUsuarioCorreoForm(request.POST, instance=user)
        if perfil_form.is_valid() and correo_form.is_valid():
            perfil_form.save()
            correo_form.save()
            return redirect('usuarios:perfil')
    else:
        perfil_form = PerfilUsuarioForm(instance=perfil)
        correo_form = PerfilUsuarioCorreoForm(instance=user)

    return render(request, 'usuarios/perfil.html', {
        'perfil_form': perfil_form,
        'correo_form': correo_form,
        'user': user,  # Pasamos el usuario para acceder a su información en la plantilla
    })