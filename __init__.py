#! /usr/bin/env python3
from contextlib import suppress
import os, os.path
import shlex
import sys

__version__ = '0.2.1'
__all__ = [ '__version__' ]

#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARNING)

from .pager import pager # ought to be an external module
from . import parser, tools, shtools, tagfile
from .utils import *

__all__.extend('parser tools shtools tagfile'.split())
