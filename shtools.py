#!/usr/bin/env python3
import os, os.path
import shlex
import sys

import logging
logger=logging.getLogger(__name__)
debug, info, warning, error, panic = logger.debug, logger.info, logger.warning, logger.error, logger.critical

from .tools import *
from .utils import *

def _move(src, dest):
	assert os.path.exists(src)
	if os.path.exists(dest):
		assert os.path.isdir(dest)
	if os.path.relpath(src) == os.path.relpath(dest):
		return ''
	shsrc = shlex.quote(src)
	if dest.endswith(src):
		shdest = os.path.join(shlex.quote(dest[:-len(src)]), '"$src"')
	elif dest.startswith(src):
		shdest = os.path.join('"$src"', shlex.quote(dest[len(src):]))
	else:
		shdest = shlex.quote(dest)
	syntax = '''src={shsrc} dest={shdest}
  [[ -d "$dest" ]] || mkdir -p "$dest"
  [[ -d "$src" ]] && $MV -t "$dest" "$src"/*.* || file_error "$src"
'''.format(**locals())
	return syntax
def hier_arrange(*args, prefix='', init='', **kwargs):
	if not args:
		args = ('.',)
	if args == ('.',):
		fargs = ''
	else:
		fargs = sq(*args)
	do_sort = kwargs.pop('do_sort', True)
	chunks = chunk(*args, **kwargs) # returns a list of (size, (src, dest)) with dest=None for no change
	if not chunks:
		raise StopIteration
	total_size = sum(s for s, _ in chunks)
	if prefix:
		try:
			if prefix.format(0) == prefix:
				prefix += '{}'
		except:
			raise ValueError("Poorly-formed prefix string {}".format(prefix))
		if os.path.sep not in prefix:
			prefix += os.path.sep
	if init:
		yield init
	else:	
		yield '''#! /bin/bash
set -e

function file_error() { echo "$@" not a directory, ignoring >&2; }
'''
		if sys.platform.startswith('darwin'):
			yield '''MV="gmv -nt"
FIND=gfind
'''
		#elif sys.platform.startswith('win32'): # ...
		else:
			yield '''MV="mv -nv"
FIND=find

# {:.1f} MB in {} volumes
'''.format(total_size/10E6, len(chunks))
		yield '''# $FIND {fargs} \( -name .DS_Store -o -iname Thumbs.DB -o -empty \) -delete
# $FIND {fargs} -empty -delete
'''.format(**locals())
	for n, (size, pairs) in enumerate(chunks, start=1):
		if prefix:
			vol_root = prefix.format(n)
			yield '''
### Volume {n}: {size:,} bytes
vol_root={vol_root}
'''.format(**locals())
			for src, dest in pairs:
				if dest and do_sort:
					dest = vol_root+os.path.sep+dest
				else:
					dest = vol_root+os.path.sep+src
				yield _move(src, dest)
		else:
			for src, dest in pairs:
				if dest: # dest can be None if re-sorting not needed
					yield _move(src, dest)
	if not init:
		yield '''
$FIND {fargs} -empty -delete
'''.format(**locals())

def arrange_dirs(*args, fileout='', **kwargs):
	def _get_lines(*args, **kwargs):
		ha = list(hier_arrange(*args, **kwargs)) # heir_arrange is a generator of syntax lines
		if ha:
			yield from ha
	if hasattr(fileout, 'write'):
		debug("Writing to {}".format(fileout))
		fileout.write(os.linesep.join(_get_lines(*args, **kwargs)))
	elif isinstance(fileout, int):
		with open(fileout, 'w') as fo:
			return arrange_dirs(*args, fileout=fo, **kwargs)
	elif isinstance(fileout, str) and fileout:
		with open(fileout, 'w') as fo:
			return arrange_dirs(*args, fileout=fo, **kwargs)
	else:
		if fileout:
			warning("'{}' invalid, writing to standard out".format(fileout))
		print('\n'.join(_get_lines(*args, **kwargs)) )
