from django.core.management.base import BaseCommand
from productos.models import Supermercado, Producto, Precio
from decimal import Decimal
import random
from django.utils import timezone
from datetime import timedelta
import os
from django.conf import settings
import csv
from django.db import transaction
# Comando para generar datos de prueba para Supermercados, Productos y Precios

#docker exec -it carrito_django bash
#python manage.py generar_datos_prueba --productos 500 --borrar
class Command(BaseCommand):
    help = 'Genera un set completo de datos de prueba para Supermercados, Productos y Precios'

    def add_arguments(self, parser):
        parser.add_argument('--productos', type=int, default=500, help='Número de productos a generar')
        parser.add_argument('--borrar', action='store_true', help='Borrar datos existentes antes de generar nuevos')
        parser.add_argument('--exportar', action='store_true', help='Exportar los datos a archivos CSV')

    def handle(self, *args, **options):
        num_productos = options['productos']
        borrar_datos = options['borrar']
        exportar_datos = options['exportar']

        # Supermercados específicos seleccionados
        supermercados = [
            {"nombre": "Mercadona", "direccion": "Calle Valencia 123, Madrid", "geolocalizacion": "40.416775,-3.703790"},
            {"nombre": "Dia", "direccion": "Calle Gran Vía 789, Madrid", "geolocalizacion": "40.420160,-3.704700"},
            {"nombre": "Lidl", "direccion": "Avenida Andalucía 321, Sevilla", "geolocalizacion": "37.389092,-5.984459"},
            {"nombre": "Alcampo", "direccion": "Avenida Constitución 234, Zaragoza", "geolocalizacion": "41.648823,-0.889085"},
            {"nombre": "Consum", "direccion": "Avenida del Puerto 567, Valencia", "geolocalizacion": "39.469907,-0.376288"},
            {"nombre": "Ahorramas", "direccion": "Calle Orense 890, Madrid", "geolocalizacion": "40.456321,-3.694560"},
        ]

        # 9 Categorías principales simplificadas
        categorias = [
            "Alimentación fresca",
            "Alimentación seca y no perecedera", 
            "Congelados",
            "Dulces y aperitivos",
            "Bebidas",
            "Higiene personal y salud",
            "Limpieza del hogar",
            "Bebé y maternidad",
            "Mascotas"
        ]

        # Unidades de medida comunes
        unidades = ["kg", "g", "l", "ml", "unidad", "pack", "botella", "lata", "docena", "bandeja"]

        # Productos organizados por las nuevas categorías
        productos_por_categoria = {
            "Alimentación fresca": [
                # Frutas
                {"nombre": "Manzanas Golden", "descripcion": "Manzanas variedad Golden"},
                {"nombre": "Plátanos de Canarias", "descripcion": "Plátanos de las Islas Canarias"},
                {"nombre": "Naranjas de mesa", "descripcion": "Naranjas para consumo directo"},
                {"nombre": "Limones", "descripcion": "Limones frescos"},
                {"nombre": "Peras conferencia", "descripcion": "Peras variedad conferencia"},
                {"nombre": "Fresas", "descripcion": "Fresas frescas de temporada"},
                {"nombre": "Kiwi", "descripcion": "Kiwis verdes"},
                {"nombre": "Aguacate", "descripcion": "Aguacates maduración controlada"},
                
                # Verduras
                {"nombre": "Tomates", "descripcion": "Tomates para ensalada"},
                {"nombre": "Lechuga iceberg", "descripcion": "Lechuga iceberg fresca"},
                {"nombre": "Cebolla", "descripcion": "Cebollas blancas"},
                {"nombre": "Patatas", "descripcion": "Patatas para cocinar"},
                {"nombre": "Zanahorias", "descripcion": "Zanahorias frescas"},
                {"nombre": "Pimiento verde", "descripcion": "Pimientos verdes italianos"},
                {"nombre": "Calabacín", "descripcion": "Calabacín verde fresco"},
                {"nombre": "Pepino", "descripcion": "Pepino fresco"},
                {"nombre": "Champiñones", "descripcion": "Bandeja de champiñones laminados"},
                {"nombre": "Espinacas", "descripcion": "Espinacas frescas en hojas"},
                
                # Carnes
                {"nombre": "Pechuga de pollo", "descripcion": "Filetes de pechuga de pollo"},
                {"nombre": "Muslos de pollo", "descripcion": "Muslos de pollo frescos"},
                {"nombre": "Carne picada mixta", "descripcion": "Carne picada de cerdo y ternera"},
                {"nombre": "Filetes de ternera", "descripcion": "Filetes de primera de ternera"},
                {"nombre": "Chuletas de cordero", "descripcion": "Chuletas de cordero lechal"},
                {"nombre": "Lomo de cerdo", "descripcion": "Cinta de lomo fresco"},
                
                # Pescados
                {"nombre": "Merluza", "descripcion": "Filetes de merluza fresca"},
                {"nombre": "Salmón", "descripcion": "Lomos de salmón fresco"},
                {"nombre": "Dorada", "descripcion": "Dorada fresca entera"},
                {"nombre": "Bacalao", "descripcion": "Filetes de bacalao fresco"},
                {"nombre": "Gambas", "descripcion": "Gambas crudas peladas"},
                
                # Panadería
                {"nombre": "Pan de molde integral", "descripcion": "Pan de molde con harina integral"},
                {"nombre": "Baguette", "descripcion": "Baguette tradicional recién horneada"},
                {"nombre": "Pan rústico", "descripcion": "Pan de masa madre con corteza crujiente"},
                {"nombre": "Croissants frescos", "descripcion": "Croissants recién horneados"},
                
                # Lácteos
                {"nombre": "Leche entera", "descripcion": "Leche de vaca entera UHT"},
                {"nombre": "Yogur natural", "descripcion": "Yogur natural sin azúcar añadido"},
                {"nombre": "Queso manchego", "descripcion": "Queso curado de oveja manchega"},
                {"nombre": "Mantequilla", "descripcion": "Mantequilla tradicional sin sal"},
                {"nombre": "Nata para cocinar", "descripcion": "Nata líquida para cocinar"},
                
                # Huevos
                {"nombre": "Huevos frescos L", "descripcion": "Docena de huevos frescos tamaño L"},
                {"nombre": "Huevos camperos", "descripcion": "Huevos de gallinas camperas"}
            ],
            
            "Alimentación seca y no perecedera": [
                # Arroces
                {"nombre": "Arroz redondo", "descripcion": "Arroz grano redondo para paella"},
                {"nombre": "Arroz largo", "descripcion": "Arroz grano largo"},
                {"nombre": "Arroz basmati", "descripcion": "Arroz basmati aromático"},
                
                # Pastas
                {"nombre": "Pasta espaguetis", "descripcion": "Pasta tipo espaguetis"},
                {"nombre": "Pasta macarrones", "descripcion": "Pasta tipo macarrones"},
                {"nombre": "Pasta penne", "descripcion": "Pasta tipo penne"},
                
                # Legumbres
                {"nombre": "Lentejas rojas", "descripcion": "Lentejas rojas secas"},
                {"nombre": "Garbanzos secos", "descripcion": "Garbanzos secos para cocer"},
                {"nombre": "Alubias blancas", "descripcion": "Alubias blancas secas"},
                
                # Conservas
                {"nombre": "Atún en aceite", "descripcion": "Latas de atún en aceite de girasol"},
                {"nombre": "Tomate frito", "descripcion": "Bote de tomate frito casero"},
                {"nombre": "Garbanzos cocidos", "descripcion": "Bote de garbanzos cocidos"},
                {"nombre": "Sardinas en aceite", "descripcion": "Lata de sardinas en aceite de oliva"},
                
                # Aceites y salsas
                {"nombre": "Aceite de oliva virgen", "descripcion": "Aceite de oliva virgen extra"},
                {"nombre": "Aceite de girasol", "descripcion": "Aceite de girasol refinado"},
                {"nombre": "Vinagre de Jerez", "descripcion": "Vinagre de Jerez envejecido"},
                {"nombre": "Salsa de tomate", "descripcion": "Salsa de tomate natural"},
                
                # Harinas y productos de panadería
                {"nombre": "Harina de trigo", "descripcion": "Harina de trigo común"},
                {"nombre": "Pan rallado", "descripcion": "Pan rallado para rebozar"},
                
                # Productos bio
                {"nombre": "Quinoa ecológica", "descripcion": "Quinoa de cultivo ecológico"},
                {"nombre": "Pasta integral bio", "descripcion": "Pasta integral de cultivo ecológico"}
            ],
            
            "Congelados": [
                {"nombre": "Guisantes congelados", "descripcion": "Bolsa de guisantes congelados"},
                {"nombre": "Judías verdes congeladas", "descripcion": "Bolsa de judías verdes congeladas"},
                {"nombre": "Pizza margarita", "descripcion": "Pizza margarita congelada"},
                {"nombre": "Pizza 4 quesos", "descripcion": "Pizza cuatro quesos congelada"},
                {"nombre": "Croquetas de jamón", "descripcion": "Croquetas de jamón congeladas"},
                {"nombre": "Empanadillas de atún", "descripcion": "Empanadillas de atún congeladas"},
                {"nombre": "Patatas fritas congeladas", "descripcion": "Bolsa de patatas fritas congeladas"},
                {"nombre": "Merluza congelada", "descripcion": "Filetes de merluza congelada"},
                {"nombre": "Gambas peladas congeladas", "descripcion": "Gambas peladas congeladas"},
                {"nombre": "Helado de vainilla", "descripcion": "Helado de vainilla en tarrina"},
                {"nombre": "Helado de chocolate", "descripcion": "Helado de chocolate en tarrina"},
                {"nombre": "Sorbete de limón", "descripcion": "Sorbete de limón natural"},
                {"nombre": "Verduras para sopa", "descripcion": "Mezcla de verduras para sopa"},
                {"nombre": "Lasaña precocinada", "descripcion": "Lasaña boloñesa congelada"}
            ],
            
            "Dulces y aperitivos": [
                # Chocolates
                {"nombre": "Chocolate con leche", "descripcion": "Tableta de chocolate con leche"},
                {"nombre": "Chocolate negro 70%", "descripcion": "Tableta de chocolate negro 70%"},
                {"nombre": "Chocolate blanco", "descripcion": "Tableta de chocolate blanco"},
                
                # Galletas
                {"nombre": "Galletas maría", "descripcion": "Paquete de galletas tipo maría"},
                {"nombre": "Galletas digestive", "descripcion": "Galletas digestive integral"},
                {"nombre": "Galletas con chocolate", "descripcion": "Galletas con chips de chocolate"},
                
                # Snacks
                {"nombre": "Patatas fritas lisas", "descripcion": "Bolsa de patatas fritas lisas"},
                {"nombre": "Patatas fritas onduladas", "descripcion": "Bolsa de patatas fritas onduladas"},
                {"nombre": "Frutos secos", "descripcion": "Mezcla de frutos secos"},
                {"nombre": "Almendras tostadas", "descripcion": "Almendras tostadas y saladas"},
                {"nombre": "Cacahuetes", "descripcion": "Cacahuetes tostados con sal"},
                {"nombre": "Pipas de girasol", "descripcion": "Pipas de girasol tostadas"},
                
                # Cereales
                {"nombre": "Cereales corn flakes", "descripcion": "Cereales de desayuno tipo corn flakes"},
                {"nombre": "Cereales integrales", "descripcion": "Cereales integrales con fibra"},
                {"nombre": "Muesli", "descripcion": "Muesli con frutos secos"},
                
                # Repostería
                {"nombre": "Magdalenas", "descripcion": "Pack de magdalenas"},
                {"nombre": "Donuts glaseados", "descripcion": "Pack de donuts glaseados"},
                {"nombre": "Mermelada de fresa", "descripcion": "Mermelada de fresa"}
            ],
            
            "Bebidas": [
                {"nombre": "Agua mineral", "descripcion": "Agua mineral natural sin gas"},
                {"nombre": "Agua con gas", "descripcion": "Agua mineral con gas"},
                {"nombre": "Coca-Cola", "descripcion": "Refresco de cola Coca-Cola"},
                {"nombre": "Fanta Naranja", "descripcion": "Refresco de naranja Fanta"},
                {"nombre": "Zumo de naranja", "descripcion": "Zumo de naranja natural refrigerado"},
                {"nombre": "Zumo de piña", "descripcion": "Zumo de piña sin azúcar añadido"},
                {"nombre": "Cerveza Mahou", "descripcion": "Cerveza rubia Mahou"},
                {"nombre": "Cerveza Estrella Galicia", "descripcion": "Cerveza rubia Estrella Galicia"},
                {"nombre": "Cerveza sin alcohol", "descripcion": "Cerveza rubia sin alcohol"},
                {"nombre": "Vino tinto crianza", "descripcion": "Vino tinto Rioja Crianza"},
                {"nombre": "Vino blanco verdejo", "descripcion": "Vino blanco Rueda Verdejo"},
                {"nombre": "Whisky", "descripcion": "Whisky escocés"},
                {"nombre": "Café molido", "descripcion": "Café molido natural"},
                {"nombre": "Té verde", "descripcion": "Té verde en bolsitas"},
                {"nombre": "Bebida de avena", "descripcion": "Bebida vegetal de avena"},
                {"nombre": "Bebida de almendras", "descripcion": "Bebida vegetal de almendras"}
            ],
            
            "Higiene personal y salud": [
                {"nombre": "Gel de ducha", "descripcion": "Gel de ducha para piel sensible"},
                {"nombre": "Champú anticaspa", "descripcion": "Champú anticaspa con zinc"},
                {"nombre": "Acondicionador", "descripcion": "Acondicionador para cabello graso"},
                {"nombre": "Pasta de dientes", "descripcion": "Pasta dental con flúor"},
                {"nombre": "Cepillo de dientes", "descripcion": "Cepillo de dientes medio"},
                {"nombre": "Desodorante roll-on", "descripcion": "Desodorante roll-on 48h"},
                {"nombre": "Crema hidratante", "descripcion": "Crema hidratante facial"},
                {"nombre": "Papel higiénico", "descripcion": "Rollo de papel higiénico doble capa"},
                {"nombre": "Compresas", "descripcion": "Compresas higiénicas normales"},
                {"nombre": "Tampones", "descripcion": "Tampones con aplicador"},
                {"nombre": "Maquinillas de afeitar", "descripcion": "Maquinillas desechables 3 hojas"},
                {"nombre": "Espuma de afeitar", "descripcion": "Espuma de afeitar para piel sensible"},
                {"nombre": "Ibuprofeno", "descripcion": "Ibuprofeno 400mg sin receta"},
                {"nombre": "Paracetamol", "descripcion": "Paracetamol 500mg sin receta"},
                {"nombre": "Vitamina C", "descripcion": "Complemento vitamina C"}
            ],
            
            "Limpieza del hogar": [
                {"nombre": "Lejía", "descripcion": "Lejía para desinfección"},
                {"nombre": "Detergente lavadora", "descripcion": "Detergente líquido para lavadora"},
                {"nombre": "Suavizante", "descripcion": "Suavizante con aroma fresco"},
                {"nombre": "Lavavajillas líquido", "descripcion": "Detergente lavavajillas a mano"},
                {"nombre": "Pastillas lavavajillas", "descripcion": "Pastillas para lavavajillas automático"},
                {"nombre": "Limpiador multiusos", "descripcion": "Limpiador para múltiples superficies"},
                {"nombre": "Amoniaco", "descripcion": "Amoniaco perfumado limpiador"},
                {"nombre": "Limpiador baño", "descripcion": "Limpiador específico para baño"},
                {"nombre": "Limpiador cocina", "descripcion": "Limpiador desengrasante para cocina"},
                {"nombre": "Ambientador spray", "descripcion": "Ambientador en spray"},
                {"nombre": "Papel de cocina", "descripcion": "Rollo de papel de cocina extrafuerte"},
                {"nombre": "Bolsas de basura", "descripcion": "Bolsas de basura resistentes"},
                {"nombre": "Estropajos", "descripcion": "Pack de estropajos para cocina"},
                {"nombre": "Bayetas", "descripcion": "Pack de bayetas multiusos"}
            ],
            
            "Bebé y maternidad": [
                {"nombre": "Pañales talla 3", "descripcion": "Pañales desechables talla 3"},
                {"nombre": "Pañales talla 4", "descripcion": "Pañales desechables talla 4"},
                {"nombre": "Toallitas bebé", "descripcion": "Toallitas húmedas para bebé"},
                {"nombre": "Leche de fórmula", "descripcion": "Leche de fórmula para lactantes"},
                {"nombre": "Potitos de verduras", "descripcion": "Tarrito de verduras para bebé"},
                {"nombre": "Potitos de frutas", "descripcion": "Tarrito de frutas para bebé"},
                {"nombre": "Cereales bebé", "descripcion": "Cereales sin gluten para bebé"},
                {"nombre": "Gel bebé", "descripcion": "Gel de baño para bebé"},
                {"nombre": "Champú bebé", "descripcion": "Champú suave para bebé"},
                {"nombre": "Crema cambio pañal", "descripcion": "Crema protectora para cambio de pañal"},
                {"nombre": "Biberones", "descripcion": "Biberón anticólicos"},
                {"nombre": "Chupetes", "descripcion": "Chupetes anatómicos"}
            ],
            
            "Mascotas": [
                {"nombre": "Pienso perro adulto", "descripcion": "Pienso seco para perro adulto"},
                {"nombre": "Pienso cachorro", "descripcion": "Pienso seco para cachorro"},
                {"nombre": "Pienso gato adulto", "descripcion": "Pienso seco para gato adulto"},
                {"nombre": "Comida húmeda perro", "descripcion": "Latas de comida húmeda para perro"},
                {"nombre": "Comida húmeda gato", "descripcion": "Latas de comida húmeda para gato"},
                {"nombre": "Arena para gatos", "descripcion": "Arena aglomerante para gatos"},
                {"nombre": "Snacks perro", "descripcion": "Premios y snacks para perro"},
                {"nombre": "Huesos masticables", "descripcion": "Huesos de cuero para masticar"},
                {"nombre": "Champú perros", "descripcion": "Champú específico para perros"},
                {"nombre": "Collar antipulgas", "descripcion": "Collar antipulgas y garrapatas"},
                {"nombre": "Juguetes perro", "descripcion": "Juguetes de goma para perro"},
                {"nombre": "Correa perro", "descripcion": "Correa extensible para perro"}
            ]
        }

        with transaction.atomic():
            if borrar_datos:
                self.stdout.write(self.style.WARNING('Borrando datos existentes...'))
                Precio.objects.all().delete()
                Producto.objects.all().delete()
                Supermercado.objects.all().delete()
            
            # Crear supermercados
            self.stdout.write(self.style.SUCCESS('Creando supermercados...'))
            supermercados_obj = []
            for s in supermercados:
                supermercado, created = Supermercado.objects.get_or_create(
                    nombre=s["nombre"],
                    defaults={
                        "direccion": s["direccion"],
                        "geolocalizacion": s["geolocalizacion"]
                    }
                )
                supermercados_obj.append(supermercado)
                if created:
                    self.stdout.write(f'  - Creado supermercado: {supermercado.nombre}')

            # Contar productos existentes
            productos_actuales = Producto.objects.count()
            productos_necesarios = max(0, num_productos - productos_actuales)
            
            if productos_necesarios > 0:
                self.stdout.write(self.style.SUCCESS(f'Generando {productos_necesarios} productos nuevos...'))
                
                # Crear un conjunto de productos garantizando un mínimo de cada categoría
                productos_nuevos = []
                
                # Primero, asegurar productos para todas las categorías predefinidas
                for categoria, productos_lista in productos_por_categoria.items():
                    # Tomar todos los productos de la lista o hasta 20 por categoría
                    for producto_data in productos_lista[:min(len(productos_lista), 20)]:
                        producto = Producto(
                            nombre=producto_data["nombre"],
                            categoria=categoria,
                            unidad_medida=self._get_unidad_for_producto(producto_data["nombre"], unidades),
                            descripcion=producto_data["descripcion"]
                        )
                        productos_nuevos.append(producto)
                
                # Si necesitamos más productos, generar aleatoriamente
                productos_restantes = productos_necesarios - len(productos_nuevos)
                if productos_restantes > 0:
                    for i in range(productos_restantes):
                        categoria = random.choice(categorias)
                        # Intentar elegir un producto de la categoría que no hayamos usado
                        productos_disponibles = productos_por_categoria.get(categoria, [])
                        if productos_disponibles:
                            producto_data = random.choice(productos_disponibles)
                            nombre = f"{producto_data['nombre']} Extra {i}"
                            descripcion = f"{producto_data['descripcion']} - Variante {i}"
                        else:
                            # Si no hay productos predefinidos o se agotaron, generar uno aleatorio
                            nombre = f"Producto {categoria} {i}"
                            descripcion = f"Descripción del producto {nombre}"
                        
                        producto = Producto(
                            nombre=nombre,
                            categoria=categoria,
                            unidad_medida=self._get_unidad_for_producto(nombre, unidades),
                            descripcion=descripcion
                        )
                        productos_nuevos.append(producto)
                
                # Guardar todos los productos de una vez
                Producto.objects.bulk_create(productos_nuevos)
            
            # Obtener todos los productos ya existentes para generar precios
            todos_productos = list(Producto.objects.all())
            self.stdout.write(self.style.SUCCESS(f'Generando precios para {len(todos_productos)} productos...'))
            
            # Crear precios (cada producto tendrá precio en varios supermercados)
            precios_nuevos = []
            for producto in todos_productos:
                # Determinar en cuántos supermercados estará este producto (entre 3 y todos)
                num_supermercados = random.randint(3, len(supermercados_obj))
                supermercados_producto = random.sample(supermercados_obj, num_supermercados)
                
                # Establecer un precio base según la categoría
                precio_base = self._get_precio_base(producto.categoria)
                
                for supermercado in supermercados_producto:
                    # Variación según el supermercado (algunos más caros, otros más baratos)
                    factor_precio = self._get_factor_precio(supermercado.nombre)
                    
                    # Añadir una pequeña variación aleatoria
                    variacion = random.uniform(0.90, 1.10)
                    
                    precio_final = round(precio_base * factor_precio * variacion, 2)
                    
                    # Comprobar si ya existe este precio
                    precio_existente = Precio.objects.filter(
                        id_producto=producto,
                        id_supermercado=supermercado
                    ).first()
                    
                    if precio_existente:
                        # Actualizar precio existente con una pequeña variación
                        precio_existente.precio = precio_final
                        precio_existente.fecha_actualizacion = timezone.now()
                        precio_existente.save()
                    else:
                        # Crear nuevo precio
                        precio = Precio(
                            id_producto=producto,
                            id_supermercado=supermercado,
                            precio=precio_final,
                            fecha_actualizacion=timezone.now() - timedelta(days=random.randint(0, 30))
                        )
                        precios_nuevos.append(precio)
                
                # Crear lotes de 1000 precios para evitar problemas de memoria
                if len(precios_nuevos) >= 1000:
                    Precio.objects.bulk_create(precios_nuevos)
                    precios_nuevos = []
            
            # Guardar los precios restantes
            if precios_nuevos:
                Precio.objects.bulk_create(precios_nuevos)
            
            # Exportar a CSV si se solicitó
            if exportar_datos:
                self._exportar_a_csv()
            
            # Informar sobre la cantidad de datos generados
            self.stdout.write(self.style.SUCCESS(f'--- RESUMEN DE DATOS GENERADOS ---'))
            self.stdout.write(f'Supermercados: {Supermercado.objects.count()}')
            self.stdout.write(f'Productos: {Producto.objects.count()}')
            self.stdout.write(f'Precios: {Precio.objects.count()}')
            
            # Mostrar distribución por categorías
            self.stdout.write(self.style.SUCCESS('--- DISTRIBUCIÓN POR CATEGORÍAS ---'))
            for categoria in categorias:
                count = Producto.objects.filter(categoria=categoria).count()
                self.stdout.write(f'{categoria}: {count} productos')
    
    def _get_unidad_for_producto(self, nombre, unidades):
        """Determina la unidad de medida más adecuada según el nombre del producto"""
        nombre = nombre.lower()
        if any(word in nombre for word in ["leche", "zumo", "agua", "vino", "cerveza", "aceite"]):
            return "l" if "agua" in nombre or "leche" in nombre else "ml"
        elif any(word in nombre for word in ["detergente", "suavizante", "gel", "champú"]):
            return "ml"
        elif any(word in nombre for word in ["manzana", "pera", "plátano", "naranja", "patata", "cebolla", "tomate"]):
            return "kg"
        elif any(word in nombre for word in ["papel", "servilleta", "rollo", "pañales", "toallitas"]):
            return "pack"
        elif any(word in nombre for word in ["galleta", "cereal", "snack", "patata", "pienso"]):
            return "g"
        elif any(word in nombre for word in ["huevos", "magdalenas", "donuts"]):
            return "docena"
        else:
            return random.choice(unidades)
    
    def _get_precio_base(self, categoria):
        """Determina un precio base según la nueva categoría del producto"""
        rangos_precio = {
            "Alimentación fresca": (0.80, 15.00),
            "Alimentación seca y no perecedera": (0.60, 8.00),
            "Congelados": (2.00, 12.00),
            "Dulces y aperitivos": (0.80, 6.00),
            "Bebidas": (0.70, 25.00),
            "Higiene personal y salud": (1.50, 15.00),
            "Limpieza del hogar": (1.20, 8.00),
            "Bebé y maternidad": (2.50, 20.00),
            "Mascotas": (1.50, 25.00)
        }
        
        rango = rangos_precio.get(categoria, (1.00, 5.00))
        return round(random.uniform(rango[0], rango[1]), 2)
    
    def _get_factor_precio(self, nombre_supermercado):
        """Determina un factor de precio según el supermercado"""
        factores = {
            "Mercadona": 1.00,
            "Dia": 0.95,
            "Lidl": 0.93,
            "Alcampo": 0.98,
            "Consum": 1.04,
            "Ahorramas": 0.97
        }
        
        return factores.get(nombre_supermercado, 1.00)
    
    def _exportar_a_csv(self):
        """Exporta los datos a archivos CSV"""
        csv_dir = os.path.join(settings.BASE_DIR, 'csv_export')
        os.makedirs(csv_dir, exist_ok=True)
        
        # Exportar supermercados
        supermercados_path = os.path.join(csv_dir, 'supermercados.csv')
        with open(supermercados_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id_supermercado', 'nombre', 'direccion', 'geolocalizacion'])
            for s in Supermercado.objects.all():
                writer.writerow([s.id_supermercado, s.nombre, s.direccion, s.geolocalizacion])
        
        # Exportar productos
        productos_path = os.path.join(csv_dir, 'productos.csv')
        with open(productos_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id_producto', 'nombre', 'categoria', 'unidad_medida', 'descripcion'])
            for p in Producto.objects.all():
                writer.writerow([p.id_producto, p.nombre, p.categoria, p.unidad_medida, p.descripcion])
        
        # Exportar precios (puede ser un archivo grande)
        precios_path = os.path.join(csv_dir, 'precios.csv')
        with open(precios_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id_precio', 'id_producto', 'id_supermercado', 'precio', 'fecha_actualizacion'])
            # Exportar en lotes para evitar problemas de memoria
            batch_size = 5000
            total_precios = Precio.objects.count()
            
            for offset in range(0, total_precios, batch_size):
                for p in Precio.objects.all()[offset:offset+batch_size]:
                    writer.writerow([
                        p.id_precio, 
                        p.id_producto.id_producto, 
                        p.id_supermercado.id_supermercado, 
                        p.precio, 
                        p.fecha_actualizacion
                    ])
        
        self.stdout.write(self.style.SUCCESS(f'Datos exportados a: {csv_dir}'))
from productos.models import Supermercado, Producto, Precio
from decimal import Decimal
import random
from django.utils import timezone
from datetime import timedelta
import os
from django.conf import settings
import csv
from django.db import transaction

#docker exec -it carrito_django bash
#python manage.py generar_datos_prueba --productos 500 --borrar
class Command(BaseCommand):
    help = 'Genera un set completo de datos de prueba para Supermercados, Productos y Precios'

    def add_arguments(self, parser):
        parser.add_argument('--productos', type=int, default=500, help='Número de productos a generar')
        parser.add_argument('--borrar', action='store_true', help='Borrar datos existentes antes de generar nuevos')
        parser.add_argument('--exportar', action='store_true', help='Exportar los datos a archivos CSV')

    def handle(self, *args, **options):
        num_productos = options['productos']
        borrar_datos = options['borrar']
        exportar_datos = options['exportar']

        # Supermercados específicos seleccionados
        supermercados = [
            {"nombre": "Mercadona", "direccion": "Calle Valencia 123, Madrid", "geolocalizacion": "40.416775,-3.703790"},
            {"nombre": "Dia", "direccion": "Calle Gran Vía 789, Madrid", "geolocalizacion": "40.420160,-3.704700"},
            {"nombre": "Lidl", "direccion": "Avenida Andalucía 321, Sevilla", "geolocalizacion": "37.389092,-5.984459"},
            {"nombre": "Alcampo", "direccion": "Avenida Constitución 234, Zaragoza", "geolocalizacion": "41.648823,-0.889085"},
            {"nombre": "Consum", "direccion": "Avenida del Puerto 567, Valencia", "geolocalizacion": "39.469907,-0.376288"},
            {"nombre": "Ahorramas", "direccion": "Calle Orense 890, Madrid", "geolocalizacion": "40.456321,-3.694560"},
        ]

        # 9 Categorías principales simplificadas
        categorias = [
            "Alimentación fresca",
            "Alimentación seca y no perecedera", 
            "Congelados",
            "Dulces y aperitivos",
            "Bebidas",
            "Higiene personal y salud",
            "Limpieza del hogar",
            "Bebé y maternidad",
            "Mascotas"
        ]

        # Unidades de medida comunes
        unidades = ["kg", "g", "l", "ml", "unidad", "pack", "botella", "lata", "docena", "bandeja"]

        # Productos organizados por las nuevas categorías
        productos_por_categoria = {
            "Alimentación fresca": [
                # Frutas
                {"nombre": "Manzanas Golden", "descripcion": "Manzanas variedad Golden"},
                {"nombre": "Plátanos de Canarias", "descripcion": "Plátanos de las Islas Canarias"},
                {"nombre": "Naranjas de mesa", "descripcion": "Naranjas para consumo directo"},
                {"nombre": "Limones", "descripcion": "Limones frescos"},
                {"nombre": "Peras conferencia", "descripcion": "Peras variedad conferencia"},
                {"nombre": "Fresas", "descripcion": "Fresas frescas de temporada"},
                {"nombre": "Kiwi", "descripcion": "Kiwis verdes"},
                {"nombre": "Aguacate", "descripcion": "Aguacates maduración controlada"},
                
                # Verduras
                {"nombre": "Tomates", "descripcion": "Tomates para ensalada"},
                {"nombre": "Lechuga iceberg", "descripcion": "Lechuga iceberg fresca"},
                {"nombre": "Cebolla", "descripcion": "Cebollas blancas"},
                {"nombre": "Patatas", "descripcion": "Patatas para cocinar"},
                {"nombre": "Zanahorias", "descripcion": "Zanahorias frescas"},
                {"nombre": "Pimiento verde", "descripcion": "Pimientos verdes italianos"},
                {"nombre": "Calabacín", "descripcion": "Calabacín verde fresco"},
                {"nombre": "Pepino", "descripcion": "Pepino fresco"},
                {"nombre": "Champiñones", "descripcion": "Bandeja de champiñones laminados"},
                {"nombre": "Espinacas", "descripcion": "Espinacas frescas en hojas"},
                
                # Carnes
                {"nombre": "Pechuga de pollo", "descripcion": "Filetes de pechuga de pollo"},
                {"nombre": "Muslos de pollo", "descripcion": "Muslos de pollo frescos"},
                {"nombre": "Carne picada mixta", "descripcion": "Carne picada de cerdo y ternera"},
                {"nombre": "Filetes de ternera", "descripcion": "Filetes de primera de ternera"},
                {"nombre": "Chuletas de cordero", "descripcion": "Chuletas de cordero lechal"},
                {"nombre": "Lomo de cerdo", "descripcion": "Cinta de lomo fresco"},
                
                # Pescados
                {"nombre": "Merluza", "descripcion": "Filetes de merluza fresca"},
                {"nombre": "Salmón", "descripcion": "Lomos de salmón fresco"},
                {"nombre": "Dorada", "descripcion": "Dorada fresca entera"},
                {"nombre": "Bacalao", "descripcion": "Filetes de bacalao fresco"},
                {"nombre": "Gambas", "descripcion": "Gambas crudas peladas"},
                
                # Panadería
                {"nombre": "Pan de molde integral", "descripcion": "Pan de molde con harina integral"},
                {"nombre": "Baguette", "descripcion": "Baguette tradicional recién horneada"},
                {"nombre": "Pan rústico", "descripcion": "Pan de masa madre con corteza crujiente"},
                {"nombre": "Croissants frescos", "descripcion": "Croissants recién horneados"},
                
                # Lácteos
                {"nombre": "Leche entera", "descripcion": "Leche de vaca entera UHT"},
                {"nombre": "Yogur natural", "descripcion": "Yogur natural sin azúcar añadido"},
                {"nombre": "Queso manchego", "descripcion": "Queso curado de oveja manchega"},
                {"nombre": "Mantequilla", "descripcion": "Mantequilla tradicional sin sal"},
                {"nombre": "Nata para cocinar", "descripcion": "Nata líquida para cocinar"},
                
                # Huevos
                {"nombre": "Huevos frescos L", "descripcion": "Docena de huevos frescos tamaño L"},
                {"nombre": "Huevos camperos", "descripcion": "Huevos de gallinas camperas"}
            ],
            
            "Alimentación seca y no perecedera": [
                # Arroces
                {"nombre": "Arroz redondo", "descripcion": "Arroz grano redondo para paella"},
                {"nombre": "Arroz largo", "descripcion": "Arroz grano largo"},
                {"nombre": "Arroz basmati", "descripcion": "Arroz basmati aromático"},
                
                # Pastas
                {"nombre": "Pasta espaguetis", "descripcion": "Pasta tipo espaguetis"},
                {"nombre": "Pasta macarrones", "descripcion": "Pasta tipo macarrones"},
                {"nombre": "Pasta penne", "descripcion": "Pasta tipo penne"},
                
                # Legumbres
                {"nombre": "Lentejas rojas", "descripcion": "Lentejas rojas secas"},
                {"nombre": "Garbanzos secos", "descripcion": "Garbanzos secos para cocer"},
                {"nombre": "Alubias blancas", "descripcion": "Alubias blancas secas"},
                
                # Conservas
                {"nombre": "Atún en aceite", "descripcion": "Latas de atún en aceite de girasol"},
                {"nombre": "Tomate frito", "descripcion": "Bote de tomate frito casero"},
                {"nombre": "Garbanzos cocidos", "descripcion": "Bote de garbanzos cocidos"},
                {"nombre": "Sardinas en aceite", "descripcion": "Lata de sardinas en aceite de oliva"},
                
                # Aceites y salsas
                {"nombre": "Aceite de oliva virgen", "descripcion": "Aceite de oliva virgen extra"},
                {"nombre": "Aceite de girasol", "descripcion": "Aceite de girasol refinado"},
                {"nombre": "Vinagre de Jerez", "descripcion": "Vinagre de Jerez envejecido"},
                {"nombre": "Salsa de tomate", "descripcion": "Salsa de tomate natural"},
                
                # Harinas y productos de panadería
                {"nombre": "Harina de trigo", "descripcion": "Harina de trigo común"},
                {"nombre": "Pan rallado", "descripcion": "Pan rallado para rebozar"},
                
                # Productos bio
                {"nombre": "Quinoa ecológica", "descripcion": "Quinoa de cultivo ecológico"},
                {"nombre": "Pasta integral bio", "descripcion": "Pasta integral de cultivo ecológico"}
            ],
            
            "Congelados": [
                {"nombre": "Guisantes congelados", "descripcion": "Bolsa de guisantes congelados"},
                {"nombre": "Judías verdes congeladas", "descripcion": "Bolsa de judías verdes congeladas"},
                {"nombre": "Pizza margarita", "descripcion": "Pizza margarita congelada"},
                {"nombre": "Pizza 4 quesos", "descripcion": "Pizza cuatro quesos congelada"},
                {"nombre": "Croquetas de jamón", "descripcion": "Croquetas de jamón congeladas"},
                {"nombre": "Empanadillas de atún", "descripcion": "Empanadillas de atún congeladas"},
                {"nombre": "Patatas fritas congeladas", "descripcion": "Bolsa de patatas fritas congeladas"},
                {"nombre": "Merluza congelada", "descripcion": "Filetes de merluza congelada"},
                {"nombre": "Gambas peladas congeladas", "descripcion": "Gambas peladas congeladas"},
                {"nombre": "Helado de vainilla", "descripcion": "Helado de vainilla en tarrina"},
                {"nombre": "Helado de chocolate", "descripcion": "Helado de chocolate en tarrina"},
                {"nombre": "Sorbete de limón", "descripcion": "Sorbete de limón natural"},
                {"nombre": "Verduras para sopa", "descripcion": "Mezcla de verduras para sopa"},
                {"nombre": "Lasaña precocinada", "descripcion": "Lasaña boloñesa congelada"}
            ],
            
            "Dulces y aperitivos": [
                # Chocolates
                {"nombre": "Chocolate con leche", "descripcion": "Tableta de chocolate con leche"},
                {"nombre": "Chocolate negro 70%", "descripcion": "Tableta de chocolate negro 70%"},
                {"nombre": "Chocolate blanco", "descripcion": "Tableta de chocolate blanco"},
                
                # Galletas
                {"nombre": "Galletas maría", "descripcion": "Paquete de galletas tipo maría"},
                {"nombre": "Galletas digestive", "descripcion": "Galletas digestive integral"},
                {"nombre": "Galletas con chocolate", "descripcion": "Galletas con chips de chocolate"},
                
                # Snacks
                {"nombre": "Patatas fritas lisas", "descripcion": "Bolsa de patatas fritas lisas"},
                {"nombre": "Patatas fritas onduladas", "descripcion": "Bolsa de patatas fritas onduladas"},
                {"nombre": "Frutos secos", "descripcion": "Mezcla de frutos secos"},
                {"nombre": "Almendras tostadas", "descripcion": "Almendras tostadas y saladas"},
                {"nombre": "Cacahuetes", "descripcion": "Cacahuetes tostados con sal"},
                {"nombre": "Pipas de girasol", "descripcion": "Pipas de girasol tostadas"},
                
                # Cereales
                {"nombre": "Cereales corn flakes", "descripcion": "Cereales de desayuno tipo corn flakes"},
                {"nombre": "Cereales integrales", "descripcion": "Cereales integrales con fibra"},
                {"nombre": "Muesli", "descripcion": "Muesli con frutos secos"},
                
                # Repostería
                {"nombre": "Magdalenas", "descripcion": "Pack de magdalenas"},
                {"nombre": "Donuts glaseados", "descripcion": "Pack de donuts glaseados"},
                {"nombre": "Mermelada de fresa", "descripcion": "Mermelada de fresa"}
            ],
            
            "Bebidas": [
                {"nombre": "Agua mineral", "descripcion": "Agua mineral natural sin gas"},
                {"nombre": "Agua con gas", "descripcion": "Agua mineral con gas"},
                {"nombre": "Coca-Cola", "descripcion": "Refresco de cola Coca-Cola"},
                {"nombre": "Fanta Naranja", "descripcion": "Refresco de naranja Fanta"},
                {"nombre": "Zumo de naranja", "descripcion": "Zumo de naranja natural refrigerado"},
                {"nombre": "Zumo de piña", "descripcion": "Zumo de piña sin azúcar añadido"},
                {"nombre": "Cerveza Mahou", "descripcion": "Cerveza rubia Mahou"},
                {"nombre": "Cerveza Estrella Galicia", "descripcion": "Cerveza rubia Estrella Galicia"},
                {"nombre": "Cerveza sin alcohol", "descripcion": "Cerveza rubia sin alcohol"},
                {"nombre": "Vino tinto crianza", "descripcion": "Vino tinto Rioja Crianza"},
                {"nombre": "Vino blanco verdejo", "descripcion": "Vino blanco Rueda Verdejo"},
                {"nombre": "Whisky", "descripcion": "Whisky escocés"},
                {"nombre": "Café molido", "descripcion": "Café molido natural"},
                {"nombre": "Té verde", "descripcion": "Té verde en bolsitas"},
                {"nombre": "Bebida de avena", "descripcion": "Bebida vegetal de avena"},
                {"nombre": "Bebida de almendras", "descripcion": "Bebida vegetal de almendras"}
            ],
            
            "Higiene personal y salud": [
                {"nombre": "Gel de ducha", "descripcion": "Gel de ducha para piel sensible"},
                {"nombre": "Champú anticaspa", "descripcion": "Champú anticaspa con zinc"},
                {"nombre": "Acondicionador", "descripcion": "Acondicionador para cabello graso"},
                {"nombre": "Pasta de dientes", "descripcion": "Pasta dental con flúor"},
                {"nombre": "Cepillo de dientes", "descripcion": "Cepillo de dientes medio"},
                {"nombre": "Desodorante roll-on", "descripcion": "Desodorante roll-on 48h"},
                {"nombre": "Crema hidratante", "descripcion": "Crema hidratante facial"},
                {"nombre": "Papel higiénico", "descripcion": "Rollo de papel higiénico doble capa"},
                {"nombre": "Compresas", "descripcion": "Compresas higiénicas normales"},
                {"nombre": "Tampones", "descripcion": "Tampones con aplicador"},
                {"nombre": "Maquinillas de afeitar", "descripcion": "Maquinillas desechables 3 hojas"},
                {"nombre": "Espuma de afeitar", "descripcion": "Espuma de afeitar para piel sensible"},
                {"nombre": "Ibuprofeno", "descripcion": "Ibuprofeno 400mg sin receta"},
                {"nombre": "Paracetamol", "descripcion": "Paracetamol 500mg sin receta"},
                {"nombre": "Vitamina C", "descripcion": "Complemento vitamina C"}
            ],
            
            "Limpieza del hogar": [
                {"nombre": "Lejía", "descripcion": "Lejía para desinfección"},
                {"nombre": "Detergente lavadora", "descripcion": "Detergente líquido para lavadora"},
                {"nombre": "Suavizante", "descripcion": "Suavizante con aroma fresco"},
                {"nombre": "Lavavajillas líquido", "descripcion": "Detergente lavavajillas a mano"},
                {"nombre": "Pastillas lavavajillas", "descripcion": "Pastillas para lavavajillas automático"},
                {"nombre": "Limpiador multiusos", "descripcion": "Limpiador para múltiples superficies"},
                {"nombre": "Amoniaco", "descripcion": "Amoniaco perfumado limpiador"},
                {"nombre": "Limpiador baño", "descripcion": "Limpiador específico para baño"},
                {"nombre": "Limpiador cocina", "descripcion": "Limpiador desengrasante para cocina"},
                {"nombre": "Ambientador spray", "descripcion": "Ambientador en spray"},
                {"nombre": "Papel de cocina", "descripcion": "Rollo de papel de cocina extrafuerte"},
                {"nombre": "Bolsas de basura", "descripcion": "Bolsas de basura resistentes"},
                {"nombre": "Estropajos", "descripcion": "Pack de estropajos para cocina"},
                {"nombre": "Bayetas", "descripcion": "Pack de bayetas multiusos"}
            ],
            
            "Bebé y maternidad": [
                {"nombre": "Pañales talla 3", "descripcion": "Pañales desechables talla 3"},
                {"nombre": "Pañales talla 4", "descripcion": "Pañales desechables talla 4"},
                {"nombre": "Toallitas bebé", "descripcion": "Toallitas húmedas para bebé"},
                {"nombre": "Leche de fórmula", "descripcion": "Leche de fórmula para lactantes"},
                {"nombre": "Potitos de verduras", "descripcion": "Tarrito de verduras para bebé"},
                {"nombre": "Potitos de frutas", "descripcion": "Tarrito de frutas para bebé"},
                {"nombre": "Cereales bebé", "descripcion": "Cereales sin gluten para bebé"},
                {"nombre": "Gel bebé", "descripcion": "Gel de baño para bebé"},
                {"nombre": "Champú bebé", "descripcion": "Champú suave para bebé"},
                {"nombre": "Crema cambio pañal", "descripcion": "Crema protectora para cambio de pañal"},
                {"nombre": "Biberones", "descripcion": "Biberón anticólicos"},
                {"nombre": "Chupetes", "descripcion": "Chupetes anatómicos"}
            ],
            
            "Mascotas": [
                {"nombre": "Pienso perro adulto", "descripcion": "Pienso seco para perro adulto"},
                {"nombre": "Pienso cachorro", "descripcion": "Pienso seco para cachorro"},
                {"nombre": "Pienso gato adulto", "descripcion": "Pienso seco para gato adulto"},
                {"nombre": "Comida húmeda perro", "descripcion": "Latas de comida húmeda para perro"},
                {"nombre": "Comida húmeda gato", "descripcion": "Latas de comida húmeda para gato"},
                {"nombre": "Arena para gatos", "descripcion": "Arena aglomerante para gatos"},
                {"nombre": "Snacks perro", "descripcion": "Premios y snacks para perro"},
                {"nombre": "Huesos masticables", "descripcion": "Huesos de cuero para masticar"},
                {"nombre": "Champú perros", "descripcion": "Champú específico para perros"},
                {"nombre": "Collar antipulgas", "descripcion": "Collar antipulgas y garrapatas"},
                {"nombre": "Juguetes perro", "descripcion": "Juguetes de goma para perro"},
                {"nombre": "Correa perro", "descripcion": "Correa extensible para perro"}
            ]
        }

        with transaction.atomic():
            if borrar_datos:
                self.stdout.write(self.style.WARNING('Borrando datos existentes...'))
                Precio.objects.all().delete()
                Producto.objects.all().delete()
                Supermercado.objects.all().delete()
            
            # Crear supermercados
            self.stdout.write(self.style.SUCCESS('Creando supermercados...'))
            supermercados_obj = []
            for s in supermercados:
                supermercado, created = Supermercado.objects.get_or_create(
                    nombre=s["nombre"],
                    defaults={
                        "direccion": s["direccion"],
                        "geolocalizacion": s["geolocalizacion"]
                    }
                )
                supermercados_obj.append(supermercado)
                if created:
                    self.stdout.write(f'  - Creado supermercado: {supermercado.nombre}')

            # Contar productos existentes
            productos_actuales = Producto.objects.count()
            productos_necesarios = max(0, num_productos - productos_actuales)
            
            if productos_necesarios > 0:
                self.stdout.write(self.style.SUCCESS(f'Generando {productos_necesarios} productos nuevos...'))
                
                # Crear un conjunto de productos garantizando un mínimo de cada categoría
                productos_nuevos = []
                
                # Primero, asegurar productos para todas las categorías predefinidas
                for categoria, productos_lista in productos_por_categoria.items():
                    # Tomar todos los productos de la lista o hasta 20 por categoría
                    for producto_data in productos_lista[:min(len(productos_lista), 20)]:
                        producto = Producto(
                            nombre=producto_data["nombre"],
                            categoria=categoria,
                            unidad_medida=self._get_unidad_for_producto(producto_data["nombre"], unidades),
                            descripcion=producto_data["descripcion"]
                        )
                        productos_nuevos.append(producto)
                
                # Si necesitamos más productos, generar aleatoriamente
                productos_restantes = productos_necesarios - len(productos_nuevos)
                if productos_restantes > 0:
                    for i in range(productos_restantes):
                        categoria = random.choice(categorias)
                        # Intentar elegir un producto de la categoría que no hayamos usado
                        productos_disponibles = productos_por_categoria.get(categoria, [])
                        if productos_disponibles:
                            producto_data = random.choice(productos_disponibles)
                            nombre = f"{producto_data['nombre']} Extra {i}"
                            descripcion = f"{producto_data['descripcion']} - Variante {i}"
                        else:
                            # Si no hay productos predefinidos o se agotaron, generar uno aleatorio
                            nombre = f"Producto {categoria} {i}"
                            descripcion = f"Descripción del producto {nombre}"
                        
                        producto = Producto(
                            nombre=nombre,
                            categoria=categoria,
                            unidad_medida=self._get_unidad_for_producto(nombre, unidades),
                            descripcion=descripcion
                        )
                        productos_nuevos.append(producto)
                
                # Guardar todos los productos de una vez
                Producto.objects.bulk_create(productos_nuevos)
            
            # Obtener todos los productos ya existentes para generar precios
            todos_productos = list(Producto.objects.all())
            self.stdout.write(self.style.SUCCESS(f'Generando precios para {len(todos_productos)} productos...'))
            
            # Crear precios (cada producto tendrá precio en varios supermercados)
            precios_nuevos = []
            for producto in todos_productos:
                # Determinar en cuántos supermercados estará este producto (entre 3 y todos)
                num_supermercados = random.randint(3, len(supermercados_obj))
                supermercados_producto = random.sample(supermercados_obj, num_supermercados)
                
                # Establecer un precio base según la categoría
                precio_base = self._get_precio_base(producto.categoria)
                
                for supermercado in supermercados_producto:
                    # Variación según el supermercado (algunos más caros, otros más baratos)
                    factor_precio = self._get_factor_precio(supermercado.nombre)
                    
                    # Añadir una pequeña variación aleatoria
                    variacion = random.uniform(0.90, 1.10)
                    
                    precio_final = round(precio_base * factor_precio * variacion, 2)
                    
                    # Comprobar si ya existe este precio
                    precio_existente = Precio.objects.filter(
                        id_producto=producto,
                        id_supermercado=supermercado
                    ).first()
                    
                    if precio_existente:
                        # Actualizar precio existente con una pequeña variación
                        precio_existente.precio = precio_final
                        precio_existente.fecha_actualizacion = timezone.now()
                        precio_existente.save()
                    else:
                        # Crear nuevo precio
                        precio = Precio(
                            id_producto=producto,
                            id_supermercado=supermercado,
                            precio=precio_final,
                            fecha_actualizacion=timezone.now() - timedelta(days=random.randint(0, 30))
                        )
                        precios_nuevos.append(precio)
                
                # Crear lotes de 1000 precios para evitar problemas de memoria
                if len(precios_nuevos) >= 1000:
                    Precio.objects.bulk_create(precios_nuevos)
                    precios_nuevos = []
            
            # Guardar los precios restantes
            if precios_nuevos:
                Precio.objects.bulk_create(precios_nuevos)
            
            # Exportar a CSV si se solicitó
            if exportar_datos:
                self._exportar_a_csv()
            
            # Informar sobre la cantidad de datos generados
            self.stdout.write(self.style.SUCCESS(f'--- RESUMEN DE DATOS GENERADOS ---'))
            self.stdout.write(f'Supermercados: {Supermercado.objects.count()}')
            self.stdout.write(f'Productos: {Producto.objects.count()}')
            self.stdout.write(f'Precios: {Precio.objects.count()}')
            
            # Mostrar distribución por categorías
            self.stdout.write(self.style.SUCCESS('--- DISTRIBUCIÓN POR CATEGORÍAS ---'))
            for categoria in categorias:
                count = Producto.objects.filter(categoria=categoria).count()
                self.stdout.write(f'{categoria}: {count} productos')
    
    def _get_unidad_for_producto(self, nombre, unidades):
        """Determina la unidad de medida más adecuada según el nombre del producto"""
        nombre = nombre.lower()
        if any(word in nombre for word in ["leche", "zumo", "agua", "vino", "cerveza", "aceite"]):
            return "l" if "agua" in nombre or "leche" in nombre else "ml"
        elif any(word in nombre for word in ["detergente", "suavizante", "gel", "champú"]):
            return "ml"
        elif any(word in nombre for word in ["manzana", "pera", "plátano", "naranja", "patata", "cebolla", "tomate"]):
            return "kg"
        elif any(word in nombre for word in ["papel", "servilleta", "rollo", "pañales", "toallitas"]):
            return "pack"
        elif any(word in nombre for word in ["galleta", "cereal", "snack", "patata", "pienso"]):
            return "g"
        elif any(word in nombre for word in ["huevos", "magdalenas", "donuts"]):
            return "docena"
        else:
            return random.choice(unidades)
    
    def _get_precio_base(self, categoria):
        """Determina un precio base según la nueva categoría del producto"""
        rangos_precio = {
            "Alimentación fresca": (0.80, 15.00),
            "Alimentación seca y no perecedera": (0.60, 8.00),
            "Congelados": (2.00, 12.00),
            "Dulces y aperitivos": (0.80, 6.00),
            "Bebidas": (0.70, 25.00),
            "Higiene personal y salud": (1.50, 15.00),
            "Limpieza del hogar": (1.20, 8.00),
            "Bebé y maternidad": (2.50, 20.00),
            "Mascotas": (1.50, 25.00)
        }
        
        rango = rangos_precio.get(categoria, (1.00, 5.00))
        return round(random.uniform(rango[0], rango[1]), 2)
    
    def _get_factor_precio(self, nombre_supermercado):
        """Determina un factor de precio según el supermercado"""
        factores = {
            "Mercadona": 1.00,
            "Dia": 0.95,
            "Lidl": 0.93,
            "Alcampo": 0.98,
            "Consum": 1.04,
            "Ahorramas": 0.97
        }
        
        return factores.get(nombre_supermercado, 1.00)
    
    def _exportar_a_csv(self):
        """Exporta los datos a archivos CSV"""
        csv_dir = os.path.join(settings.BASE_DIR, 'csv_export')
        os.makedirs(csv_dir, exist_ok=True)
        
        # Exportar supermercados
        supermercados_path = os.path.join(csv_dir, 'supermercados.csv')
        with open(supermercados_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id_supermercado', 'nombre', 'direccion', 'geolocalizacion'])
            for s in Supermercado.objects.all():
                writer.writerow([s.id_supermercado, s.nombre, s.direccion, s.geolocalizacion])
        
        # Exportar productos
        productos_path = os.path.join(csv_dir, 'productos.csv')
        with open(productos_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id_producto', 'nombre', 'categoria', 'unidad_medida', 'descripcion'])
            for p in Producto.objects.all():
                writer.writerow([p.id_producto, p.nombre, p.categoria, p.unidad_medida, p.descripcion])
        
        # Exportar precios (puede ser un archivo grande)
        precios_path = os.path.join(csv_dir, 'precios.csv')
        with open(precios_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id_precio', 'id_producto', 'id_supermercado', 'precio', 'fecha_actualizacion'])
            # Exportar en lotes para evitar problemas de memoria
            batch_size = 5000
            total_precios = Precio.objects.count()
            
            for offset in range(0, total_precios, batch_size):
                for p in Precio.objects.all()[offset:offset+batch_size]:
                    writer.writerow([
                        p.id_precio, 
                        p.id_producto.id_producto, 
                        p.id_supermercado.id_supermercado, 
                        p.precio, 
                        p.fecha_actualizacion
                    ])
        
        self.stdout.write(self.style.SUCCESS(f'Datos exportados a: {csv_dir}'))