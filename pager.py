#! /usr/bin/env python3

import contextlib
import io
import os
import subprocess
import sys

PAGER = os.environ.get('PAGER', 'less')

@contextlib.contextmanager
def pager(s=io.StringIO(),
		  command=[PAGER],
		  callback=None):
	if sys.stdin.isatty(): # os.isatty(1):
		def _output(t):
			p = subprocess.Popen(command,
				stdin=subprocess.PIPE,
				universal_newlines=True)
			p.communicate( callback(t) if callback else t )
	else:
		def _output(t):
			print( callback(t) if callback else t )
	with contextlib.redirect_stdout(s):
		yield
	bsize=s.tell()
	if bsize:
		s.seek(0)
		_output(s.read())
#
if __name__ == '__main__':
	with pager() as p:
		print("Hello World")
		print("Brought to you by the letter p")
