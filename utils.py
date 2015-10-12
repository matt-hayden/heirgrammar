#!/usr/bin/env python3
import os, os.path
import shlex
import sys

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
