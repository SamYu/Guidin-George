from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from backend.serializers import UserLoginSerializer
from rest_framework.response import Response
from django.conf import settings
from backend.models import DirectionThread
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from datetime import datetime, timedelta
import re

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
    User = get_user_model()
    serializer_class = UserLoginSerializer

    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    default_number = settings.TWILIO_DEFAULT_CALLERID
    client = Client(account_sid, auth_token)

current_step_options = [
    ('USER_LOCATION', 'USER_LOCATION'),
    ('DESTINATION', 'DESTINATION'),
    ('DEST_CHOICES', 'DEST_CHOICES'),
    ('ARRIVED', 'ARRIVED'),
]
    max_time_threshold = timedelta(hours=2)


    #input handler
    def list(self, request):
        from_num = request.query_params.get('From', None)
        reply_number = self.format_phone(from_num) if from_num else '+14169095217'
        request_body = request.query_params.get('Body')
        return_body = ''
        request_user = self.User.objects.get(phone = reply_number)
        user_threads = DirectionThread.objects.filter(
            user = request_user
        ).order_by('-date_time')
        latest_thread = user_threads[0] if len(user_threads) else None
        new_thread = latest_thread

        if request_body == 'Hi' or request_body == 'Hello':
            if not latest_thread or latest_thread.current_step == 'ARRIVED':
                new_thread = DirectionThread.objects.create(
                    user = request_user
                )

                send_text(self, current_step_dialog(self, new_thread), reply_number)
        else:
            store_data(latest_thread)





            latest_thread.incrementStep()
        #else:
        #    return_body = 'That was not Hello'

        return Response(request.data)
    #
    def current_step_dialog(self, message_thread):
        return_body = ''
        if (message_thread.current_step == 'USER_LOCATION'):
            return_body = 'Hello, this is ____. Please text back your location to begin calculating a route.'
        elif (message_thread.current_step == 'DESTINATION'):
            return_body = 'Please text back your destination.'
        elif (message_thread.current_step == 'DEST_CHOICES'):
            return_body = 'Here are your options '
        elif (message_thread.current_step == 'ARRIVED'):
            return_body = 'Thank you for using ____.'
        return (return_body)

    def store_data(self, message_thread):
        if message_thread.current_step == 'USER_LOCATION':
            message_thread.start_location = request_body
        elif message_thread.current_step == 'DESTINATION':
            message_thread.end_location == request_body





        if (latest_thread and latest_thread.current_step == 'USER_LOCATION'):
            last_thread_age = datetime.now() - latest_thread.date_time
            if last_thread_age > self.max_time_threshold:
                return_body = 'Your last session was {0} ago, would you like to start a new session?'.format(last_thread_age)

        else:
            return_body = 'That was not Hello'

        self.send_text(return_body, reply_number)
        return Response(request.data)
>>>>>>> origin/master

    def send_text(self, return_body, reply_number):
        message = self.client.messages \
                .create(
                     body=return_body,
                     from_=self.default_number,
                     to=reply_number
                )

    def format_phone(self, phone_number):
        # strip non-numeric characters
        phone = re.sub(r'\D', '', phone_number)
        # remove leading 1 (area codes never start with 1)
        phone = phone.lstrip('1')
        return '{}{}{}'.format(phone[0:3], phone[3:6], phone[6:])
