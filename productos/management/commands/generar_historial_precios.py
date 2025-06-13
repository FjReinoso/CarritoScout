from django.core.management.base import BaseCommand
from productos.models import Supermercado, Producto, Precio
from django.utils import timezone
from datetime import timedelta
import random
##python manage.py generar_historial_precios
class Command(BaseCommand):
    help = 'Genera 5 sets de precios históricos (más baratos) para todos los productos y supermercados existentes, con fechas de 1 a 5 meses atrás.'

    def handle(self, *args, **options):
        supermercados = list(Supermercado.objects.all())
        productos = list(Producto.objects.all())
        if not supermercados or not productos:
            self.stdout.write(self.style.ERROR('No hay supermercados o productos en la base de datos.'))
            return

        precios_nuevos = []
        meses_historico = 5
        total = 0
        for producto in productos:
            for supermercado in supermercados:
                # Tomar el precio actual más reciente como referencia
                precio_actual = Precio.objects.filter(
                    id_producto=producto,
                    id_supermercado=supermercado
                ).order_by('-fecha_actualizacion').first()
                if not precio_actual:
                    continue

                precio_base = float(precio_actual.precio)
                for meses_atras in range(1, meses_historico + 1):
                    # El precio en el pasado es más barato (hasta un 15% menos hace 5 meses)
                    factor_descuento = 1 - (0.03 * meses_atras + random.uniform(0, 0.02))  # 3-5% menos por mes
                    precio_hist = round(precio_base * factor_descuento, 2)
                    fecha_hist = timezone.now() - timedelta(days=30 * meses_atras + random.randint(0, 5))
                    # Evitar duplicados para la misma fecha
                    if not Precio.objects.filter(id_producto=producto, id_supermercado=supermercado, fecha_actualizacion__date=fecha_hist.date()).exists():
                        precio_historico = Precio(
                            id_producto=producto,
                            id_supermercado=supermercado,
                            precio=precio_hist,
                            fecha_actualizacion=fecha_hist
                        )
                        precios_nuevos.append(precio_historico)
                        total += 1
                    if len(precios_nuevos) >= 1000:
                        Precio.objects.bulk_create(precios_nuevos)
                        precios_nuevos = []
        if precios_nuevos:
            Precio.objects.bulk_create(precios_nuevos)
        self.stdout.write(self.style.SUCCESS(f'Se han generado {total} precios históricos para los productos y supermercados existentes.'))
