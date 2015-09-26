#! /usr/bin/env python3

import contextlib
import io
import os
import subprocess

PAGER = os.environ.get('PAGER', 'less')

@contextlib.contextmanager
def pager(s=io.StringIO(),
		  command=[PAGER],
		  callback=None):
	
	with contextlib.redirect_stdout(s):
		yield
	bsize=s.tell()
	if bsize:
		s.seek(0)
		if os.isatty(1):
			p = subprocess.Popen(command, stdin=subprocess.PIPE, universal_newlines=True)
			p.communicate( callback(s.read()) if callback else s.read() )
		else:
			print( callback(s.read()) if callback else s.read() )
#
if __name__ == '__main__':
	with pager() as p:
		print("Hello World")
		print("Brought to you by the letter p")
