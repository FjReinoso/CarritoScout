#docker exec -it carrito_django bash
#python manage.py generar_datos_prueba --productos 500 --borrar

# Hacer las migraciones
docker-compose exec web python manage.py makemigrations

# Aplicar las migraciones
docker-compose exec web python manage.py migrate

# Ver el estado de las migraciones
docker-compose exec web python manage.py showmigrations