# Generated by Django 4.1.5 on 2023-01-23 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_cart_cartitems'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
