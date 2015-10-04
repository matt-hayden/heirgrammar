#!/usr/bin/env python3
import glob
import os, os.path
import shlex
import sys

from . import *

### GENERIC
from .pager import pager # ought to be an external module

def get_command_line(args=sys.argv):
	script_filename = args[0]
	_, exe = os.path.split(sys.executable)
	root, filename = os.path.split(script_filename)
	if filename == '__main__.py':
		_, modname = os.path.split(root)
		return [ exe, '-m', modname ]+args[1:]
	else:
		return args
def sq(*args):
	return ' '.join(shlex.quote(str(m)) for m in args)
###

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
	yield     arg
	yield     "{nontags} unused".format(**locals())
	yield     "{:>30} {:^15} {:^9}".format("tag", "combined rank", "priority^")
	for t in tags:
		yield "{!r:>30} {: 15d} {: 9d}".format(t, t.rank, t.pri)
	yield     "{:>30} {: 15d} {: 9d}".format("total", sum(t.rank for t in tags), max(t.pri for t in tags))
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

