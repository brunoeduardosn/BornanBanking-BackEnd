# Generated by Django 5.1.1 on 2024-10-28 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_santander', '0010_santanderbillinglog_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='santanderbillinglog',
            name='billing',
        ),
    ]
