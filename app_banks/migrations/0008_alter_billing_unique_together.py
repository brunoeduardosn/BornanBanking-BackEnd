# Generated by Django 5.1.1 on 2024-10-29 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_banks', '0007_remove_bank_config_alter_billing_document_kind'),
        ('app_core', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='billing',
            unique_together={('tenant', 'document', 'bank_number')},
        ),
    ]
