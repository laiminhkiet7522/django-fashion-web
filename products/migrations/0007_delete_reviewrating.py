# Generated by Django 5.1.4 on 2025-01-07 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_reviewrating'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ReviewRating',
        ),
    ]