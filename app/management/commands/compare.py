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
            '-p', type='str', dest='primary',
            help=(
                'Absolute path to the CSV file containing the SLOC per'
                'function as generated by SciTools Understand.'
            )
        ),
        make_option(
            '-s', type='str', dest='secondary',
            help=(
                'Absolute path to the CSV file containing the SLOC per'
                'function as generated by SciTools Understand.'
            )
        ),
    )

    help = (
        'Compares SLOC generated by SciTools Understand for source code that '
        'is not pre-processed and for that which is pre-processed.'
    )

    def handle(self, *args, **options):
        primary = options['primary']
        secondary = options['secondary']

        if not primary or not os.path.exists(os.path.expanduser(primary)):
            raise Exception('{0} is not a valid CSV path'.format(primary))
        if not secondary or not os.path.exists(os.path.expanduser(secondary)):
            raise Exception('{0} is not a valid CSV path'.format(secondary))

        primary_dataset = dict()
        secondary_dataset = dict()

        function = None
        with open(primary) as file_:
            reader = csv.reader(file_)

            for row in reader:
                if 'Function' in row[0]:
                    function = Function()

                    function.name = row[1]
                    function.file = row[2]

                    if function not in primary_dataset:
                        primary_dataset[function] = int(row[3])
                    else:
                        logger.debug(
                            '{0} duplicate in {1}'.format(function, primary)
                        )

        with open(secondary) as file_:
            reader = csv.reader(file_)

            for row in reader:
                if 'Function' in row[0]:
                    function = Function()

                    function.name = row[1]
                    function.file = row[2]

                    if function not in secondary_dataset:
                        secondary_dataset[function] = int(row[3])
                    else:
                        logger.debug(
                            '{0} duplicate in {1}'.format(function, secondary)
                        )

        match = 0
        for item in secondary_dataset:
            if item in primary_dataset:
                if secondary_dataset[item] == primary_dataset[item]:
                    match += 1

        logger.info(
            '{0}/{1} having matching SLOC'.format(
                match, len(secondary_dataset)
            )
        )