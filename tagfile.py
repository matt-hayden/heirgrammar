#! /usr/bin/env python3
import collections
from contextlib import suppress
import json
import os, os.path
#import string

from . import debug, info, warning, error, panic
from . import parser

#bad_chars = ''' '{}[]()*&?<>#!".'''
def get_common_prefix(strings):
	lengths = [ len(s) for s in strings ]
	shortest, longest = min(lengths), max(lengths)
	p = ''
	for i in range(shortest):
		t = set(s[i] for s in strings)
		if len(t) == 1:
			p += t.pop()
		else:
			break
	return p

def parse_tagfile(filename):
	with open(filename) as fi:
		tags = json.load(fi)
	common = tags.pop('*', [])
	common_tags, common_nontags = parser.split(common)
	for k, v in tags.items():
		my_tags, my_nontags = parser.split(v)
		yield k, (parser.combine(common_tags, my_tags), common_nontags+my_nontags)
