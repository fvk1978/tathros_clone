# coding:utf-8
import string

import random
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from proto.management.commands import importcategories
from proto.models import Photographer, Category, Photo


def random_string(number):
    return ''.join([random.choice(string.ascii_letters) for _ in range(number)])


def create_categories():
    importcategories.Command().handle()


def create_user():
    user = User.objects.create_user(
        random_string(20),
        'portfolio_test@email.com',
        'password'
    )
    return user


def user_and_photographer():
    user = create_user()

    photographer = Photographer.objects.create(
        user=user,
        company_name=random_string(20),
        mobile_number='+99 999999999',
        vat_number='00000000',
        birth_date=timezone.now().date(),
        news_letter=True
    )

    photographer.category_set.add(Category.objects.first())
    return user, photographer


def create_user_and_photographer():
    categories = list(Category.objects.all())

    user, photographer = user_and_photographer()

    for _ in range(5):
        photo = photographer.photos.create(
            title=random_string(20),
            description=random_string(50),
            image=random_string(20)
        )

        photo_categories = random.sample(categories, 3)
        for category in photo_categories:
            photo.category_set.add(category)

    return user, photographer


class UserTestCase(TestCase):

    def setUp(self):
        create_categories()
        self.user, self.photographer = create_user_and_photographer()
        self.client.login(username=self.user.username, password='password')

    def tearDown(self):
        Photo.objects.all().delete()
        Photographer.objects.all().delete()
        User.objects.all().delete()
        Category.objects.all().delete()
