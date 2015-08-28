#!/usr/bin/env python3
#import string

from Tag import tag, attribs

def define_tags(lines, direction=-1, init=['import string'], **kwargs):
	# customization:
	w = direction
	#
	my_globals = dict(kwargs) # copy
	my_globals['attribs'] = attribs
	my_globals['tag'] = tag
	if isinstance(init, str):
		init = [ init ]
	for line in init:
		exec(line, my_globals)

	for line_no, line in enumerate(lines):
		if line.startswith('#'):
			continue
		for tokens in line.split(';'):
			params = dict(kwargs) # copy
			params['line'] = line_no
			# customization:
			params['rank'] = w
			#
			orig_params = dict(params)
			for token in tokens.split():
				if '=' in token:
					exec(token, my_globals, params)
				else:
					if '_' in token:
						t = tag(token, synonyms=[token.replace('_', ' ')])
					else:
						t = tag(token)
					t.update(params)
		# customization:
		w <<= 1
		#
#
def convert(iterable):
	items, negations = [], []
	a = items.append
	for token in iterable:
		if token.startswith('no'):
			n = token[2:]
			if n in attribs:
				negations.append(tag(n))
			else:
				a(token)
		elif token in attribs:
			t = tag(token)
			# customization:
			if hasattr(t, 'appends'):
				[ a(c) for c in t.appends ]
			if hasattr(t, 'removes'):
				[ negations.append(r) for r in t.removes ]
			#
			a(tag(token))
		else:
			a(token)
	for n in negations:
		try:
			items.remove(n)
		except:
			print("Couldn't remove {}".format(n))
	return items
if __name__ == '__main__':
	# setup tags
	define_tags('''
						red				rank+=1	yellow blue
rank+=1					purple orange;	rank+=1	green		code_without_noncode_to_the_right_must_parse_but_is_ignored=NotImplemented
srank=0					off_white
removes=[tag('green')]	puce
appends=[tag('puce')]	mauve
my_custom_property=string.hexdigits		notice_that_string_is_imported_via_exec
	'''.splitlines(), my_custom_property=-1)
	for k, v in sorted(attribs.items(), key=lambda k_v: k_v[-1]['rank']):
		print(k, v)
		
