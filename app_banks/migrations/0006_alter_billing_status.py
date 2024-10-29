# Generated by Django 5.1.1 on 2024-10-26 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_banks', '0005_remove_billing_key_dictkey_remove_billing_key_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billing',
            name='status',
            field=models.CharField(choices=[('created', 'Criado'), ('registered', 'Registrado'), ('canceled', 'Cancelado'), ('paid', 'Pago'), ('overdue', 'Vencido'), ('protest', 'Protestado'), ('updating', 'Atualizando'), ('processing_payment', 'Processando Pagamento'), ('error', 'Erro')], default='created', max_length=20),
        ),
    ]
