"""
Command-line argument parser
"""

import argparse


try:
	"""
	If used in a package, package logging functions are used instead of stderr.
	"""
	from . import debug, info, warning, error, fatal
except:
	def error(*args, **kwargs):
		print(*args, file=sys.stderr, **kwargs)
	debug = info = warning = fatal = error


class ArgWrap:
	def __init__(self, arg):
		if isinstance(arg, str):
			self.func = None
			self.name = arg
		else:
			self.func = arg
			if arg.__name__.lower().startswith('cli_'):
				self.name = arg.__name__[len('cli_'):].strip('_')
			else:
				self.name = arg.__name__.strip('_')
		self.args = []
		self.options = {}
	def __rshift__(self, ap):
		"""
		Foo('echo', echo) >> subparser
		"""
		self.register(ap)
	def register(self, ap):
		subparser = ap.add_parser(self.name)
		self.make_options(subparser)
		subparser.set_defaults(func=self.parse_options)
		newarg = subparser.add_argument
		newarg('args', nargs='*')
	def call(self):
		if self.func:
			return self.func(*self.args, **self.options)
		else:
			return eval(self.name+'(*self.args, **self.options)')
	def __repr__(self):
		return '<{},{},{},{}>'.format(self.name, self.func, self.args, self.options)
	"""
	Subclass this and implement the following:

	@staticmethod
	def make_options(subparser):
		# do whatever to empower the argparse.ArgumentParser object 'subparser'
	def parse_options(self, options_in):
		# do whatever to self.args and self.options to reflect the namespace
		# options_in
	"""
	@staticmethod
	def make_options(subparser):
		if isinstance(subparser, argparse.ArgumentParser):
			newarg = subparser.add_argument
		else:
			newarg = subparser
		### subclass away...
	def parse_options(self, options_in):
		# overload me, following this pattern:
		self.args, self.options = [], {}
		return self
