# Generated by Django 5.1.1 on 2024-10-26 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_santander', '0008_alter_santanderbillinglog_payload_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='santanderbillinglog',
            name='payload',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='santanderbillinglog',
            name='response',
            field=models.TextField(blank=True, null=True),
        ),
    ]