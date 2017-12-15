# coding:utf-8
from django.core.urlresolvers import reverse

from proto.tests.utils import UserTestCase


__all__ = ['PhotoListTestCase']


class PhotoListTestCase(UserTestCase):
    def test_photo_list_should_return_available_photos(self):
        # setup
        response = self.client.get(reverse('api_photos'))

        # tests
        self.assertGreater(len(response.data), 0)
