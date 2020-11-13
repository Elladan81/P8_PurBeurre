import datetime
from django.core.management.base import BaseCommand
from substitute_food.database_fill import fill_cron


class Command(BaseCommand):
    help = "Fill the database with 100 pages of OFF data"

    def handle(self, *args, **options):
        fill_cron_thread = fill_cron()
        fill_cron_thread.start()
        self.stdout.write(self.style.SUCCESS('Database filled with success'))
        #f = open("/opt/django/purbeurre/log.txt", 'a')
        #.write(f'{datetime.datetime.now()} : Database filled with success \n')
