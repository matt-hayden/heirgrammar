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
    --no-commas=BOOL  Don't split directory names with commas [default: False]
    --all-commas=BOOL  Split on all commas, rather than just commas that split predefined tags [default: False]
    --use-tagfiles=BOOL  Find .tags (JSON format) and insert tags appropriately [default: True]
    -A PATTERN, --append=PATTERN  Comma-separated tags that will be added, AND emphasized
    -B PATTERN, --prepend=PATTERN  Comma-separated tags that will be added, but not emphasized
    -m INT, --min-rank=INT  Ignore operations not meeting a threshold
    -o FILE, --output=FILE  Some output is more useful when directed at a file
    -p PATTERN, --prefix=PATTERN  When directories reach --volumesize, then they will begin based on this pattern [e.g. vol_{:03d}]
    -r RULES_FILES..., --rules=RULES_FILES...  [default: rules,.rules,../rules,../.rules]
    -s INT, --volumesize=INT  assume directories of INT bytes are preferred [e.g. 24411.5E6]
    -S, --do-sort  With dirsplit, also sort through directories [default: False]
    -x PATTERNS, --exclude=PATTERNS...  [default: delme,sortme,working]

"""
import sys

import docopt

from . import *
from .cli import main

options = docopt.docopt(__doc__, version=__version__) # make sure to pop 'PATHS' out as file arguments
args = options.pop('PATHS')
sys.exit(main(*args, **options))
