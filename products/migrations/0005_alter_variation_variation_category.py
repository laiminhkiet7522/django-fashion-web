# Generated by Django 5.1.4 on 2024-12-24 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_product_id_alter_productimage_id_variation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('Color', 'Color'), ('Size', 'Size')], max_length=100),
        ),
    ]
