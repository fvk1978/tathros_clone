from django.conf import settings
from django.core.urlresolvers import reverse

from proto.models import Category, Location, Impression
from proto.tests.utils import UserTestCase


class PhotoListInitialTestCase(UserTestCase):
    def test_home_displays_correctly(self):
        # setup
        response = self.client.get(reverse('home'))
        categories = Category.objects.all()

        # tests
        self.assertEqual(response.status_code, 200)
        for category in response.context['categories']:
            self.assertIn(category, categories)
        self.assertLessEqual(response.context['photos'].count(),
                             settings.PHOTOS_PER_BATCH)


class PhotographersByPhotoTestCase(UserTestCase):
    def test_photographers_by_photo_returns_this_photographer(self):
        # setup
        response = self.client.post(
            reverse('photographers'),
            {
                'ids': self.photographer.active_photos().first().id,
                'lat': 52.531677,
                'lng': 13.381777,
                'range': 100
            })

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.photographer, response.context['photographers'])

    def test_photographers_by_photo_adds_likes(self):
        # setup
        photo = self.photographer.photos.first()
        likes = photo.likes.count()
        response = self.client.post(
            reverse('photographers'),
            {
                'ids': photo.id,
                'lat': 52.531677,
                'lng': 13.381777,
                'range': 100
            })

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(likes + 1, photo.likes.count())


class PartialPhotosTestCase(UserTestCase):
    def test_partial_photos_wont_return_photos_when_lat_or_lng_are_present(self):
        # setup
        response = self.client.post(
            reverse('partial_photos'),
            {
                'geo[name]': 'Mitte, Berlin',
                'geo[range]': 1000
            })

        # tests
        self.assertEqual(response.context['photos'], [])

    def test_partial_photos_should_return_user_photo_and_add_impression(self):
        # setup
        location = Location(
            zip_code='10559',
            country='Deutschland',
            state='Deutschland',
            city='Berlin',
            street='Liboristr. 61',
            photographer=self.photographer,
        )
        location.save()
        response = self.client.post(
            reverse('partial_photos'),
            {
                'geo[name]': 'Mitte, Berlin',
                'geo[lat]': 52.5167,
                'geo[lng]': 13.3667,
                'geo[range]': 1000
            })

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.photographer.photos.first(),
                      response.context['photos'])
        self.assertEqual(self.photographer.active_photos().count(),
                         Impression.objects.all().count())

        # teardown
        location.delete()

    def test_partial_photos_should_return_user_photo_with_null_point_when_range_is_0(self):
        # setup
        location = Location(
            zip_code='10559',
            country='Deutschland',
            state='Deutschland',
            city='Berlin',
            street='Liboristr. 61',
            photographer=self.photographer,
            point=None
        )
        location.save()
        response = self.client.post(
            reverse('partial_photos'),
            {
                'geo[name]': 'Mitte, Berlin',
                'geo[lat]': 52.5167,
                'geo[lng]': 13.3667,
                'geo[range]': 0
            })

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.photographer.photos.first(),
                      response.context['photos'])

        # teardown
        location.delete()

    def test_partial_photos_should_return_user_photo_with_specific_category_slug(self):
        # setup
        location = Location(
            zip_code='10559',
            country='Deutschland',
            state='Deutschland',
            city='Berlin',
            street='Liboristr. 61',
            photographer=self.photographer,
        )
        location.save()
        category = self.photographer.category_set.first()
        response = self.client.post(
            reverse('partial_photos'),
            {
                'geo[name]': 'Mitte, Berlin',
                'geo[lat]': 52.5167,
                'geo[lng]': 13.3667,
                'geo[range]': 1000,
                'category': category.slug
            })

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.photographer.photos.first(),
                      response.context['photos'])

        # teardown
        location.delete()


class PartialPhotographersTestCase(UserTestCase):
    def test_post_return_photographer_without_hidden_ids(self):
        # setup
        location = Location(
            zip_code='10559',
            country='Deutschland',
            state='Deutschland',
            city='Berlin',
            street='Liboristr. 61',
            photographer=self.photographer,
        )
        location.save()
        response = self.client.post(
            reverse('partial_photographers'),
            {
                'query_string': '10559',
            })
        photographers = response.context['photographers']

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.photographer, photographers)

        # teardown
        location.delete()

    def test_post_return_photographer_with_hidden_ids(self):
        # setup
        location = Location(
            zip_code='10559',
            country='Deutschland',
            state='Deutschland',
            city='Berlin',
            street='Liboristr. 61',
            photographer=self.photographer,
        )
        location.save()
        response = self.client.post(
            reverse('partial_photographers'),
            {
                'query_string': '10559',
                'hidden_ids[]': [self.photographer.active_photos().first().pk]
            })
        photographers = response.context['photographers']

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.photographer, photographers)

        # teardown
        location.delete()
