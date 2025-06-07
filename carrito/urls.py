from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('actualizar/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('eliminar/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('crear/', views.crear_carrito, name='crear_carrito'),
    path('finalizar/', views.finalizar_carrito, name='finalizar_carrito'),
    path('historial/', views.historial_carritos, name='historial'),
    path('historial/<int:historial_id>/', views.detalle_historial, name='detalle_historial'),
]
