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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios:login')
    else:
        form = UserCreationForm()
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
            perfil = form.save(commit=False)
            perfil.user = request.user
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
            return redirect('usuarios:perfil')
    else:
        perfil_form = PerfilUsuarioForm(instance=perfil)
        correo_form = PerfilUsuarioCorreoForm(instance=user)

    return render(request, 'usuarios/perfil.html', {
        'perfil_form': perfil_form,
        'correo_form': correo_form,
    })