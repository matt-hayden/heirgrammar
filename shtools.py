#!/usr/bin/env python3
import os, os.path
import shlex
import sys

from . import debug, info, warning, error, panic
from . import tools

def _move(src, dest):
	assert os.path.isdir(src)
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
		fargs = ' '.join(shlex.quote(a) for a in args) # see quote assert above
	chunks = tools.chunk(*args, **kwargs) # returns a list of (size, (src, dest)) with dest=None for no change
	if not chunks:
		raise StopIteration
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
		yield '''#!/bin/bash
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

# {} volumes
'''.format(len(chunks))
		yield '''$FIND {fargs} \( -name .DS_Store -o -iname Thumbs.DB -o -empty \) -delete
$FIND {fargs} -empty -delete
'''.format(**locals())
	for n, (size, pairs) in enumerate(chunks, start=1):
		if prefix:
			yield '''
### Volume {n}: {size:,} bytes
'''.format(**locals())
			for src, dest in pairs:
				dest = prefix.format(n)+dest if dest else prefix.format(n)+src
				yield _move(src, dest)
		else:
			for src, dest in pairs:
				assert dest
				yield _move(src, dest)
	if not init:
		yield '''
$FIND {fargs} -empty -delete
'''.format(**locals())

if __name__ == '__main__':
	from glob import glob
	import sys

	parser.setup(glob('rules/*.rules'))
	ha = list(hier_arrange(*sys.argv[1:]))
	if ha:
		print("# Resulting script:")
		for line in ha:
			print(line)
	else:
		warning("No results for {}".format(' '.join(sys.argv)))
