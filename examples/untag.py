
import collections
from contextlib import suppress
import json
import os, os.path
import string


import logging
logging.basicConfig(level=logging.DEBUG)
from logging import debug, info, warning, error, critical
panic=critical


from Sorter import parser, cli
from Sorter.Taxon import tag

tag_counts = collections.Counter()
cli.setup()

import sys
args = sys.argv[1:]

bad_chars = ''' '{}[]()*&?<>#!".'''
def get_common_prefix(strings):
	lengths = [ len(s) for s in strings ]
	shortest, longest = min(lengths), max(lengths)
	p = ''
	for i in range(shortest):
		t = set(s[i] for s in strings)
		if len(t) == 1:
			p += t.pop()
		else:
			break
	return p

destroot = 'untagged_{}'.format(os.getpid())
assert not os.path.exists(destroot)

dirs_by_name = collections.defaultdict(dict)
for arg in args:
	for root, dirs, files in os.walk(arg):
		src = os.path.relpath(root)
		files = [ f for f in files if not f.startswith('.') ]
		dirs = [ d for d in dirs if not d.startswith('.') ]
		fullnames = [ os.path.join(src,f) for f in files ]

		if not files:
			continue
		debug(src)
		tags, nontags = parser.split(src.split(os.path.sep))
		if nontags:
			dest = os.path.sep.join(nontags)
		else:
			names = sorted(files)
			dest = get_common_prefix(names)
			if not dest or dest.isdigit():
				sizes = [ (os.path.getsize(f), f) for f in fullnames ]
				total_size = sum(s for s, _ in sizes)
				_, biggest = max(sizes, key=lambda p: p[0])
				_, biggest_ext = os.path.splitext(biggest)
				dest = '{}_{}_{}'.format(biggest_ext, total_size, len(files))
		dest = ''.join('_' if c in bad_chars else c for c in dest).strip('_')
		
		tag_counts.update(tags)
		
		info(src+" => "+dest)
		for f in fullnames:
			assert f not in dirs_by_name[dest]
			dirs_by_name[dest][f] = [ str(t) for t in tags ]
for destdir, tree in sorted(dirs_by_name.items()):
	dest = os.path.join(destroot, destdir)
	with suppress(FileExistsError):
		os.makedirs(dest)
	tags = { os.path.basename(f): tags for f, tags in tree.items() }
	if len(tags) != len(tree):
		error("filename collision: "+dest)
		for p, f in sorted((os.path.split(fn) for fn in tree.keys()), key=lambda p: p[-1]):
			print("{:>99}/{}".format(p,f))
		print()
for destdir, tree in sorted(dirs_by_name.items()):
	dest = os.path.join(destroot, destdir)
	#with suppress(FileExistsError):
	#	os.makedirs(dest)
	tags = { os.path.basename(f): tags for f, tags in tree.items() }
	#assert len(tags) == len(tree), "filename collision: {}".format(tree)
	print()
	info(dest)
	tagfile = os.path.join(dest, '.tags')
	info("Writing "+tagfile)
	with open(tagfile, 'w') as fo:
		json.dump(tags, fo)
	with open(tagfile) as fi:
		debug(json.load(fi))
	with open(os.path.join(dest, '.orig'), 'w') as fo:
		fo.write(destdir)
	print()
	for src_fn in tree.keys():
		dest_fn = os.path.join(dest, os.path.basename(src_fn))
		assert not os.path.exists(dest_fn)
		debug(("Linking", src_fn, dest_fn))
		os.link(src_fn, dest_fn)

