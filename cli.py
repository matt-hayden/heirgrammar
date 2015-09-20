#!/usr/bin/env python3
import glob
import os, os.path
import sys

from . import *

def setup(args=[ 'rules', '.rules', '../rules', '../.rules' ], **kwargs):
	for searchme in args:
		if os.path.isdir(searchme):
			info("Using *.rules files found in '{}'".format(searchme))
			rule_files = sorted(glob.glob(os.path.join(searchme, '*.rules')))
			break
	else:
		panic("No rules file found")
		sys.exit(-1)
	parser.setup(rule_files)
	return rule_files

def arrange_dirs(*args, **kwargs):
	fileout = kwargs.pop('fileout', None)
	fout = open(fileout, 'w') if fileout else sys.stdout

	ha = list(shtools.hier_arrange(*args, **kwargs)) # heir_arrange is a generator of syntax lines
	if ha:
		print("#!/bin/bash", file=fout)
		for line in ha:
			print(line, file=fout)
	if fileout:
		fout.close()
