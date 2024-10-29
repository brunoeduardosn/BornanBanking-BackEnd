from io import BytesIO
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime, timedelta, date
from decimal import Decimal

def send_mail(
    template_name: str,
    context: dict,
    subject: str,
    from_email: str,
    to: list[str],
    cc: list[str] = None,
    single_email: bool = False,
    reply_to: list[str] = None,
    attachment: list[tuple[str:BytesIO]] = None,
):
    """
    Função para enviar e-mail utilizando um template personalizado.

    Parâmetros:
    - template_name (str): O nome do template a ser utilizado para o corpo do e-mail.
    - context (dict): O contexto contendo as variáveis a serem utilizadas no template.
    - subject (str): O assunto do e-mail.
    - from_email (str): O endereço de e-mail remetente.
    - to (list[str]): A lista de endereços de e-mail dos destinatários.
    - cc (list[str], opcional): A lista de endereços de e-mail para cópia (CC). Padrão é None.
    - single_email (bool, opcional): Define se o e-mail será enviado individualmente para cada destinatário.
      Se True, cada destinatário receberá o e-mail como se fosse o único destinatário. Padrão é False.
    - reply_to (list[str], opcional): A lista de endereços de e-mail para resposta. Padrão é None.
    - attachment (list[tuple[str, BytesIO]], opcional): A lista de anexos do e-mail.
      Cada anexo é uma tupla contendo o nome do arquivo e o conteúdo do arquivo em BytesIO. Padrão é None.

    Exemplo de uso:
    send_mail(
        template_name='meu_template.html',
        context={'nome': 'Fulano', 'saldo': 100.0},
        subject='Importante: Saldo Atualizado',
        from_email='meuemail@example.com',
        to=['destinatario1@example.com', 'destinatario2@example.com'],
        cc=['copia1@example.com', 'copia2@example.com'],
        single_email=True,
        reply_to=['responder@example.com'],
        attachment=[('relatorio.pdf', bytes_io_object)],
    )
    
    
    send_mail(
        template_name="billing/billing_notification.html",
        context={
            "logo": logo_url,
            "amount": financialassetpaymentcommit.payment_commitment.amount,
            "due_date": billing.due_date,
            "description": "Geração de Cobrança",
            "financial_agent": financial_product_contract.financial_product.financial_agent.organization.name,
        },
        subject="Notificação de Cobrança",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
        single_email=True,
    )
    """
    connection = get_connection(fail_silently=True)
    connection.open()
    try:
        html_content = render_to_string(template_name, context)
        message = strip_tags(html_content)
        if single_email:
            for to_email in to:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=[to_email],
                    connection=connection,
                    cc=cc,
                    reply_to=reply_to,
                )
                msg.attach_alternative(html_content, "text/html")
                if attachment:
                    for name, content in attachment:
                        msg.attach(name, content.read())
                msg.send()
        else:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=from_email,
                to=to,
                connection=connection,
                cc=cc,
                reply_to=reply_to,
            )
            msg.attach_alternative(html_content, "text/html")
            if attachment:
                for name, content in attachment:
                    msg.attach(name, content.read())
            msg.send()
    except Exception as e:
        return str(e)

    connection.close()


def remove_empty_fields(data):
    """
    Remove campos com valores None ou vazios de um dicionário.
    """
    if isinstance(data, dict):
        return {k: remove_empty_fields(v) for k, v in data.items() if v not in [None, '', [], {}]}
    elif isinstance(data, list):
        return [remove_empty_fields(v) for v in data if v not in [None, '', [], {}]]
    else:
        return data

def convert_decimal_to_str(data):
    """
    Converte valores Decimal para string em um dicionário.
    """
    if isinstance(data, dict):
        return {k: convert_decimal_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_str(v) for v in data]
    elif isinstance(data, Decimal):
        return str(data)
    else:
        return data

def convert_date_to_str(data):
    """
    Converte valores date para string em um dicionário.
    """
    if isinstance(data, dict):
        return {k: convert_date_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_date_to_str(v) for v in data]
    elif isinstance(data, (datetime, date)):
        return data.strftime('%Y-%m-%d')
    else:
        return data