#!/usr/bin/env python3
"""Apply rules to rename directories. Note that already-sorted directories are ignored, which is maybe not what you expect for the volume-splitting functions
  Usage:
    Sorter dirsplit [options] [--] [PATHS]...
    Sorter du [options] [--] [PATHS]...
    Sorter print [options] [--] [PATHS]...
    Sorter sort [options] [--] [PATHS]...
    Sorter test [options] [--] EXPR...

  Options:
    -h --help  show this help message and exit
    --version  show version and exit
    -x, --exclude=PATTERNS...  [default: delme,sortme,working]
    -o, --output=FILE  Some output is more useful when directed at a file
    -p, --prefix=TEXT  When directories reach --volumesize, then they will begin based on this pattern [default: vol_{:03d}]
    -r RULES_FILES..., --rules=RULES_FILES...  [default: rules,.rules,../rules,../.rules]
    -V, --volumesize=INT  assume directories of INT bytes are preferred [try: 24411.5E6]
    --all-commas=BOOL  Split on all commas, rather than just commas that split tags [default: False]

"""
import sys

import docopt

from . import *
from .cli import main

args = docopt.docopt(__doc__, version=__version__) # make sure to pop 'PATHS' out as file arguments
sys.exit(main(*args.pop('PATHS'), **args))
