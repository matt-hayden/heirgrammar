#!/usr/bin/env python3
from contextlib import suppress
import os, os.path
from os.path import exists, isfile, isdir
import shutil

from . import debug, info, warning, error, panic
from . import parser
from . import TagFile

class Namespace(dict):
	def __init__(self, *args, **kwargs):
		super(Namespace, self).__init__(*args, **kwargs)
		self.__dict__ = self

def path_split(path, stopwords=['delme', 'rules', 'sortme', 'working'], sep=os.path.sep):
	path_parts = [ p for p in path.split(sep) if p not in ['', '.', '..'] ]
	parts = []
	a = parts.append
	for p in path_parts:
		if ',' in p:
			sub_parts = p.split(',')
			tags, nontags = parser.split(sub_parts)
			if nontags:
				a(p)
			else:
				parts.extend(sub_parts)
		else:
			a(p)
	#if any(w in parts for w in stopwords):
	if set(stopwords) & set(parts):
		return [], path
	tags, s = parser.split(parts)
	return tags, sep.join(str(p) for p in s)
def path_arrange(*args, **kwargs):
	sep = kwargs.get('sep', os.path.sep)
	tags, newpath = path_split(*args, **kwargs)
	if tags:
		highest_pri = max(t.pri for t in tags)
		total_rank = sum(t.rank for t in tags)
	else:
		highest_pri = total_rank = 0
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
	info('Moving {} to {}'.format(arg, my_dest))
	tf.merge(newpath, tags)
	return newpath, tagfile
def walk(*args, **kwargs):
	for arg in args:
		assert not isinstance(arg, list)
		assert os.path.isdir(arg)
		for root, dirs, files in os.walk(arg):
			src = os.path.relpath(root)
			if (not files) or (src in ['.', '..', '']):
				debug("Skipping "+src)
				continue
			else:
				file_paths = [ os.path.join(src, f) for f in files ]
				with suppress(FileNotFoundError):
					stat_by_file = [ (f, os.stat(f) ) for f in file_paths ]
				file_size = sum(s.st_size for (f, s) in stat_by_file)
			pri, rank, newpath = path_arrange(src, **kwargs)
			yield pri, rank, file_size, (src, None if (src==os.path.relpath(newpath)) else newpath)
def _chunker(rows, volumesize, this_size=0, this_vol=[]):
	assert volumesize
	errors = []
	e = errors.append
	for row in rows:
		p, r, s, (src, dest) = row
		if (volumesize < s):
			e(row)
			continue
		elif volumesize < this_size+s:
			yield this_size, this_vol
			this_size, this_vol = s, [ (src, dest) ]
		else:
			this_size += s
			this_vol.append( (src, dest) )
	if this_size: # last
		yield this_size, this_vol
	if errors:
		max_size = max(s for _, _, s, _ in errors)
		error("{} file(s) too big for {:,} byte volume, "
			  "consider volumes of at least {:,}".format(len(errors), volumesize, max_size) )
		for row in errors:
			p, r, s, (src, dest) = row
			info("File '{}' too big for {:,} byte volume".format(src, volumesize) )
def chunk(*args, chunker=_chunker, **kwargs):
	volumesize = kwargs.pop('volumesize', 0)
	if kwargs.pop('by_priority', True):
		debug("Sort order: priority, rank, size")
		def key(arg):
			p, r, s, _ = arg
			return -p, r, -s
	else:
		debug("Sort order: rank, size")
		def key(arg):
			p, r, s, _ = arg
			return r, -s
	my_list = sorted(walk(*args, **kwargs), key=key)
	if not volumesize:
		osize = len(my_list)
		my_list = [ (p, r, s, (src, dest)) for (p, r, s, (src, dest)) in my_list if dest ]
		debug("{} directories unchanged".format(osize-len(my_list)) )
	total_size = sum(s for _, _, s, _ in my_list)
	if not total_size:
		return []
	if not volumesize or (total_size <= volumesize):
		if total_size:
			return [(total_size, [pairs for _, _, _, pairs in my_list])]
		else:
			return []
	else:
		return list(chunker(my_list, volumesize))
#
if __name__ == '__main__':
	from glob import glob
	import sys

	parser.setup(glob('rules/*.rules'))
	for arg in sys.argv[1:]:
		print(arg, path_split(arg))
