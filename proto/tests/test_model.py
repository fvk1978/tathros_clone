from django.conf import settings
from django.db.models.aggregates import Count
from django.test import TestCase
from django.utils import timezone

from proto.models import Category, Location, Subscription
from proto.models import PhotographerSubscription, Like, Impression
from proto.tests.utils import UserTestCase

__all__ = ['CategoryTestCase', 'PhotographerTestCase', 'LocationTestCase']


class CategoryTestCase(TestCase):

    def test_category(self):
        # setup
        category = Category.objects.create(name='Test Category')

        # tests
        self.assertIsNotNone(category.slug)
        self.assertIsNotNone(category.image)
        self.assertIn('placeholder', category.image.url)

        # teardown
        category.delete()


class PhotographerTestCase(UserTestCase):

    def test_photographer_full_name(self):
        # setup
        full_name = self.photographer.full_name()

        # tests
        self.assertIn(self.user.first_name, full_name)
        self.assertIn(self.user.last_name, full_name)

    def test_photographer_top_photos(self):
        # setup
        likes = [10, 5, 2, 1]
        photos = []
        for like_count, photo in zip(likes, self.photographer.photos.all()):
            for _ in range(like_count):
                like = Like()
                like.photo = photo
                like.save()
            photos.append(photo)

        top_photos = self.photographer.top_photos()

        # tests
        self.assertEqual(settings.TOP_PHOTOS_COUNT, top_photos.count())
        self.assertListEqual(photos[:settings.TOP_PHOTOS_COUNT],
                             list(top_photos))

        # teardown
        Like.objects.all().delete()

    def test_photographer_subscription(self):
        # setup
        subscription = Subscription.objects.create(
            name='Test subscription', description='Test subscription desc',
            likes=999, photos=999, price=999, is_premium=True)

        photographer_subscription = PhotographerSubscription.objects.create(
            program='Test program',
            start=timezone.now() - timezone.timedelta(days=10),
            end=timezone.now() + timezone.timedelta(days=10),
            photographer=self.photographer, subscription=subscription)

        # tests
        self.assertEqual(self.photographer.subscription(),
                         photographer_subscription.subscription)

        # teardown
        photographer_subscription.delete()
        subscription.delete()

    def test_photographer_likes(self):
        # setup
        likes = [10, 5, 2, 1]
        for like_count, photo in zip(likes, self.photographer.photos.all()):
            for _ in range(like_count):
                like = Like()
                like.photo = photo
                like.save()

        # tests
        self.assertEqual(self.photographer.likes(), sum(likes))

        # teardown
        Like.objects.all().delete()

    def test_photographer_impressions(self):
        # setup
        impressions = [10, 9, 8]
        for impr, photo in zip(impressions, self.photographer.photos.all()):
            for _ in range(impr):
                impression = Impression()
                impression.photo = photo
                impression.save()

        # tests
        self.assertEqual(self.photographer.impressions(), sum(impressions))

        # teardown
        Impression.objects.all().delete()

    def test_photographer_active_categories(self):
        # setup: we assume the only photos in the database are from this user.
        active_categories = \
            Category.objects.annotate(num_photos=Count('photos'))\
            .filter(num_photos__gt=0)

        # tests
        self.assertEqual(self.photographer.active_categories().count(),
                         active_categories.count())

        for category in self.photographer.active_categories():
            self.assertIn(category, active_categories)

    def test_photographer_category_photos(self):
        # tests
        for category in self.photographer.active_categories():
            for photo in self.photographer.category_photos(category):
                self.assertEqual(photo.photographer, self.photographer)

    def test_photographer_random_category_photo(self):
        # tests
        for category in self.photographer.active_categories():
            photo = self.photographer.random_category_photo(category)
            self.assertEqual(
                self.photographer.active_photos().filter(pk=photo.pk).count(),
                1)

    def test_photographer_active_photos(self):
        # setup
        photo = self.photographer.photos.first()
        photo.disabled = True
        photo.save()

        # tests
        self.assertEqual(self.photographer.active_photos().count(),
                         self.photographer.photos.count() - 1)

        # teardown
        photo.disabled = False
        photo.save()


class LocationTestCase(UserTestCase):

    def test_Location_full_address(self):
        # setup
        location = Location.objects.create(
            zip_code='29584',
            country='Deutschland',
            state='Deutschland',
            city='Grove',
            street='Nerzweg 2',
            photographer=self.photographer)

        full_address = location.full_address()

        # tests
        self.assertIn(location.street, full_address)
        self.assertIn(location.city, full_address)
        self.assertIn(location.zip_code, full_address)

        # teardown
        Location.objects.all().delete()
