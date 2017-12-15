from django.conf import settings
import googlemaps


def get_geo_location(location):
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY)
    gmaps.geocode(location.full_address())
