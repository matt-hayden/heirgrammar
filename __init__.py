#!/usr/bin/env python3
from contextlib import suppress
import os

__version__ = '0.1'
__all__ = 'debug info warning error panic'.split()

import logging
logger = logging.getLogger(__name__)
debug, info, warning, error, panic = logger.debug, logger.info, logger.warning, logger.error, logger.critical

if not __debug__:
	def debug(*args, **kwargs):
		pass

#
from . import parser, tools, shtools

__all__.extend('parser tools shtools'.split())
