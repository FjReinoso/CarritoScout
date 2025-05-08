from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import login_view, registro_view, pagina_principal

urlpatterns = [
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('logout/', LogoutView.as_view(next_page='usuarios:login'), name='logout'),
    path('principal/', pagina_principal, name='pagina_principal'),
]