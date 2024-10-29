# Generated by Django 5.1.1 on 2024-10-29 15:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_banks', '0008_alter_billing_unique_together'),
        ('app_santander', '0011_remove_santanderbillinglog_billing'),
    ]

    operations = [
        migrations.AddField(
            model_name='santanderbillinglog',
            name='billing',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app_banks.billing'),
            preserve_default=False,
        ),
    ]