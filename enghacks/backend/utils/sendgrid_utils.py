from django.conf import settings
from twilio.rest import Client

def send_text(return_body, reply_number):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    Client(account_sid, auth_token).messages.create(
        body=return_body,
        from_=settings.TWILIO_DEFAULT_CALLERID,
        to=reply_number
    )
