from carrito.models import Carrito
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
            # Buscar carrito activo donde el usuario es dueño o compartido
            carrito_activo = Carrito.objects.filter(
                Q(usuario=request.user) | Q(usuarios_compartidos=request.user),
                activo=True
            ).first()
            context['carrito_activo'] = carrito_activo
            if carrito_activo:
                logger.debug(f"Carrito activo encontrado: ID {carrito_activo.id_carrito}, Nombre: {carrito_activo.nombre_display}")
            else:
                logger.debug(f"No se encontró carrito activo para el usuario {request.user.username}")
        except Exception as e:
            logger.error(f"Error al obtener carrito activo: {e}")
    
    return context