#!/usr/bin/env python3
import glob
import sys

from . import *

def arrange_dirs(*args, **kwargs):
	parser.setup(glob.glob('rules/*.rules'))
	ha = list(shtools.hier_arrange(*args, **kwargs)) # heir_arrange is a generator of syntax lines
	if ha:
		print("#!/bin/bash")
		for line in ha:
			print(line)
