from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.core.files.storage import FileSystemStorage
from django.db.models import Count
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from phonenumber_field.modelfields import PhoneNumberField
from django.template.defaultfilters import slugify
import datetime
import googlemaps
import logging

from safedelete import safedelete_mixin_factory, SOFT_DELETE, \
    DELETED_VISIBLE_BY_PK, safedelete_manager_factory, DELETED_INVISIBLE


class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


SoftDeleteMixin = safedelete_mixin_factory(policy=SOFT_DELETE,
                                           visibility=DELETED_VISIBLE_BY_PK)


class SoftDeletableModel(SoftDeleteMixin):
    disabled = models.BooleanField(default=False)
    active_objects = safedelete_manager_factory(models.Manager, models.QuerySet,
                                                DELETED_INVISIBLE)()

    class Meta:
        abstract = True


class Category(TimeStampedModel, SoftDeletableModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    image = models.ImageField(
        upload_to=FileSystemStorage(location='/static/categories'),
        default='/static/categories/placeholder.png',
        blank=True, null=True
    )

    photographers = models.ManyToManyField('Photographer',
                                           related_query_name='category')
    photos = models.ManyToManyField('Photo', related_query_name='category')

    # Shouldn't be doing this. Report when necessary.
    objects = models.Manager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save()

    def __str__(self):
        return self.name


class Photographer(TimeStampedModel, SoftDeletableModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    website = models.CharField(blank=True,
                               max_length=100)
    phone_number = PhoneNumberField(blank=True)
    mobile_number = PhoneNumberField()
    vat_number = models.CharField(max_length=100)
    email_notification_code = models.CharField(blank=True,
                                               max_length=100)
    birth_date = models.DateField()
    profile_image = models.ImageField(blank=True,
                                      upload_to='profile_pictures')
    news_letter = models.BooleanField()
    categories = models.ManyToManyField('Category',
                                        through=Category.photographers.through)
    is_mock = models.BooleanField(default=False)

    def top_photos(self):
        # Returns n top photos by likes
        return self.photos\
            .annotate(like_count=Count('likes'))\
            .order_by('-like_count', 'created_on', 'modified_on')\
            [:settings.TOP_PHOTOS_COUNT]

    def subscription(self):
        # returns the active subscription for the user, assumes that there is
        # only one
        today = datetime.date.today()
        photographer_subscription = \
            self.subscriptions.get(disabled=False, start__gte=today,
                                   end__lte=today)
        return photographer_subscription.subscription

    def likes(self):
        photos = self.photos.all()
        return Like.objects.filter(photo__in=photos).count()

    def impressions(self):
        photos = self.photos.all()
        return Impression.objects.filter(photo__in=photos).count()

    def active_categories(self):
        return Category.objects.filter(photos__in=self.active_photos()).distinct()

    def category_photos(self, category):
        return self.active_photos().filter(category__in=[category])

    def random_category_photo(self, category):
        return self.category_photos(category).order_by('?').first()

    def active_photos(self):
        return self.photos.filter(disabled=False, deleted=False)

    def full_name(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    def __str__(self):
        return self.full_name()


class Photo(TimeStampedModel, SoftDeletableModel):
    title = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=255, default='')
    image = models.ImageField(upload_to='proto/gallery')
    photographer = models.ForeignKey(Photographer, related_name='photos')
    categories = models.ManyToManyField('Category',
                                        through=Category.photos.through)

    class Meta:
        ordering = ['?']

    def __str__(self):
        return "{} #{}".format(self.photographer.full_name(),
                               int(self.id / Photographer.objects.count()))


class Location(TimeStampedModel, SoftDeletableModel):
    SCALE = 100
    zip_code = models.CharField(max_length=10, db_index=True)
    country = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255, default=None)
    street = models.CharField(max_length=255, default=None)
    photographer = models.ForeignKey(Photographer,
                                     related_name='locations')
    objects = models.GeoManager()
    point = models.PointField(null=True, blank=True, srid=4326, geography=True)

    def __init__(self, *args, **kwargs):
        self.lat = kwargs.pop('lat', None)
        self.lng = kwargs.pop('lng', None)
        super(Location, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # TODO: implement test that checks that this logic does not occur when
        # values are passed
        if not self.lat or not self.lng:
            try:
                client = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY)
                geo_data = client.geocode(self.full_address())
                location = geo_data[0]['geometry']['location']
                self.lng = location['lng']
                self.lat = location['lat']

            except (AttributeError, IndexError, googlemaps.exceptions.Timeout) as e:
                logging.warning("GeoLocation not found for {} \n Exception: {}\n\n"
                                .format(self.full_address(), e))

        if all([cord not in [None, settings.INCORRECT_LOCATION_PLACEHOLDER] for
                cord in [self.lat, self.lng]]):
            point = "POINT({} {})".format(self.lng, self.lat)
            self.point = GEOSGeometry(point, srid=4326)
            super(Location, self).save(*args, **kwargs)

    def full_address(self):
        return "{}, {}, {}"\
            .format(self.street, self.city, self.zip_code)

    def __str__(self):
        return "{}: {}, {}".format(self.photographer.full_name(),
                                   self.full_address(),
                                   self.point)


class Subscription(TimeStampedModel, SoftDeletableModel):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=255, blank=True)
    likes = models.IntegerField()
    photos = models.IntegerField()
    price = models.IntegerField()
    is_premium = models.BooleanField(default=False)


class PhotographerSubscription(TimeStampedModel, SoftDeletableModel):
    program = models.CharField(max_length=100)
    start = models.DateField(auto_now=True)
    end = models.DateField(auto_now=True)
    photographer = models.ForeignKey(Photographer,
                                     on_delete=models.CASCADE,
                                     related_name='subscriptions')
    subscription = models.ForeignKey(Subscription,
                                     on_delete=models.CASCADE,
                                     related_name='subscriptions')


class Metric(TimeStampedModel):
    user = models.ForeignKey(User,
                             blank=True,
                             null=True,
                             on_delete=models.DO_NOTHING)
    ip = models.CharField(max_length=30, blank=True)

    class Meta:
        abstract = True


class Like(Metric):
    photo = models.ForeignKey(Photo,
                              on_delete=models.DO_NOTHING,
                              related_name='likes')


class Impression(Metric):
    photo = models.ForeignKey(Photo,
                              on_delete=models.DO_NOTHING,
                              related_name='impressions')
