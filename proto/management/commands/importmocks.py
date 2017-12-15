from django.core.management.base import BaseCommand, CommandError
from proto.models import Photographer, PhotographerSubscription, Location,\
    Photo, Category, Subscription, Like
from django.core.files import File
from django.contrib.auth.models import User
from django.conf import settings
import csv
import os
import random
import datetime
import logging
import copy


class Command(BaseCommand):
    # set to true to import real data via CSV
    REAL_DATA = False
    LINE_DELIMITER = '\n'
    VALUE_DELIMITER = ','
    DEFAULT_PHOTOS_PER_PHOTOGRAPHER = 1
    CSV_COLUMNS = 13
    SUBSCRIPTION_SIZES = [5, 100, -1]
    LIKE_TO_PHOTO_RATIO = 50
    CATEGORIES_PER_PHOTOGRAPHER_MAX = 5
    CATEGORIES_PER_PHOTOGRAPHER_MIN = 1
    DEFAULT_STATE = 'Deutschland'
    CWD = os.getcwd()
    INPUT_FILE_PHOTOGRAPHERS = os.path.join(CWD, 'proto/mocks/photographers.csv')
    INPUT_FILE_CATEGORIES = os.path.join(CWD, 'proto/mocks/photo_categories')
    IMG_PATH = os.path.join(os.getcwd(), 'proto/mocks/img')
    help = 'Run this command to convert json fixtures to models'

    def __init__(self, *args, **kwargs):
        logging.basicConfig(filename='geo_import.log', level=logging.WARNING)
        self.categories = []
        self.created_categories = []
        self.photographers = []
        self.subscriptions = []
        self.photosPerPhotographer = None
        self.mockLocation = False
        self.csv_dirty = False
        self.headers = []

        self.imageCount = len([name for name in os.listdir(self.IMG_PATH)
                               if os.path.isfile(os.path.join(self.IMG_PATH,
                                                 name))])
        # prevent duplicate user names
        self.uCounter = dict()
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('photosPerPhotographer', nargs='?', type=int)
        parser.add_argument('dropData', nargs='?',
                            type=bool, default=False)
        parser.add_argument('mockLocation', nargs='?',
                    type=bool, default=False)

    def handle(self, *args, **options):
        if Photographer.objects.filter(is_mock=True):
            msg = 'Mocks already imported, falling back to doing nothing'
            print(msg)
            logging.warning(msg)
            return

        if options.get('dropData'):
            Like.objects.all().delete()
            User.objects.all().delete()
            Category.objects.all().delete()
            Subscription.objects.all().delete()

        self.mockLocation = options.get('mockLocation')

        self.photosPerPhotographer = options.get('photosPerPhotographer',
                                                 self.DEFAULT_PHOTOS_PER_PHOTOGRAPHER)
        self.get_objects()
        self.create_objects()
        self.write_out()

    def get_unique_index(self, max_index, used_indexes):
        # Try to avoid duplicates where possible
        rand = None
        while True:
            rand = random.randint(0, max_index)
            if rand not in used_indexes:
                used_indexes.append(rand)
                break
            elif len(used_indexes) -1 >= max_index:
                break
        return rand

    def get_categories(self):
        with open(self.INPUT_FILE_CATEGORIES, 'r') as stream:
            self.categories = [
                (name, filename) for name, filename in
                [line.split(self.VALUE_DELIMITER) for line in stream.read().split(self.LINE_DELIMITER)]
            ]

    def get_photographers(self):
        with open(self.INPUT_FILE_PHOTOGRAPHERS, 'r', encoding="ISO-8859-1", ) as stream:
            reader  = csv.reader(stream, delimiter=self.VALUE_DELIMITER, quotechar='|')
            for row in reader:
                if not self.headers:
                    self.headers = [item.strip() for item in row]
                else:
                    processed_row = {self.headers[i]: row[i].strip() for i in range(self.CSV_COLUMNS)}
                    self.photographers.append(processed_row)

    def get_objects(self):
        self.get_categories()
        self.get_photographers()

    def create_objects(self):
        self.create_categories()
        self.create_subscriptions()
        self.create_photographers()

    def create_subscriptions(self, sizes=SUBSCRIPTION_SIZES):
        for photos in sizes:
            title = "{} {}".format("Subscription", photos)
            likes = photos * self.LIKE_TO_PHOTO_RATIO
            subscription = Subscription(name=title, photos=photos, likes=likes,
                                        price=1)
            subscription.save()
            self.subscriptions.append(subscription)

    def create_categories(self):
        for cat, image in self.categories:
            c = Category(name=cat, image='/static/categories/{}'.format(image))
            c.save()
            self.created_categories.append(c)

    def generate_categories_for_photographer(self, p):
        categories = []
        num_categories = random.randint(
            self.CATEGORIES_PER_PHOTOGRAPHER_MIN,
            self.CATEGORIES_PER_PHOTOGRAPHER_MAX
        )
        while len(categories) < num_categories:
            max_idx = len(self.created_categories) - 1
            idx = random.randint(0, max_idx)
            cat = self.created_categories[idx]

            if cat not in categories:
                #cheaper than model lookup
                categories.append(cat)
                p.categories.add(cat)
        p.save()
        return categories

    def create_photographers(self):
        if self.photographers is None:
            raise CommandError('Please load the mocks')

        images = os.listdir(self.IMG_PATH)
        counter = 1
        total = len(self.photographers)
        for ref_obj in self.photographers:
            obj = copy.deepcopy(ref_obj)
            print("imported {} out of {}".format(counter, total))
            counter += 1
            uname = "{}_{}".format(obj['first_name'], obj['last_name'])

            if self.uCounter.get(uname, None):
                original_name = uname
                uname += str(self.uCounter[uname])
                self.uCounter[original_name] += 1
            else:
                self.uCounter[uname] = 1

            u, created = User.objects.get_or_create(username=uname, email=obj.pop('email'),
                                                    first_name=obj.pop('first_name'), last_name=obj.pop('last_name'))
            u.set_password(settings.MOCK_USER_PASSWORD)

            location = {
                'country': obj.pop('country', self.DEFAULT_STATE),
                'state': obj.pop('state', self.DEFAULT_STATE),
                'city': obj.pop('city'),
                'street': obj.pop('street'),
                'zip_code': obj.pop('zip_code'),
                'lat': obj.pop('lat'),
                'lng': obj.pop('lng'),
            }

            if self.mockLocation:
                location['lat'] = settings.SEARCH_DEFAULTS['lat']
                location['lng'] = settings.SEARCH_DEFAULTS['lng']

            components = obj['birth_date'].split('.')

            for i in range(2):
                if int(components[i]) < 10:
                    components[i] = '0' + components[i]

            # Format photographer fields
            obj['user'] = u
            obj['birth_date'] = '.'.join(components)
            obj['birth_date'] = datetime.datetime.strptime(obj['birth_date'], '%d.%m.%Y').date()
            obj['is_mock'] = not self.REAL_DATA
            # Remove the id field, solve broken registration
            obj.pop(self.headers[0])


            p = Photographer(**obj)
            p.save()
            categories = self.generate_categories_for_photographer(p)
            max_index = len(images) - 1
            used_indexes = []
            for i in range(0, self.photosPerPhotographer):
                rand = self.get_unique_index(max_index, used_indexes)

                img = images[rand]
                full_img_path = os.path.join(self.IMG_PATH, img)
                with open(full_img_path, 'rb') as stream:
                    file = File(stream)
                    ph = Photo()
                    ph.photographer = p
                    new_name = "{}_{}.jpg".format(u.id, i + 1)
                    ph.image.save(new_name, file, save=True)
                    ph.save()
                    ph.categories.add(random.choice(categories))

            location['photographer'] = p

            l = Location(**location)
            l.save()
            self.update_row_location(ref_obj, l)

            s = PhotographerSubscription(
                subscription=random.choice(self.subscriptions),
                photographer=p
            )

            s.save()

    def update_row_location(self, row, location):
        # Location lookup occurs in Location.save, optimize csv for next run without the API
        if not self.mockLocation:
            if location.point:
                if row.get('lng') != location.point.x or\
                    row.get('lat') != location.point.y:
                        self.csv_dirty = True
                        row['lng'] = location.point.x
                        row['lat'] = location.point.y
            else:
                # Location is incorrect and cannot be geocoded!
                row['lng'] = None
                row['lat'] = None

    def write_out(self):
        def write_row(row, stream):
            res = "{}{}".format(self.VALUE_DELIMITER.join([str(val) for val in row]), self.LINE_DELIMITER)
            stream.write(res)

        if self.csv_dirty:
            with open (self.INPUT_FILE_PHOTOGRAPHERS, 'w') as write_stream:
                write_stream.seek(0)
                write_stream.truncate()
                write_row(self.headers, write_stream)
                for r in self.photographers:
                    if not all([r['lat'], r['lng']]):
                        r['lat'] = settings.INCORRECT_LOCATION_PLACEHOLDER
                        r['lng'] = settings.INCORRECT_LOCATION_PLACEHOLDER
                    r = [r.get(key, settings.INCORRECT_LOCATION_PLACEHOLDER) for key in self.headers]
                    write_row(r, write_stream)
