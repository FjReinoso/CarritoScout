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