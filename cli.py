#!/usr/bin/env python3
import glob
import os, os.path
import sys

from . import *
from .pager import pager

info("CLI using parser "+parser.__version__)

def setup(args=[ 'rules', '.rules', '../rules', '../.rules' ], **kwargs):
	assert args
	if isinstance(args, str):
		return setup([args], **kwargs)
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
#
def test(arg, sep=os.path.sep):
	tags, nontags = parser.split(arg.replace(',', sep).split(sep) )
	_, _, newpath = tools.path_arrange(arg)
	yield         "{arg} => {newpath}:".format(**locals())
	if tags:
		yield     "{:>30} {:^15} {:^9}".format("tag", "combined rank", "priority^")
		for t in tags:
			yield "{!r:>30} {: 15d} {: 9d}".format(t, t.rank, t.pri)
		yield     "{:>30} {: 15d} {: 9d}".format("total", sum(t.rank for t in tags), max(t.pri for t in tags))
	if nontags:
		yield     "{nontags} are not tags".format(**locals())
#
def main(*args, **kwargs):
	rules_dirs = kwargs.pop('--rules').split(',')
	setup(rules_dirs)
	if kwargs['print']:
		with pager():
			return parser.print_Taxonomy()
	elif kwargs['test']:
		with pager():
			for arg in kwargs.pop('EXPR'):
				print('\n'.join(test(arg)) )
				print()
		return 0
	debug("Processing command-line options:")
	options = {}

	stopwords = set(s.strip() for s in kwargs.pop('--exclude').split(','))
	stopwords.update(set(rules_dirs))
	assert 'rules' in stopwords # TODO

	options['stopwords'] = stopwords

	options['all_commas'] = kwargs.pop('--all-commas', None)
	options['fileout'] = kwargs.pop('--output', None)
	options['prefix'] = kwargs.pop('--prefix', None)
	options['use_tagfiles'] = kwargs.pop('--use-tagfiles', None)

	if kwargs['--prepend']:
		try:
			a, b = parser.split(kwargs['--prepend'].split(','))
			options['prepend_tags'] = a+b
		except:
			warning("--prepend={} invalid, ignoring".format(kwargs.pop('--prepend')) )
	if kwargs['--append']:
		try:
			a, b = parser.split(kwargs['--append'].split(','))
			options['append_tags'] = a+b
		except:
			warning("--append={} invalid, ignoring".format(kwargs.pop('--append')) )

	if kwargs['dirsplit']:
		try:
			vs = int(float(kwargs['--volumesize']))
			assert 0 < vs
		except:
			raise ValueError("Invalid volume size: {}".format(kwargs.pop('--volumesize')) )
		shtools.arrange_dirs(*args,
					 prefix=options.pop('prefix') or 'vol_{:03d}',
					 volumesize=vs,
					 **options)
	elif kwargs['sort']:
		shtools.arrange_dirs(*args, **options)
	return 0

