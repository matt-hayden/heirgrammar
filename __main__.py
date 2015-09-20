#!/usr/bin/env python3
"""Apply rules to rename directories. Note that already-sorted directories are ignored, which is maybe not what you expect for the volume-splitting functions
  Usage:
    Sorter du [options] [--] [PATHS]...
    Sorter print [options] [--] [PATHS]...
    Sorter sort [options] [--] [PATHS]...
    Sorter test [options] [--] EXPR

  Options:
    -h --help  show this help message and exit
    --version  show version and exit
    -x, --exclude=PATTERNS...  [default: delme sortme]
    -o, --output=FILE  Some output is more useful when directed at a file
    -p, --prefix=TEXT  When directories reach --volumesize, then they will begin based on this pattern [default: vol_{:03d}]
    -r RULES_FILES..., --rules=RULES_FILES...
    -V, --volumesize=INT  assume directories of INT bytes are preferred [try: 24411.5E6]

"""
import docopt

from . import __version__
from .cli import *
from .parser import print_Taxonomy

def main(arguments=docopt.docopt(__doc__, version=__version__)):
	print(arguments)

	if arguments['--rules']:
		r=arguments.pop('--rules')
		setup([r]) # TODO: r ought to be a list already
	else:
		setup()
	if arguments['--exclude']:
		stopwords = [ s.strip() for s in arguments.pop('--exclude').split(',') ]
	else:
		stopwords = [ 'delme', 'sortme', 'working' ]
	if 'rules' not in stopwords:
		stopwords += ['rules']

	print(arguments)

	if arguments['print']:
		return print_Taxonomy()
	elif arguments['sort']:
		if arguments['--volumesize']:
			vs = int(float(arguments.pop('--volumesize')))
			arrange_dirs(*arguments['PATHS'],
						 volumesize=vs,
						 prefix=arguments.pop('--prefix'),
						 fileout=arguments.pop('--output', None),
						 stopwords=stopwords )
		else:
			arrange_dirs(*arguments['PATHS'],
						 fileout=arguments.pop('--output', None),
						 stopwords=stopwords )
	elif arguments['test']:
		print(parser.split(arguments['EXPR'].split(',') ) )

import sys
sys.exit(main())
