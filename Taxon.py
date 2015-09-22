#!/usr/bin/env python

if not 'Taxonomy' in globals():
	Taxonomy = { None: {'id': 0, 'name': None } }
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
		return self.name or 'None'
	def __repr__(self):
		#return "<{}({})>".format(self.name, len(self.__dict__))
		return "<{}>".format(self.name)
	def __int__(self):
		return self.id
#	def __bool__(self):
#		return 0 != int(self) 

if not 'lookup_table' in globals():
	lookup_table = {}

#
# customize here if using special characters on the ends of tags::
def name_cleaner(text):
	text = text.strip('+_')
	for vc in ''' '"''':
		text = text.replace(vc, '_')
	return text
#
#

def tag(item, table=lookup_table, synonyms=[], prep_string=name_cleaner):
	N = len(Taxonomy)
	if isinstance(item, TaxonBaseObject):
		t = item
		#n = item.name
		#t = table.get(n, item)
	elif isinstance(item, int):
		#id = item % N # could cause undefined behaviour
		for el, kv in Taxonomy.items():
			if item == kv['id']:
				t = tag(el)
				break
		else:
			raise NotImplementedError("id={} not found".format(item))
	elif isinstance(item, str):
		s = prep_string(item)
		if s in table:
			t = table[s]
		else: # won't get called until later, when TaxonObject (below) has been declared
			t = TaxonObject(s)
	#elif item: # hope it's hashable
	else:
		t = TaxonObject(item)
#	else:
#		t = tag(0)
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

lookup_table['None'] = lookup_table['NULL'] = lookup_table[False] = tag(None)

