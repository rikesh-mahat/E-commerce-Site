# Generated by Django 4.1.5 on 2023-01-28 03:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_profile_mobile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='is_paid',
            new_name='is_checkedout',
        ),
    ]