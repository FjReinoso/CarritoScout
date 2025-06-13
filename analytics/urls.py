from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.evolucion_precios, name='evolucion_precios'),
    path('data/', views.evolucion_precios_data, name='evolucion_precios_data'),
]
