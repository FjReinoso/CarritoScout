# productos/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Producto, Supermercado, Precio

def producto_list(request):
    # Obtener parámetros de filtro
    categoria = request.GET.get('categoria')
    supermercado_id = request.GET.get('supermercado')
    search_query = request.GET.get('search', '')
    order_by = request.GET.get('order_by', 'nombre')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    # Obtener selecciones múltiples para filtros (desde sidebar)
    supermercados_ids = request.GET.get('supermercados', '').split(',') if request.GET.get('supermercados') else []
    categorias_list = request.GET.get('categorias', '').split(',') if request.GET.get('categorias') else []
    
    # Limpiar valores vacíos
    supermercados_ids = [id for id in supermercados_ids if id.strip()]
    categorias_list = [cat for cat in categorias_list if cat.strip()]
    
    # QuerySet base - usar prefetch_related para optimizar
    productos = Producto.objects.prefetch_related('precios__id_supermercado')
    
    # Aplicar filtros
    if categoria and categoria != 'todas':
        productos = productos.filter(categoria=categoria)
    
    # Aplicar filtro de categorías múltiples si está disponible
    if categorias_list:
        productos = productos.filter(categoria__in=categorias_list)
    
    if search_query:
        productos = productos.filter(nombre__icontains=search_query)
        
    # Filtrar por supermercado específico
    if supermercado_id:
        productos = productos.filter(precios__id_supermercado=supermercado_id)
        
    # Aplicar filtro de supermercados múltiples si está disponible
    if supermercados_ids:
        productos = productos.filter(precios__id_supermercado__in=supermercados_ids)
        
    # Filtrar por rango de precios
    if precio_min:
        try:
            productos = productos.filter(precios__precio__gte=float(precio_min))
        except ValueError:
            pass
    
    if precio_max:
        try:
            productos = productos.filter(precios__precio__lte=float(precio_max))
        except ValueError:
            pass
            
    # Eliminar duplicados que pueden ocurrir debido a múltiples entradas de precios
    productos = productos.distinct()
    
    # Aplicar ordenamiento
    if order_by == 'precio_asc':
        productos = productos.annotate(min_precio=Min('precios__precio')).order_by('min_precio')
    elif order_by == 'precio_desc':
        productos = productos.annotate(max_precio=Max('precios__precio')).order_by('-max_precio')
    elif order_by == 'nombre_desc':
        productos = productos.order_by('-nombre')
    else:  # Por defecto ordenar por nombre ascendente
        productos = productos.order_by('nombre')
        
    # Obtener datos de filtros
    supermercados = Supermercado.objects.all().order_by('nombre')
    categorias = Producto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
    
    # Rango de precios para filtros
    try:
        precio_global_min = Precio.objects.all().aggregate(Min('precio'))['precio__min'] or 0
        precio_global_max = Precio.objects.all().aggregate(Max('precio'))['precio__max'] or 100
    except:
        precio_global_min, precio_global_max = 0, 100
    
    # Configurar paginación
    items_per_page = 12
    paginator = Paginator(productos, items_per_page)
    page = request.GET.get('page', 1)
    
    try:
        productos_page = paginator.page(page)
    except PageNotAnInteger:
        productos_page = paginator.page(1)
    except EmptyPage:
        productos_page = paginator.page(paginator.num_pages)
    
    # Petición AJAX para botón "Cargar Más"
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Verificar si el parámetro partial está presente (para Cargar Más)
        if request.GET.get('partial') == 'true':
            # Renderizar solo los items de productos para respuesta AJAX
            html = render_to_string(
                'productos/plantillaProducto.html',
                {'productos': productos_page.object_list}
            )
            
            return JsonResponse({
                'html': html,
                'has_next': productos_page.has_next(),
                'next_page': productos_page.next_page_number() if productos_page.has_next() else None,
                'current_page': productos_page.number,
                'total_pages': paginator.num_pages,
                'total_products': paginator.count
            })
    
    # Carga inicial de página o navegación regular
    context = {
        'productos': productos_page.object_list,
        'supermercados': supermercados,
        'categorias': categorias,
        'selected_categoria': categoria,
        'selected_supermercado': supermercado_id,
        'selected_order': order_by,
        'search_query': search_query,
        'precio_min': precio_min or precio_global_min,
        'precio_max': precio_max or precio_global_max,
        'precio_global_min': precio_global_min,
        'precio_global_max': precio_global_max,
        'has_more': productos_page.has_next(),
        'current_page': productos_page.number,
        'total_pages': paginator.num_pages,
        'total_products': paginator.count,
        'page_obj': productos_page,
    }
    
    return render(request, 'productos/index.html', context)

def producto_detail(request, producto_id):
    producto = Producto.objects.get(id_producto=producto_id)
    precios = Precio.objects.filter(id_producto=producto_id).select_related('id_supermercado')
    
    context = {
        'producto': producto,
        'precios': precios,
    }
    
    return render(request, 'productos/detalleProducto.html', context)