from carrito.models import Carrito
import logging

logger = logging.getLogger(__name__)

def carrito_context(request):
    """Context processor para obtener el carrito activo del usuario"""
    context = {
        'carrito_activo': None,
    }
    
    if request.user.is_authenticated:
        try:
            # Intenta obtener el carrito activo - con logging para debug
            carrito_activo = Carrito.objects.get(usuario=request.user, activo=True)
            context['carrito_activo'] = carrito_activo
            logger.debug(f"Carrito activo encontrado: ID {carrito_activo.id_carrito}, Nombre: {carrito_activo.nombre_display}")
        except Carrito.DoesNotExist:
            logger.debug(f"No se encontró carrito activo para el usuario {request.user.username}")
            # NO crear carrito automáticamente
        except Carrito.MultipleObjectsReturned:
            # Si hay múltiples carritos activos, tomar el primero
            carrito_activo = Carrito.objects.filter(usuario=request.user, activo=True).first()
            context['carrito_activo'] = carrito_activo
            logger.debug(f"Múltiples carritos activos encontrados, usando el ID {carrito_activo.id_carrito}")
    
    return context