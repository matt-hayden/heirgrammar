#! /usr/bin/env python3

import logging
logger = logging.getLogger('' if __name__ == '__main__' else __name__)
debug, info, warning, error, fatal = logger.debug, logger.info, logger.warning, logger.error, logger.critical

import argparse


def main(ap):
	args = ap.parse_args()
	logging.basicConfig(level=args.logging_level)
	args.func(args) << 1

class SubparserBase:
	def __init__(self, name, func=None):
		self.name = name
		self.func = func
	def __rshift__(self, ap=None):
		subparser = ap.add_parser(self.name)
		self.make_options(subparser)
		subparser.set_defaults(func=self.parse_options)
		newarg = subparser.add_argument
		newarg('args', nargs='*')
	def __lshift__(self, other):
		f = self.func or globals()[self.name]
		return f(*self.args, **self.options)
	def __repr__(self):
		return '<{},{},{},{}>'.format(self.name, self.func, self.args, self.options)
	@staticmethod
	def make_options(subparser):
		if isinstance(subparser, argparse.ArgumentParser):
			newarg = subparser.add_argument
		else:
			newarg = subparser
		### subclass away...
	def parse_options(self, options_in):
		# overload me, following this pattern:
		self.args, self.options = [], []
		return self
