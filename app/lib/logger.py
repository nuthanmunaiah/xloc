import os
import sys


def error(message, exit=True):
    sys.stderr.write('ERROR: {0}\n'.format(message))
    if exit:
        sys.exit(1)


def info(message):
    sys.stdout.write('INFO: {0}\n'.format(message))


def debug(message):
    if 'DEBUG' in os.environ:
        sys.stdout.write('DEBUG: {0}\n'.format(message))
