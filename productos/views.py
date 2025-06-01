from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Producto, Supermercado, Precio

def producto_list(request):
    # Get filter parameters
    categoria = request.GET.get('categoria')
    supermercado_id = request.GET.get('supermercado')
    search_query = request.GET.get('search', '')
    order_by = request.GET.get('order_by', 'nombre')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    # Get multiple selections for filters (from sidebar)
    supermercados_ids = request.GET.get('supermercados', '').split(',') if request.GET.get('supermercados') else []
    categorias_list = request.GET.get('categorias', '').split(',') if request.GET.get('categorias') else []
    
    # Clean empty values
    supermercados_ids = [id for id in supermercados_ids if id.strip()]
    categorias_list = [cat for cat in categorias_list if cat.strip()]
    
    # Base queryset with price annotations
    productos = Producto.objects.all()
    
    # Apply filters
    if categoria and categoria != 'todas':
        productos = productos.filter(categoria=categoria)
    
    # Apply multiple category filter if available
    if categorias_list:
        productos = productos.filter(categoria__in=categorias_list)
    
    if search_query:
        productos = productos.filter(nombre__icontains=search_query)
        
    # Filter by price range (requires joining with Precio)
    if supermercado_id:
        productos = productos.filter(precios__id_supermercado=supermercado_id)
        
    # Apply multiple supermarket filter if available
    if supermercados_ids:
        productos = productos.filter(precios__id_supermercado__in=supermercados_ids)
        
    if precio_min:
        productos = productos.filter(precios__precio__gte=float(precio_min))
    
    if precio_max:
        productos = productos.filter(precios__precio__lte=float(precio_max))
    
    # Remove duplicates that might occur due to multiple price entries
    productos = productos.distinct()
    
    # Apply ordering
    if order_by == 'precio_asc':
        productos = productos.annotate(min_precio=Min('precios__precio')).order_by('min_precio')
    elif order_by == 'precio_desc':
        productos = productos.annotate(max_precio=Max('precios__precio')).order_by('-max_precio')
    elif order_by == 'nombre_desc':
        productos = productos.order_by('-nombre')
    else:  # Default to name ascending
        productos = productos.order_by('nombre')
      # Get filters data
    supermercados = Supermercado.objects.all().order_by('nombre')
    categorias = Producto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
    
    # Price range for filters
    precio_global_min = Precio.objects.all().aggregate(Min('precio'))['precio__min']
    precio_global_max = Precio.objects.all().aggregate(Max('precio'))['precio__max']
    
    # Setup pagination
    items_per_page = 12
    paginator = Paginator(productos, items_per_page)
    page = request.GET.get('page', 1)
    
    try:
        productos_page = paginator.page(page)
    except PageNotAnInteger:
        productos_page = paginator.page(1)
    except EmptyPage:
        productos_page = paginator.page(paginator.num_pages)
    
    # AJAX request for "Load More" button
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Check if partial parameter is present (for Load More)
        if request.GET.get('partial') == 'true':
            # Render only the product items for AJAX response
            html = render_to_string(
                'productos/product_list_items.html',
                {'productos': productos_page.object_list, 'request': request}
            )
            
            return JsonResponse({
                'html': html,
                'has_next': productos_page.has_next(),
                'next_page': productos_page.next_page_number() if productos_page.has_next() else None,
                'current_page': productos_page.number,
                'total_pages': paginator.num_pages,
                'total_products': paginator.count
            })
    
    # Initial page load or regular navigation
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
    
    return render(request, 'productos/detalleProductos.html', context)