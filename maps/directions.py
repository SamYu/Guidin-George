import googlemaps
import json
import urllib
from urllib import urlencode
from datetime import datetime
import unicodedata
import re

gmaps = googlemaps.Client(key='AIzaSyBadB6G00B0XCY3GoybhFADV9ZnrOP_Usw')

# Geocoding an address
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
# reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit

# origin = "Mavis and Bristol"
# destination = "Credit%20Valley%20Hospital"
# mode = "walking"
#
#
# now = datetime.now()
# # directions_result = gmaps.directions(origin, destination, mode)
# directions_result = gmaps.directions("Sydney Town Hall",
#                                      "Parramatta, NSW",
#                                      mode="transit",
#                                      departure_time=now)
# print(directions_result)
#

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
    print(combined_lst)




print(lst_of_directions("Mavis and Bristol", "Mavis and Eglinton"))
