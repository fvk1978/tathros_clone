# coding:utf-8
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from proto.forms import UserForm, PhotographerForm
from proto.models import Photographer
from proto.tests.utils import UserTestCase


class RegisterTestCase(TestCase):
    def test_register_should_display_correctly(self):
        # setup
        response = self.client.get(reverse('register'))

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['user_form'], UserForm)
        self.assertIsInstance(response.context['photographer_form'],
                              PhotographerForm)

    def test_register_should_create_user_and_photographer(self):
        # setup
        users = User.objects.all().count()
        photographers = Photographer.objects.all().count()

        response = self.client.post(reverse('register'), {
            'username': 'test_user',
            'password': 'test_password',
            'email': 'email@email.com',
            'company_name': 'test company',
            'website': '',
            'mobile_number': '+44 7700 900498',
            'phone_number': '+44 7700 900498',
            'birth_date': '11/11/1990',
        }, follow=True)

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertGreater(User.objects.all().count(), users)
        self.assertGreater(Photographer.objects.all().count(), photographers)

        # teardown
        Photographer.objects.all().delete()
        User.objects.all().delete()


class LoginTestCase(UserTestCase):
    def test_login_should_display_correctly(self):
        # setup
        self.client.logout()
        response = self.client.get(reverse('login'))

        # tests
        self.assertEqual(response.status_code, 200)

        # teardown
        self.client.login(username=self.user.username, password='password')

    def test_login_should_log_in_user(self):
        # setup
        self.client.logout()
        response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': 'password'
        }, follow=True)

        # tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user, self.user)


class LogoutTestCase(UserTestCase):
    def test_logout_should_log_out_user(self):
        # setup
        response = self.client.get(reverse('logout'), follow=True)

        # tests
        self.assertNotEqual(response.context['request'].user, self.user)

        # teardown
        self.client.login(username=self.user.username, password='password')
