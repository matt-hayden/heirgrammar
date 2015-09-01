#!/usr/bin/env python

try:
	assert(isinstance(attribs, dict))
except NameError:
	attribs = {}
#
class TagBaseObject:
	def __init__(self, name, namespace=attribs, **params):
		if name in namespace:
			namespace[name].update(params)
		else:
			params['id'] = len(attribs)
			params['name'] = name
			namespace[name] = params
		self.__dict__ = namespace[name]
	def update(self, *args):
		self.__dict__.update(*args)
	def __str__(self):
		return self.name
	def __repr__(self):
		#return "<{}({})>".format(self.name, len(self.__dict__))
		return "<{}>".format(self.name)
#
try:
	assert(isinstance(lookup_table, dict))
except NameError:
	lookup_table = {}
#
def name_cleaner(text):
	text = text.strip('+_')
	if ' ' in text:
		text = text.replace(' ', '_')
	return text
def tag(item, table=lookup_table, synonyms=[]):
	if isinstance(item, TagBaseObject):
		n = item.name
		t = table.get(n, item)
	else:
		s = name_cleaner(item)
		if s in table:
			t = table[s]
		else: # won't get called until later, when TagObject has been declared
			t = TagObject(s)
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
			assert isinstance(self, TagBaseObject)
			return self.name == name_cleaner(other)
	# if defining __eq__ then also define __hash__
	def __hash__(self):
		return self.id
