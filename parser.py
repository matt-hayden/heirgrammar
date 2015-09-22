#!/usr/bin/env python3
import os, os.path
import re

from . import debug, info, warning, error, panic

from .Taxon import *


def define_tags(lines, direction=-1, init='''import string\nprint("# yee-haw!")''', **kwargs):
	"""This is the major setup function for the module."""
	# customize here:
	highest_pri = len(lines)
	w = direction << highest_pri
	#
	my_globals = { 'Taxonomy': Taxonomy, 'tag': tag }
	exec(init, my_globals)
	for line_no, line in enumerate(lines):
		if not line.strip():
			continue
		for tokens in line.split(';'):
			params = dict(kwargs) # copy
			params['line'] = line_no
			# customize here:
			params['rank'] = w
			params['pri'] = line_no if (0 <= direction) else highest_pri-line_no
			#
			for token in tokens.split():
				if '=' in token:
					exec(token, my_globals, params)
				else:
					if '_' in token:
						# synonyms lookup to the token
						t = tag(token, synonyms=[token.replace('_', ' ')])
					else:
						t = tag(token)
					t.update(params)
		# customize here:
		w >>= 1
		#
#
def pack(list_of_tags):
	"""Given a list of strings and TaxonObjects, remove TaxonObjects with the same rank as the right-most TaxonObject (in-place). This also applies to duplicates.
	"""
	for i in range(-1, -len(list_of_tags), -1):
		if hasattr(list_of_tags[i], 'rank'):
			break
	else: # never broke during loop
		return list_of_tags
	r = list_of_tags[i].rank
	for t in list_of_tags[:i]:
		if hasattr(t, 'rank'):
			if (r == t.rank):
				list_of_tags.remove(t)
	return list_of_tags
#
def convert(iterable, negations=None):
	"""
>>> convert('red green blue banana APPLE nogreen purple red'.split())
['banana', 'APPLE', <purple>, <red>]

"""
	items = []
	negations = negations or []
	#a = items.append # delme
	def extend(list_of_tags, item):
		"""Relies heavily on members added during runtime.
		"""
		if isinstance(item, TaxonObject):
			if hasattr(item, 'purge'):
				if item.purge:
					return list_of_tags
			if hasattr(item, 'removes'):
				negations.extend(item.removes)
			#if hasattr(item, 'fallback'): # TODO: causes weird error at items.append(item)
			#	items = item.fallback+items
			if hasattr(item, 'prepends'):
				for p in item.prepends:
					items.append(p)
					list_of_tags = pack(list_of_tags)
			items.append(item)
			list_of_tags = pack(list_of_tags)
			if hasattr(item, 'appends'):
				items.extend(item.appends)
		elif (item in Taxonomy):
			extend(list_of_tags, tag(item))
		else:
			items.append(item)
		return pack(list_of_tags)
	for field, literal in enumerate(iterable):
		if literal in Taxonomy:
			extend(items, literal)
			#if literal == tag(None):
			#	items = []
			#else:
			#	extend(items, literal)
			continue
		else:
			token = name_cleaner(literal)
			if token.startswith('no'):
				n = token[2:]
				if n in Taxonomy:
					t = tag(n)
					negations.append(t)
				else:
					extend(items, token)
				continue
			elif token in Taxonomy:
				extend(items, token)
			else:
				extend(items, literal)
	for n in negations:
		try:
			items.remove(n)
		except:
			debug("Failed to remove {}".format(n))
	return pack(items)
def split(iterable, **kwargs):
	def key(t):
		return t.rank
	cts = convert(iterable, **kwargs)
	tags, nontags = [], []
	for item in cts:
		(tags if isinstance(item, TaxonObject) else nontags).append(item)
		tags.sort(key=key)
	return tags, nontags
def arrange(iterable, **kwargs):
	"""
>>> arrange('green blue +18 nogreen puce'.split()) 
(10, -9, [<blue>, <puce>, '+18'])

>>> arrange('green blue +18 nogreen mauve'.split()) 
(10, -27, [<blue>, <purple>, <puce>, <mauve>, '+18'])

"""
	tags, nontags = split(iterable, **kwargs)
	if tags:
		highest_pri = max(t.pri for t in tags)
		total_rank = sum(t.rank for t in tags)
	else:
		highest_pri = total_rank = 0
	return highest_pri, total_rank, tags+nontags
def _read(*args, delim=re.compile('\n[ \t]*\n')):
	for fn in sorted(args):
		assert os.path.isfile(fn) and os.path.getsize(fn)
		debug("Reading "+fn)
		with open(fn) as fi:
			yield from delim.split(fi.read())
def setup(arg, **kwargs):
	if not arg:
		Taxonomy = {None: {'id': 0, 'name': None }}
		return
	elif isinstance(arg, str): # single filename
		return setup([arg], **kwargs)
	elif isinstance(arg, (list, tuple)): # list of filenames
		define_tags(list(_read(*arg)), **kwargs)
	else:
		raise NotImplemented
	return arg
def print_Taxonomy(header="lno "+"rank".rjust(25)+" -pri- count label"):
	def key(args):
		"""Deals in the elements of Taxonomy.items()
		"""
		name, members = args
		if 'pri' in members:
			return -members['pri'], members['rank'], name
		if 'rank' in members:
			return 0, members['rank'], name
		else:
			return 0, 0, name
		#return 'isolate' in members, members.get('pri', 0), -members.get('rank', 0), name
	if header:
		print(header)
		print("="*len(header))
	for n, (name, attribs) in enumerate(sorted(Taxonomy.items(), key=key)):
		try:
			r = attribs['rank']
			p = attribs['pri']
			nbr_count = sum(1 for t, a in Taxonomy.items() if a.get('rank',None) == r)
			print("{:03d} {:25d} {:5.1f} {:5d} {}".format(n, r, p, nbr_count, tag(name) ))
		except KeyError as e:
			print(name, "unsortable:", e)
if __name__ == '__main__':
	import doctest
	from glob import glob

	setup(sorted(glob('rules/*')))
	print_Taxonomy()
	doctest.testmod()
