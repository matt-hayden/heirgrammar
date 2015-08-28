#!/usr/bin/env python3
#from Tag import tag, attribs, name_cleaner
from Tag import *

def define_tags(lines, direction=-1, init='import string\nprint("yee-haw!")', **kwargs):
	# customization:
	w = direction
	#
	my_globals = dict(kwargs) # copy
	my_globals['attribs'] = attribs
	my_globals['tag'] = tag
	exec(init, my_globals)
	for line_no, line in enumerate(lines):
		for tokens in line.split(';'):
			params = dict(kwargs) # copy
			params['line'] = line_no
			# customization:
			params['rank'] = params['srank'] = w
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
	'''Given a list of strings and TagObjects, remove tied-ranked TagObjects in-place. This also removes duplicates
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
def convert(iterable):
	items, negations = [], []
	a = items.append
	def extend(list_of_tags, item):
		'''Contains much customization code
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
if __name__ == '__main__':
	"""Example syntax:
	red, yellow and blue are defined on the first line, with yellow and blue having higher rank than red.
	purple and orange will have higher rank than green. The extra code past green will be ignored because there are no tags following it.
	off_white has a custom property called srank
	puce has a property called 'removes' which makes it erase any preceeding green
	mauve has a property called 'appends' which brings puce in immediately behind it
	"""
	with open('examples') as fi:
		define_tags(fi.read().splitlines(), custom_attr='Wednesday')
	for k, v in sorted(attribs.items(), key=lambda k_v: k_v[-1]['rank']):
		print(k, v)
		
