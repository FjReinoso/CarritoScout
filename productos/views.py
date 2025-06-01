from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Min, Max
from .models import Producto, Supermercado, Precio

def producto_list(request):
    # Get filter parameters
    categoria = request.GET.get('categoria')
    supermercado_id = request.GET.get('supermercado')
    search_query = request.GET.get('search', '')
    order_by = request.GET.get('order_by', 'nombre')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    # Base queryset with price annotations
    productos = Producto.objects.all()
    
    # Apply filters
    if categoria and categoria != 'todas':
        productos = productos.filter(categoria=categoria)
    
    if search_query:
        productos = productos.filter(nombre__icontains=search_query)
        
    # Filter by price range (requires joining with Precio)
    if supermercado_id:
        productos = productos.filter(precios__id_supermercado=supermercado_id)
        
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
    
    # AJAX for infinite scroll
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        page = int(request.GET.get('page', 1))
        per_page = 12  # Number of products per request
        start = (page - 1) * per_page
        end = page * per_page
        
        productos_page = productos[start:end]
        
        # Check if there are more products
        has_next = len(productos) > end
        
        # Render only the product items for AJAX response
        html = render_to_string(
            'productos/product_list_items.html',
            {'productos': productos_page, 'request': request}
        )
        
        return JsonResponse({
            'html': html,
            'has_next': has_next,
            'next_page': page + 1 if has_next else None
        })
    
    # Initial page load - render first batch with all filters
    initial_productos = productos[:12]  # First 12 products
    
    context = {
        'productos': initial_productos,
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
        'has_more': len(productos) > 12,
        'current_page': 1,
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