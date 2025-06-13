from django.shortcuts import render
from django.http import JsonResponse
from productos.models import Producto, Supermercado, Precio
from django.db.models import Q
import datetime

# Página principal de evolución de precios

def evolucion_precios(request):
    productos = Producto.objects.all()
    supermercados = Supermercado.objects.all()
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    return render(request, 'analytics/evolucion_precios.html', {
        'productos': productos,
        'supermercados': supermercados,
        'categorias': categorias,
    })

# Endpoint para datos de la gráfica (AJAX)
def evolucion_precios_data(request):
    tipo = request.GET.get('tipo', 'producto')
    id = request.GET.get('id')
    data = []
    labels = []
    if tipo == 'producto' and id:
        precios = Precio.objects.filter(id_producto=id).order_by('fecha_actualizacion')
        labels = [p.fecha_actualizacion.strftime('%Y-%m-%d') for p in precios]
        data = [float(p.precio) for p in precios]
    elif tipo == 'categoria' and id:
        productos = Producto.objects.filter(categoria=id)
        precios = Precio.objects.filter(id_producto__in=productos).order_by('fecha_actualizacion')
        # Agrupar por fecha y calcular promedio
        fechas = sorted(set(p.fecha_actualizacion.date() for p in precios))
        for fecha in fechas:
            precios_fecha = precios.filter(fecha_actualizacion__date=fecha)
            if precios_fecha.exists():
                labels.append(str(fecha))
                data.append(float(sum(p.precio for p in precios_fecha) / precios_fecha.count()))
    elif tipo == 'supermercado' and id:
        precios = Precio.objects.filter(id_supermercado=id).order_by('fecha_actualizacion')
        fechas = sorted(set(p.fecha_actualizacion.date() for p in precios))
        for fecha in fechas:
            precios_fecha = precios.filter(fecha_actualizacion__date=fecha)
            if precios_fecha.exists():
                labels.append(str(fecha))
                data.append(float(sum(p.precio for p in precios_fecha) / precios_fecha.count()))
    return JsonResponse({'labels': labels, 'data': data})
