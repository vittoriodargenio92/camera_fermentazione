# Generated by Django 3.1.3 on 2020-12-07 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fermentazione', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fermentation',
            name='max_temp',
            field=models.FloatField(default=22.0),
        ),
        migrations.AlterField(
            model_name='fermentation',
            name='min_temp',
            field=models.FloatField(default=18.0),
        ),
    ]
