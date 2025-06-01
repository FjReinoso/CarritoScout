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

#docker exec -it nombre_del_contenedor bash
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

        # Definir supermercados principales en España
        supermercados = [
            {"nombre": "Mercadona", "direccion": "Calle Valencia 123, Madrid", "geolocalizacion": "40.416775,-3.703790"},
            {"nombre": "Carrefour", "direccion": "Avenida Diagonal 456, Barcelona", "geolocalizacion": "41.385064,2.173404"},
            {"nombre": "Dia", "direccion": "Calle Gran Vía 789, Madrid", "geolocalizacion": "40.420160,-3.704700"},
            {"nombre": "Lidl", "direccion": "Avenida Andalucía 321, Sevilla", "geolocalizacion": "37.389092,-5.984459"},
            {"nombre": "Aldi", "direccion": "Paseo Castellana 654, Madrid", "geolocalizacion": "40.433852,-3.690780"},
            {"nombre": "Eroski", "direccion": "Calle Urbieta 987, San Sebastián", "geolocalizacion": "43.312527,-1.981634"},
            {"nombre": "El Corte Inglés", "direccion": "Plaza Cataluña 5, Barcelona", "geolocalizacion": "41.386874,2.170047"},
            {"nombre": "Alcampo", "direccion": "Avenida Constitución 234, Zaragoza", "geolocalizacion": "41.648823,-0.889085"},
            {"nombre": "Consum", "direccion": "Avenida del Puerto 567, Valencia", "geolocalizacion": "39.469907,-0.376288"},
            {"nombre": "Ahorramas", "direccion": "Calle Orense 890, Madrid", "geolocalizacion": "40.456321,-3.694560"},
            {"nombre": "Hipercor", "direccion": "Avenida Maisonnave 432, Alicante", "geolocalizacion": "38.345996,-0.490686"},
            {"nombre": "BonArea", "direccion": "Carretera Nacional II, Km 510, Lleida", "geolocalizacion": "41.617583,0.620020"},
            {"nombre": "MAS", "direccion": "Avenida de la Palmera 789, Sevilla", "geolocalizacion": "37.371490,-5.988380"},
            {"nombre": "Condis", "direccion": "Rambla Catalunya 321, Barcelona", "geolocalizacion": "41.396234,2.160844"}
        ]

        # Definir categorías según los filtros de la interfaz
        categorias = ["Lacteos", "Pan", "Limpieza", "Frutas", "Verduras", "Bebidas", 
                     "Carnes", "Pescados", "Congelados", "Conservas", "Cereales", "Dulces", "Snacks"]

        # Unidades de medida comunes
        unidades = ["kg", "g", "l", "ml", "unidad", "pack", "botella", "lata", "docena", "bandeja"]

        # Diccionarios para productos por categoría
        productos_por_categoria = {
            "Lacteos": [
                {"nombre": "Leche entera", "descripcion": "Leche de vaca entera UHT"},
                {"nombre": "Leche semidesnatada", "descripcion": "Leche de vaca semidesnatada UHT"},
                {"nombre": "Leche desnatada", "descripcion": "Leche de vaca desnatada UHT"},
                {"nombre": "Yogur natural", "descripcion": "Yogur natural sin azúcar añadido"},
                {"nombre": "Yogur de fresa", "descripcion": "Yogur con sabor a fresa"},
                {"nombre": "Yogur griego", "descripcion": "Yogur estilo griego cremoso"},
                {"nombre": "Queso manchego", "descripcion": "Queso curado de oveja manchega"},
                {"nombre": "Queso fresco", "descripcion": "Queso fresco tipo burgos"},
                {"nombre": "Queso rallado", "descripcion": "Mezcla de quesos rallados para pasta"},
                {"nombre": "Mantequilla", "descripcion": "Mantequilla tradicional sin sal"},
                {"nombre": "Nata para cocinar", "descripcion": "Nata líquida para cocinar"},
                {"nombre": "Nata para montar", "descripcion": "Nata para montar postres"},
                {"nombre": "Batido de chocolate", "descripcion": "Batido sabor chocolate"},
                {"nombre": "Batido de fresa", "descripcion": "Batido sabor fresa"},
                {"nombre": "Queso en lonchas", "descripcion": "Lonchas de queso para sandwich"},
                {"nombre": "Kéfir", "descripcion": "Bebida fermentada probiótica"}
            ],
            "Pan": [
                {"nombre": "Pan de molde integral", "descripcion": "Pan de molde con harina integral"},
                {"nombre": "Pan de molde blanco", "descripcion": "Pan de molde tradicional"},
                {"nombre": "Baguette", "descripcion": "Baguette tradicional recién horneada"},
                {"nombre": "Pan rústico", "descripcion": "Pan de masa madre con corteza crujiente"},
                {"nombre": "Pan de centeno", "descripcion": "Pan elaborado con harina de centeno"},
                {"nombre": "Chapata", "descripcion": "Pan tipo chapata italiano"},
                {"nombre": "Pan rallado", "descripcion": "Pan rallado para rebozar"},
                {"nombre": "Pan hamburguesa", "descripcion": "Pack de panes para hamburguesa"},
                {"nombre": "Pan hot dog", "descripcion": "Pack de panes para hot dog"},
                {"nombre": "Pan sin gluten", "descripcion": "Pan especial sin gluten"},
                {"nombre": "Panecillos", "descripcion": "Panecillos individuales"},
                {"nombre": "Pan tostado", "descripcion": "Rebanadas de pan tostado"}
            ],
            "Limpieza": [
                {"nombre": "Detergente lavadora", "descripcion": "Detergente líquido para lavadora"},
                {"nombre": "Suavizante", "descripcion": "Suavizante con aroma fresco"},
                {"nombre": "Lavavajillas", "descripcion": "Detergente lavavajillas a mano"},
                {"nombre": "Pastillas lavavajillas", "descripcion": "Pastillas para lavavajillas automático"},
                {"nombre": "Limpiador multiusos", "descripcion": "Limpiador para múltiples superficies"},
                {"nombre": "Lejía", "descripcion": "Lejía para desinfección"},
                {"nombre": "Amoniaco", "descripcion": "Amoniaco perfumado limpiador"},
                {"nombre": "Limpiador baño", "descripcion": "Limpiador específico para baño"},
                {"nombre": "Limpiador cocina", "descripcion": "Limpiador desengrasante para cocina"},
                {"nombre": "Papel higiénico", "descripcion": "Rollo de papel higiénico doble capa"},
                {"nombre": "Papel de cocina", "descripcion": "Rollo de papel de cocina extrafuerte"},
                {"nombre": "Servilletas", "descripcion": "Pack de servilletas de papel"},
                {"nombre": "Bolsas de basura", "descripcion": "Bolsas de basura resistentes"},
                {"nombre": "Estropajos", "descripcion": "Pack de estropajos para cocina"},
                {"nombre": "Escoba", "descripcion": "Escoba con cerdas sintéticas"}
            ],
            "Frutas": [
                {"nombre": "Manzanas Golden", "descripcion": "Manzanas variedad Golden"},
                {"nombre": "Manzanas Reineta", "descripcion": "Manzanas variedad Reineta"},
                {"nombre": "Plátanos de Canarias", "descripcion": "Plátanos de las Islas Canarias"},
                {"nombre": "Naranjas de mesa", "descripcion": "Naranjas para consumo directo"},
                {"nombre": "Naranjas para zumo", "descripcion": "Naranjas para exprimir"},
                {"nombre": "Limones", "descripcion": "Limones frescos"},
                {"nombre": "Peras conferencia", "descripcion": "Peras variedad conferencia"},
                {"nombre": "Fresas", "descripcion": "Fresas frescas de temporada"},
                {"nombre": "Piña", "descripcion": "Piña tropical entera"},
                {"nombre": "Kiwi", "descripcion": "Kiwis verdes"},
                {"nombre": "Aguacate", "descripcion": "Aguacates maduración controlada"},
                {"nombre": "Mango", "descripcion": "Mango tropical maduro"},
                {"nombre": "Melón", "descripcion": "Melón tipo Galia"},
                {"nombre": "Sandía", "descripcion": "Sandía sin pepitas"},
                {"nombre": "Uvas", "descripcion": "Racimo de uvas blancas sin semillas"}
            ],
            "Verduras": [
                {"nombre": "Tomates", "descripcion": "Tomates para ensalada"},
                {"nombre": "Lechuga iceberg", "descripcion": "Lechuga iceberg fresca"},
                {"nombre": "Cebolla", "descripcion": "Cebollas blancas"},
                {"nombre": "Patatas", "descripcion": "Patatas para cocinar"},
                {"nombre": "Zanahorias", "descripcion": "Zanahorias frescas"},
                {"nombre": "Pimiento verde", "descripcion": "Pimientos verdes italianos"},
                {"nombre": "Pimiento rojo", "descripcion": "Pimientos rojos dulces"},
                {"nombre": "Calabacín", "descripcion": "Calabacín verde fresco"},
                {"nombre": "Berenjena", "descripcion": "Berenjena negra"},
                {"nombre": "Pepino", "descripcion": "Pepino fresco"},
                {"nombre": "Ajos", "descripcion": "Cabeza de ajos"},
                {"nombre": "Champiñones", "descripcion": "Bandeja de champiñones laminados"},
                {"nombre": "Espinacas", "descripcion": "Espinacas frescas en hojas"},
                {"nombre": "Brócoli", "descripcion": "Brócoli fresco"},
                {"nombre": "Coliflor", "descripcion": "Coliflor blanca"}
            ],
            "Bebidas": [
                {"nombre": "Agua mineral", "descripcion": "Agua mineral natural sin gas"},
                {"nombre": "Agua con gas", "descripcion": "Agua mineral con gas"},
                {"nombre": "Coca-Cola", "descripcion": "Refresco de cola Coca-Cola"},
                {"nombre": "Fanta Naranja", "descripcion": "Refresco de naranja Fanta"},
                {"nombre": "Fanta Limón", "descripcion": "Refresco de limón Fanta"},
                {"nombre": "Cerveza Mahou", "descripcion": "Cerveza rubia Mahou"},
                {"nombre": "Cerveza Estrella Galicia", "descripcion": "Cerveza rubia Estrella Galicia"},
                {"nombre": "Vino tinto", "descripcion": "Vino tinto Rioja Crianza"},
                {"nombre": "Vino blanco", "descripcion": "Vino blanco Rueda Verdejo"},
                {"nombre": "Zumo de naranja", "descripcion": "Zumo de naranja natural refrigerado"},
                {"nombre": "Zumo de piña", "descripcion": "Zumo de piña sin azúcar añadido"},
                {"nombre": "Café molido", "descripcion": "Café molido natural"},
                {"nombre": "Cápsulas café", "descripcion": "Cápsulas de café compatibles"},
                {"nombre": "Té verde", "descripcion": "Té verde en bolsitas"},
                {"nombre": "Cerveza sin alcohol", "descripcion": "Cerveza rubia sin alcohol"}
            ],
            "Carnes": [
                {"nombre": "Pechuga de pollo", "descripcion": "Filetes de pechuga de pollo"},
                {"nombre": "Muslos de pollo", "descripcion": "Muslos de pollo frescos"},
                {"nombre": "Pollo entero", "descripcion": "Pollo entero fresco"},
                {"nombre": "Carne picada mixta", "descripcion": "Carne picada de cerdo y ternera"},
                {"nombre": "Filetes de ternera", "descripcion": "Filetes de primera de ternera"},
                {"nombre": "Costillas de cerdo", "descripcion": "Costillas de cerdo frescas"},
                {"nombre": "Solomillo de cerdo", "descripcion": "Solomillo de cerdo entero"},
                {"nombre": "Chuletas de cordero", "descripcion": "Chuletas de cordero lechal"},
                {"nombre": "Hamburguesas", "descripcion": "Hamburguesas de ternera"},
                {"nombre": "Salchichas frankfurt", "descripcion": "Salchichas tipo frankfurt"},
                {"nombre": "Lomo de cerdo", "descripcion": "Cinta de lomo fresco"},
                {"nombre": "Jamón york", "descripcion": "Jamón cocido extra en lonchas"}
            ],
            "Pescados": [
                {"nombre": "Merluza", "descripcion": "Filetes de merluza fresca"},
                {"nombre": "Salmón", "descripcion": "Lomos de salmón fresco"},
                {"nombre": "Dorada", "descripcion": "Dorada fresca entera"},
                {"nombre": "Bacalao", "descripcion": "Filetes de bacalao fresco"},
                {"nombre": "Atún", "descripcion": "Lomos de atún fresco"},
                {"nombre": "Mejillones", "descripcion": "Mejillones frescos"},
                {"nombre": "Gambas", "descripcion": "Gambas crudas peladas"},
                {"nombre": "Calamares", "descripcion": "Anillas de calamar fresco"},
                {"nombre": "Langostinos", "descripcion": "Langostinos cocidos"},
                {"nombre": "Palitos de cangrejo", "descripcion": "Palitos de cangrejo refrigerados"},
                {"nombre": "Boquerones", "descripcion": "Boquerones frescos"},
                {"nombre": "Sardinas", "descripcion": "Sardinas frescas"}
            ],
            "Congelados": [
                {"nombre": "Guisantes congelados", "descripcion": "Bolsa de guisantes congelados"},
                {"nombre": "Judías verdes congeladas", "descripcion": "Bolsa de judías verdes congeladas"},
                {"nombre": "Pizza margarita", "descripcion": "Pizza margarita congelada"},
                {"nombre": "Pizza 4 quesos", "descripcion": "Pizza cuatro quesos congelada"},
                {"nombre": "Helado de vainilla", "descripcion": "Helado de vainilla en tarrina"},
                {"nombre": "Helado de chocolate", "descripcion": "Helado de chocolate en tarrina"},
                {"nombre": "Croquetas de jamón", "descripcion": "Croquetas de jamón congeladas"},
                {"nombre": "Empanadillas de atún", "descripcion": "Empanadillas de atún congeladas"},
                {"nombre": "Patatas fritas congeladas", "descripcion": "Bolsa de patatas fritas congeladas"},
                {"nombre": "Verduras para sopa", "descripcion": "Mezcla de verduras para sopa"},
                {"nombre": "Merluza congelada", "descripcion": "Filetes de merluza congelada"},
                {"nombre": "Gambas peladas congeladas", "descripcion": "Gambas peladas congeladas"}
            ],
            "Conservas": [
                {"nombre": "Atún en aceite", "descripcion": "Latas de atún en aceite de girasol"},
                {"nombre": "Atún al natural", "descripcion": "Latas de atún al natural"},
                {"nombre": "Mejillones en escabeche", "descripcion": "Lata de mejillones en escabeche"},
                {"nombre": "Sardinas en aceite", "descripcion": "Lata de sardinas en aceite de oliva"},
                {"nombre": "Espárragos blancos", "descripcion": "Lata de espárragos blancos"},
                {"nombre": "Maíz dulce", "descripcion": "Lata de maíz dulce"},
                {"nombre": "Aceitunas rellenas", "descripcion": "Lata de aceitunas rellenas de anchoa"},
                {"nombre": "Aceitunas negras", "descripcion": "Lata de aceitunas negras sin hueso"},
                {"nombre": "Pimientos del piquillo", "descripcion": "Lata de pimientos del piquillo"},
                {"nombre": "Tomate frito", "descripcion": "Bote de tomate frito casero"},
                {"nombre": "Tomate triturado", "descripcion": "Bote de tomate natural triturado"},
                {"nombre": "Garbanzos cocidos", "descripcion": "Bote de garbanzos cocidos"}
            ],
            "Cereales": [
                {"nombre": "Arroz redondo", "descripcion": "Arroz grano redondo"},
                {"nombre": "Arroz largo", "descripcion": "Arroz grano largo"},
                {"nombre": "Arroz basmati", "descripcion": "Arroz basmati aromático"},
                {"nombre": "Pasta espaguetis", "descripcion": "Pasta tipo espaguetis"},
                {"nombre": "Pasta macarrones", "descripcion": "Pasta tipo macarrones"},
                {"nombre": "Pasta fideos", "descripcion": "Pasta tipo fideos finos"},
                {"nombre": "Harina de trigo", "descripcion": "Harina de trigo común"},
                {"nombre": "Harina integral", "descripcion": "Harina integral de trigo"},
                {"nombre": "Pan rallado", "descripcion": "Pan rallado para rebozar"},
                {"nombre": "Cereales desayuno", "descripcion": "Cereales de desayuno tipo corn flakes"},
                {"nombre": "Cereales integrales", "descripcion": "Cereales integrales con fibra"},
                {"nombre": "Avena", "descripcion": "Copos de avena para desayuno"}
            ],
            "Dulces": [
                {"nombre": "Chocolate con leche", "descripcion": "Tableta de chocolate con leche"},
                {"nombre": "Chocolate negro", "descripcion": "Tableta de chocolate negro 70%"},
                {"nombre": "Chocolate blanco", "descripcion": "Tableta de chocolate blanco"},
                {"nombre": "Galletas maría", "descripcion": "Paquete de galletas tipo maría"},
                {"nombre": "Galletas digestive", "descripcion": "Galletas digestive integral"},
                {"nombre": "Galletas chocolate", "descripcion": "Galletas con chips de chocolate"},
                {"nombre": "Croissants", "descripcion": "Pack de croissants"},
                {"nombre": "Magdalenas", "descripcion": "Pack de magdalenas"},
                {"nombre": "Donuts", "descripcion": "Pack de donuts glaseados"},
                {"nombre": "Mermelada fresa", "descripcion": "Mermelada de fresa"},
                {"nombre": "Mermelada melocotón", "descripcion": "Mermelada de melocotón"},
                {"nombre": "Nocilla", "descripcion": "Crema de cacao y avellanas"}
            ],
            "Snacks": [
                {"nombre": "Patatas fritas", "descripcion": "Bolsa de patatas fritas lisas"},
                {"nombre": "Patatas fritas onduladas", "descripcion": "Bolsa de patatas fritas onduladas"},
                {"nombre": "Frutos secos", "descripcion": "Mezcla de frutos secos"},
                {"nombre": "Almendras", "descripcion": "Almendras tostadas y saladas"},
                {"nombre": "Cacahuetes", "descripcion": "Cacahuetes tostados con sal"},
                {"nombre": "Pipas de girasol", "descripcion": "Pipas de girasol tostadas"},
                {"nombre": "Aceitunas", "descripcion": "Aceitunas verdes con anchoa"},
                {"nombre": "Cortezas", "descripcion": "Cortezas de cerdo"},
                {"nombre": "Gusanitos", "descripcion": "Snacks de maíz sabor queso"},
                {"nombre": "Nachos", "descripcion": "Nachos de maíz"},
                {"nombre": "Palomitas microondas", "descripcion": "Palomitas para microondas"}
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
                    # Tomar todos los productos de la lista o hasta 10 por categoría
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
                    for _ in range(productos_restantes):
                        categoria = random.choice(categorias)
                        # Intentar elegir un producto de la categoría que no hayamos usado
                        productos_disponibles = productos_por_categoria.get(categoria, [])
                        if productos_disponibles:
                            producto_data = random.choice(productos_disponibles)
                            nombre = producto_data["nombre"]
                            descripcion = producto_data["descripcion"]
                        else:
                            # Si no hay productos predefinidos o se agotaron, generar uno aleatorio
                            nombre = f"Producto {categoria} {_}"
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
    
    def _get_unidad_for_producto(self, nombre, unidades):
        """Determina la unidad de medida más adecuada según el nombre del producto"""
        nombre = nombre.lower()
        if any(word in nombre for word in ["leche", "zumo", "agua", "vino", "cerveza", "aceite"]):
            return "l" if "agua" in nombre or "leche" in nombre else "ml"
        elif any(word in nombre for word in ["detergente", "suavizante", "champu"]):
            return "l"
        elif any(word in nombre for word in ["manzana", "pera", "plátano", "naranja", "patata", "cebolla", "tomate"]):
            return "kg"
        elif any(word in nombre for word in ["papel", "servilleta", "rollo"]):
            return "pack"
        elif any(word in nombre for word in ["galleta", "cereal", "snack", "patata"]):
            return "g"
        else:
            return random.choice(unidades)
    
    def _get_precio_base(self, categoria):
        """Determina un precio base según la categoría del producto"""
        rangos_precio = {
            "Lacteos": (0.75, 3.50),
            "Pan": (0.60, 2.50),
            "Limpieza": (1.50, 6.00),
            "Frutas": (1.20, 4.50),
            "Verduras": (0.90, 3.50),
            "Bebidas": (0.80, 12.00),
            "Carnes": (3.50, 15.00),
            "Pescados": (4.50, 18.00),
            "Congelados": (2.00, 7.50),
            "Conservas": (0.90, 5.00),
            "Cereales": (0.80, 3.00),
            "Dulces": (1.20, 4.50),
            "Snacks": (0.90, 3.50)
        }
        
        rango = rangos_precio.get(categoria, (1.00, 5.00))
        return round(random.uniform(rango[0], rango[1]), 2)
    
    def _get_factor_precio(self, nombre_supermercado):
        """Determina un factor de precio según el supermercado"""
        factores = {
            "Mercadona": 1.00,
            "Carrefour": 1.02,
            "Dia": 0.95,
            "Lidl": 0.93,
            "Aldi": 0.94,
            "Eroski": 1.03,
            "El Corte Inglés": 1.15,
            "Alcampo": 0.98,
            "Consum": 1.04,
            "Ahorramas": 0.97,
            "Hipercor": 1.12,
            "BonArea": 0.92,
            "MAS": 0.99,
            "Condis": 1.05
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
        
        self.stdout.write(self.style.SUCCESS(f'Datos exportados a:{csv_dir}'))