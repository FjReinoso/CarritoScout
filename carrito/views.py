from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import F, Sum, Count
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Carrito, CarritoProducto, HistorialCarrito, InvitacionCarrito
from productos.models import Producto
@login_required
@require_POST
def crear_carrito(request):
    """Vista para crear un nuevo carrito vía AJAX desde el modal"""
    try:
        nombre = request.POST.get('nombre', '').strip()
        activo = request.POST.get('activo') == 'true'
        
        # Si el usuario quiere establecer este carrito como activo,
        # desactivar todos los demás carritos del usuario
        if activo:
            Carrito.objects.filter(usuario=request.user, activo=True).update(activo=False)
        
        # Crear el nuevo carrito
        carrito = Carrito.objects.create(
            usuario=request.user,
            nombre=nombre if nombre else None,
            activo=activo,
            fecha_creacion=timezone.now()
        )
        
        # Preparar el mensaje
        mensaje = f"Carrito #{carrito.id_carrito} creado exitosamente"
        if nombre:
            mensaje = f"Carrito '{nombre}' creado exitosamente"
        
        return JsonResponse({
            'status': 'success',
            'message': mensaje,
            'carrito_id': carrito.id_carrito,
            'redirect_url': reverse('carrito:ver_carrito') if activo else None
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al crear el carrito. Inténtalo de nuevo.'
        })
    
@login_required
def ver_carrito(request):
    """Vista principal del carrito"""
    # Buscar el carrito activo del usuario
    carrito = Carrito.objects.filter(usuario=request.user, activo=True).first()
    
    # Obtener todos los carritos del usuario
    todos_carritos = Carrito.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    # Si no hay carrito activo, usar variables por defecto
    if not carrito:
        context = {
            'carrito': None,
            'items': [],
            'todos_carritos': todos_carritos,
            'total_carritos': todos_carritos.count(),
            'carritos_compartidos': 0,
        }
        return render(request, 'carrito/carrito.html', context)
    
    # Si hay carrito, continuar con la lógica normal
    items = CarritoProducto.objects.filter(carrito=carrito).select_related('producto')
    
    # Estadísticas
    carritos_compartidos = Carrito.objects.filter(
        usuarios_compartidos=request.user
    ).count()
    
    context = {
        'carrito': carrito,
        'items': items,
        'todos_carritos': todos_carritos,
        'total_carritos': todos_carritos.count(),
        'carritos_compartidos': carritos_compartidos,
    }
    
    return render(request, 'carrito/carrito.html', context)
@login_required
@require_POST
def activar_carrito(request):
    """Vista para activar un carrito específico"""
    try:
        carrito_id = request.POST.get('carrito_id')
        
        if not carrito_id:
            return JsonResponse({
                'status': 'error',
                'message': 'ID de carrito no proporcionado'
            })
        
        # Verificar que el carrito existe y pertenece al usuario
        carrito = get_object_or_404(Carrito, id_carrito=carrito_id, usuario=request.user)
        
        # Desactivar todos los carritos del usuario
        Carrito.objects.filter(usuario=request.user, activo=True).update(activo=False)
        
        # Activar el carrito seleccionado
        carrito.activo = True
        carrito.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Carrito {carrito.nombre_display} activado correctamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al activar el carrito. Inténtalo de nuevo.'
        })

@login_required
@require_POST
def eliminar_carrito(request):
    """Vista para eliminar un carrito específico"""
    try:
        carrito_id = request.POST.get('carrito_id')
        
        if not carrito_id:
            return JsonResponse({
                'status': 'error',
                'message': 'ID de carrito no proporcionado'
            })
        
        # Verificar que el carrito existe y pertenece al usuario
        carrito = get_object_or_404(Carrito, id_carrito=carrito_id, usuario=request.user)
        
        # No permitir eliminar el carrito activo si es el único
        if carrito.activo:
            otros_carritos = Carrito.objects.filter(usuario=request.user).exclude(id_carrito=carrito_id)
            if not otros_carritos.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'No puedes eliminar tu único carrito. Crea otro carrito primero.'
                })
        
        carrito_nombre = carrito.nombre_display
        was_active = carrito.activo
        carrito.delete()
        
        # Si era el carrito activo, activar otro carrito
        if was_active:
            otro_carrito = Carrito.objects.filter(usuario=request.user).first()
            if otro_carrito:
                otro_carrito.activo = True
                otro_carrito.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Carrito {carrito_nombre} eliminado correctamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al eliminar el carrito. Inténtalo de nuevo.'
        })

@login_required
@require_POST
def agregar_al_carrito(request):
    """Vista para agregar productos al carrito vía AJAX"""
    producto_id = request.POST.get('producto_id')
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad <= 0:
        return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser mayor que cero'}, status=400)
    
    producto = get_object_or_404(Producto, id_producto=producto_id)
    
    # Obtener o crear carrito activo
    carrito, created = Carrito.objects.get_or_create(
        usuario=request.user, 
        activo=True, 
        defaults={'fecha_creacion': timezone.now()}
    )
    
    # Verificar si el producto ya está en el carrito
    carrito_producto, created = CarritoProducto.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': cantidad}
    )
    
    # Si ya existía, incrementar la cantidad
    if not created:
        carrito_producto.cantidad = F('cantidad') + cantidad
        carrito_producto.save()
    
    # Obtener los datos actualizados del carrito
    carrito.refresh_from_db()
    
    return JsonResponse({
        'status': 'success',
        'message': f'{producto.nombre} añadido al carrito',
        'cart_count': carrito.total_productos,
        'cart_total': carrito.precio_total
    })

@login_required
@require_POST
def actualizar_cantidad(request):
    """Vista para actualizar la cantidad de un producto en el carrito"""
    item_id = request.POST.get('item_id')
    nueva_cantidad = int(request.POST.get('cantidad', 1))
    
    if nueva_cantidad <= 0:
        return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser mayor que cero'}, status=400)
    
    # Obtener el item del carrito
    item = get_object_or_404(CarritoProducto, id=item_id, carrito__usuario=request.user)
    
    # Actualizar cantidad
    item.cantidad = nueva_cantidad
    item.save()
    
    carrito = item.carrito
    
    return JsonResponse({
        'status': 'success',
        'message': 'Cantidad actualizada',
        'cart_count': carrito.total_productos,
        'cart_total': carrito.precio_total,
        'item_subtotal': item.subtotal
    })

@login_required
@require_POST
def eliminar_del_carrito(request):
    """Vista para eliminar un producto del carrito"""
    item_id = request.POST.get('item_id')
    
    # Obtener el item del carrito
    item = get_object_or_404(CarritoProducto, id=item_id, carrito__usuario=request.user)
    carrito = item.carrito
    producto_nombre = item.producto.nombre
    
    # Eliminar el producto
    item.delete()
    
    # Refrescar datos del carrito
    carrito.refresh_from_db()
    
    return JsonResponse({
        'status': 'success',
        'message': f'{producto_nombre} eliminado del carrito',
        'cart_count': carrito.total_productos,
        'cart_total': carrito.precio_total
    })

@login_required
@require_POST
def vaciar_carrito(request):
    """Vista para vaciar completamente el carrito"""
    carrito = get_object_or_404(Carrito, usuario=request.user, activo=True)
    
    # Eliminar todos los productos del carrito
    carrito.items.all().delete()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Carrito vaciado',
        'cart_count': 0,
        'cart_total': 0
    })

@login_required
def finalizar_carrito(request):
    """Vista para finalizar un carrito y guardarlo como historial"""
    carrito = get_object_or_404(Carrito, usuario=request.user, activo=True)
    
    # Verificar que el carrito no esté vacío
    if carrito.items_count == 0:
        messages.error(request, "No puede finalizar un carrito vacío")
        return redirect('carrito:ver_carrito')
    
    with transaction.atomic():
        # Crear el historial del carrito
        historial = HistorialCarrito.objects.create(
            carrito=carrito,
            usuario=request.user,
            costo_total=carrito.precio_total,
            fecha_finalizacion=timezone.now()
        )
        
        # Desactivar el carrito actual
        carrito.activo = False
        carrito.save()
        
        # Crear un nuevo carrito activo para futuras compras
        Carrito.objects.create(
            usuario=request.user,
            fecha_creacion=timezone.now(),
            activo=True
        )
    
    messages.success(request, "¡Carrito finalizado con éxito! El historial ha sido guardado.")
    return redirect('carrito:historial')

@login_required
def historial_carritos(request):
    """Vista para mostrar el historial de carritos del usuario"""
    historiales = HistorialCarrito.objects.filter(
        usuario=request.user
    ).select_related('carrito').order_by('-fecha_finalizacion')
    
    context = {
        'historiales': historiales
    }
    
    return render(request, 'carrito/historial.html', context)

@login_required
def detalle_historial(request, historial_id):
    """Vista para ver el detalle de un carrito del historial"""
    historial = get_object_or_404(
        HistorialCarrito, 
        id_historial_carrito=historial_id, 
        usuario=request.user
    )
    
    items = CarritoProducto.objects.filter(
        carrito=historial.carrito
    ).select_related('producto')
    
    context = {
        'historial': historial,
        'items': items
    }
    
    return render(request, 'carrito/detalle_historial.html', context)
@login_required
@require_POST
def invitar_usuario(request):
    """Vista para invitar un usuario a un carrito"""
    try:
        email = request.POST.get('email', '').strip()
        carrito_id = request.POST.get('carrito_id')
        
        if not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Por favor ingresa un email válido'
            })
        
        # Verificar que el carrito existe y pertenece al usuario
        carrito = get_object_or_404(Carrito, id_carrito=carrito_id, usuario=request.user)
        
        # Buscar el usuario por email
        try:
            usuario_invitado = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'No se encontró un usuario con ese email'
            })
        
        # Verificar que no sea el mismo usuario
        if usuario_invitado == request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'No puedes invitarte a ti mismo'
            })
        
        # Verificar que no esté ya invitado
        if InvitacionCarrito.objects.filter(carrito=carrito, usuario=usuario_invitado).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Este usuario ya tiene una invitación pendiente o ya está en el carrito'
            })
        
        # Crear la invitación
        invitacion = InvitacionCarrito.objects.create(
            carrito=carrito,
            usuario=usuario_invitado,
            fecha_invitacion=timezone.now()
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Usuario {email} invitado correctamente',
            'user_name': usuario_invitado.username,
            'user_email': email
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al enviar la invitación. Inténtalo de nuevo.'
        })

@login_required
@require_POST
def responder_invitacion(request):
    """Vista para aceptar o rechazar una invitación a carrito"""
    try:
        invitacion_id = request.POST.get('invitacion_id')
        accion = request.POST.get('accion')  # 'aceptar' o 'rechazar'
        
        invitacion = get_object_or_404(
            InvitacionCarrito, 
            id=invitacion_id, 
            usuario=request.user,
            estado='pendiente'
        )
        
        if accion == 'aceptar':
            invitacion.estado = 'aceptada'
            invitacion.fecha_respuesta = timezone.now()
            invitacion.save()
            
            # Agregar el usuario al carrito compartido
            invitacion.carrito.usuarios_compartidos.add(request.user)
            
            mensaje = f'Te has unido al carrito #{invitacion.carrito.id_carrito}'
            
        elif accion == 'rechazar':
            invitacion.estado = 'rechazada'
            invitacion.fecha_respuesta = timezone.now()
            invitacion.save()
            
            mensaje = 'Invitación rechazada'
            
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Acción no válida'
            })
        
        return JsonResponse({
            'status': 'success',
            'message': mensaje
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al procesar la invitación'
        })