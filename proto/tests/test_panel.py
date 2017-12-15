from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from os import listdir
from os.path import join

from proto.models import Category, Photo
from proto.tests.utils import UserTestCase, random_string

__all__ = ['PersonalSettingsTestCase', 'PortfolioTestCase',
           'CategoryDetailTestCase', 'UploadTestCase', 'UpdateTestCase',
           'DeleteTestCase']


class PersonalSettingsTestCase(UserTestCase):
    def test_personal_settings_is_login_protected(self):
        # setup
        self.client.logout()
        response = self.client.get(reverse('settings_personal'))

        # tests
        self.assertNotEqual(response.status_code, 200)

        # teardown
        self.client.login(username=self.user.username, password='password')

    def test_personal_settings_is_visible(self):
        # setup
        response = self.client.get(reverse('settings_personal'))

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user, self.user)

    def test_personal_settings_shows_valid_user_info(self):
        # setup
        response = self.client.get(reverse('settings_personal'))
        forms = response.context['forms']

        # tests
        # TODO: Add remaining non-functioning fields
        self.assertEqual(forms['form'].initial['birth_date'],
                         self.photographer.birth_date)
        self.assertEqual(forms['form'].initial['company_name'],
                         self.photographer.company_name)
        self.assertEqual(forms['form'].initial['mobile_number'].as_international,
                         self.photographer.mobile_number.as_international)
        self.assertEqual(forms['form'].initial['phone_number'],
                         self.photographer.phone_number)
        self.assertEqual(forms['form'].initial['profile_image'],
                         self.photographer.profile_image)
        self.assertEqual(forms['form'].initial['website'],
                         self.photographer.website)

        self.assertEqual(forms['form_user'].initial['email'],
                         self.user.email)
        self.assertEqual(forms['form_user'].initial['first_name'],
                         self.user.first_name)
        self.assertEqual(forms['form_user'].initial['last_name'],
                         self.user.last_name)

    def test_personal_settings_form_updates_user_and_photographer_info(self):
        # setup
        user_info_to_update = {
            'first_name': 'Test name',
            'last_name': 'Test lastname',
            'email': 'test@email.com',
            'birth_date': '1/1/1990',
            'company_name': 'Test company',
            'mobile_number': '+1 202 555 0124',
            'phone_number': '+1 202 555 0124',
            'website': 'http://test.com'
        }
        response = self.client.post(reverse('settings_personal'),
                                    user_info_to_update, follow=True)
        self.user = User.objects.get(pk=self.user.pk)
        self.photographer = self.user.photographer
        forms = response.context['forms']

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(forms['form'].initial['birth_date'],
                         self.photographer.birth_date)
        self.assertEqual(forms['form'].initial['company_name'],
                         self.photographer.company_name)
        self.assertEqual(forms['form'].initial['mobile_number'].as_international,
                         self.photographer.mobile_number.as_international)
        self.assertEqual(forms['form'].initial['phone_number'],
                         self.photographer.phone_number)
        self.assertEqual(forms['form'].initial['profile_image'],
                         self.photographer.profile_image)
        self.assertEqual(forms['form'].initial['website'],
                         self.photographer.website)

        self.assertEqual(forms['form_user'].initial['email'],
                         self.user.email)
        self.assertEqual(forms['form_user'].initial['first_name'],
                         self.user.first_name)
        self.assertEqual(forms['form_user'].initial['last_name'],
                         self.user.last_name)


class ScoreboardTestCase(UserTestCase):
    def test_scoreboard_is_login_protected(self):
        # setup
        self.client.logout()
        response = self.client.get(reverse('settings_scoreboard'))

        # tests
        self.assertNotEqual(response.status_code, 200)

        # teardown
        self.client.login(username=self.user.username, password='password')

    def test_scoreboard_is_visible(self):
        # setup
        response = self.client.get(reverse('settings_scoreboard'))

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user, self.user)

    def test_scoreboard_displays_photographer_data(self):
        # setup
        response = self.client.get(reverse('settings_scoreboard'))

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['p'], self.photographer)


class PortfolioTestCase(UserTestCase):
    def test_portfolio_is_login_protected(self):
        # setup
        self.client.logout()
        response = self.client.get(reverse('settings_portfolio'))

        # tests
        self.assertNotEqual(response.status_code, 200)

        # teardown
        self.client.login(username=self.user.username, password='password')

    def test_portfolio_is_visible(self):
        # setup
        response = self.client.get(reverse('settings_portfolio'))

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user, self.user)

    def test_portfolio_displays_all_photo_categories(self):
        # setup
        response = self.client.get(reverse('settings_portfolio'))
        response_categories = response.context['categories']
        user_categories = self.photographer.active_categories()

        # tests
        for category, count in response_categories:
            self.assertIn(category, user_categories)
            self.assertEqual(
                count,
                self.photographer.category_photos(category).count()
            )

    def test_portfolio_displays_top_photos(self):
        # setup
        response = self.client.get(reverse('settings_portfolio'))
        top_photos = response.context['top_photos']

        # tests
        for photo in top_photos:
            self.assertIn(photo,  self.photographer.top_photos())


class CategoryDetailTestCase(UserTestCase):
    def test_category_detail_is_login_protected(self):
        # setup
        self.client.logout()
        user_category = self.photographer.active_categories().first()
        response = self.client.get(
            reverse('settings_category',
                    args=(user_category.pk, user_category.slug)))

        # tests
        self.assertNotEqual(response.status_code, 200)

        # teardown
        self.client.login(username=self.user.username, password='password')

    def test_category_detail_is_visible(self):
        # setup
        user_category = self.photographer.active_categories().first()
        response = self.client.get(
            reverse('settings_category',
                    args=(user_category.pk, user_category.slug)))

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user, self.user)

    def test_category_detail_displays_active_user_category(self):
        # setup
        user_category = self.photographer.active_categories().first()
        response = self.client.get(
            reverse('settings_category',
                    args=(user_category.pk, user_category.slug)))
        category = response.context['category']

        # test
        self.assertEqual(user_category, category)

    def test_category_detail_fails_displaying_unused_user_category(self):
        # setup
        user_categories = self.photographer.active_categories()
        other_categories = Category.objects.exclude(pk__in=user_categories)
        other_category = other_categories.first()
        response = self.client.get(
            reverse('settings_category',
                    args=(other_category.pk, other_category.slug)))

        # test
        self.assertNotEqual(response.status_code, 200)


class UploadTestCase(UserTestCase):
    def test_upload_is_login_protected(self):
        # setup
        self.client.logout()
        response = self.client.get(reverse('settings_upload'))

        # tests
        self.assertNotEqual(response.status_code, 200)

        # teardown
        self.client.login(username=self.user.username, password='password')

    def test_upload_is_visible(self):
        # setup
        response = self.client.get(reverse('settings_upload'))

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user, self.user)

    def test_upload_successfully_stores_user_photo(self):
        # setup
        categories = Category.objects.order_by('?')[:3]
        image_path = listdir(join(settings.BASE_DIR, 'static', 'assets', 'img'))[0]
        image_path = join(settings.BASE_DIR, 'static', 'assets', 'img', image_path)
        photo_count = self.photographer.photos.count()

        with open(image_path, 'rb') as image:
            photo_data = {
                'title': random_string(10),
                'description': random_string(10),
                'image': image,
                'categories': (category.pk for category in categories)
            }
            response = self.client.post(reverse('settings_upload'), photo_data,
                                        follow=True)

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertGreater(self.photographer.photos.count(), photo_count)

    def test_upload_adds_new_categories(self):
        # setup
        category = Category.objects.order_by('?').first()
        image_path = listdir(join(settings.BASE_DIR, 'static', 'assets', 'img'))[0]
        image_path = join(settings.BASE_DIR, 'static', 'assets', 'img', image_path)
        photo_count = self.photographer.photos.count()
        new_category = random_string(10)

        with open(image_path, 'rb') as image:
            photo_data = {
                'title': random_string(10),
                'description': random_string(10),
                'image': image,
                'categories': [category, new_category]
            }
            response = self.client.post(reverse('settings_upload'), photo_data,
                                        follow=True)

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertGreater(self.photographer.photos.count(), photo_count)
        self.assertEqual(Category.objects.filter(name=new_category).count(), 1)


class UpdateTestCase(UserTestCase):
    def test_update_is_login_protected(self):
        # setup
        self.client.logout()
        photo = self.photographer.photos.first()
        response = self.client.get(reverse('settings_edit', args=(photo.pk,)))

        # tests
        self.assertNotEqual(response.status_code, 200)

        # teardown
        self.client.login(username=self.user.username, password='password')

    def test_update_is_visible(self):
        # setup
        photo = self.photographer.photos.first()
        response = self.client.get(reverse('settings_edit', args=(photo.pk,)))

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user, self.user)

    def test_update_displays_active_user_photo(self):
        # setup
        photographer_photo = self.photographer.photos.first()
        response = self.client.get(reverse('settings_edit',
                                           args=(photographer_photo.pk,)))
        photo = response.context['form'].instance

        # tests
        self.assertEqual(photo, photographer_photo)

    def test_update_fails_displaying_unused_user_photo(self):
        # setup
        photographer_photo = self.photographer.photos.first()
        photographer_photo.delete()
        response = self.client.get(reverse('settings_edit',
                                           args=(photographer_photo.pk,)))

        # tests
        self.assertNotEqual(response.status_code, 200)

    def test_update_sucessfully_updates_photo_details(self):
        photographer_photo = self.photographer.photos.first()
        categories = photographer_photo.categories.all()
        photo_data = {
            'title': random_string(10),
            'description': random_string(10),
            'categories': (category.pk for category in categories)
        }
        self.client.post(
            reverse('settings_edit', args=(photographer_photo.pk,)),
            photo_data, follow=True)
        updated_photo = Photo.objects.get(pk=photographer_photo.pk)

        # tests
        self.assertEqual(photo_data['title'], updated_photo.title)
        self.assertEqual(photo_data['description'], updated_photo.description)
        self.assertListEqual(list(categories),
                             list(updated_photo.category_set.all()))

    def test_update_adds_new_categories(self):
        photographer_photo = self.photographer.photos.first()
        categories = photographer_photo.categories.all()
        new_category = [random_string(10)]
        photo_data = {
            'title': random_string(10),
            'description': random_string(10),
            'categories': [category.pk for category in categories] + new_category
        }
        self.client.post(
            reverse('settings_edit', args=(photographer_photo.pk,)),
            photo_data, follow=True)

        # tests
        self.assertEqual(Category.objects.filter(name=new_category[0]).count(), 1)


class DeleteTestCase(UserTestCase):
    def test_delete_is_login_protected(self):
        # setup
        self.client.logout()
        photo = self.photographer.photos.first()
        response = self.client.get(reverse('settings_delete', args=(photo.pk,)))

        # tests
        self.assertNotEqual(response.status_code, 200)

        # teardown
        self.client.login(username=self.user.username, password='password')

    def test_delete_is_visible(self):
        # setup
        photo = self.photographer.photos.first()
        response = self.client.get(reverse('settings_delete', args=(photo.pk,)))

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user, self.user)

    def test_delete_displays_active_user_photo(self):
        # setup
        photographer_photo = self.photographer.photos.first()
        response = self.client.get(reverse('settings_delete',
                                           args=(photographer_photo.pk,)))
        photo = response.context['object']

        # tests
        self.assertEqual(photo, photographer_photo)

    def test_delete_fails_displaying_unused_user_photo(self):
        # setup
        photographer_photo = self.photographer.photos.first()
        photographer_photo.delete()
        response = self.client.get(reverse('settings_delete',
                                           args=(photographer_photo.pk,)))

        # tests
        self.assertNotEqual(response.status_code, 200)

    def test_delete_sucessfully_deletes_user_photo(self):
        # setup
        photographer_photo = self.photographer.photos.first()
        self.client.post(reverse('settings_delete',
                                 args=(photographer_photo.pk,)), follow=True)

        # tests
        self.assertEqual(
            self.photographer.photos.filter(pk=photographer_photo.pk).count(),
            0)
