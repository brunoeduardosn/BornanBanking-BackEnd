# Generated by Django 5.1.1 on 2024-10-24 18:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_banks', '0001_initial'),
        ('app_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_core.tenant'),
        ),
        migrations.AddField(
            model_name='billing',
            name='bank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_banks.bank'),
        ),
        migrations.AddField(
            model_name='billing',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_core.tenant'),
        ),
    ]
