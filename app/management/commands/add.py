import csv
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
                'function as generated by SciTools Understand.'
            )
        ),
    )

    help = (
        'Loads the SLOC per function from a CSV file created by SciTools'
        'Understand into a SQLite database.'
    )

    def handle(self, *args, **options):
        source = options['source']

        if not source or not os.path.exists(os.path.expanduser(source)):
            raise Exception('{0} is not a valid CSV path'.format(source))

        function = None
        duplicates = list()
        functions = set()
        with open(source) as file_:
            reader = csv.reader(file_)
            for row in reader:
                if 'Function' in row[0]:
                    name = row[1]
                    file = row[2]
                    sloc = int(row[3])

                    function = Function()

                    function.name = name
                    function.file = file
                    function.sloc = sloc

                    if function not in functions:
                        functions.add(function)
                    else:
                        duplicates.append(function)
                        function = [f for f in functions if f == function][0]
                        duplicates.append(function)
                        functions.remove(function)

        if len(functions) > 0:
            logger.debug('Adding {0} functions.'.format(len(functions)))
            Function.objects.bulk_create(functions)

            if len(duplicates) > 0:
                for function in duplicates:
                    logger.debug(
                        'Duplicate {0} in {1} with {2} SLOC'.format(
                            function.name, function.file, function.sloc
                        )
                    )
            logger.info('Loaded {0} functions.'.format(len(functions)))