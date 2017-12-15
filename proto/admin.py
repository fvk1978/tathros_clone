from django.contrib.gis import admin

from proto.models import Photo, Location, PhotographerSubscription
from proto.models import Photographer

admin.site.register(Photographer)
admin.site.register(Photo)
admin.site.register(PhotographerSubscription)
admin.site.register(Location)
