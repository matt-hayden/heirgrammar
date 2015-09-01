#!/usr/bin/env python3
import re

from Tag import *

def debug(*args):
	pass

def define_tags(lines, direction=-1, init='''import string\nprint("yee-haw!")''', **kwargs):
	"""This function is the major setup function for the module. The init value is a string of Python commands, for example imports.
	"""
	# customization:
	w, highest_pri = direction, len(lines)
	#
	my_globals = dict(kwargs) # copy
	my_globals['attribs'] = attribs
	my_globals['tag'] = tag
	exec(init, my_globals)
	for line_no, line in enumerate(lines):
		if not line.strip():
			continue
		for tokens in line.split(';'):
			params = dict(kwargs) # copy
			params['line'] = line_no
			# customization:
			params['rank'] = w
			params['pri'] = highest_pri-line_no
			#
			#orig_params = dict(params)
			for token in tokens.split():
				if '=' in token:
					exec(token, my_globals, params)
				else:
					if '_' in token:
						t = tag(token, synonyms=[token.replace('_', ' ')])
					else:
						t = tag(token)
					t.update(params)
			del params
		# customization:
		w <<= 1
	del my_globals
#
def pack(list_of_tags):
	"""Given a list of strings and TagObjects, remove tie-ranked TagObjects in-place. This also removes duplicates.
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
def convert(iterable, negations=None):
	"""
>>> convert('red green blue banana APPLE nogreen purple red'.split())
['banana', 'APPLE', <purple>, <red>]

"""
	items = []
	negations = negations or []
	a = items.append
	def extend(list_of_tags, item):
		"""Relies heavily on members added during runtime.
		"""
		if isinstance(item, TagObject):
			if hasattr(item, 'removes'):
				negations.extend(item.removes)
			if hasattr(item, 'prepends'):
				items.extend(item.prepends)
			a(item)
			list_of_tags = pack(list_of_tags)
			if hasattr(item, 'appends'):
				items.extend(item.appends)
		elif (item in attribs):
			extend(list_of_tags, tag(item))
		else:
			a(item)
		return list_of_tags
	for field, literal in enumerate(iterable):
		if literal in attribs:
			extend(items, literal)
			continue
		else:
			token = name_cleaner(literal)
			if token.startswith('no'):
				n = token[2:]
				if n in attribs:
					t = tag(n)
					negations.append(t)
				else:
					extend(items, token)
				continue
			elif token in attribs:
				extend(items, token)
			else:
				extend(items, literal)
	for n in negations:
		try:
			items.remove(n)
		except:
			debug("Failed to remove {}".format(n))
	return items
def split(iterable, key=lambda t: -t.rank, **kwargs):
	cts = convert(iterable, **kwargs)
	tags, nontags = [], []
	for item in cts:
		(tags if isinstance(item, TagObject) else nontags).append(item)
		tags.sort(key=key)
	return tags, nontags
def arrange(iterable, **kwargs):
	"""
>>> arrange('green blue +18 nogreen puce'.split()) 
(10, -9, [<blue>, <puce>, '+18'])

>>> arrange('green blue +18 nogreen mauve'.split()) 
(10, -25, [<blue>, <puce>, <mauve>, '+18'])

"""
	tags, nontags = split(iterable, **kwargs)
	if tags:
		highest_pri = max(t.pri for t in tags)
		total_rank = sum(t.rank for t in tags)
	else:
		highest_pri = total_rank = 0
	return highest_pri, total_rank, tags+nontags
def setup(filenames, delim=re.compile('\n[ \t]*\n'), init=[], **kwargs):
	content = init
	for fn in filenames:
		with open(fn) as fi:
			content += delim.split(fi.read())
	define_tags(content, **kwargs)
def print_attribs(header="lno "+"rank".rjust(25)+" -pri- count label"):
	def attribs_key(args):
		"""Deals in the elements of attribs.items()
		"""
		name, members = args
		return -members['rank'], name
		return 'isolate' in members, -members['pri'], -members['rank'], name
	if header:
		print(header)
		print("="*len(header))
	for n, (t, a) in enumerate(sorted(attribs.items(), key=attribs_key)):
		r = a['rank']
		p = a['pri']
		nbr_count = sum(1 for t, a in attribs.items() if a['rank'] == r)
		print("{:03d} {:25d} {:5.1f} {:5d} {}".format(n, r, p, nbr_count, tag(t) ))
if __name__ == '__main__':
	import doctest
	from glob import glob

	setup(sorted(glob('*.rules')))
	print_attribs()
	doctest.testmod()
