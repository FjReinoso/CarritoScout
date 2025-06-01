from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.producto_list, name='producto_list'),
    path('<int:producto_id>/', views.producto_detail, name='producto_detail'),
]