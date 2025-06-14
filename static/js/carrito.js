class CarritoManager {
    constructor() {
        this.djangoData = null;
        this.currentCartIdToDelete = null;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.loadDjangoData();
            this.setupEventListeners();
            this.setupInvitationListeners(); // Añadir listeners de invitaciones
        });
    }

    loadDjangoData() {
        const dataScript = document.getElementById('django-data');
        if (dataScript) {
            try {
                this.djangoData = JSON.parse(dataScript.textContent);
            } catch (error) {
                console.error('Error parsing Django data:', error);
                this.djangoData = {};
            }
        }
    }    setupEventListeners() {
        // Event listeners para carrito activo (solo si existe)
        if (this.djangoData.hasActiveCart) {
            this.setupCartItemListeners();
            this.setupInviteUserListeners();
            this.setupShoppingListListeners();
        }

        // Event listeners generales
        this.setupCartManagementListeners();
        this.setupModalListeners();
        this.setupCartSelectorListeners(); // Nueva funcionalidad para seleccionar carritos
    }

    setupCartItemListeners() {
        // Botones de incrementar cantidad
        document.querySelectorAll('.increase-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const itemId = e.target.dataset.itemId;
                const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
                let value = parseInt(input.value);
                input.value = value + 1;
                this.updateQuantity(itemId, input.value);
            });
        });

        // Botones de decrementar cantidad
        document.querySelectorAll('.decrease-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const itemId = e.target.dataset.itemId;
                const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
                let value = parseInt(input.value);
                if (value > 1) {
                    input.value = value - 1;
                    this.updateQuantity(itemId, input.value);
                }
            });
        });

        // Inputs de cantidad
        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', (e) => {
                const itemId = e.target.dataset.itemId;
                if (parseInt(e.target.value) < 1) {
                    e.target.value = 1;
                }
                this.updateQuantity(itemId, e.target.value);
            });
        });

        // Botones de eliminar producto
        document.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Usar currentTarget para asegurar que siempre se obtiene el item_id correcto
                const itemId = e.currentTarget.dataset.itemId;
                if (confirm('¿Estás seguro que deseas eliminar este producto del carrito?')) {
                    this.removeItem(itemId);
                }
            });
        });

        // Botón de vaciar carrito
        const vaciarBtn = document.getElementById('vaciarCarrito');
        if (vaciarBtn) {
            vaciarBtn.addEventListener('click', () => {
                if (confirm('¿Estás seguro que deseas vaciar el carrito?')) {
                    this.emptyCart();
                }
            });
        }
    }

    setupInviteUserListeners() {
        const inviteUserBtn = document.getElementById('inviteUserBtn');
        if (inviteUserBtn) {
            inviteUserBtn.addEventListener('click', () => {
                this.inviteUser();
            });
        }

        const inviteUserModal = document.getElementById('inviteUserModal');
        if (inviteUserModal) {
            inviteUserModal.addEventListener('hidden.bs.modal', () => {
                const emailInput = document.getElementById('userEmail');
                if (emailInput) emailInput.value = '';
            });
        }
    }

    setupShoppingListListeners() {
        const printBtn = document.getElementById('printShoppingList');
        if (printBtn) {
            printBtn.addEventListener('click', () => {
                this.printShoppingList();
            });
        }


        document.querySelectorAll('.shopping-list-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const parentItem = e.target.closest('.shopping-list-item');
                if (e.target.checked) {
                    parentItem.style.textDecoration = 'line-through';
                    parentItem.style.color = '#999';
                } else {
                    parentItem.style.textDecoration = 'none';
                    parentItem.style.color = '';
                }
            });
        });
    }    setupCartManagementListeners() {
        // Botones de activar carrito
        document.querySelectorAll('.activar-carrito-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const carritoId = btn.dataset.carritoId;
                
                // Confirmar la activación del carrito
                if (confirm('¿Deseas activar este carrito? El carrito activo actual se desactivará.')) {
                    this.activateCart(carritoId);
                }
            });
        });

        // Botones de eliminar carrito
        document.querySelectorAll('.eliminar-carrito-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const carritoId = btn.dataset.carritoId;
                this.showDeleteCartModal(carritoId);
            });
        });

        // Botón de crear carrito
        const createCartBtn = document.getElementById('createCartBtn');
        if (createCartBtn) {
            createCartBtn.addEventListener('click', () => {
                this.createCart();
            });
        }

        // Botón de confirmar eliminación
        const confirmDeleteBtn = document.getElementById('confirmDeleteCart');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', () => {
                this.deleteCart();
            });
        }
    }setupModalListeners() {
        const createCartModal = document.getElementById('createCartModal');
        if (createCartModal) {
            createCartModal.addEventListener('hidden.bs.modal', () => {
                document.getElementById('cartName').value = '';
                document.getElementById('setAsActive').checked = false;
            });
        }
    }    setupCartSelectorListeners() {
        // Los carritos ahora solo se activan mediante botones específicos
        // Esta función puede ser usada para futuras funcionalidades de selección visual
        document.querySelectorAll('.cart-list-item').forEach(item => {
            item.addEventListener('click', (e) => {
                // Prevenir que los clics en botones activen esta función
                if (e.target.closest('button')) {
                    return;
                }
                
                // Resaltar visualmente el carrito seleccionado (opcional)
                document.querySelectorAll('.cart-list-item').forEach(el => {
                    el.classList.remove('selected');
                });
                item.classList.add('selected');
                
                console.log('Cart selected for viewing:', item.dataset.cartId);
            });
        });
    }

    setupInvitationListeners() {
        document.querySelectorAll('.btn-aceptar-invitacion').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const invitacionId = btn.dataset.invitacionId;
                if (!invitacionId) return;
                btn.disabled = true;
                try {
                    const response = await fetch('/carrito/responder_invitacion/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': this.djangoData.csrfToken
                        },
                        body: `invitacion_id=${invitacionId}&accion=aceptar`
                    });
                    const data = await response.json();
                    if (data.status === 'success') {
                        this.showNotification(data.message, 'success');
                        btn.closest('li').remove();
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        this.showNotification(data.message, 'danger');
                        btn.disabled = false;
                    }
                } catch (error) {
                    this.showNotification('Error al aceptar la invitación', 'danger');
                    btn.disabled = false;
                }
            });
        });
        document.querySelectorAll('.btn-rechazar-invitacion').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const invitacionId = btn.dataset.invitacionId;
                if (!invitacionId) return;
                btn.disabled = true;
                try {
                    const response = await fetch('/carrito/responder_invitacion/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': this.djangoData.csrfToken
                        },
                        body: `invitacion_id=${invitacionId}&accion=rechazar`
                    });
                    const data = await response.json();
                    if (data.status === 'success') {
                        this.showNotification(data.message, 'success');
                        btn.closest('li').remove();
                    } else {
                        this.showNotification(data.message, 'danger');
                        btn.disabled = false;
                    }
                } catch (error) {
                    this.showNotification('Error al rechazar la invitación', 'danger');
                    btn.disabled = false;
                }
            });
        });
    }

    // === MÉTODOS DE API ===

    async updateQuantity(itemId, newQuantity) {
        try {
            const response = await fetch(this.djangoData.urls.updateQuantity, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.djangoData.csrfToken
                },
                body: `item_id=${itemId}&cantidad=${newQuantity}`
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.updateCartBadge(data.cart_count);
                this.updateItemDisplay(itemId, data.item_subtotal);
                this.updateCartTotals(data.cart_total, data.cart_count);
                this.showNotification('Cantidad actualizada', 'success');
            } else {
                this.showNotification(data.message, 'danger');
            }
        } catch (error) {
            this.showNotification('Error al actualizar cantidad', 'danger');
            console.error('Error:', error);
        }
    }

    async removeItem(itemId) {
        try {
            const response = await fetch(this.djangoData.urls.removeFromCart, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.djangoData.csrfToken
                },
                body: `item_id=${itemId}`
            });

            const data = await response.json();

            if (data.status === 'success') {
                const itemEl = document.getElementById(`item-${itemId}`);
                if (itemEl) itemEl.remove();

                this.updateCartBadge(data.cart_count);
                this.updateCartTotals(data.cart_total, data.cart_count);
                this.showNotification(data.message, 'success');

                if (data.cart_count == 0) {
                    location.reload();
                }
            } else {
                this.showNotification(data.message, 'danger');
            }
        } catch (error) {
            this.showNotification('Error al eliminar producto', 'danger');
            console.error('Error:', error);
        }
    }

    async emptyCart() {
        try {
            const response = await fetch(this.djangoData.urls.emptyCart, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.djangoData.csrfToken
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.updateCartBadge(data.cart_count);
                this.showNotification(data.message, 'success');
                location.reload();
            } else {
                this.showNotification(data.message, 'danger');
            }
        } catch (error) {
            this.showNotification('Error al vaciar el carrito', 'danger');
            console.error('Error:', error);
        }
    }

    async createCart() {
        const cartName = document.getElementById('cartName').value.trim();
        const setAsActive = document.getElementById('setAsActive').checked;

        const displayName = cartName || 'Nuevo carrito';
        this.showNotification(`Creando ${displayName}...`, 'info');

        try {
            const response = await fetch(this.djangoData.urls.createCart, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.djangoData.csrfToken
                },
                body: `nombre=${encodeURIComponent(cartName)}&activo=${setAsActive}`
            });

            const data = await response.json();

            if (data.status === 'success') {
                const modal = bootstrap.Modal.getInstance(document.getElementById('createCartModal'));
                modal.hide();

                this.showNotification(data.message, 'success');
                
                // Actualizar información del carrito en la navbar si se activó
                if (setAsActive && typeof updateCartInfo === 'function') {
                    updateCartInfo(data.cart_count, data.cart_name);
                }

                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    location.reload();
                }
            } else {
                this.showNotification(data.message, 'danger');
            }
        } catch (error) {
            this.showNotification('Error al crear el carrito', 'danger');
            console.error('Error:', error);
        }
    }

    async inviteUser() {
        const emailInput = document.getElementById('userEmail');
        if (!emailInput) {
            this.showNotification('No se encontró el campo de email', 'danger');
            return;
        }
        const email = emailInput.value;
        if (!email) {
            this.showNotification('Por favor ingresa el email del usuario', 'warning');
            return;
        }
        this.showNotification(`Invitando a ${email}...`, 'info');
        try {
            const response = await fetch(this.djangoData.urls.inviteUser, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.djangoData.csrfToken
                },
                body: `email=${encodeURIComponent(email)}&carrito_id=${this.djangoData.cartId}`
            });
            const data = await response.json();
            if (data.status === 'success') {
                const userBadge = document.createElement('span');
                userBadge.className = 'user-badge pending';
                userBadge.innerHTML = `
                    <i class="bi bi-person me-1"></i> ${data.user_name} (Pendiente)
                `;
                const userBadgesContainer = document.querySelector('.user-badges');
                if (userBadgesContainer) {
                    userBadgesContainer.appendChild(userBadge);
                }
                const modal = bootstrap.Modal.getInstance(document.getElementById('inviteUserModal'));
                modal.hide();
                this.showNotification(data.message, 'success');
                emailInput.value = '';
            } else {
                this.showNotification(data.message, 'danger');
            }
        } catch (error) {
            this.showNotification('Error al enviar la invitación', 'danger');
            console.error('Error:', error);
        }
    }    
    async activateCart(carritoId) {
        this.showNotification('Activando carrito...', 'info');

        try {
            const response = await fetch(this.djangoData.urls.activateCart, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.djangoData.csrfToken
                },
                body: `carrito_id=${carritoId}`
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.showNotification(data.message, 'success');
                
                // Actualizar información del carrito en la navbar
                this.updateCartName(data.cart_name);
                
                // Actualizar la interfaz local sin recargar toda la página
                this.updateCartSelection(carritoId);
                
                // Actualizar el objeto djangoData para reflejar el nuevo carrito activo
                this.djangoData.hasActiveCart = true;
                this.djangoData.cartId = carritoId;
                //Recargamos la página para reflejar los cambios
                console.log("DEBUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUG");
                window.location.reload();
            } else {
                this.showNotification(data.message, 'danger');
            }
        } catch (error) {
            this.showNotification('Error al activar el carrito', 'danger');
            console.error('Error:', error);
        }
    }

    showDeleteCartModal(carritoId) {
        this.currentCartIdToDelete = carritoId;
        const modal = new bootstrap.Modal(document.getElementById('deleteCartModal'));
        modal.show();
    }

    async deleteCart() {
        if (!this.currentCartIdToDelete) return;

        this.showNotification('Eliminando carrito...', 'info');

        try {
            const response = await fetch(this.djangoData.urls.deleteCart, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.djangoData.csrfToken
                },
                body: `carrito_id=${this.currentCartIdToDelete}`
            });

            const data = await response.json();

            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteCartModal'));
            modal.hide();

            if (data.status === 'success') {
                this.showNotification(data.message, 'success');
                location.reload();
            } else {
                this.showNotification(data.message, 'danger');
            }
        } catch (error) {
            this.showNotification('Error al eliminar carrito', 'danger');
            console.error('Error:', error);
        } finally {
            this.currentCartIdToDelete = null;
        }
    }

    // === MÉTODOS DE UI ===

    updateCartBadge(count) {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    }

    updateItemDisplay(itemId, subtotal) {
        const itemEl = document.getElementById(`item-${itemId}`);
        if (itemEl) {
            const priceEl = itemEl.querySelector('.col-md-2.text-end h5');
            if (priceEl) priceEl.textContent = subtotal + '€';
        }
    }

    updateCartTotals(cartTotal, cartCount) {
        // Actualiza el total en el resumen
        const cartTotalEl = document.querySelector('.cart-summary strong:last-child');
        if (cartTotalEl) cartTotalEl.textContent = cartTotal + '€';

        // Actualiza el número de productos en el resumen
        const resumenProductosEl = document.querySelector('.cart-summary .mb-2 span:first-child');
        if (resumenProductosEl) resumenProductosEl.textContent = `Productos (${cartCount}):`;

        // Actualiza el dinero de productos en el resumen
        const resumenProductosDineroEl = document.querySelector('.cart-summary .mb-2 span:last-child');
        if (resumenProductosDineroEl) resumenProductosDineroEl.textContent = cartTotal + '€';

        // Actualiza el número de productos en la línea superior
        const productCountEl = document.querySelector('.mb-3 strong');
        if (productCountEl) productCountEl.textContent = cartCount;        // Actualiza el precio promedio por producto en estadísticas rápidas
        // Busca el h6 que contenga 'Precio por producto' y actualiza el siguiente h3
        const estadisticasCards = document.querySelectorAll('.statistics-card');
        estadisticasCards.forEach(card => {
            const h6s = card.querySelectorAll('h6');
            h6s.forEach((h6, idx) => {
                if (h6.textContent.trim().toLowerCase().includes('precio por producto')) {
                    const h3 = card.querySelectorAll('h3')[idx];
                    if (h3) {
                        if (cartCount > 0) {
                            const promedio = (parseFloat(cartTotal) / cartCount).toFixed(2);
                            h3.textContent = `${promedio}€`;
                        } else {
                            h3.textContent = '0,00€';
                        }
                    }
                }
            });
        });
    }

    printShoppingList() {
        const printContents = document.querySelector('.shopping-list').innerHTML;
        const originalContents = document.body.innerHTML;

        const printStyles = `
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .shopping-list-header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #FF6A88; padding-bottom: 10px; }
                .shopping-list-section { margin-bottom: 15px; }
                .shopping-list-section h4 { background: linear-gradient(90deg, #FF9A8B 0%, #FF6A88 55%, #FF99AC 100%); color: white; padding: 5px 15px; border-radius: 5px; display: inline-block; font-size: 1.1rem; }
                .shopping-list-item { margin-bottom: 5px; display: flex; align-items: center; }
                .shopping-list-checkbox { margin-right: 10px; }
            </style>
        `;

        document.body.innerHTML = printStyles + '<div class="shopping-list">' + printContents + '</div>';
        window.print();
        document.body.innerHTML = originalContents;
        location.reload();
    }

    downloadShoppingList() {
        this.showNotification('Descargando lista de compra...', 'info');
        setTimeout(() => {
            this.showNotification('Lista de compra descargada', 'success');
        }, 1500);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-toast`;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-${this.getIconForType(type)} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1055;
            min-width: 300px;
            max-width: 400px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                notification.style.transition = 'opacity 0.5s ease';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 500);
            }
        }, 5000);
    }    getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'x-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Nuevo método para actualizar el nombre del carrito en la navbar
    updateCartName(name) {
        const cartNameEl = document.getElementById('cart-name');
        if (cartNameEl) {
            cartNameEl.textContent = name || 'Sin carrito';
        }
    }    // Nuevo método para actualizar la selección visual de carritos
    updateCartSelection(activeCarritoId) {
        // Remover la clase active de todos los carritos y actualizar botones
        document.querySelectorAll('.cart-list-item').forEach(item => {
            const cartId = item.dataset.cartId;
            const badge = item.querySelector('.badge');
            const activateBtn = item.querySelector('.activar-carrito-btn');
            
            if (cartId === activeCarritoId) {
                // Este es el carrito que se acaba de activar
                item.classList.add('active');
                if (badge) {
                    badge.textContent = 'Activo';
                    badge.className = 'badge bg-success rounded-pill';
                }
                // Ocultar el botón de activar y mostrar solo el badge
                if (activateBtn) {
                    activateBtn.style.display = 'none';
                }
            } else {
                // Otros carritos se vuelven inactivos
                item.classList.remove('active');
                if (badge) {
                    badge.textContent = 'Inactivo';
                    badge.className = 'badge bg-secondary rounded-pill';
                }
                // Mostrar el botón de activar
                if (activateBtn) {
                    activateBtn.style.display = 'inline-block';
                } else {
                    // Si no existe el botón, crear uno nuevo
                    const buttonContainer = item.querySelector('.d-flex.align-items-center.gap-2');
                    if (buttonContainer && !buttonContainer.querySelector('.activar-carrito-btn')) {
                        const newActivateBtn = document.createElement('button');
                        newActivateBtn.className = 'btn btn-sm btn-outline-success activar-carrito-btn';
                        newActivateBtn.dataset.carritoId = cartId;
                        newActivateBtn.title = 'Activar este carrito';
                        newActivateBtn.innerHTML = '<i class="bi bi-check-circle"></i> Activar';
                        
                        // Agregar event listener al nuevo botón
                        newActivateBtn.addEventListener('click', (e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            if (confirm('¿Deseas activar este carrito? El carrito activo actual se desactivará.')) {
                                this.activateCart(cartId);
                            }
                        });
                        
                        buttonContainer.insertBefore(newActivateBtn, badge);
                    }
                }
            }
        });
    }
}

// Inicializar la aplicación
const carritoManager = new CarritoManager();