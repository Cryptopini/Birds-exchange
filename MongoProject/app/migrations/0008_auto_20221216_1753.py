# Generated by Django 3.1.3 on 2022-12-16 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20221216_1449'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='id',
            new_name='_id',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='id',
            new_name='_id',
        ),
        migrations.AlterField(
            model_name='customer',
            name='balance',
            field=models.FloatField(default=7),
        ),
    ]
