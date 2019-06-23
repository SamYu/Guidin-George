import googlemaps
from pprint import pprint
import time

API_KEY = "AIzaSyBadB6G00B0XCY3GoybhFADV9ZnrOP_Usw"

# define client
from enghacks.backend.models import Place

gmaps = googlemaps.Client(key= API_KEY)

# define search
#latitude, longitude coordinate

# def test_func():
#     places_result = gmaps.places(query="McDonalds", location= "42.497971, -92.382751", radius=10)
#     import pdb; pdb.set_trace()
#     print(places_result)
#
# test_func()

def places_lst(query, user_lat, user_lng, radius):

    location = str(user_lat) + ", " + str(user_lng)
    places_result = gmaps.places(query, location, radius)
    import pdb; pdb.set_trace()
    return(places_result['results'])

    for place in places_result['results']:
        address = place['formatted_address']
        name = place['name']
        lat = float(place['geometry']['location']['lat'])
        lng = float(place['geometry']['location']['lng'])
        distance = distance_bw_points(lat, lng, origin)
        # Place.objects.create(
        #     address=address,
        #     name=name
        # )

def po_to_text(lop):
    counter = 1
    text_lst = []
    for place in lop:
        str = ""
        str = str + str(counter) + ". " + place.name + "," place.address + "," + place.distance + " away.")
        text_lst.append(str)
        counter ++
    full_string = " --- ".join(text_lst)
    print(full_string)
