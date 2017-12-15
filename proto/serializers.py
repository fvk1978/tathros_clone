from rest_framework import serializers
from proto.models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'title', 'description', 'image',)
