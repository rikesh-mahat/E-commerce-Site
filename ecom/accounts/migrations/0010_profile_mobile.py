# Generated by Django 4.1.5 on 2023-01-26 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_cartitems_cart_alter_order_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='mobile',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
