# Generated by Django 3.1.3 on 2020-12-07 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fermentazione', '0002_auto_20201207_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='register',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
