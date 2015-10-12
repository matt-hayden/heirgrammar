#!/usr/bin/env python3
from contextlib import suppress
import os, os.path
import shlex
import sys

__version__ = '0.2'
__all__ = [ '__version__' ]

import logging
logger = logging.getLogger(__name__)
if __debug__:
	logging.basicConfig(level=logging.DEBUG)
else:
	logger.setLevel(logging.WARNING)
debug, info, warning, error, panic = logger.debug, logger.info, logger.warning, logger.error, logger.critical
__all__.extend('debug info warning error panic'.split())

from .pager import pager # ought to be an external module
from . import parser, tools, shtools, tagfile
from .utils import *

__all__.extend('parser tools shtools tagfile'.split())
