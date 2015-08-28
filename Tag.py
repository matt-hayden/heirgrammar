#!/usr/bin/env python

try:
	assert(isinstance(attribs, dict))
except NameError:
	attribs = {}
#
class TagBaseObject:
	def __init__(self, name, namespace=attribs, **params):
		if name not in namespace:
			params['id'] = len(attribs)
			params['name'] = name
			namespace[name] = params
		else:
			namespace[name].update(params)
		self.__dict__ = namespace[name]
	def update(self, *args):
		self.__dict__.update(*args)
	def __str__(self):
		return self.name
	def __repr__(self):
		return "<{}{}>".format(self.name, self.__dict__)
#
try:
	assert(isinstance(lookup_table, dict))
except NameError:
	lookup_table = {}
#
def tag_name_cleaner(text):
	if ' ' in text:
		return text.replace(' ', '_')
	return text
def tag(item, table=lookup_table, synonyms=[]):
	if isinstance(item, TagBaseObject):
		t = table.get(item.name, item)
	else:
		s = tag_name_cleaner(item)
		t = table.get(s, TagObject(s)) # won't get called until later, when TagObject has been declared
	if isinstance(synonyms, str):
		synonyms = synonyms.split()
	for linkname in synonyms:
		table[linkname] = t
	return t
#
class TagObject(TagBaseObject):
	def __eq__(self, other):
		if isinstance(other, TagBaseObject):
			return self.id == other.id
		else:
			return self.id == tag(other).id
	# if defining __eq__ then also define __hash__
	def __hash__(self):
		return self.id
