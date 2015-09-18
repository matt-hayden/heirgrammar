#!/usr/bin/env python3
import os, os.path
from os.path import exists, isfile, isdir
import random

class TagFile:
	def __init__(self, pathorfile):
		if isfile(pathorfile):
			debug('Using '+pathorfile)
			self.tagfile = pathorfile
		else:
			if isdir(pathorfile):
				self.tagdir = pathorfile
			else:
				self.tagdir = os.path.dirname(pathorfile)
				if not exists(self.tagdir):
					os.makedirs(self.tagdir)
			self.tagfile = os.path.join(self.tagdir, '.tags')
	def __repr__(self):
		return "TagFile('{}')".format(self.tagfile)
	def append(self, filename, tags):
		assert filename
		assert tags
		if not isinstance(tags, str):
			tags = ','.join(str(t) for t in tags)
		entry='{}\t{}\n'.format(filename, tags)
		debug("Appending '{}' to '{}'".format(entry, self.tagfile))
	def write(self, *args, **kwargs):
		with open(self.tagfile, 'a') as fo:
			fo.write(*args, **kwargs)
	def find(self, filename, tags=[]):
		with open(self.tagfile) as fi:
			for line_no, line in enumerate(fi):
				fi_filename, fi_tags = line.split('\t')
				if filename == fi_filename:
					if tags:
						if set(fi_tags.split(',')) == set(tags.split(',')):
							return line_no, line
					else:
						return line_no, line
				# elif filename in fif: ...
		return -1, ''
	def __contains__(self, itemortuple):
		if isinstance(itemortuple, (list, tuple)):
			line_no, _ = self.find(*itemortuple)
		else:
			line_no, _ = self.find(itemortuple)
		return (line_no < 0)
	def __length_hint__(self):
		total_k = os.path.getsize(self.tagfile)>>10
		with open(self.tagfile) as fi:
			sample = fi.read(1024)
		nlines = sample.count('\n')
		return nlines if (len(sample) < 1024) else (total_k)*(nlines+0.5)
	def delete(self, numberorline):
		if isinstance(numberorline, int):
			debug("TODO: Deleting line {}".format(numberorline))
		elif isinstance(numberorline, str):
			debug("TODO: Deleting line {}".format(numberorline))
	def merge(self, filename, tags):
		line_no, oldtext = self.find(filename)
		if (0 <= line_no):
			self.delete(line_no)
		self.append(filename, tags)
