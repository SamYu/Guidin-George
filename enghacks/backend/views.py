from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from backend.serializers import UserSerializer

from twilio.twiml.messaging_response import MessagingResponse


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
    serializer_class = UserSerializer