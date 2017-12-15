from . import importmocks


class Command(importmocks.Command):
    def handle(self, *args, **options):
        importmocks.Category.objects.all().delete()

        self.get_categories()
        self.create_categories()

        photographers = importmocks.Photographer.objects.all()
        for p in photographers:
            self.generate_categories_for_photographer(p)
            p.save()
