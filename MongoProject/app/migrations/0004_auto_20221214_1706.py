# Generated by Django 3.1.3 on 2022-12-14 17:06

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20221214_1702'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
                ('surname', models.CharField(max_length=32)),
                ('email', models.CharField(max_length=32)),
                ('balance', models.FloatField(default=6)),
                ('trend', models.FloatField(default=0)),
                ('enrollment', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.customer'),
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
