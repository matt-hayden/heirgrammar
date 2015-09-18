#!/usr/bin/env python3
import os, os.path
import sys

from . import debug, info, warning, error, panic
from . import tools

def _move(src, dest):
	assert os.path.isdir(src)
	if "'" in src or "'" in dest:
		return '# TODO: {} -> {}'.format(src, dest)
	if os.path.exists(dest):
		assert os.path.isdir(dest)
	if os.path.relpath(src) == os.path.relpath(dest):
		return ''
	syntax = '''# '{src}' -> '{dest}'
[[ -d '{dest}' ]] || mkdir -p '{dest}'
[[ -d '{src}' ]] && $MV -t '{dest}' '{src}'/*
'''.format(**locals())
	return syntax
def hier_arrange(*args, prefix='', init='', **kwargs):
	if args == ('.',):
		fargs = ''
	else:
		fargs = ' '.join("'{}'".format(a) for a in args) # see quote assert above
	chunks = tools.chunk(*args, **kwargs)
	if not chunks:
		raise StopIteration
	if prefix:
		if '{}' not in prefix:
			prefix += '{}'
		if not prefix.endswith(os.path.sep):
			prefix += os.path.sep
	if init:
		yield ''
		yield init
		yield ''
	else:	
		if sys.platform.startswith('darwin'):
			yield '''MV="gmv -nt"'''
			yield '''FIND=gfind'''
		#elif sys.platform.startswith('win32'): # ...
		else:
			yield '''MV="mv -nv"'''
			yield '''FIND=find'''
		yield ''
		yield ''
		yield '''$FIND {fargs} \( -name .DS_Store -o -iname Thumbs.DB -o -empty \) -delete'''.format(**locals())
		yield '''$FIND {fargs} -empty -delete'''.format(**locals())
	for n, (size, pairs) in enumerate(chunks, start=1):
		for src, dest in pairs:
			if prefix:
				dest = prefix.format(n)+dest
			yield _move(src, dest)
	if not init:
		yield ''
		yield '''$FIND {fargs} -empty -delete'''.format(**locals())
		yield ''

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
