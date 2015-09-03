#!/usr/bin/env python

try:
	assert isinstance(Taxonomy, dict)
except NameError:
	Taxonomy = {'NULL': {'id': 0, 'name': None }}
#
class TaxonBaseObject:
	def __init__(self, name, namespace=Taxonomy, **params):
		if name in namespace:
			namespace[name].update(params)
		else:
			params['id'] = len(Taxonomy)
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
	def __int__(self):
		return self.id
	def __bool__(self):
		return 0 != int(self) 
#
try:
	assert(isinstance(lookup_table, dict))
except NameError:
	lookup_table = {}
#
# customize:
def name_cleaner(text):
	text = text.strip('+_')
	if ' ' in text:
		text = text.replace(' ', '_')
	return text
#
def tag(item, table=lookup_table, synonyms=[]):
	N = len(Taxonomy)
	if isinstance(item, TaxonBaseObject):
		t = item
		#n = item.name
		#t = table.get(n, item)
	elif isinstance(item, int):
		id = item % N
		for el, kv in Taxonomy.items():
			if id == kv['id']:
				t = tag(el)
				break
	elif isinstance(item, str):
		s = name_cleaner(item)
		if s in table:
			t = table[s]
		else: # won't get called until later, when TaxonObject (below) has been declared
			t = TaxonObject(s)
	elif item: # hope it's hashable
		t = TaxonObject(item)
	else:
		t = tag(0)
	if isinstance(synonyms, str):
		synonyms = synonyms.split()
	for linkname in synonyms:
		table[linkname] = t
	return t
#
class TaxonObject(TaxonBaseObject):
	def __eq__(self, other):
		if isinstance(other, TaxonBaseObject):
			return int(self) == int(other)
		else:
			assert isinstance(self, TaxonBaseObject)
			return self.name == name_cleaner(other)
	# if defining __eq__ then also define __hash__
	def __hash__(self):
		return int(self)
