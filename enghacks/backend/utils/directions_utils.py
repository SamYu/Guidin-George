from backend.models import Place
from backend.utils.messages import SELECT_DEST_MESSAGE
from geopy.distance import geodesic
import re

def calculate_distance(lat1, long1, lat2, long2):
    place1 = (lat1, long1)
    place2 = (lat2, long2)
    distance_in_km = round(geodesic(place1, place2).km, 2)
    if distance_in_km < 1:
        return str(distance_in_km * 1000) + "m"
    else:
        return str(distance_in_km) + " km"

def directions_to_text(gmaps, origin, destination):
    directionsObj = gmaps.directions(origin, destination, "walking")
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

    full_string = "\n".join(combined_lst)
    intro = "Here are the directions: \n"
    outro = 'Text \"Complete\" when you have arrived!'
    long_string = intro + full_string + '\n' + outro
    MAX_STRING_LEN = 1200
    string_arr = [long_string[i:i+MAX_STRING_LEN] for i in range(0, len(long_string), MAX_STRING_LEN)]
    return string_arr

def geocode_address(gmaps, address):
    geocode = gmaps.geocode(address)
    lat = geocode[0]['geometry']['location']['lat']
    lng = geocode[0]['geometry']['location']['lng']
    return lat, lng

def get_places_lst(gmaps, query, user_lat, user_lng, radius, direction_thread):
    location = str(user_lat) + ', ' + str(user_lng)
    places_result = gmaps.places(query, location, radius)
    places_array = []
    for place in places_result['results']:
        address = place['formatted_address']
        name = place['name']
        lat = float(place['geometry']['location']['lat'])
        lng = float(place['geometry']['location']['lng'])
        distance = calculate_distance(
            lat1=user_lat,
            long1=user_lng,
            lat2=lat,
            long2=lng,
        )
        new_place = Place.objects.create(
            address=address,
            name=name,
            direction_thread=direction_thread,
            distance=distance,
        )
        places_array.append(new_place)
    places_array.sort(key=lambda place: place.distance)
    return places_array[:5]

def places_list_to_string(list_of_places):
    counter = 1
    text_lst = []
    for place in list_of_places:
        place_string = ""
        place_string += '[' + str(counter) + '] ' + place.name + "," + place.address + "," + '(' + str(place.distance) + ' km' + ')'
        text_lst.append(place_string)
        counter += 1
    full_string = "\n".join(text_lst)
    full_string = SELECT_DEST_MESSAGE + full_string
    return full_string
