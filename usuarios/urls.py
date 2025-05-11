from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    login_view, 
    registro_view, 
    registro_basico, 
    registro_opcional, 
    pagina_principal, 
    perfil_view
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('registro/basico/', registro_basico, name='registro_basico'),
    path('registro/opcional/', registro_opcional, name='registro_opcional'),
    path('logout/', LogoutView.as_view(next_page='usuarios:login'), name='logout'),
    path('principal/', pagina_principal, name='pagina_principal'),
    path('perfil/', perfil_view, name='perfil'),
]