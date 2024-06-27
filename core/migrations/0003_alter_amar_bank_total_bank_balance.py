# Generated by Django 4.2.4 on 2024-06-27 03:49

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_amar_bank_bank_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amar_bank',
            name='total_bank_balance',
            field=models.DecimalField(decimal_places=2, default={'balance__sum': Decimal('122100.00')}, max_digits=12),
        ),
    ]
