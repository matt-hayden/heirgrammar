#! /usr/bin/env python3

import contextlib
import io
import os
import subprocess

PAGER = os.environ.get('PAGER', 'less')

def get_pager_process(command=[PAGER]):
	p = subprocess.Popen(command, stdin=subprocess.PIPE, universal_newlines=True)
	return p.communicate

@contextlib.contextmanager
def pager(s=io.StringIO(),
		  call=(get_pager_process() if os.isatty(1) else print),
		  callback=None):
	
	with contextlib.redirect_stdout(s):
		yield
	bsize=s.tell()
	if bsize:
		s.seek(0)
		call( callback(s.read()) if callback else s.read() )
#
if __name__ == '__main__':
	with pager() as p:
		print("Hello World")
		print("Brought to you by the letter p")
