# Generated by Django 3.1.3 on 2023-01-02 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20230102_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='balance',
            field=models.FloatField(default=3),
        ),
    ]
