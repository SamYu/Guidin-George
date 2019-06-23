from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from backend.serializers import UserLoginSerializer
from rest_framework.response import Response
from django.conf import settings
from backend.models import DirectionThread, Place
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from datetime import datetime, timedelta
import re
import googlemaps
from geopy.distance import geodesic


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

    max_time_threshold = timedelta(hours=2)
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY)

    #input handler
    def list(self, request):
        from_num = request.query_params.get('From', None)
        if from_num:
            reply_number = self.format_phone(from_num)
        else:
            raise('Not SMS')
        request_body = request.query_params.get('Body')
        return_body = ''
        request_user = self.User.objects.get(phone = reply_number)
        user_threads = DirectionThread.objects.filter(
            user = request_user
        ).order_by('-date_time')
        latest_thread = user_threads[0] if len(user_threads) else None

        if not latest_thread or latest_thread.current_step == 'ARRIVED':
            latest_thread = self._create_new_thread(request_user)
            return_body = self._current_step_dialog(latest_thread)
            self.send_text(return_body, reply_number)
            return Response(request.data)

        if latest_thread:
            last_thread_age = datetime.now() - latest_thread.date_time
            if last_thread_age > self.max_time_threshold:
                return_body = 'Your last session was {0} ago, starting new session.'.format(last_thread_age)
                latest_thread = self._create_new_thread(request_user)
                self.send_text(return_body, reply_number)
                return Response(request.data)      
        elif latest_thread.current_step == 'USER_LOCATION':
            latest_thread.start_location = request_body
            latest_thread.save
            return_body = self._current_step_dialog(latest_thread)
            self.send_text(return_body, reply_number)
            latest_thread.increment_step()
            return Response(request.data)

        elif latest_thread.current_step == 'DESTINATION':
            user_location = latest_thread.start_location
            user_lat, user_lng = self.geocode_address(user_location)
            places_list = self.get_places_lst(
                query=request_body,
                user_lat=user_lat,
                user_lng=user_lng,
                radius=5,
                direction_thread=latest_thread
            )
            ## ADD PRINT PLACES LIST FUNCTION
            return_body = self._current_step_dialog(latest_thread)
            self.send_text(return_body, reply_number)
            latest_thread.increment_step()
            return Response(request.data)

        elif latest_thread.current_step == 'DEST_CHOICES':
            places_list = latest_thread.places_list
            if self.is_integer(request_body):
                choice_number = int(request_body) - 1
                if choice_number < len(places_list):
                    selected_dest = places_list[choice_number]
                    latest_thread.end_location = selected_dest.address
                    # JOSIAH'S FUNCTION
                    return_body = self.lst_of_directions(
                        latest_thread.start_location,
                        latest_thread.end_location,
                    )
                    self.send_text(return_body, reply_number)
                    latest_thread.increment_step()
                    return Response(request.data)
            else:
                return_body = 'Invalid choice, please enter a number between 1 and {}'.format(
                    len(places_list)
                )
                self.send_text(return_body, reply_number)
                return Response(request.data)        

        elif latest_thread.current_step == 'IN_TRANSIT':
            latest_thread.increment_step()
            return_body = self._current_step_dialog(latest_thread)
            self.send_text(return_body, reply_number)

        return Response(request.data)


    def is_integer(self, text):
        try: 
            int(text)
            return True
        except ValueError:
            return False


    def _create_new_thread(self, request_user):
        new_thread = DirectionThread.objects.create(
                    user = request_user
        )
        return new_thread


    def _current_step_dialog(self, message_thread):
        return_body = ''
        if not message_thread or message_thread.current_step == 'ARRIVED':
            return_body = 'Hello, this is ____. Please text back your location to begin calculating a route.'
        elif (message_thread.current_step == 'USER_LOCATION'):
            return_body = 'Please text back your destination.'
        elif (message_thread.current_step == 'IN_TRANS'):
            return_body = 'Thank you for using ____.'
        return (return_body)

    def send_text(self, return_body, reply_number):
        self.client.messages \
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
   
    def lst_of_directions(self, origin, destination):
        directionsObj = self.gmaps.directions(origin, destination, "walking")
        # return(directionsObj[0]['overview_polyline']['warnings'])
        x = (directionsObj[0]['legs'][0]['steps'])

        distance_lst = []
        for elem in x:
            distance_lst.append(str(elem['distance']['text']))

        step_lst_html = []
        for elem in x:
            step_lst_html.append(str(elem['html_instructions']))

        step_lst = []
        for elem in step_lst_html:
            elem = re.sub('<.*?>', ' ', elem)
            step_lst.append(elem)

        combined_lst = []
        for index in range(len(step_lst)):
            distanceStep = step_lst[index] + "(" + distance_lst[index] + ")"
            combined_lst.append(distanceStep)

        full_string = " --- ".join(combined_lst)
        intro = "Here are the directions: "
        return(intro + full_string)
      
    def geocode_address(self, address):
        geocode = self.gmaps.geocode(address)
        lat = geocode[0]['geometry']['location']['lat']
        lng = geocode[0]['geometry']['location']['lng']
        return lat, lng

    def calculate_distance(self, lat1, long1, lat2, long2):
        place1 = (lat1, long1)
        place2 = (lat2, long2)
        distance_in_km = round(geodesic(place1, place2).km, 2)
        if distance_in_km < 1:
            return str(distance_in_km * 1000) + "m"
        else:
            return str(distance_in_km) + " km"

    def get_places_lst(self, query, user_lat, user_lng, radius, direction_thread):
        location = str(user_lat) + ', ' + str(user_lng)
        places_result = self.gmaps.places(query, location, radius)
        places_array = []
        for place in places_result['results']:
            address = place['formatted_address']
            name = place['name']
            lat = float(place['geometry']['location']['lat'])
            lng = float(place['geometry']['location']['lng'])
            distance_str = self.calculate_distance(
                lat1=user_lat,
                long1=user_lng,
                lat2=lat,
                long2=lng,
            )
            new_place = Place.objects.create(
                address=address,
                name=name,
                direction_thread=direction_thread,
                distance=distance_str,
            )
            places_array.append(new_place)
        return places_array

