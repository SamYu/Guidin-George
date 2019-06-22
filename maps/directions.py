import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyBadB6G00B0XCY3GoybhFADV9ZnrOP_Usw')

# Geocoding an address
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
# reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit

origin = "Mavis and Bristol"
destination = "Credit Valley Hospital"
mode = "walking"


now = datetime.now()
# directions_result = gmaps.directions(origin, destination, mode)
directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="transit",
                                     departure_time=now)
print(directions_result)
