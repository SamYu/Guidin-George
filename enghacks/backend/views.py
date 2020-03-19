from datetime import datetime, timedelta
import re
import googlemaps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response

from backend.models import (
    DirectionThread,
    Place
)
from backend.serializers import UserLoginSerializer
from backend.utils.directions_utils import (
    directions_to_text,
    geocode_address,
    get_places_lst,
    places_list_to_string,
)
from backend.utils.format_utils import (
    is_integer,
    format_phone,
)
from backend.utils.sendgrid_utils import (
    send_text
)
from backend.utils.messages import (
    ARRIVAL_MESSAGE,
    DEST_CONFIRM_MESSAGE,
    ENTER_DESTINATION_MESSAGE,
    INTRO_MESSAGE,
    INVALID_CHOICE_MESSAGE,
    INVALID_DEST_MESSAGE,
    LAST_SESSION_TIME,
    LOADING_MESSAGE,
)

class UserLoginViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

class SMSDirectionsViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    serializer_class = UserLoginSerializer

    MAX_TIME_THRESHOLD = timedelta(hours=2)
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY)

    def list(self, request):

        # Verify request is Twilio SMS
        from_num = request.query_params.get('From', None)
        if from_num:
            reply_number = format_phone(from_num)
        else:
            raise('Not SMS')

        # Get request data
        request_body = request.query_params.get('Body')
        return_body = ''
        request_user = self.User.objects.get(phone = reply_number)
        user_threads = DirectionThread.objects.filter(
            user = request_user
        ).order_by('-date_time')
        latest_thread = user_threads[0] if len(user_threads) else None

        # Initialize new thread if needed
        if request_body == 'Reset' or not latest_thread or latest_thread.current_step == DirectionThread.ARRIVED:
            latest_thread = self._create_new_thread(request_user)
            return_body = INTRO_MESSAGE.format(
                request_user.first_name
            )
            send_text(return_body, reply_number)
            return Response(request.data)

        # Verify last thread is recent if exists
        if latest_thread:
            last_thread_age = timezone.now() - latest_thread.date_time
            if last_thread_age > self.MAX_TIME_THRESHOLD:
                return_body = LAST_SESSION_TIME.format(last_thread_age) +\
                    INTRO_MESSAGE.format(
                    request_user.first_name
                )
                latest_thread = self._create_new_thread(request_user)
                send_text(return_body, reply_number)
                return Response(request.data)

        # Get start location
        if latest_thread.current_step == DirectionThread.USER_LOCATION:
            self._get_start_location(reply_number, latest_thread, request_body)
            return Response(request.data)

        # Get destination and return choices
        elif latest_thread.current_step == DirectionThread.DESTINATION:
            self._get_destination(reply_number, latest_thread, request_body)
            return Response(request.data)

        # Get exact destination choice and return directions
        elif latest_thread.current_step == DirectionThread.DEST_CHOICES:
            self._get_dest_choice(reply_number, latest_thread, request_body)
            return Response(request.data)        

        # Complete thread 
        elif latest_thread.current_step == DirectionThread.IN_TRANSIT:
            return_body = ARRIVAL_MESSAGE.format(
                latest_thread.end_location
            )
            send_text(return_body, reply_number)
            latest_thread.increment_step()
        return Response(request.data)

    def _create_new_thread(self, request_user):
        new_thread = DirectionThread.objects.create(
                    user = request_user
        )
        return new_thread

    def _get_start_location(self, reply_number, latest_thread, request_body):
        latest_thread.start_location = request_body
        latest_thread.save()
        return_body = ENTER_DESTINATION_MESSAGE.format(latest_thread.start_location)
        send_text(return_body, reply_number)
        latest_thread.increment_step()

    def _get_destination(self, reply_number, latest_thread, request_body):
        user_location = latest_thread.start_location
        user_lat, user_lng = geocode_address(self.gmaps, user_location)
        send_text(LOADING_MESSAGE, reply_number)
        places_list = get_places_lst(
            gmaps=self.gmaps,
            query=request_body,
            user_lat=user_lat,
            user_lng=user_lng,
            radius=5,
            direction_thread=latest_thread
        )
        return_body = places_list_to_string(places_list)
        if len(places_list) == 0:
            invalid_body = INVALID_DEST_MESSAGE.format(
                    request_body
                )
            send_text(invalid_body, reply_number)
        else:
            send_text(return_body, reply_number)
            latest_thread.increment_step()

    def _get_dest_choice(self, reply_number, latest_thread, request_body):
        places_list = latest_thread.places_list.order_by('distance')
        if is_integer(request_body):
            choice_number = int(request_body) - 1
            # If valid choice send confirmation
            if choice_number < len(places_list):
                selected_dest = places_list[choice_number]
                latest_thread.end_location = selected_dest.address
                pending_body = DEST_CONFIRM_MESSAGE.format(
                    latest_thread.end_location
                )
                send_text(pending_body, reply_number)
                return_body_arr = directions_to_text(
                    self.gmaps,
                    latest_thread.start_location,
                    latest_thread.end_location,
                )
                for return_body in return_body_arr:
                    send_text(return_body, reply_number)
                latest_thread.increment_step()
                return
        # Reject on invalid choice
        return_body = INVALID_CHOICE_MESSAGE.format(
            len(places_list)
        )
        send_text(return_body, reply_number)
