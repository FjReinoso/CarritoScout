

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
        // Obtener parámetros de la URL
        const urlParams = new URLSearchParams(window.location.search);
        
        // Inicializar filtros de supermercados
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
        
        // Inicializar filtros de categorías
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
        
        // Actualizar campos ocultos y mostrar filtros activos
        updateHiddenFields();
        updateActiveFilters();
        
        // Mostrar indicador en el botón de filtros si hay filtros activos
        if (selectedSupermarkets.length > 0 || selectedCategories.length > 0 || 
            urlParams.has('search') || urlParams.has('precio_min') || 
            urlParams.has('precio_max') || urlParams.has('order_by')) {
            filterBtn.classList.add('btn-danger');
        }
    }
    
    // Manejar clics en tarjetas de filtro de supermercados
    document.querySelectorAll('.supermarket-filter').forEach(card => {
        card.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const name = this.getAttribute('data-name');
            
            if (this.classList.contains('selected')) {
                // Quitar de seleccionados
                this.classList.remove('selected');
                selectedSupermarkets = selectedSupermarkets.filter(sm => sm.id !== id);
            } else {
                // Añadir a seleccionados
                this.classList.add('selected');
                selectedSupermarkets.push({ id, name });
            }
            
            updateHiddenFields();
            updateActiveFilters();
        });
    });
    
    // Manejar clics en tarjetas de filtro de categorías
    document.querySelectorAll('.category-filter').forEach(card => {
        card.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            
            if (this.classList.contains('selected')) {
                // Quitar de seleccionados
                this.classList.remove('selected');
                selectedCategories = selectedCategories.filter(cat => cat !== category);
            } else {
                // Añadir a seleccionados
                this.classList.add('selected');
                selectedCategories.push(category);
            }
            
            updateHiddenFields();
            updateActiveFilters();
        });
    });
    
    // Botón de aplicar filtros
    document.getElementById('apply-filters').addEventListener('click', function() {
        document.getElementById('filter-form').submit();
        closeSidebar(); // Cerrar sidebar al aplicar filtros
    });
    
    // Actualizar campos ocultos del formulario
    function updateHiddenFields() {
        document.getElementById('selected-supermarkets').value = selectedSupermarkets.map(sm => sm.id).join(',');
        document.getElementById('selected-categories').value = selectedCategories.join(',');
    }
    
    // Actualizar visualización de filtros activos
    function updateActiveFilters() {
        const filterBadges = document.getElementById('filter-badges');
        filterBadges.innerHTML = '';
        
        // Añadir badges de supermercados
        selectedSupermarkets.forEach(sm => {
            filterBadges.innerHTML += `
                <span class="badge bg-primary d-flex align-items-center" data-type="supermarket" data-id="${sm.id}">
                    ${sm.name}
                    <button type="button" class="btn-close btn-close-white ms-2" aria-label="Remove"></button>
                </span>
            `;
        });
        
        // Añadir badges de categorías
        selectedCategories.forEach(category => {
            filterBadges.innerHTML += `
                <span class="badge bg-info d-flex align-items-center" data-type="category" data-category="${category}">
                    ${category}
                    <button type="button" class="btn-close btn-close-white ms-2" aria-label="Remove"></button>
                </span>
            `;
        });
        
        // Mostrar/ocultar franja de filtros
        document.getElementById('active-filters').style.display = 
            (selectedSupermarkets.length > 0 || selectedCategories.length > 0) ? 'block' : 'none';
        
        // Añadir manejadores de clic para eliminar filtros
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
    
    // Limpiar todos los filtros
    document.getElementById('clear-all-filters').addEventListener('click', function() {
        // Limpiar estados seleccionados
        document.querySelectorAll('.filter-card.selected').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Limpiar arrays de filtros
        selectedSupermarkets = [];
        selectedCategories = [];
        
        // Actualizar campos ocultos y visualización de filtros
        updateHiddenFields();
        updateActiveFilters();
        
        // Resetear campos del formulario
        document.getElementById('search').value = '';
        document.getElementById('precio_min').value = '';
        document.getElementById('precio_max').value = '';
        document.getElementById('order_by').selectedIndex = 0;
    });
    
    // Manejador de clic en el botón de búsqueda
    document.getElementById('search-btn').addEventListener('click', function() {
        document.getElementById('filter-form').submit();
        closeSidebar(); // Cerrar sidebar después de buscar
    });
    
    // Inicializar filtros existentes
    initializeFilters();
    
    // ===============================
    // SCROLL INFINITO Y CARGA DE PRODUCTOS
    // ===============================
    let loading = false;
    let scrollDebounceTimer;
    
    const loadMoreProducts = function() {
        // Si ya estamos cargando o no hay más productos, no hacer nada
        const hasMore = document.getElementById('has-more').value === 'true';
        if (loading || !hasMore) return;
        
        const currentPage = parseInt(document.getElementById('current-page').value);
        const nextPage = currentPage + 1;
        
        // Obtener la URL base actual
        let url;
        const currentUrl = document.getElementById('current-url').value;
        if (currentUrl) {
            url = new URL(window.location.origin + currentUrl);
        } else {
            url = new URL(window.location.href);
        }
        
        // Configurar parámetros para la siguiente página
        url.searchParams.set('page', nextPage);
        url.searchParams.set('partial', 'true');
        
        // Mostrar indicador de carga
        loading = true;
        document.getElementById('loading-indicator').style.display = 'block';
        
        // Realizar la petición
        fetch(url, {
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
                // Agregar los nuevos productos al contenedor
                document.getElementById('productos-container').insertAdjacentHTML('beforeend', data.html);
                
                // Actualizar el estado de paginación
                document.getElementById('current-page').value = nextPage;
                document.getElementById('has-more').value = data.has_next;
                
                // Verificar si hay productos en la respuesta
                if (!data.html.trim()) {
                    document.getElementById('has-more').value = 'false';
                    console.log('No más productos disponibles');
                }
            } else {
                console.error('Formato de respuesta incorrecto:', data);
                document.getElementById('has-more').value = 'false';
            }
        })
        .catch(error => {
            console.error('Error al cargar más productos:', error);
            // Mostrar mensaje de error al usuario
            const container = document.getElementById('productos-container');
            container.insertAdjacentHTML('beforeend', 
                `<div class="col-12 text-center mt-3">
                    <div class="alert alert-danger">
                        Error al cargar más productos. Por favor, intenta recargar la página.
                    </div>
                </div>`
            );
        })
        .finally(() => {
            // Siempre ocultar el indicador de carga y restablecer el estado
            loading = false;
            document.getElementById('loading-indicator').style.display = 'none';
        });
    };
    
    // Mejorar el manejo del evento de scroll con debounce
    const handleScroll = function() {
        clearTimeout(scrollDebounceTimer);
        scrollDebounceTimer = setTimeout(() => {
            // Comprobar si estamos cerca del final de la página
            const scrollPosition = window.scrollY + window.innerHeight;
            const pageHeight = document.documentElement.scrollHeight;
            
            // Si estamos a 500px o menos del final, cargar más productos
            if (pageHeight - scrollPosition <= 500) {
                loadMoreProducts();
            }
        }, 100); // 100ms de debounce
    };
    
    window.addEventListener('scroll', handleScroll);
    
    // Cargar productos inicialmente si hay pocos en la página
    setTimeout(() => {
        if (document.documentElement.scrollHeight <= window.innerHeight) {
            loadMoreProducts();
        }
    }, 500);
});