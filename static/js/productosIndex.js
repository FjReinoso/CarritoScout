document.addEventListener('DOMContentLoaded', function() {
    // ===============================
    // CONFIGURACIÓN DEL SIDEBAR
    // ===============================
    const filterBtn = document.getElementById('filter-btn');
    const sidebar = document.getElementById('sidebar');
    const closeSidebarBtn = document.getElementById('close-sidebar');
    const sidebarBackdrop = document.getElementById('sidebar-backdrop');
    const contentWrapper = document.getElementById('content-wrapper');
    
    function openSidebar() {
        sidebar.classList.add('show');
        sidebarBackdrop.classList.add('show');
        if (window.innerWidth >= 992) {
            contentWrapper.classList.add('shifted');
        }
    }
    
    function closeSidebar() {
        sidebar.classList.remove('show');
        sidebarBackdrop.classList.remove('show');
        contentWrapper.classList.remove('shifted');
    }
    
    filterBtn.addEventListener('click', openSidebar);
    closeSidebarBtn.addEventListener('click', closeSidebar);
    sidebarBackdrop.addEventListener('click', closeSidebar);
    
    // ===============================
    // GESTIÓN DE FILTROS
    // ===============================
    let selectedSupermarkets = [];
    let selectedCategories = [];
    
    // Inicializar filtros desde la URL
    function initializeFilters() {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('supermercados')) {
            const supermarketIds = urlParams.get('supermercados').split(',');
            supermarketIds.forEach(id => {
                const card = document.querySelector(`.supermarket-filter[data-id="${id}"]`);
                if (card) {
                    card.classList.add('selected');
                    selectedSupermarkets.push({
                        id: id,
                        name: card.getAttribute('data-name')
                    });
                }
            });
        }
        if (urlParams.has('categorias')) {
            const categories = urlParams.get('categorias').split(',');
            categories.forEach(category => {
                const card = document.querySelector(`.category-filter[data-category="${category}"]`);
                if (card) {
                    card.classList.add('selected');
                    selectedCategories.push(category);
                }
            });
        }
        updateHiddenFields();
        updateActiveFilters();
        if (selectedSupermarkets.length > 0 || selectedCategories.length > 0 || 
            urlParams.has('search') || urlParams.has('precio_min') || 
            urlParams.has('precio_max') || urlParams.has('order_by')) {
            filterBtn.classList.add('btn-danger');
        }
    }
    
    document.querySelectorAll('.supermarket-filter').forEach(card => {
        card.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const name = this.getAttribute('data-name');
            if (this.classList.contains('selected')) {
                this.classList.remove('selected');
                selectedSupermarkets = selectedSupermarkets.filter(sm => String(sm.id) !== String(id));
            } else {
                this.classList.add('selected');
                if (!selectedSupermarkets.some(sm => String(sm.id) === String(id))) {
                    selectedSupermarkets.push({ id: String(id), name });
                }
            }
            updateHiddenFields();
            updateActiveFilters();
        });
    });
    
    document.querySelectorAll('.category-filter').forEach(card => {
        card.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            if (this.classList.contains('selected')) {
                this.classList.remove('selected');
                selectedCategories = selectedCategories.filter(cat => cat !== category);
            } else {
                this.classList.add('selected');
                selectedCategories.push(category);
            }
            updateHiddenFields();
            updateActiveFilters();
        });
    });
    
    document.getElementById('apply-filters').addEventListener('click', function() {
        document.getElementById('filter-form').submit();
        closeSidebar();
    });
    
    function updateHiddenFields() {
        // Filtrar valores vacíos o nulos para evitar 'null' en la query
        document.getElementById('selected-supermarkets').value = selectedSupermarkets
            .map(sm => String(sm.id))
            .filter(id => id && id !== 'null' && id !== 'undefined')
            .join(',');
        document.getElementById('selected-categories').value = selectedCategories
            .filter(cat => cat && cat !== 'null' && cat !== 'undefined')
            .join(',');
    }
    
    function updateActiveFilters() {
        const filterBadges = document.getElementById('filter-badges');
        filterBadges.innerHTML = '';
        selectedSupermarkets.forEach(sm => {
            filterBadges.innerHTML += `
                <span class="badge bg-primary d-flex align-items-center" data-type="supermarket" data-id="${sm.id}">
                    ${sm.name}
                    <button type="button" class="btn-close btn-close-white ms-2" aria-label="Remove"></button>
                </span>
            `;
        });
        selectedCategories.forEach(category => {
            filterBadges.innerHTML += `
                <span class="badge bg-info d-flex align-items-center" data-type="category" data-category="${category}">
                    ${category}
                    <button type="button" class="btn-close btn-close-white ms-2" aria-label="Remove"></button>
                </span>
            `;
        });
        document.getElementById('active-filters').style.display = 
            (selectedSupermarkets.length > 0 || selectedCategories.length > 0) ? 'block' : 'none';
        document.querySelectorAll('#filter-badges .btn-close').forEach(btn => {
            btn.addEventListener('click', function(e) {
                const badge = e.target.parentElement;
                const type = badge.getAttribute('data-type');
                if (type === 'supermarket') {
                    const id = badge.getAttribute('data-id');
                    const card = document.querySelector(`.supermarket-filter[data-id="${id}"]`);
                    if (card) card.classList.remove('selected');
                    selectedSupermarkets = selectedSupermarkets.filter(sm => String(sm.id) !== String(id));
                } else if (type === 'category') {
                    const category = badge.getAttribute('data-category');
                    const card = document.querySelector(`.category-filter[data-category="${category}"]`);
                    if (card) card.classList.remove('selected');
                    selectedCategories = selectedCategories.filter(cat => cat !== category);
                }
                updateHiddenFields();
                updateActiveFilters();
            });
        });
    }
    
    document.getElementById('clear-all-filters').addEventListener('click', function() {
        document.querySelectorAll('.filter-card.selected').forEach(card => {
            card.classList.remove('selected');
        });
        selectedSupermarkets = [];
        selectedCategories = [];
        updateHiddenFields();
        updateActiveFilters();
        document.getElementById('search').value = '';
        document.getElementById('precio_min').value = '';
        document.getElementById('precio_max').value = '';
        document.getElementById('order_by').selectedIndex = 0;
    });
    
    document.getElementById('search-btn').addEventListener('click', function() {
        document.getElementById('filter-form').submit();
        closeSidebar();
    });
    
    initializeFilters();
    
    // ===============================
    // BOTÓN "CARGAR MÁS" PRODUCTOS
    // ===============================
    let loading = false;
    
    const updatePaginationInfo = function(data) {
        const paginationInfo = document.querySelector('.pagination-info');
        if (paginationInfo && data.total_products) {
            const currentProductsCount = document.querySelectorAll('#productos-container .col').length;
            const pageInfo = data.total_pages > 1 ? ` (Página ${data.current_page} de ${data.total_pages})` : '';
            paginationInfo.innerHTML = `
                <small>
                    Mostrando ${currentProductsCount} de ${data.total_products} productos${pageInfo}
                </small>
            `;
        }
    };

    const loadMoreProducts = function() {
        const hasMore = document.getElementById('has-more').value === 'true';
        if (loading || !hasMore) return;

        const currentPage = parseInt(document.getElementById('current-page').value);
        const nextPage = currentPage + 1;

        const params = [];

        const supermarkets = document.getElementById('selected-supermarkets')?.value;
        if (supermarkets) params.push('supermercados=' + encodeURIComponent(supermarkets));

        const categories = document.getElementById('selected-categories')?.value;
        if (categories) {
            const encodedCategories = categories.split(',').map(cat => encodeURIComponent(cat)).join(',');
            params.push('categorias=' + encodedCategories);
        }

        const search = document.getElementById('search')?.value;
        if (search) params.push('search=' + encodeURIComponent(search));

        const precioMin = document.getElementById('precio_min')?.value;
        if (precioMin) params.push('precio_min=' + encodeURIComponent(precioMin));

        const precioMax = document.getElementById('precio_max')?.value;
        if (precioMax) params.push('precio_max=' + encodeURIComponent(precioMax));

        const orderBy = document.getElementById('order_by')?.value;
        if (orderBy) params.push('order_by=' + encodeURIComponent(orderBy));

        params.push('page=' + nextPage);
        params.push('partial=true');

        const finalUrl = '/productos/?' + params.join('&');

        console.log('Fetching next page from URL:', finalUrl);

        loading = true;
        const loadMoreBtn = document.getElementById('load-more-btn');
        const loadingIndicator = document.getElementById('loading-indicator');

        if (loadMoreBtn) {
            loadMoreBtn.disabled = true;
            loadMoreBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Cargando...';
        }
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }

        fetch(finalUrl, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.html) {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = data.html;
                const newProducts = tempDiv.querySelectorAll('.col');
                newProducts.forEach(product => {
                    const productCard = product.querySelector('.product-card');
                    if (productCard) {
                        productCard.classList.add('newly-loaded');
                    }
                });
                document.getElementById('productos-container').insertAdjacentHTML('beforeend', tempDiv.innerHTML);
                document.getElementById('current-page').value = nextPage;
                document.getElementById('has-more').value = data.has_next;
                updatePaginationInfo(data);
                if (loadMoreBtn) {
                    if (data.has_next) {
                        loadMoreBtn.disabled = false;
                        loadMoreBtn.innerHTML = '<i class="fas fa-plus me-2"></i>Cargar Más Productos';
                    } else {
                        loadMoreBtn.style.display = 'none';
                        const noMoreMsg = document.createElement('div');
                        noMoreMsg.className = 'all-products-loaded';
                        noMoreMsg.innerHTML = '<i class="fas fa-check-circle"></i>Todos los productos han sido cargados';
                        loadMoreBtn.parentElement.appendChild(noMoreMsg);
                    }
                }
            } else {
                console.error('Formato de respuesta incorrecto:', data);
                document.getElementById('has-more').value = 'false';
            }
        })
        .catch(error => {
            console.error('Error al cargar más productos:', error);
            const container = document.getElementById('productos-container');
            container.insertAdjacentHTML('beforeend', 
                `<div class="col-12 text-center mt-3">
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error al cargar más productos. Por favor, intenta recargar la página.
                    </div>
                </div>`
            );
            if (loadMoreBtn) {
                loadMoreBtn.disabled = false;
                loadMoreBtn.innerHTML = '<i class="fas fa-redo me-2"></i>Reintentar';
            }
        })
        .finally(() => {
            loading = false;
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        });
    };

    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreProducts);
    }

    // ===============================
    // FUNCIONALIDAD AGREGAR AL CARRITO
    // ===============================
    
    // Función para obtener el token CSRF
    function getCsrfToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        // Buscar en las cookies si no está en un input
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return '';
    }

    // Función para mostrar notificaciones
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-toast`;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-${getIconForType(type)} me-2"></i>
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
        }, 4000);
    }

    function getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'x-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Función para actualizar el badge del carrito en la navbar
    function updateCartBadge(count) {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    }

    // Función para actualizar el nombre del carrito en la navbar
    function updateCartName(name) {
        const cartNameEl = document.getElementById('cart-name');
        if (cartNameEl) {
            cartNameEl.textContent = name || 'Sin carrito';
        }
    }

    // Función principal para agregar productos al carrito
    async function addToCart(productId, productName, button) {
        // Verificar si el usuario está autenticado
        if (!document.querySelector('[name=csrfmiddlewaretoken]') && !getCsrfToken()) {
            showNotification('Debes iniciar sesión para agregar productos al carrito', 'warning');
            return;
        }

        // Mostrar estado de carga en el botón
        const originalContent = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Agregando...';

        try {
            const response = await fetch('/carrito/agregar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: `producto_id=${productId}&cantidad=1`
            });

            const data = await response.json();            if (data.status === 'success') {
                // Mostrar una notificación adaptada si se creó un carrito automáticamente
                showNotification(data.message, 'success');
                
                // Actualizar el badge del carrito
                updateCartBadge(data.cart_count);
                
                // Actualizar el nombre del carrito si se proporcionó
                if (data.cart_name) {
                    updateCartName(data.cart_name);
                }
                
                // Cambiar temporalmente el botón a "Agregado"
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
                showNotification(data.message || 'Error al agregar el producto', 'danger');
                button.innerHTML = originalContent;
                button.disabled = false;
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error de conexión. Intenta nuevamente.', 'danger');
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    }

    // Event listeners para todos los botones "Agregar al carrito"
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            
            if (!productId) {
                showNotification('Error: ID de producto no encontrado', 'danger');
                return;
            }
            
            addToCart(productId, productName, this);
        });
    });
});