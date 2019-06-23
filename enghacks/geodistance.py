from geopy.distance import geodesic

def calculate_distance(lat1, long1, lat2, long2):
    place1 = (lat1, long1)
    place2 = (lat2, long2)
    distance_in_km = round(geodesic(place1, place2).km, 2)
    if distance_in_km < 1:
        return str(distance_in_km * 1000) + "m"
    else:
        return str(distance_in_km) + " km"
