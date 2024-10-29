# Generated by Django 5.1.1 on 2024-10-25 17:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_banks', '0004_bank_environment'),
        ('app_core', '0001_initial'),
        ('app_santander', '0003_configuration'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Billing',
            new_name='SantanderBilling',
        ),
        migrations.RenameModel(
            old_name='BillingLog',
            new_name='SantanderBillingLog',
        ),
        migrations.RenameModel(
            old_name='BillingPatch',
            new_name='SantanderBillingPatch',
        ),
        migrations.RenameModel(
            old_name='Configuration',
            new_name='SantanderConfiguration',
        ),
        migrations.AlterField(
            model_name='santanderbillinglog',
            name='billing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_banks.billing'),
        ),
        migrations.AlterField(
            model_name='santanderbillingpatch',
            name='billing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_banks.billing'),
        ),
    ]