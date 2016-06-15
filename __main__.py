#! /usr/bin/env python3
import logging
if __debug__:
	logging.basicConfig(level=logging.DEBUG, filename='log')
logging.basicConfig(level=logging.WARNING)

import sys

from .cli import main
from .args import get_arguments

#sys.exit(main(*sys.argv[1:]))
#sys.exit( main(get_arguments()) )
main(get_arguments())
