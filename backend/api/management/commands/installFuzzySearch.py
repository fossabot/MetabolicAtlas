from api.models import *
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connections


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--drop-extension', action='store_true', default=False, dest='drop_extention', help='drop fuzzymatch extension')

    def handle(self, *args, **options):
        for db_name, db in settings.DATABASES.items():
            # print (db)
            if db_name in ['default', 'gems']:
                # skip not model databases
                continue

            if db['ENGINE'] != 'django.db.backends.postgresql':
                print("Warning: database '%s' is not using postgreSQL engine, cannot install fuzzymatch extension" % db_name)
                continue

            with connections[db_name].cursor() as cursor:
                if options['drop_extention']:
                    cursor.execute("DROP EXTENSION IF EXISTS fuzzystrmatch")
                else:
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch")
                    cursor.execute("SELECT * FROM pg_extension")
                    rows = cursor.fetchall()
                    installed = False
                    for row in rows:
                        if row[0] == 'fuzzystrmatch':
                            installed = True
                            print("Extension fuzzystrmatch installed for database '%s'" % db_name)
                            break
                    if not installed:
                        print("Error: extention fuzzystrmatch not installed for database '%s'" % db_name)
                        exit()


