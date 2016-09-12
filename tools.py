#!/usr/bin/env python3
from contextlib import suppress
import os, os.path
from os.path import exists, isfile, isdir
import shlex
import shutil

import logging
logger = logging.getLogger(__name__)
debug, info, warning, error, panic = logger.debug, logger.info, logger.warning, logger.error, logger.critical

import tqdm

from . import parser, tagfile

def path_split(path,
			   sep=os.path.sep,
			   all_commas=None,
			   no_commas=None,
			   stopwords=['delme', 'rules', 'sortme', 'working'],
			   **kwargs):
	"""
	Returns:
		(tags, destination directory)
	"""
	options = kwargs
	def _expand_commas(splitted_path):
		for p in splitted_path:
			if not no_commas:
				sub_parts = [ c.strip('+_ ') for c in p.split(',') ]
			else:
				sub_parts = [p.strip('+_ ')]
			assert sub_parts
			tags, nontags = parser.split(sub_parts)
			if not tags:
				yield p
			elif nontags and not all_commas:
				yield p
			else:
				#debug("Splitting on commas")
				yield from tags
				yield from nontags
	#
	if isinstance(path, str):
		path_parts = [ p for p in path.split(sep) if p not in ['', '.', '..'] ]
	else:
		raise ValueError(path)

	### Custom:
	try:
		p, n = path_parts[0].rsplit('.', 1)
		if n.isdigit():
			debug("Removing extension from {}".format(path_parts[0]))
			path_parts[0] = p
		elif n in [ '~{}~'.format(x) for x in range(1,9+1) ]:
			debug("Removing backup extension from {}".format(path_parts[0]))
			path_parts[0] = p
	except:
		pass
	###
	parts = path_parts if no_commas else list(_expand_commas(path_parts))
	sw = set(stopwords) & set(parts)
	if sw:
		debug("Stopword reached in {}".format(parts))
		if sw == set(['delme']):
			print('# {trash} {}'.format(shlex.quote(path), trash='trash'))
		return [], path
	tags, s = parser.split(parts, **options)
	return tags, sep.join(str(p) for p in s)
def path_arrange(*args, sep=os.path.sep, **kwargs):
	options = kwargs
	tags, newpath = path_split(*args, **options)
	if tags:
		try:
			highest_pri = max(t.pri for t in tags)
		except:
			highest_pri = 0
		try:
			total_rank = sum(t.rank for t in tags)
		except:
			total_rank = 0
	else:
		highest_pri = total_rank = 0
	return highest_pri, total_rank, sep.join(str(t) for t in tags+[newpath])
def walk(*args, min_rank=None, use_tagfiles=True, **kwargs):
	if min_rank is not None:
		try:
			min_rank = int(min_rank)
		except:
			error("Bad argument: --min-rank={}".format(min_rank))
	options = kwargs
	for arg in args:
		assert isinstance(arg, str)
		if not os.path.isdir(arg):
			warning("Skipping file "+arg)
		for root, dirs, files in os.walk(arg):
			file_tags = None # directory mode
			dirs = [ d for d in dirs if not d.startswith('.') ] # prune out hidden directories
			if use_tagfiles and '.tags' in files:
				tagfilename = os.path.join(root, '.tags')
				info("Including "+tagfilename)
				tag_pairs = tagfile.parse_tagfile(tagfilename)
				file_tags = { f: tl for f, tl in tag_pairs if f in files } # file mode
			files = [ f for f in files if not f.startswith('.') ] # prune out hidden files
			src = os.path.relpath(root)
			if (not files) or (src in ['.', '..', '']):
				#debug("Skipping fileless {src}".format(**locals()) )
				continue
			with suppress(FileNotFoundError):
				stat_by_file = { f: os.stat(os.path.join(root, f)) for f in files }
			dir_pri, dir_rank, dir_newpath = path_arrange(src, **options)
			if (min_rank is not None) and (dir_rank <= min_rank): # these are negative numbers
				warning("min-rank skips "+arg)
				continue
			if file_tags:
				dir_tags, dir_path = path_split(dir_newpath, **options)
				info("Files tagged:")
				for f, tl in file_tags.items():
					info("\t{f}: {tl}".format(**locals()) )
				info("Will override {dir_tags}+{dir_path}".format(**locals()) )
				for f in files:
					s = stat_by_file[f].st_size
					if f in file_tags:
						my_tags, my_nontags = file_tags.pop(f)
						new_parts, _ = parser.combine(dir_tags, my_tags)
						assert not _
						S = [ str(p) for p in new_parts ]+[dir_path]+my_nontags
						newpath = os.path.join(*S)
					else:
						newpath = dir_newpath
					if src == os.path.relpath(newpath):
						debug("{}: no change".format(f))
						newpath = None
					else:
						info("{f} => {newpath}".format(**locals()) )
					yield dir_pri, dir_rank, s, (os.path.join(src, f), newpath)
			else:
				total_size = sum(s.st_size for (f, s) in stat_by_file.items())
				newpath = dir_newpath
				if src == os.path.relpath(newpath):
					newpath = None
				yield dir_pri, dir_rank, total_size, (src, newpath)
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
	if this_size: # last one
		yield this_size, this_vol
	if errors:
		max_size = max(s for _, _, s, _ in errors)
		error("{} file(s) too big for {:,} byte volume, "
			  "consider volumes of at least {:,}".format(len(errors), volumesize, max_size) )
		for row in errors:
			p, r, s, (src, dest) = row
			info("File '{}' too big for {:,} byte volume".format(src, volumesize) )
def chunk(*args,
		  chunker=_chunker,
		  by_priority=True,
		  volumesize=None,
		  **kwargs):
	options = kwargs
	if by_priority:
		debug("Sort order: priority, rank, size")
		def key(arg):
			p, r, s, _ = arg
			return -p, r, -s
	else:
		debug("Sort order: rank, size")
		def key(arg):
			p, r, s, _ = arg
			return r, -s
	my_list = sorted(tqdm.tqdm(walk(*args, **options),
							   desc="{} arguments".format(len(args)) ),
					 key=key)
	if not volumesize:
		osize = len(my_list)
		my_list = [ (p, r, s, (src, dest)) for (p, r, s, (src, dest)) in my_list if dest ]
		info("{} directories unchanged".format(osize-len(my_list)) )
	total_size = sum(s for _, _, s, _ in my_list)
	if not total_size:
		return []
	if not volumesize or (total_size <= volumesize):
		if total_size:
			return [(total_size, [pairs for _, _, _, pairs in my_list])]
		else:
			return []
	else:
		return list( tqdm.tqdm(chunker(my_list, volumesize),
							   desc='Sorting...') )
#
if __name__ == '__main__':
	from glob import glob
	import sys

	parser.setup(glob('rules/*.rules'))
	for arg in sys.argv[1:]:
		print(arg, path_split(arg, **options))
