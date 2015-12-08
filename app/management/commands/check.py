import csv
import operator
import os
import sys

from optparse import make_option, OptionValueError
from django.conf import settings
from django.core.management.base import BaseCommand


from app.lib import logger
from app.models import Function


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '-s', type='str', dest='source',
            help=(
                'Absolute path to the CSV file containing the SLOC per'
                'function as contained in the PostgreSQL database.'
            )
        ),
    )

    help = (
        'Checks the SLOC per function contained in a CSV file created by'
        'exporting the data from a PostgreSQL database against that contained '
        'in a SQLite database that contains the SLOC per function from '
        'SciTools Understand.'
    )

    def handle(self, *args, **options):
        source = options['source']

        if not source or not os.path.exists(os.path.expanduser(source)):
            raise Exception('{0} is not a valid CSV path'.format(source))

        found = 0
        missing = set()
        with open(source) as file_:
            reader = csv.reader(file_)
            function = None
            for row in reader:
                name = row[0]
                file = row[1]
                sloc = int(row[2]) if row[2] else None

                function = None
                functions = Function.objects.filter(name=name)
                if functions.exists():
                    function = functions.filter(file=file)
                    if function.exists():
                        # Exact Match
                        function = function.get()
                    elif functions.count() == 1:
                        # Guesstimate: When filtering a function by name alone
                        # yields one result, it may be appropriate to assume
                        # that result to be the one we are looking for.
                        function = functions.get()
                        logger.debug(
                            '{0} ~ {1}'.format(name, function.identity)
                        )

                if function is not None and type(function) is Function:
                    found += 1
                else:
                    missing.add('{0}@{1}'.format(name, file))

        logger.info('{0} functions have SLOC'.format(found))
        logger.info('{0} functions do not have SLOC'.format(len(missing)))
        for item in missing:
            logger.debug('{0}'.format(item))
