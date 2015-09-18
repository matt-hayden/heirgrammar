#!/usr/bin/env python3
import glob
import os, os.path
import sys

from . import *

for searchme in [ 'rules', '.rules', '../rules', '../.rules' ]:
	if os.path.isdir(searchme):
		info("Using .rules files found in '{}'".format(searchme))
		RULES_FILES = sorted(glob.glob(os.path.join(searchme, '*.rules')))
		break
else:
	panic("No rules file found")
	sys.exit(-1)
parser.setup(RULES_FILES)

def arrange_dirs(*args, **kwargs):
	ha = list(shtools.hier_arrange(*args, **kwargs)) # heir_arrange is a generator of syntax lines
	if ha:
		print("#!/bin/bash")
		for line in ha:
			print(line)
