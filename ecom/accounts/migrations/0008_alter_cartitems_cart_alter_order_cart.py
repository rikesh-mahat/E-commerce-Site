# Generated by Django 4.1.5 on 2023-01-26 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_cart_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitems',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cart_items', to='accounts.cart'),
        ),
        migrations.AlterField(
            model_name='order',
            name='cart',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='accounts.cart'),
        ),
    ]