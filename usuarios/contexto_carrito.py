from carrito.models import CarritoActivoUsuario
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

def carrito_context(request):
    """Context processor para obtener el carrito activo del usuario (propio o compartido)"""
    context = {
        'carrito_activo': None,
    }
    
    if request.user.is_authenticated:
        try:
            # Buscar el carrito activo usando la tabla CarritoActivoUsuario
            carrito_activo_obj = CarritoActivoUsuario.objects.filter(usuario=request.user).select_related('carrito').first()
            context['carrito_activo'] = carrito_activo_obj.carrito if carrito_activo_obj else None
        except Exception as e:
            logger.error(f"Error al obtener carrito activo: {e}")
    
    return context