document.addEventListener('DOMContentLoaded', function() {
    // Obtener token CSRF
    function getCsrfToken() {
        // Obtiene el token CSRF solo del formulario oculto
        const csrfInput = document.querySelector('#csrf-form input[name="csrfmiddlewaretoken"]');
        return csrfInput ? csrfInput.value : null;
    }

    // Mostrar notificaciones
    function mostrarNotificacion(tipo, mensaje) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${tipo === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-${tipo === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 4000);
    }

    // Actualizar badge del carrito
    function updateCartBadge(count) {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    }

    // Actualizar nombre del carrito
    function updateCartName(name) {
        const cartNameEl = document.getElementById('cart-name');
        if (cartNameEl) {
            cartNameEl.textContent = name || 'Sin carrito';
        }
    }

    // Agregar producto al carrito
    async function addToCart(productId, productName, supermercadoId, precio, button) {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            mostrarNotificacion('warning', 'Debes iniciar sesión para agregar productos al carrito');
            return;
        }
        const originalContent = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Añadiendo...';
        try {
            // Construir el body con supermercado y precio si existen
            let body = `producto_id=${productId}&cantidad=1`;
            if (supermercadoId) body += `&supermercado_id=${supermercadoId}`;
            if (precio) body += `&precio_unitario=${precio}`;
            const response = await fetch('/carrito/agregar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: body
            });
            if (!response.ok) throw new Error();
            const data = await response.json();
            if (data.status === 'success') {
                mostrarNotificacion('success', data.message);
                if (data.cart_count !== undefined) updateCartBadge(data.cart_count);
                if (data.cart_name) updateCartName(data.cart_name);
                button.innerHTML = '<i class="fas fa-check me-1"></i>Agregado';
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-success');
                setTimeout(() => {
                    button.innerHTML = originalContent;
                    button.classList.remove('btn-outline-success');
                    button.classList.add('btn-success');
                    button.disabled = false;
                }, 1500);
            } else {
                mostrarNotificacion('danger', data.message || 'Error al agregar el producto');
                button.innerHTML = originalContent;
                button.disabled = false;
            }
        } catch {
            mostrarNotificacion('danger', 'Error de conexión. Intenta nuevamente.');
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    }

    // Event listeners para los botones "Agregar al carrito"
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            const supermercadoId = this.dataset.supermercadoId || null;
            const precio = this.dataset.precio || null;
            if (!productId) {
                mostrarNotificacion('danger', 'Error: ID de producto no encontrado');
                return;
            }
            addToCart(productId, productName, supermercadoId, precio, this);
        });
    });
});