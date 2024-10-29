# Generated by Django 5.1.1 on 2024-10-26 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_banks', '0004_bank_environment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billing',
            name='key_dictkey',
        ),
        migrations.RemoveField(
            model_name='billing',
            name='key_type',
        ),
        migrations.RemoveField(
            model_name='billing',
            name='messages',
        ),
        migrations.RemoveField(
            model_name='billing',
            name='txid',
        ),
        migrations.AddField(
            model_name='billing',
            name='deduction_value',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
        migrations.AddField(
            model_name='billing',
            name='fine_value',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
        migrations.AddField(
            model_name='billing',
            name='interest_value',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
        migrations.AddField(
            model_name='billing',
            name='protest_type',
            field=models.CharField(choices=[('SEM_PROTESTO', 'Sem Protesto'), ('DIAS_CORRIDOS', 'Dias Corridos'), ('DIAS_UTEIS', 'Dias útes'), ('CADASTRO_CONVENIO', 'Cadastro do Convênio')], default='CADASTRO_CONVENIO'),
        ),
        migrations.AddField(
            model_name='billing',
            name='status',
            field=models.CharField(choices=[('created', 'Criado'), ('registered', 'Registrado'), ('canceled', 'Cancelado'), ('paid', 'Pago'), ('overdue', 'Vencido'), ('protest', 'Protestado'), ('updating', 'Atualizando'), ('processing_payment', 'Processando Pagamento')], default='created', max_length=20),
        ),
        migrations.AlterField(
            model_name='billing',
            name='document_kind',
            field=models.CharField(choices=[('DUPLICATA_MERCANTIL', 'Duplicata Mercantil'), ('DUPLICATA_SERVICO', 'Duplicata de Serviço'), ('LC', 'Letra de Câmbio'), ('NOTA_PROMISSORIA', 'Nota Promissória'), ('NOTA_PROMISSORIA_RURAL', 'Nota Promissória Rural'), ('RECIBO', 'Recibo'), ('APOLICE_SEGURO', 'Apólice de Seguro'), ('BOLETO_CARTAO_CREDITO', 'Boleto de Cartão de Crédito'), ('BOLETO_PROPOSTA', 'Boleto de Proposta'), ('BOLETO_DEPOSITO_APORTE', 'Boleto Depósito Aporte'), ('CHEQUE', 'Cheque'), ('NOTA_PROMISSORIA_DIRETA', 'Nota Promissória Direta'), ('OUTROS', 'Outros')]),
        ),
    ]
