# Acceder al contenedor de Django
docker exec -it carrito_django bash

# Generar datos de prueba 
python manage.py generar_datos_prueba --productos 500 --borrar

# Hacer las migraciones
 python manage.py makemigrations

# Aplicar las migraciones
 python manage.py migrate

# Ver el estado de las migraciones
 python manage.py showmigrations

# Apagar maquinas 
flyctl machines list -a carritoscout --json | ConvertFrom-Json | ForEach-Object { flyctl machine stop $_.id -a carritoscout }
flyctl machines list -a carritodb --json | ConvertFrom-Json | ForEach-Object { flyctl machine stop $_.id -a carritodb }

# Encender máquinas
flyctl machines list -a carritoscout --json | ConvertFrom-Json | ForEach-Object { flyctl machine start $_.id -a carritoscout }
flyctl machines list -a carritodb --json | ConvertFrom-Json | ForEach-Object { flyctl machine start $_.id -a carritodb }

# Comandos varios de fly.io

## Realiza el deploy(directorio si o si)
flyctl deploy

## Ejecuta migraciones en la máquina de Fly.io
flyctl ssh console -C "python manage.py migrate"

## Generar datos de prueba solo productos
flyctl ssh console -C "python manage.py generar_datos_prueba --productos 500 --borrar"

# Generar precios históricos (siempre despues de productos)
flyctl ssh console -C "python manage.py generar_historial_precios"

PS C:\Users\ifjre\OneDrive\Documentos\GitHub\CarritoScout> flyctl ssh console -C "python manage.py generar_datos_prueba --productos 500 --borrar"
No machine specified, using 68321eefd19938 in region cdg
Connecting to fdaa:1c:1374:a7b:39d:d706:f2d:2... complete
Borrando datos existentes...
Creando supermercados...
  - Creado supermercado: Mercadona
  - Creado supermercado: Dia
  - Creado supermercado: Lidl
  - Creado supermercado: Alcampo
  - Creado supermercado: Consum
  - Creado supermercado: Ahorramas
Generando 500 productos nuevos...
Generando precios para 500 productos...
--- RESUMEN DE DATOS GENERADOS ---
Supermercados: 6
Productos: 500
Precios: 2229
--- DISTRIBUCIÓN POR CATEGORÍAS ---
Alimentación fresca: 60 productos
Alimentación seca y no perecedera: 64 productos
Congelados: 55 productos
Dulces y aperitivos: 49 productos
Bebidas: 62 productos
Higiene personal y salud: 51 productos
Limpieza del hogar: 53 productos
Bebé y maternidad: 59 productos
Mascotas: 47 productos

PS C:\Users\ifjre\OneDrive\Documentos\GitHub\CarritoScout> flyctl ssh console -C "python manage.py generar_historial_precios"
No machine specified, using 68321eefd19938 in region cdg
Connecting to fdaa:1c:1374:a7b:39d:d706:f2d:2... complete
Se han generado 11138 precios históricos para los productos y supermercados existentes.
PS C:\Users\ifjre\OneDrive\Documentos\GitHub\CarritoScout>