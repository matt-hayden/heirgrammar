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

def path_split(path, stopwords=['delme', 'rules', 'sortme', 'working'], sep=os.path.sep, **kwargs):
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
	tags, s = parser.split(parts, **kwargs)
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
			file_paths = [ os.path.join(src, f) for f in files ]
			if (not files) or (src in ['.', '..', '']):
				debug("Skipping "+src)
				continue
			pri, rank, newpath = path_arrange(src, **kwargs)
			if src == os.path.relpath(newpath):
				debug("Doing nothing: "+src)
				continue
			with suppress(FileNotFoundError):
				stat_by_file = [ (f, os.stat(f) ) for f in file_paths ]
			file_size = sum(s.st_size for (f, s) in stat_by_file)
			yield pri, rank, file_size, (src, newpath)
def chunk(*args, **kwargs):
	volumesize = kwargs.pop('volumesize', 0)
	if kwargs.pop('pri', False):
		def key(arg):
			p, r, s, _ = arg
			return -p, r, -s
	else:
		def key(arg):
			p, r, s, _ = arg
			return r, -s
	chunker = kwargs.pop('chunker', None)
	if not chunker:
		def chunker(my_list, this_size=0, this_vol=[]):
			for p, r, s, (src, dest) in my_list:
				assert s < volumesize
				if volumesize < this_size+s:
					yield this_size, this_vol
					this_size, this_vol = s, [ (src, dest) ]
				else:
					this_size += s
					this_vol.append( (src, dest) )
			if this_size: # last
				yield this_size, this_vol
	my_list = sorted(walk(*args, **kwargs), key=key)
	my_size = sum(s for p, r, s, _ in my_list)
	if not volumesize or (my_size <= volumesize):
		if my_size:
			return [(my_size, [pairs for _, _, _, pairs in my_list])]
		else:
			return None
	return list(chunker(my_list))
#
if __name__ == '__main__':
	from glob import glob
	import sys

	parser.setup(glob('rules/*.rules'))
	for arg in sys.argv[1:]:
		print(arg, path_split(arg))
