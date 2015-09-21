#! /usr/bin/env python3

import contextlib
import io
import os
import subprocess

PAGER = os.environ.get('PAGER', 'less')

@contextlib.contextmanager
def pager(command_line=[PAGER], callback=None):
	s = io.StringIO()
	with contextlib.redirect_stdout(s):
		yield command_line
	p = subprocess.Popen(command_line, stdin=subprocess.PIPE, universal_newlines=True)
	s.seek(0)
	p.communicate( callback(s.read()) if callback else s.read() )
#
if __name__ == '__main__':
	with pager() as p:
		print("Hello World")
		print("Brought to you by {}".format(' '.join(p)))
