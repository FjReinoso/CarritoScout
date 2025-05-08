from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required

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

@login_required
def pagina_principal(request):
    return render(request, 'usuarios/pagina_principal.html')