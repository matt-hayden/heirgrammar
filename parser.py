#!/usr/bin/env python3
from Tag import *

def define_tags(lines, direction=-1, init='import string\nprint("yee-haw!")', **kwargs):
	# customization:
	w, hr = direction, len(lines)
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
			params['pri'] = hr-line_no
			#
			orig_params = dict(params)
			for token in tokens.split():
				if '=' in token:
					exec(token, my_globals, params)
				else:
					if '_' in token:
						t = tag(token, synonyms=[token.replace('_', ' ')])
					else:
						t = tag(token)
					t.update(params)
		# customization:
		w <<= 2
		#
#
def pack(list_of_tags):
	'''Given a list of strings and TagObjects, remove tied-ranked TagObjects in-place. This also removes duplicates.
	'''
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
	items = []
	negations = negations or []
	a = items.append
	def extend(list_of_tags, item):
		'''Relies heavily on members added during runtime.
		'''
		if isinstance(item, TagObject):
			# customization:
			if hasattr(item, 'removes'):
				negations.extend(item.removes)
			a(item)
			list_of_tags = pack(list_of_tags)
			# customization:
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
			print("Couldn't remove {}".format(n))
	return items
def arrange(iterable, key=lambda t: -t.rank, **kwargs):
	cts = convert(iterable, **kwargs)
	tags, nontags = [], []
	for item in cts:
		(tags if isinstance(item, TagObject) else nontags).append(item)
		tags.sort(key=key)
	highest_pri = max(t.pri for t in tags)
	total_rank = sum(t.rank for t in tags)
	return highest_pri, total_rank, tags+nontags
def attribs_key(args):
	'''Deals with the elements of attribs.items()
	'''
	name, members = args
	#return -members['rank']
	return 'isolate' in members, -members['pri'], -members['rank']
if __name__ == '__main__':
	with open('examples') as fi:
		define_tags(fi.read().splitlines(), custom_attr='Wednesday')
	for n, (t, a) in enumerate(sorted(attribs.items(), key=attribs_key)):
		r = a['rank']
		p = a['pri']
		nbr_count = sum(1 for t, a in attribs.items() if a['rank'] == r)
		print("{:03d}".format(n), t, r, p, nbr_count)
		
