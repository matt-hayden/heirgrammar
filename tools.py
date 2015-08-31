#!/usr/bin/env python3
import os, os.path
from os.path import exists, isfile, isdir
import shutil

import parser, TagFile

debug=print


def path_split(path, stopwords=['sortme'], sep=os.path.sep, **kwargs):
	parts = [ p for p in path.split(sep) if p not in ['', '.', '..'] ]
	#if any(w in parts for w in stopwords):
	if set(stopwords) & set(parts):
		return
	tags, s = parser.split(parts, **kwargs)
	return tags, sep.join(str(p) for p in s)
def path_arrange(*args, **kwargs):
	sep = kwargs.get('sep', os.path.sep)
	tags, newpath = path_split(*args, **kwargs)
	highest_pri = max(t.pri for t in tags)
	total_rank = sum(t.rank for t in tags)
	return highest_pri, total_rank, sep.join(str(t) for t in tags+[newpath])
def path_detag(arg, tagfile='.tags', move=shutil.move, dest='tagged', **kwargs):
	tags, newpath = path_split(arg, **kwargs)
	if tags:
		my_dest = os.path.join(dest, newpath)
	else:
		debug('Moving {} to {}'.format(arg, dest))
		debug('Not entering {} into a tagfile'.format(arg))
		return newpath, None
	if newpath in ['.', '..', '']:
		tf = TagFile.TagFile(os.path.join(dest, tagfile))
	else:
		tf = TagFile.TagFile(os.path.join(my_dest, tagfile))
	if not isdir(my_dest):
		os.makedirs(my_dest)
	debug('Moving {} to {}'.format(arg, my_dest))
	tf.merge(newpath, tags)
	return newpath, tagfile
def walk(*args, **kwargs):
	for root, dirs, files in os.walk(*args, **kwargs):
		if files:
			print(root, path_arrange(root))
def check_if_sorted(arg, **kwargs):
	_, _, newpath = path_arrange(arg, **kwargs)
	return (newpath in arg)
#
if __name__ == '__main__':
	parser.setup('examples')
