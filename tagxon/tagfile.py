
import collections
import json
import os, os.path

from . import debug, info, warning, error, fatal

def get_common_prefix(*args):
	lengths = [ len(s) for s in args ]
	shortest, longest = min(lengths), max(lengths)
	p = ''
	for i in range(shortest):
		t = set(s[i] for s in args)
		if len(t) == 1:
			p += t.pop()
		else:
			break
	return p

def parse_tagfile(filename, tags=[], nontags=[]):
	with open(filename) as fi:
		tag_lookup = json.load(fi)
	if '*' in tag_lookup:
		tags, nontags = parser.split(tag_lookup.pop('*'))
	for k, v in tag_lookup.items():
		my_tags, my_nontags = parser.split(v)
		if tags:
			new_tags, _ =  parser.combine(tags, my_tags)
			assert not _
			yield k, (new_tags, nontags+my_nontags)
		else:
			yield k, (my_tags, nontags+my_nontags)
