
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('productos', '0001_initial'),
        ('carrito', '0004_carrito_nombre'),
    ]

    operations = [
        migrations.AddField(
            model_name='carritoproducto',
            name='supermercado',
            field=models.ForeignKey(
                to='productos.Supermercado',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
                blank=True,
                verbose_name='Supermercado',
            ),
        ),
        migrations.AddField(
            model_name='carritoproducto',
            name='precio_unitario',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='Precio unitario',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='carritoproducto',
            unique_together={('carrito', 'producto', 'supermercado')},
        ),
    ]
