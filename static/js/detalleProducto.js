    document.addEventListener('DOMContentLoaded', function() {
        // Funcionalidad de añadir al carrito
        const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
        addToCartButtons.forEach(button => {
            button.addEventListener('click', function() {
                const productoId = this.getAttribute('data-product-id');
                const productoName = this.getAttribute('data-product-name');
                const supermercadoId = this.getAttribute('data-supermercado-id');
                const precio = this.getAttribute('data-precio');
                
                // Cambiar estado del botón
                const originalHtml = this.innerHTML;
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Añadiendo...';
                
                // Simular llamada a API
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = originalHtml;
                    mostrarNotificacion('success', `${productoName} añadido al carrito`);
                }, 800);
                
                console.log('Añadiendo al carrito:', {
                    productoId,
                    productoName,
                    supermercadoId,
                    precio
                });
            });
        });
        
        // Función para mostrar notificaciones minimalistas
        function mostrarNotificacion(tipo, mensaje) {
            const notification = document.createElement('div');
            notification.className = `alert alert-${tipo === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
            notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: none;';
            notification.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-check-circle me-2"></i>
                    <span>${mensaje}</span>
                    <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 3000);
        }
    });