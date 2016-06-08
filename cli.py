#!/usr/bin/env python3
import glob
import os, os.path
import sys

import logging
logger = logging.getLogger(__name__)
debug, info, warning, error, panic = logger.debug, logger.info, logger.warning, logger.error, logger.critical

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
		for arg in kwargs.pop('EXPR'):
			print('\n'.join(test(arg)) )
			print()
		return 0
	debug("Processing command-line options:")
	options = {}

	options['all_commas']		= kwargs.pop('--all-commas') in (True, 'True', 'TRUE')
	options['fileout']			= kwargs.pop('--output', None)
	if kwargs['--min-rank'] is not None:
		options['min_rank']		= int(kwargs.pop('--min-rank'))
	options['no_commas']		= kwargs.pop('--no-commas', None) in (True, 'True', 'TRUE')
	options['prefix']			= kwargs.pop('--prefix', 'vol_{:03d}')
	options['stopwords']		= set(s.strip() for s in kwargs.pop('--exclude').split(',')) | set(rules_dirs) | set(['rules'])
	options['use_tagfiles']		= kwargs.pop('--use-tagfiles', None)

	if kwargs['--prepend']:
		try:
			a, b = parser.split(kwargs['--prepend'].split(','))
			options['prepend_tags'] = a+b
		except:
			error("Invalid argument --prepend={}".format(kwargs.pop('--prepend')) )
	if kwargs['--append']:
		try:
			a, b = parser.split(kwargs['--append'].split(','))
			options['append_tags'] = a+b
		except:
			error("Invalid argument --append={}".format(kwargs.pop('--append')) )

	if kwargs['dirsplit']:
		options['do_sort'] = kwargs.pop('--do-sort', None)
		try:
			vs = int(float(kwargs['--volumesize']))
			assert 0 < vs
		except:
			raise ValueError("Invalid argument --volumesize={}".format(kwargs.pop('--volumesize')) )
		shtools.arrange_dirs(*args, volumesize=vs, **options)
	elif kwargs['sort']:
		shtools.arrange_dirs(*args, **options)
	return 0

