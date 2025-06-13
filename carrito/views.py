from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import F, Sum, Count, Q
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Carrito, CarritoProducto, HistorialCarrito, InvitacionCarrito, CarritoActivoUsuario
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
        
        # Crear el nuevo carrito (NO agregar el creador a usuarios_compartidos)
        carrito = Carrito.objects.create(
            usuario=request.user,
            nombre=nombre if nombre else None,
            activo=activo,
            fecha_creacion=timezone.now()
        )

        # Si el usuario quiere este carrito como activo, actualizar la relación CarritoActivoUsuario
        if activo:
            from .models import CarritoActivoUsuario
            CarritoActivoUsuario.objects.update_or_create(
                usuario=request.user,
                defaults={'carrito': carrito, 'fecha_activacion': timezone.now()}
            )
        
        # Preparar el mensaje
        mensaje = f"Carrito #{carrito.id_carrito} creado exitosamente"
        if nombre:
            mensaje = f"Carrito '{nombre}' creado exitosamente"
        
        return JsonResponse({
            'status': 'success',
            'message': mensaje,
            'carrito_id': carrito.id_carrito,
            'cart_name': carrito.nombre_display, 
            'cart_count': carrito.total_productos,  
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
    # Buscar el carrito activo del usuario (propio o compartido)
    carrito_activo_obj = CarritoActivoUsuario.objects.filter(usuario=request.user).select_related('carrito').first()
    carrito = carrito_activo_obj.carrito if carrito_activo_obj else None
    
    # Obtener todos los carritos del usuario (propios y compartidos)
    todos_carritos = Carrito.objects.filter(
        Q(usuario=request.user) | Q(usuarios_compartidos=request.user)
    ).distinct().order_by('-fecha_creacion')
    
    # Invitaciones pendientes para el usuario
    invitaciones_pendientes = InvitacionCarrito.objects.filter(usuario=request.user, estado='pendiente').select_related('carrito', 'carrito__usuario')
    
    if not carrito:
        context = {
            'carrito': None,
            'items': [],
            'todos_carritos': todos_carritos,
            'total_carritos': todos_carritos.count(),
            'carritos_compartidos': 0,
            'invitaciones_pendientes': invitaciones_pendientes,
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
        'invitaciones_pendientes': invitaciones_pendientes,
    }
    
    return render(request, 'carrito/carrito.html', context)

@login_required
@require_POST
def activar_carrito(request):
    """Vista para activar un carrito específico (propio o compartido) para el usuario actual"""
    from django.db.models import Q
    try:
        carrito_id = request.POST.get('carrito_id')
        if not carrito_id:
            return JsonResponse({
                'status': 'error',
                'message': 'ID de carrito no proporcionado'
            })
        # Permitir activar si el usuario es dueño o compartido
        carrito = Carrito.objects.filter(
            Q(id_carrito=carrito_id) & (Q(usuario=request.user) | Q(usuarios_compartidos=request.user))
        ).first()
        if not carrito:
            return JsonResponse({
                'status': 'error',
                'message': 'No tienes permisos para activar este carrito.'
            })
        # Actualizar o crear la relación de carrito activo para este usuario
        CarritoActivoUsuario.objects.update_or_create(
            usuario=request.user,
            defaults={'carrito': carrito, 'fecha_activacion': timezone.now()}
        )
        return JsonResponse({
            'status': 'success',
            'message': f'Carrito {carrito.nombre_display} activado correctamente',
            'cart_name': carrito.nombre_display,
            'cart_count': carrito.total_productos
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
    """Vista para agregar productos al carrito activo del usuario (propio o compartido)"""
    try:
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))
        supermercado_id = request.POST.get('supermercado_id')
        precio_unitario = request.POST.get('precio_unitario')
        
        if not producto_id:
            return JsonResponse({
                'status': 'error',
                'message': 'ID de producto no proporcionado'
            }, status=400)
        
        if cantidad <= 0:
            return JsonResponse({
                'status': 'error',
                'message': 'La cantidad debe ser mayor que cero'
            }, status=400)
        
        # Verificar que el producto existe
        producto = get_object_or_404(Producto, id_producto=producto_id)
        supermercado = None
        if supermercado_id:
            from productos.models import Supermercado
            supermercado = get_object_or_404(Supermercado, id_supermercado=supermercado_id)
        
        # Si no se recibe precio_unitario, intentar obtenerlo del modelo Precio
        if precio_unitario is not None and precio_unitario != '':
            try:
                precio_unitario = float(precio_unitario)
            except ValueError:
                precio_unitario = None
        if precio_unitario is None and supermercado:
            from productos.models import Precio
            precio_obj = Precio.objects.filter(id_producto=producto, id_supermercado=supermercado).first()
            if precio_obj:
                precio_unitario = float(precio_obj.precio)
        if precio_unitario is None:
            precio_unitario = float(producto.precio) if producto.precio is not None else 0
        
        # Buscar el carrito activo del usuario (propio o compartido)
        carrito_activo_obj = CarritoActivoUsuario.objects.filter(usuario=request.user).select_related('carrito').first()
        
        if not carrito_activo_obj:
            return JsonResponse({
                'status': 'error',
                'message': 'No tienes un carrito activo para agregar productos.'
            }, status=400)
        carrito = carrito_activo_obj.carrito
        
        # Solo permitir agregar si el usuario es dueño o compartido
        if not (carrito.usuario == request.user or carrito.usuarios_compartidos.filter(id=request.user.id).exists()):
            return JsonResponse({
                'status': 'error',
                'message': 'No tienes permisos para modificar este carrito.'
            }, status=403)
        
        # Buscar si ya existe ese producto en ese supermercado en el carrito
        carrito_producto, created = CarritoProducto.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            supermercado=supermercado,
            defaults={'cantidad': cantidad, 'precio_unitario': precio_unitario}
        )
        
        # Si ya existía, incrementar la cantidad y actualizar precio si cambió
        if not created:
            carrito_producto.cantidad = F('cantidad') + cantidad
            carrito_producto.precio_unitario = precio_unitario
            carrito_producto.save()
            carrito_producto.refresh_from_db()
            mensaje = f'{producto.nombre} actualizado en el carrito (cantidad: {carrito_producto.cantidad})'
        else:
            mensaje = f'{producto.nombre} añadido al carrito'
        
        # Obtener los datos actualizados del carrito
        carrito.refresh_from_db()
        
        return JsonResponse({
            'status': 'success',
            'message': mensaje,
            'cart_count': carrito.total_productos,
            'cart_total': float(carrito.precio_total) if carrito.precio_total else 0,
            'cart_name': carrito.nombre_display
        })
        
    except ValueError:
        return JsonResponse({
            'status': 'error',
            'message': 'Cantidad inválida'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al agregar el producto al carrito'
        }, status=500)

@login_required
@require_POST
def actualizar_cantidad(request):
    """Vista para actualizar la cantidad de un producto en el carrito (dueño o compartido)"""
    item_id = request.POST.get('item_id')
    nueva_cantidad = int(request.POST.get('cantidad', 1))

    if nueva_cantidad <= 0:
        return JsonResponse({
            'status': 'error',
            'message': 'La cantidad debe ser mayor que cero.'
        }, status=400)

    # Permitir modificar si el usuario es dueño o compartido
    item = get_object_or_404(
        CarritoProducto,
        id=item_id,
        carrito__in=Carrito.objects.filter(Q(usuario=request.user) | Q(usuarios_compartidos=request.user))
    )

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
    """Vista para eliminar un producto del carrito activo del usuario (propio o compartido)"""
    try:
        item_id = request.POST.get('item_id')
        if not item_id:
            return JsonResponse({'status': 'error', 'message': 'Falta el item_id para eliminar el producto'}, status=400)
        item = get_object_or_404(CarritoProducto, id=item_id)
        carrito = item.carrito
        # Solo permitir eliminar si el carrito es el activo
        carrito_activo_obj = CarritoActivoUsuario.objects.filter(usuario=request.user).select_related('carrito').first()
        if not carrito_activo_obj or carrito_activo_obj.carrito.id_carrito != carrito.id_carrito:
            return JsonResponse({'status': 'error', 'message': 'Solo puedes eliminar productos de tu carrito activo.'}, status=403)
        if not (carrito.usuario == request.user or carrito.usuarios_compartidos.filter(id=request.user.id).exists()):
            return JsonResponse({'status': 'error', 'message': 'No tienes permisos para modificar este carrito.'}, status=403)
        producto_nombre = item.producto.nombre
        item.delete()
        carrito.refresh_from_db()
        return JsonResponse({
            'status': 'success',
            'message': f'{producto_nombre} eliminado del carrito',
            'cart_count': carrito.total_productos,
            'cart_total': float(carrito.precio_total) if carrito.precio_total else 0
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error interno: {e}'}, status=500)

@login_required
@require_POST
def vaciar_carrito(request):
    """Vista para vaciar completamente el carrito"""
    from django.db.models import Q
    # Buscar el carrito activo del usuario (propio o compartido)
    carrito_activo_obj = CarritoActivoUsuario.objects.filter(usuario=request.user).select_related('carrito').first()
    if not carrito_activo_obj:
        return JsonResponse({'status': 'error', 'message': 'No tienes un carrito activo.'}, status=400)
    carrito = carrito_activo_obj.carrito
    # Solo permitir si el usuario es dueño o compartido
    if not (carrito.usuario == request.user or carrito.usuarios_compartidos.filter(id=request.user.id).exists()):
        return JsonResponse({'status': 'error', 'message': 'No tienes permisos para modificar este carrito.'}, status=403)
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
    """Vista para invitar un usuario a un carrito y crear invitación pendiente"""
    import logging
    logger = logging.getLogger("carrito.invitar_usuario")
    try:
        email = request.POST.get('email', '').strip()
        carrito_id = request.POST.get('carrito_id')
        logger.info(f"[INVITAR] email={email}, carrito_id={carrito_id}, user={request.user}")
        if not email:
            logger.warning("[INVITAR] Email vacío")
            return JsonResponse({
                'status': 'error',
                'message': 'Por favor ingresa un email válido'
            })
        carrito = get_object_or_404(Carrito, id_carrito=carrito_id, usuario=request.user)
        logger.info(f"[INVITAR] Carrito encontrado: {carrito}")
        try:
            usuarios_invitados = User.objects.filter(email=email)
            if usuarios_invitados.count() == 0:
                logger.warning(f"[INVITAR] No existe usuario con email: {email}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'No se encontró un usuario con ese email'
                })
            if usuarios_invitados.count() > 1:
                logger.error(f"[INVITAR] Hay más de un usuario con el email: {email}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error: hay más de un usuario registrado con ese email. Contacta al administrador.'
                })
            usuario_invitado = usuarios_invitados.first()
            logger.info(f"[INVITAR] Usuario invitado encontrado: {usuario_invitado}")
        except Exception as e:
            logger.error(f"[INVITAR] Excepción inesperada al buscar usuario: {e}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': 'Error inesperado al buscar usuario. Contacta al administrador.'
            })
        if usuario_invitado == carrito.usuario:
            logger.warning(f"[INVITAR] El usuario invitado es el creador del carrito")
            return JsonResponse({
                'status': 'error',
                'message': 'No puedes invitarte a ti mismo'
            })
        if InvitacionCarrito.objects.filter(carrito=carrito, usuario=usuario_invitado, estado='pendiente').exists():
            logger.info(f"[INVITAR] Ya existe invitación pendiente para este usuario y carrito")
            return JsonResponse({
                'status': 'error',
                'message': 'Este usuario ya tiene una invitación pendiente para este carrito'
            })
        if InvitacionCarrito.objects.filter(carrito=carrito, usuario=usuario_invitado, estado='aceptada').exists() or \
           carrito.usuarios_compartidos.filter(id=usuario_invitado.id).exists():
            logger.info(f"[INVITAR] El usuario ya tiene acceso al carrito")
            return JsonResponse({
                'status': 'error',
                'message': 'Este usuario ya tiene acceso al carrito'
            })
        invitacion = InvitacionCarrito.objects.create(
            carrito=carrito,
            usuario=usuario_invitado,
            fecha_invitacion=timezone.now(),
            estado='pendiente',
            fecha_respuesta=None
        )
        logger.info(f"[INVITAR] Invitación creada correctamente: {invitacion}")
        return JsonResponse({
            'status': 'success',
            'message': f'Invitación enviada a {email}',
            'user_name': usuario_invitado.username,
            'user_email': email
        })
    except Exception as e:
        logger.error(f"[INVITAR] Excepción inesperada: {e}", exc_info=True)
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
        with transaction.atomic():
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
                # Agregar el usuario al carrito compartido (nunca el creador, y solo si no está ya)
                if request.user != invitacion.carrito.usuario and not invitacion.carrito.usuarios_compartidos.filter(id=request.user.id).exists():
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