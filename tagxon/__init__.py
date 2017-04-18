
import os, os.path
import sys

from . import debug, info, warning, error, fatal


from .pager import pager # ought to be an external module
from . import parser, tools, shtools, tagfile

if sys.stderr.isatty():
	import tqdm
	progress_bar = tqdm.tqdm
else:
	def progress_bar(iterable, **kwargs):
		return iterable

__all__ = 'parser tools shtools tagfile'.split()

