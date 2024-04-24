#TODO: this function calculates distance between two geological coordinates
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

def calcdistance(lat1,long1,lat2,long2):
    return geodesic((lat1,long1),(lat2,long2)).meters


def getlocation(lat,long):
    geolocator = Nominatim(user_agent="FENCE APP")
    location = geolocator.reverse(f"{lat}, {long}")

    return location.address