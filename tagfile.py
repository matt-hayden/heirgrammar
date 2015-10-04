#! /usr/bin/env python3
import collections
from contextlib import suppress
import json
import os, os.path
#import string

from . import debug, info, warning, error, panic
from . import parser

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

def parse_tagfile(filename):
	with open(filename) as fi:
		tags = json.load(fi)
	if '*' in tags:
		common = parser.convert(tags.pop('*'))
	for k, v in tags.items():
		ts = parser.convert(v)
		if common:
			yield k, parser.combine(common, ts)
		else:
			yield k, ts
