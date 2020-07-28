import datetime
from django.core.management.base import BaseCommand
from substitute_food.database_fill import fill_cron


class Command(BaseCommand):
    help = "Fill the database with 50 pages of OFF data"

    def handle(self, *args, **options):
        fill_cron_thread = fill_cron()
        fill_cron_thread.start()
        self.stdout.write(self.style.SUCCESS('Database filled with success'))
        f = open("/opt/django/Projet_Pur_Beurre/log.txt", 'a')
        f.write('{0} Database filled with success \n'.format(
            datetime.datetime.now()))
