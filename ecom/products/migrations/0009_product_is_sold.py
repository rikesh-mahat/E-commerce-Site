# Generated by Django 4.1.5 on 2023-05-01 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_sold',
            field=models.BooleanField(default=False),
        ),
    ]
