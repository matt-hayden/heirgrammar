#!/usr/bin/env python3
from contextlib import suppress
import os, os.path
import shlex
import sys

__version__ = '0.2'
__all__ = [ '__version__' ]

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if __debug__ else logging.WARNING)
debug, info, warning, error, panic = logger.debug, logger.info, logger.warning, logger.error, logger.critical
__all__.extend('debug info warning error panic'.split())


### GENERIC
from .pager import pager # ought to be an external module

def get_command_line(args=sys.argv):
	script_filename = args[0]
	_, exe = os.path.split(sys.executable)
	root, filename = os.path.split(script_filename)
	if filename == '__main__.py':
		_, modname = os.path.split(root)
		return [ exe, '-m', modname ]+args[1:]
	else:
		return args
def sq(*args):
	return ' '.join(shlex.quote(str(m)) for m in args)
###
__all__.extend('get_command_line sq'.split())


from . import parser, tools, shtools, tagfile

__all__.extend('parser tools shtools tagfile'.split())
