# Generated by Django 5.0.1 on 2024-01-16 08:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authors', '0002_customuser_shopping_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='shopping_cart',
        ),
    ]
