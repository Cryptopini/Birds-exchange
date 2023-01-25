# Generated by Django 3.1.3 on 2022-12-14 16:37

from django.db import migrations, models
import django.db.models.deletion
import io


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.UUIDField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
                ('surname', models.CharField(max_length=32)),
                ('email', models.CharField(max_length=32)),
                ('balance', models.FloatField(default=9)),
                ('trend', models.FloatField(default=0)),
                ('enrollment', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.UUIDField(auto_created=True, primary_key=True, serialize=False)),
                ('want_to_sell', models.FloatField(max_length=32, null=True)),
                ('want_to_buy', models.FloatField(max_length=32, null=True)),
                ('price', models.FloatField(max_length=32)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=io.open, max_length=32)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.users')),
            ],
        ),
    ]
