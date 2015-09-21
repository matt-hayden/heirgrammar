#!/usr/bin/env python3
import glob
import os, os.path
import sys

from . import *

def setup(args=[ 'rules', '.rules', '../rules', '../.rules' ], **kwargs):
	assert args
	debug("Searching for rules in {}".format(args))
	for searchme in args:
		if os.path.isdir(searchme):
			info("Using *.rules files found in '{}'".format(searchme))
			rule_files = sorted(glob.glob(os.path.join(searchme, '*.rules')))
			break
	else:
		panic("No rules directory found among {}".format(args))
		sys.exit(-1)
	parser.setup(rule_files)
	return rule_files

def arrange_dirs(*args, **kwargs):
	def _get_lines(*args, **kwargs):
		ha = list(shtools.hier_arrange(*args, **kwargs)) # heir_arrange is a generator of syntax lines
		if ha:
			yield "#! /bin/bash"
			yield from ha
	fileout = kwargs.pop('fileout', None)
	if hasattr(fileout, 'write'):
		info("Writing to {}".format(fileout))
		fileout.write(os.linesep.join(_get_lines(*args, **kwargs)))
	elif isinstance(fileout, str):
		debug("Writing to '{}'".format(fileout))
		with open(fileout, 'w') as fo:
			fo.write(os.linesep.join(_get_lines(*args, **kwargs)))
	else:
		warning("'{}' invalid, writing to standard out".format(fileout))
		for line in _get_lines(*args, **kwargs):
			print(line)
#
def main(args, **kwargs):
	rules_dirs = kwargs.pop('--rules').split(',')
	setup(rules_dirs)

	stopwords = set(s.strip() for s in kwargs.pop('--exclude').split(','))
	stopwords.update(set(rules_dirs))
	assert 'rules' in stopwords # TODO

	if kwargs['print']:
		return parser.print_Taxonomy()
	elif kwargs['sort']:
		if kwargs['--volumesize']:
			vs = int(float(kwargs.pop('--volumesize')))
			arrange_dirs(*kwargs,
						 volumesize=vs,
						 prefix=kwargs.pop('--prefix'),
						 fileout=kwargs.pop('--output', None),
						 stopwords=stopwords )
		else:
			arrange_dirs(*args,
						 fileout=kwargs.pop('--output', None),
						 stopwords=stopwords )
	elif kwargs['test']:
		print(parser.split(kwargs['EXPR'].split(',') ) )
	return 0

