# Generated by Django 3.2.18 on 2023-06-11 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_quasisynonym_initial_weight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quasisynonym',
            name='initial_weight',
            field=models.FloatField(verbose_name='Изначальный вес'),
        ),
    ]
