from . import importmocks


class Command(importmocks.Command):
    SUBSCRIPTION_SIZES = [100, 500, 1000]

    def handle(self, *args, **options):
        importmocks.Subscription.objects.all().delete()

        self.create_subscriptions(self.SUBSCRIPTION_SIZES)

        photographers = importmocks.Photographer.objects.all()
        for p in photographers:
            s = importmocks.PhotographerSubscription(
                subscription=
                self.subscriptions[importmocks.random.randint(0, len(self.subscriptions) - 1)],
                photographer=p
            )


