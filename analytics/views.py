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
    ids = request.GET.get('ids')
    id = request.GET.get('id')
    data = {}
    labels = set()
    from collections import defaultdict
    if ids:
        ids_list = [i for i in ids.split(',') if i]
        for single_id in ids_list:
            serie_labels = []
            serie_data = []
            if tipo == 'producto':
                precios = Precio.objects.filter(id_producto=single_id).order_by('fecha_actualizacion')
                precios_por_mes = defaultdict(list)
                for p in precios:
                    mes = p.fecha_actualizacion.strftime('%Y-%m')
                    precios_por_mes[mes].append(float(p.precio))
                serie_labels = sorted(precios_por_mes.keys())
                serie_data = [sum(precios_por_mes[mes]) / len(precios_por_mes[mes]) for mes in serie_labels]
            elif tipo == 'categoria':
                productos = Producto.objects.filter(categoria=single_id)
                precios = Precio.objects.filter(id_producto__in=productos).order_by('fecha_actualizacion')
                precios_por_mes = defaultdict(list)
                for p in precios:
                    mes = p.fecha_actualizacion.strftime('%Y-%m')
                    precios_por_mes[mes].append(float(p.precio))
                serie_labels = sorted(precios_por_mes.keys())
                serie_data = [sum(precios_por_mes[mes]) / len(precios_por_mes[mes]) for mes in serie_labels]
            elif tipo == 'supermercado':
                precios = Precio.objects.filter(id_supermercado=single_id).order_by('fecha_actualizacion')
                precios_por_mes = defaultdict(list)
                for p in precios:
                    mes = p.fecha_actualizacion.strftime('%Y-%m')
                    precios_por_mes[mes].append(float(p.precio))
                serie_labels = sorted(precios_por_mes.keys())
                serie_data = [sum(precios_por_mes[mes]) / len(precios_por_mes[mes]) for mes in serie_labels]
            data[single_id] = {'labels': serie_labels, 'data': serie_data}
            labels.update(serie_labels)
        # Unificar todos los labels (meses) para la gráfica
        labels = sorted(labels)
        return JsonResponse({'labels': labels, 'series': data})
    else:
        # Modo simple (uno solo, retrocompatible)
        if tipo == 'producto' and id:
            precios = Precio.objects.filter(id_producto=id).order_by('fecha_actualizacion')
            precios_por_mes = defaultdict(list)
            for p in precios:
                mes = p.fecha_actualizacion.strftime('%Y-%m')
                precios_por_mes[mes].append(float(p.precio))
            labels = sorted(precios_por_mes.keys())
            data = [sum(precios_por_mes[mes]) / len(precios_por_mes[mes]) for mes in labels]
            return JsonResponse({'labels': labels, 'data': data})
        elif tipo == 'categoria' and id:
            productos = Producto.objects.filter(categoria=id)
            precios = Precio.objects.filter(id_producto__in=productos).order_by('fecha_actualizacion')
            precios_por_mes = defaultdict(list)
            for p in precios:
                mes = p.fecha_actualizacion.strftime('%Y-%m')
                precios_por_mes[mes].append(float(p.precio))
            labels = sorted(precios_por_mes.keys())
            data = [sum(precios_por_mes[mes]) / len(precios_por_mes[mes]) for mes in labels]
            return JsonResponse({'labels': labels, 'data': data})
        elif tipo == 'supermercado' and id:
            precios = Precio.objects.filter(id_supermercado=id).order_by('fecha_actualizacion')
            precios_por_mes = defaultdict(list)
            for p in precios:
                mes = p.fecha_actualizacion.strftime('%Y-%m')
                precios_por_mes[mes].append(float(p.precio))
            labels = sorted(precios_por_mes.keys())
            data = [sum(precios_por_mes[mes]) / len(precios_por_mes[mes]) for mes in labels]
            return JsonResponse({'labels': labels, 'data': data})
    return JsonResponse({'labels': [], 'data': []})
