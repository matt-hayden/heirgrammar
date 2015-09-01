#!/usr/bin/env python3
import os, os.path

import parser, tools

def _move(src, dest):
	assert os.path.isdir(src)
	if os.path.exists(dest):
		assert os.path.isdir(dest)
	if os.path.relpath(src) == os.path.relpath(dest):
		return ''
	syntax = '''# '{src}' -> '{dest}'
[[ -d '{dest}' ]] || mkdir -p '{dest}'
[[ -d '{src}' ]] && $MV -nv -t '{dest}' '{src}'/*
'''.format(**locals())
	return syntax
def hier_arrange(*args, prefix='', init='', **kwargs):
	ops = list(enumerate(tools.chunk(*args, **kwargs), start=1))
	if not ops:
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
			yield '''MV=gmv'''
			yield '''FIND=gfind'''
		else:
			yield '''MV=mv'''
			yield '''FIND=find'''
	for n, (size, pairs) in ops:
		for src, dest in pairs:
			if prefix:
				dest = prefix.format(n)+dest
			yield _move(src, dest)
	if not init:
		yield '''$FIND -empty -ls -delete'''

if __name__ == '__main__':
	from glob import glob
	import sys

	parser.setup(glob('rules/*'))
	#for line in hier_arrange('.', 200E6, prefix='volume_'):
	for line in hier_arrange(sys.argv[1], 0):
		print(line)
