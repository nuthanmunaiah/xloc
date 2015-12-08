import argparse
import os
import re
import sys

import logger

RE_PREPROCESSOR_FILE = re.compile('.*\.i$')
RE_FILENAME = re.compile('^[/<]')


class Collector(object):
    def collect(self, rooted, indir, outdir, bindir):
        for dirpath, dirs, files in os.walk(indir):
            for f in [f for f in files if RE_PREPROCESSOR_FILE.search(f)]:
                self._process(rooted, dirpath, f, indir, outdir, bindir)

    def _process(self, rooted, dirpath, filename, indir, outdir, bindir):
        filepath = os.path.join(dirpath, filename)
        logger.debug('Processing {0}'.format(filepath))
        contents = self._parse(filepath)

        for outfile in contents:
            if len(contents[outfile]) > 0:
                if not rooted:
                    outfilepath = os.path.join(
                        dirpath.replace(indir, outdir), outfile
                    )
                else:
                    outfilepath = os.path.join(
                        outdir, outfile
                    )
                if bindir:
                    outfilepath = outfilepath.replace(bindir, '.')
                logger.debug(outfilepath)
                outfilepath = os.path.realpath(outfilepath)

                if not os.path.exists(outfilepath):
                    logger.debug('Generating {0}'.format(outfilepath))
                    self._make_dirs_(outfilepath)
                    with open(outfilepath, 'w') as file_:
                        for line in contents[outfile]:
                            file_.write(line)

    def _parse(self, filepath):
        logger.debug('Parsing {0}'.format(filepath))

        contents = dict()
        with open(filepath) as file_:
            lines = file_.readlines()
        num_lines = len(lines)

        if num_lines > 0:
            index = 0
            filename = None
            while index < len(lines):
                line = lines[index]

                # Header: Parse file name from the header and continue
                if line.startswith('# '):
                    filename = self._get_filename_(line.strip('\n'))
                    if filename:
                        if filename not in contents:
                            contents[filename] = list()
                else:
                    if filename:
                        # Non-header: Parse line
                        contents[filename].append(line)

                index += 1

        return contents

    def _get_filename_(self, header):
        begin = header.find('"') + 1
        end = header.find('"', begin)

        filename = header[begin:end]
        return filename if not RE_FILENAME.match(filename) else None

    def _make_dirs_(self, filepath):
        dirpath = os.path.abspath(os.path.dirname(filepath))
        os.makedirs(dirpath, exist_ok=True)


def _get_args():
    description = (
        'Generate source code files from pre-processed source code files.'
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '-b', '--bindir', action='store', default=None,
        help=(
            'Absolute path to a directory where the output files will be '
            'created. The *.i files corresponding to each of the *.o file '
            'will have paths relative to the location of the source code and '
            'not the location of the *.o file. Assuming the output directory '
            'i.e. binary directory (bindir) is created in the same directory '
            'as the source code files are, obtaining the location of the '
            'source code files involves replacing the name of the bindir with '
            'a dot (.).'
        )
    )
    parser.add_argument(
        '-r', '--rooted', action='store_true',
        help=(
            'Assume the filename specification in the intermediate files as '
            'being rooted at source root versus relative to current directory.'
        )
    )
    parser.add_argument(
        'indir', action='store', type=path,
        help=(
            'Absolute path to input directory containing the pre-processed '
            'source code i.e. source compiled with the -save-temps=obj option '
            'to gcc.'
        )
    )
    parser.add_argument(
        'outdir', action='store', type=str,
        help=(
            'Absolute path to output directory where the source files '
            'generated from processing the *.i (pre-processor expanded '
            'versions of *.c files) contained in the input directory.'
        )
    )

    return vars(parser.parse_args())


def path(value):
    value = os.path.expanduser(value)
    if not (os.path.exists(value) and os.path.isdir(value)):
        error = argparse.ArgumentTypeError(
            '{0} is not a valid path to a directory'.format(value)
        )
        raise error
    return value


if __name__ == '__main__':
    args = _get_args()

    rooted = args['rooted']
    indir = args['indir']
    outdir = args['outdir']
    bindir = args['bindir']
    if not os.path.exists(outdir):
        logger.debug('Creating {0}'.format(outdir))
        os.mkdir(outdir)

    collector = Collector()
    collector.collect(rooted, indir, outdir, bindir)
