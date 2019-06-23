from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from backend.serializers import UserLoginSerializer

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
    serializer_class = UserLoginSerializer

def lst_of_directions(origin, destination):
    directionsObj = gmaps.directions(origin, destination, "walking")
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
    return(full_string)
