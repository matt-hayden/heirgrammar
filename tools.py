#!/usr/bin/env python3
import os, os.path

from parser import arrange, define_tags

with open('examples') as fi:
	define_tags(fi.read().splitlines())

def arrange_path(path, prepends=None, appends=None, stopwords=['sortme']):
	prepends = prepends or []
	appends = appends or []
	#
	parts = [ p for p in path.split(os.path.sep) if p not in ['', '.', '..'] ]
	if any(w in parts for w in stopwords):
		return path
	print(prepends+parts+appends)
	pri, rank, new_parts = arrange(prepends+parts+appends)
	return os.path.sep.join(str(p) for p in new_parts)
	
