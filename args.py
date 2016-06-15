#! /usr/bin/env python3

import logging
logger = logging.getLogger('' if __name__ == '__main__' else __name__)
debug, info, warning, error, fatal = logger.debug, logger.info, logger.warning, logger.error, logger.critical

import argparse

from cli import SubparserBase


def setup(rules_dirs):
	print("Setting up {}".format(rules_dirs))


class TestArgs(SubparserBase):
	pass
class PrintArgs(SubparserBase):
	pass
class SortArgs(SubparserBase):
	@staticmethod
	def make_options(subparser):
		if isinstance(subparser, argparse.ArgumentParser):
			newarg = subparser.add_argument
		else:
			newarg = subparser
		newarg("--append", "-A", help="Add these tags, overriding others if present (comma-seperated)")
		newarg("--prepend", "-B", help="Add these tags, never overriding (comma-seperated)")
		newarg("--output", "-o", type=argparse.FileType('w'), help="Output to file")
		newarg("--exclude", "-x", metavar="PATTERNS", default='delme,sortme,working',
			help="Excluding any directories with these members")
		newarg("--use-tagfiles", action='store_true',
			help="When a JSON-format .tags file is present, parse it for tags")
		newarg = subparser.add_mutually_exclusive_group().add_argument
		newarg("--no-commas", action='store_true', help="Commas are not special")
		newarg("--all-commas", action='store_true',
			help="Split on every comma, not just commas seperating recognized tags")
	def parse_options(self, options_in):
		setup(options_in.rules.split(','))
		self.options = { 'append'	:	options_in.append or [],
						 'prepend':		options_in.prepend or [],
						 'exclude':		options_in.exclude.split(','),
						 'use_tagfiles':	options_in.use_tagfiles,
						 'no_commas':	options_in.no_commas,
						 'all_commas':	options_in.all_commas }
		if options_in.output:
			self.options['output_filename'] = options_in.output
		self.args = options_in.args
		return self
class DirsplitArgs(SubparserBase):
	@staticmethod
	def make_options(subparser):
		if isinstance(subparser, argparse.ArgumentParser):
			newarg = subparser.add_argument
		else:
			newarg = subparser
		SortArgs.make_options(subparser)
		newarg = subparser.add_argument
		newarg("--do-sort", "-S", action='store_true', help="Also sort directories")
		newarg("--min-rank", "-m", type=int, help="Ignore all files sorting below a minimum rank number")
		newarg("--prefix", "-p", nargs=1, default='vol_{:03d}', help="Specify the pattern for numbering target directories")
		newarg("--volumesize", "-s", type=float, help="Size, in bytes of each volume. Block size 2048")
	def parse_options(self, options_in):
		sub = SortArgs('sub').parse_options(options_in)
		self.args, self.options = sub.args, sub.options
		self.options['do_sort'] = options_in.do_sort
		if options_in.min_rank is not None:
			self.options['min_rank'] = options_in.min_rank
		self.options['prefix'] = options_in.prefix
		try:
			self.options['volumesize'] = int(options_in.volumesize)
		except:
			warning( "volumesize={} invalid".format(options_in.volumesize) )
		return self


def get_arguments(*args, **kwargs):
	ap = argparse.ArgumentParser(description="")
	newarg = ap.add_argument
	newarg("--rules", "-r", nargs=1, default='./rules,./.rules,../rules,../.rules')

	newarg = ap.add_mutually_exclusive_group().add_argument
	newarg('--quiet', '-q', action='store_const', dest='logging_level', const=logging.ERROR)
	newarg('--verbose', '-v', action='store_const', dest='logging_level', const=logging.INFO)

	sp = ap.add_subparsers(help="")
	"""
	DirsplitArgs('dirsplit').make_parser(sp)
	PrintArgs('print').make_parser(sp)
	SortArgs('sort').make_parser(sp)
	TestArgs('test').make_parser(sp)
	"""
	DirsplitArgs('dirsplit', dirsplit)	>> sp
	PrintArgs('print')	>> sp
	SortArgs('sort', sort)	>> sp
	TestArgs('test')	>> sp
	
	return ap
def sort(*args, **kwargs):
	print('sort', args, kwargs)
def dirsplit(*args, **kwargs):
	print('dirsplit', args, kwargs)
