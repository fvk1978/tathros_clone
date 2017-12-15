from django import template
from proto.models import Location

register = template.Library()


def distance(origin, destination):
    return int(origin.distance(destination) * Location.SCALE)\
        if destination and origin else None

register.filter('distance', distance)
