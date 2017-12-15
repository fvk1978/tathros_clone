from django.shortcuts import render
from django.views.generic import View
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from proto.models import Photo, Photographer, Location, Category, Like, \
    Impression
from .common import SafeFormView


class PhotoListInitial(View):
    template_name = 'index.html'

    def get(self, request):
        photos = Photo.objects.all().order_by('?')[:settings.PHOTOS_PER_BATCH]
        categories = Category.objects.all()
        context = {
            'photos': photos,
            'categories': categories,
            'search_defaults': settings.SEARCH_DEFAULTS,
            'js_handler': 'photos'
        }
        return render(request, self.template_name, context)


class PhotographersByPhoto(SafeFormView):
    template_name = 'photographers.html'

    def post(self, request):
        ids = request.POST.get('ids').split(",") or []
        self.add_likes(request, ids)
        photographers =\
            Photographer.objects.filter(photos__id__in=ids).distinct()
        point_str = 'SRID=4326;POINT({} {})'\
            .format(request.POST.get('lng'), request.POST.get('lat'))

        point = GEOSGeometry(point_str)
        context = {
            'photographers': photographers,
            'hidden_ids': ids,
            'js_handler': 'photographers',
            'scale': Location.SCALE,
            'point': point,
        }
        return render(request, self.template_name, context)

    def add_likes(self, request, photo_ids):
        ip = request.META['REMOTE_ADDR']
        user = request.user if request.user.is_authenticated() else None
        for id in photo_ids:
            like = Like(ip=ip, user=user)
            like.photo_id = id
            like.save()


class PartialPhotos(SafeFormView):
    TEMPLATE_NAME = 'partials/photos.html'
    DEFAULT_RANGE = settings.SEARCH_DEFAULTS['range']
    SCALE = 1000

    def post(self, request):
        geo = {
            'lat': request.POST.get('geo[lat]'),
            'lng': request.POST.get('geo[lng]'),
            'name': request.POST.get('geo[name]'),
            'range': request.POST.get('geo[range]'),
        }
        geo_range = int(geo['range'] or self.DEFAULT_RANGE)
        if not any([geo.get('lat'), geo.get('lng')]):
            return self.render_not_found(request)

        cat = request.POST.get('category')
        pnt_str = 'SRID=4326;POINT({} {})'.format(geo['lng'], geo['lat'])
        pnt = GEOSGeometry(pnt_str)

        # geo-filtering
        if geo_range > 0:
            # short version
            # photos = Photo.objects.filter(
            #     photographer__locations__point__distance_lte=(
            #           pnt, D(km=geo_range)))
            # debug-able version

            locations = Location.objects.filter(point__distance_lte=(pnt, D(km=geo_range)))\
                .distance(pnt).order_by('distance')
            photographers = Photographer.objects.filter(locations__in=locations)
            photos = Photo.objects.filter(photographer__in=photographers).order_by('?')
        else:
            photos = Photo.objects.exclude(photographer__locations__point__isnull=True)

        # category filtering
        if cat and cat != settings.SEARCH_DEFAULTS['category']:
            photos = photos.filter(photographer__categories__slug__exact=cat)
        page = int(request.POST.get('page', 0)) or 0

        # paginate and add exposure metric
        batch = self.paginate(photos, page)
        self.add_impressions(batch, request)

        context = {
            'photos': batch,
            'geo': geo,
            'total': len(photos) if not page else None,
        }

        return render(request, self.TEMPLATE_NAME, context)

    def render_not_found(self, request):
        context = {'photos': []}
        return render(request, self.TEMPLATE_NAME, context)

    @staticmethod
    def paginate(photos, page):
        start = page * settings.PHOTOS_PER_BATCH
        end = (page + 1) * settings.PHOTOS_PER_BATCH
        batch = photos[start:end]
        return batch

    @staticmethod
    def add_impressions(batch, request):
        ip = request.META['REMOTE_ADDR']
        user = request.user if request.user.is_authenticated() \
            else None
        for photo in batch:
            impression = Impression(ip=ip, user=user)
            impression.photo_id = photo.id
            impression.save()


class PartialPhotographers(SafeFormView):
    template_name = 'partials/photographer.html'

    def post(self, request):
        zip_code = request.POST.get('query_string')
        photo_ids = request.POST.getlist('hidden_ids[]', [])

        if photo_ids:
            photographers = Photographer.objects.filter(
                locations__zip_code__startswith=zip_code,
                photos__id__in=photo_ids)
        else:
            photographers = Photographer.objects.filter(
                locations__zip_code__startswith=zip_code)

        context = {
            'photographers': photographers,
            'hidden_ids': photo_ids,
            'js_handler': 'photos'
        }

        return render(request, self.template_name, context)
