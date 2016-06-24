#! /usr/bin/env python3

import logging
logger = logging.getLogger('' if __name__ == '__main__' else __name__)
debug, info, warning, error, panic = logger.debug, logger.info, logger.warning, logger.error, logger.critical

import argparse
import glob
import os, os.path
import sys

from .argwrap import ArgWrap

from . import parser, shtools
info("CLI using parser "+parser.__version__)


def main(*args):
	ap = argparse.ArgumentParser(description="")
	newarg = ap.add_argument
	newarg("--exclude", "-x", metavar="PATTERNS", default='delme,sortme,working',
		help="Excluding any directories with these members")
	newarg("--rules", "-r", nargs=1, default='./rules,./.rules,../rules,../.rules')

	newarg = ap.add_mutually_exclusive_group().add_argument
	newarg('--quiet', '-q', action='store_const', dest='logging_level', const=logging.ERROR)
	newarg('--verbose', '-v', action='store_const', dest='logging_level', const=logging.INFO)

	sp = ap.add_subparsers(help="")
	dirsplit >> sp
	cli_print >> sp
	cli_sort >> sp
	cli_test >> sp

	my_args = ap.parse_args(*args) if args else ap.parse_args()
	logging.basicConfig(level=my_args.logging_level)
	return my_args.func(my_args).call()
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


class DefaultArgs(ArgWrap):
	"""
	Subclass defining the arguments common to each subcommand
	"""
	def parse_options(self, options_in):
		exclude = options_in.exclude
		if isinstance(exclude, str):
			exclude = set(s.strip() for s in exclude.split(','))
		rules_dirs = options_in.rules
		if isinstance(rules_dirs, str):
			rules_dirs = [ s.strip() for s in rules_dirs.split(',') ]
		self.options['stopwords'] = exclude | set(['rules']) | set(rules_dirs)
		setup(rules_dirs)
		return self
class TestArgs(DefaultArgs):
	pass
class PrintArgs(DefaultArgs):
	pass
class SortArgs(DefaultArgs):
	"""
	Subclass defining the arguments for the 'sort' subcommand
	"""
	@staticmethod
	def make_options(subparser):
		if isinstance(subparser, argparse.ArgumentParser):
			newarg = subparser.add_argument
		else:
			newarg = subparser
		newarg("--append", "-A", metavar="tags",
			help="Add these tags, overriding others if present (comma-seperated)")
		newarg("--prepend", "-B", metavar="tags",
			help="Add these tags, never overriding (comma-seperated)")
		newarg("--output", "-o", type=argparse.FileType('w'), help="Output to file")
		newarg("--use-tagfiles", action='store_true',
			help="When a JSON-format .tags file is present, parse it for tags")
		newarg = subparser.add_mutually_exclusive_group().add_argument
		newarg("--no-commas", action='store_true', help="Commas are not special")
		newarg("--all-commas", action='store_true',
			help="Split on every comma, not just commas seperating recognized tags")
	def parse_options(self, options_in):
		super().parse_options(options_in)
		self.options.update({ 'use_tagfiles':	options_in.use_tagfiles,
						 'no_commas':	options_in.no_commas,
						 'all_commas':	options_in.all_commas })
		if options_in.output:
			self.options['fileout'] = options_in.output
		if options_in.prepend:
			try:
				a, b = parser.split(options_in.prepend.split(','))
				options['prepend_tags'] = a+b
			except:
				error( "Invalid argument --prepend={}".format(options_in.prepend) )
				raise
		if options_in.append:
			try:
				a, b = parser.split(options_in.append.split(','))
				options['append_tags'] = a+b
			except:
				error( "Invalid argument --append={}".format(options_in.append) )
				raise
		self.args = options_in.args
		return self
class DirsplitArgs(SortArgs):
	@staticmethod
	def make_options(subparser):
		if isinstance(subparser, argparse.ArgumentParser):
			newarg = subparser.add_argument
		else:
			newarg = subparser
		super(DirsplitArgs, DirsplitArgs).make_options(subparser)
		newarg = subparser.add_argument
		newarg("--do-sort", "-S", action='store_true', help="Also sort directories")
		newarg("--min-rank", "-m", type=int,
			help="Ignore all files sorting below a minimum rank number")
		newarg("--prefix", "-p", metavar="path", nargs=1, default='vol_{:03d}',
			help="Specify the pattern for numbering target directories")
		newarg("--volumesize", "-s", type=float,
			help="Size, in bytes of each volume. Block size 2048")
	def parse_options(self, options_in):
		super().parse_options(options_in)
		self.options['do_sort'] = options_in.do_sort
		if options_in.min_rank is not None:
			self.options['min_rank'] = options_in.min_rank
		self.options['prefix'] = options_in.prefix
		try:
			self.options['volumesize'] = int(options_in.volumesize)
		except:
			warning( "volumesize={} invalid".format(options_in.volumesize) )
		return self


@PrintArgs
def cli_print(*args, **kwargs):
	from .pager import pager
	with pager():
		return parser.print_Taxonomy()
@TestArgs
def cli_test(*args, **kwargs):
	info("Testing "+" ".join(args))
	for arg in args:
		print('\n'.join(test(arg)) )
		print()
@SortArgs
def cli_sort(*args, **kwargs):
	shtools.arrange_dirs(*args, **kwargs)
@DirsplitArgs
def dirsplit(*args, **kwargs):
	# identical to cli_sort, except volumesize member exists in options
	shtools.arrange_dirs(*args, **kwargs)


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
