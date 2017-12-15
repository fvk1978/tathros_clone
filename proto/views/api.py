from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.response import Response
from rest_framework.views import APIView

from proto.models import Photo
from proto.serializers import PhotoSerializer


class PhotoList(APIView):
    """
    List all photos, or create a new snippet.
    """
    # permission_classes = (GetOnly,)

    def get(self, request, format=None):
        photos = Photo.objects.all()

        paginator = Paginator(photos, settings.PHOTOS_PER_BATCH)
        page = request.GET.get('page')

        try:
            page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            photos = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results
            photos = paginator.page(paginator.num_pages)
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)
