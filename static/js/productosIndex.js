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
                selectedSupermarkets = selectedSupermarkets.filter(sm => sm.id !== id);
            } else {
                this.classList.add('selected');
                selectedSupermarkets.push({ id, name });
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
        document.getElementById('selected-supermarkets').value = selectedSupermarkets.map(sm => sm.id).join(',');
        document.getElementById('selected-categories').value = selectedCategories.join(',');
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
                    selectedSupermarkets = selectedSupermarkets.filter(sm => sm.id !== id);
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
});