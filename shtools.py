#!/usr/bin/env python3
import os, os.path
import shlex
import sys

from . import debug, info, warning, error, panic
from .tools import *
from .utils import *

def _move(src, dest):
	assert os.path.exists(src)
	if os.path.exists(dest):
		assert os.path.isdir(dest)
	if os.path.relpath(src) == os.path.relpath(dest):
		return ''
	shsrc = shlex.quote(src)
	shdest = shlex.quote(dest)
	syntax = '''# {shsrc} -> {shdest}
[[ -d {shdest} ]] || mkdir -p {shdest}
[[ -d {shsrc} ]] && $MV -t {shdest} {shsrc}/*
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
		yield '''$FIND {fargs} \( -name .DS_Store -o -iname Thumbs.DB -o -empty \) -delete
$FIND {fargs} -empty -delete
'''.format(**locals())
	for n, (size, pairs) in enumerate(chunks, start=1):
		if prefix:
			yield '''
### Volume {n}: {size:,} bytes
'''.format(**locals())
			for src, dest in pairs:
				if dest and do_sort:
					dest = prefix.format(n)+dest
				else:
					dest = prefix.format(n)+src
				yield _move(src, dest)
		else:
			for src, dest in pairs:
				assert dest
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
	elif isinstance(fileout, (str, int)):
		with open(fileout, 'w') as fo:
			return arrange_dirs(*args, fileout=fo, **kwargs)
	else:
		if fileout:
			warning("'{}' invalid, writing to standard out".format(fileout))
		print('\n'.join(_get_lines(*args, **kwargs)) )
