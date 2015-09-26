#!/usr/bin/env python3
import json
import os, os.path
import shlex

import Sorter
import Sorter.cli
from Sorter import debug, info, warning, error, panic

Sorter.cli.setup()

purge_parts=set('+more more'.split())

def expand_from_tags_files(*args):
	for arg in args:
		for root, dirs, files in os.walk(arg):
			prepend = []
			if '.tags' in files:
				tagfile = os.path.join(root, '.tags')
				with open(tagfile) as fi:
					try:
						tags_by_file = json.load(fi)
					except:
						error("{} is invalid".format(tagfile))
						raise
				if '*' in tags_by_file:
					prepend.extend(tags_by_file.pop('*'))
			else:
				warning("No .tags found in "+root)
				tagfile, tags_by_file = None, {}
			files = [ f for f in files if not f.startswith('.') ]
			dirs = [ d for d in dirs if not d.startswith('.') ]
			if not files:
				debug("Skipping "+root)
				continue
			head_part = [ p for p in root.split(os.path.sep) if p not in purge_parts ]+prepend
			for f in files:
				if f not in tags_by_file:
					if prepend:
						warning("{f} not found in {tagfile}, assuming {prepend}".format(**locals()))
					else:
						error("{f} not found in {tagfile}, skipping".format(**locals()))
						continue
				tags, nontags = Sorter.parser.split(head_part+tags_by_file.pop(f, []))
				if not tags:
					error(root+" unsortable")
					continue
				newpath = os.path.sep.join(str(t) for t in tags+nontags)
				max_pri = max(t.pri for t in tags)
				combined_rank = sum(t.rank for t in tags)
				yield max_pri, combined_rank, None, (os.path.join(root, f), newpath)
			if tags_by_file:
				warning("{} file(s) not found in {}".format(len(tags_by_file), root))
				for f in tags_by_file:
					info("{} not found".format(f))
#
def _move_script(*args):
	def key(row):
		p, r, s, _ = row
		return -p, r
	yield '''
#
set -e
MV="mv -nv"
'''
	for row in sorted(expand_from_tags_files(*args), key=key):
		pri, rank, size, (src, dest) = row
		yield '''
# pri={pri} rank={rank}
# {src} => {dest}
mkdir -p "{dest}"
[[ -e "{src}" ]] && $MV -t "{dest}" "{src}"
'''.format(**locals())

import sys
args = sys.argv[1:]
with open('runme', 'w') as fo:
	fo.write('\n'.join(_move_script(*args)))
