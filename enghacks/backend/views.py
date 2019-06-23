from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from backend.serializers import UserLoginSerializer
from rest_framework.response import Response
from django.conf import settings

from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

@csrf_exempt
def sms_response(request):
    # Start our TwiML response
    resp = MessagingResponse()

    # Add a text message
    msg = resp.message("Test message!")

    # Add a picture message
    msg.media("https://farm8.staticflickr.com/7568/15785724675_999435f19f_k.jpg")

    return HttpResponse(str(resp))

class UserLoginViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer


class SMSDirectionsViewSet(viewsets.ModelViewSet):
    serializer_class = UserLoginSerializer

    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    default_number = settings.TWILIO_DEFAULT_CALLERID
    client = Client(account_sid, auth_token)
    
    def list(self, request):
        from_num = request.query_params.get('From', None)
        reply_number = from_num if from_num else '+14169095217'

        request_body = request.query_params.get('Body')

        if request_body == 'Hello':
            return_body = 'Do you need help?'
        else: 
            return_body = 'That was not Hello'

        message = self.client.messages \
                .create(
                     body=return_body,
                     from_=self.default_number,
                     to=reply_number
                 )
        return Response(request.data)
