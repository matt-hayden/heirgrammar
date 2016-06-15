#! /usr/bin/env python3

import logging
logger = logging.getLogger('' if __name__ == '__main__' else __name__)
debug, info, warning, error, fatal = logger.debug, logger.info, logger.warning, logger.error, logger.critical

import argparse


class SubparserBase:
	def __init__(self, name):
		self.name = name
	def make_parser(self, ap):
		subparser = ap.add_parser(self.name)
		self.make_options(subparser)
		subparser.set_defaults(func=self.parse_options)
		newarg = subparser.add_argument
		newarg('args', nargs='*')
	@staticmethod
	def make_options(subparser):
		if isinstance(subparser, argparse.ArgumentParser):
			newarg = subparser.add_argument
		else:
			newarg = subparser
	def parse_options(self, options_in):
		# overload me, following this pattern:
		self.args, self.options = [], []
		return self
