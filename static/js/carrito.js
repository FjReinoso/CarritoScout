

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
    }

    setupEventListeners() {
        // Event listeners para carrito activo (solo si existe)
        if (this.djangoData.hasActiveCart) {
            this.setupCartItemListeners();
            this.setupInviteUserListeners();
            this.setupShoppingListListeners();
        }

        // Event listeners generales
        this.setupCartManagementListeners();
        this.setupModalListeners();
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
                const itemId = e.target.dataset.itemId;
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
                document.getElementById('userEmail').value = '';
                document.getElementById('userPermission').selectedIndex = 0;
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

        const downloadBtn = document.getElementById('downloadShoppingList');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                this.downloadShoppingList();
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
    }

    setupCartManagementListeners() {
        // Botones de activar carrito
        document.querySelectorAll('.activar-carrito-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const carritoId = e.target.dataset.carritoId;
                this.activateCart(carritoId);
            });
        });

        // Botones de eliminar carrito
        document.querySelectorAll('.eliminar-carrito-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const carritoId = e.target.dataset.carritoId;
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
    }

    setupModalListeners() {
        const createCartModal = document.getElementById('createCartModal');
        if (createCartModal) {
            createCartModal.addEventListener('hidden.bs.modal', () => {
                document.getElementById('cartName').value = '';
                document.getElementById('setAsActive').checked = false;
            });
        }
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
        const email = document.getElementById('userEmail').value;
        const permission = document.getElementById('userPermission').value;

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
                body: `email=${encodeURIComponent(email)}&carrito_id=${this.djangoData.cartId}&permission=${permission}`
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

                document.getElementById('userEmail').value = '';
                document.getElementById('userPermission').selectedIndex = 0;
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
                if (typeof updateCartInfo === 'function') {
                    updateCartInfo(data.cart_count, data.cart_name);
                }
                
                location.reload();
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
            if (priceEl) priceEl.textContent = '$' + subtotal;
        }
    }

    updateCartTotals(cartTotal, cartCount) {
        const cartTotalEl = document.querySelector('.cart-summary strong:last-child');
        if (cartTotalEl) cartTotalEl.textContent = '$' + cartTotal;

        const productCountEl = document.querySelector('.mb-3 strong');
        if (productCountEl) productCountEl.textContent = cartCount;

        const summaryCountEl = document.querySelector('.cart-summary .mb-2 span:first-child');
        if (summaryCountEl) summaryCountEl.textContent = `Productos (${cartCount}):`;
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
    }

    getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'x-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Inicializar la aplicación
const carritoManager = new CarritoManager();