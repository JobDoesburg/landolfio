from django.conf import settings
from django.core import mail
from django.template import loader


def send_email(
    to: str, subject: str, txt_template: str, html_template, context: dict
) -> None:
    mail.send_mail(
        subject=subject,
        message=loader.render_to_string(txt_template, context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to],
        html_message=loader.render_to_string(html_template, context),
    )
