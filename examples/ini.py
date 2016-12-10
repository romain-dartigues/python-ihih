#!/usr/bin/python
# vim:set fileencoding=utf8:
'''INI parsing with ihih - proof of concept

A quick-and-dirty, incomplete, INI parsing proof-of-concept using :mod:`ihih`.
'''

import os
import re
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ihih import IHIH, IHIHI





class _IHIHI(IHIHI):
	_escaped_chars = r'[\\\'\"\#/\;]'
	_comment = r'(\s*%(escape)s(?:\#|//|\;))'



class IHIHINI(IHIH):
	_section = r'^%(escape)s\[(?P<section>.+?)%(escape)s\]'
	_escaped_chars = r'[\\\'\"\#/\;]'
	_comment = _IHIHI._comment
	_separator = r'[\=\:]'

	def __init__(self, *args, **kwargs):
		self.r_section = re.compile(
			self._section  % {'escape': self._escape},
			re.U
		)

		super(IHIHINI, self).__init__(*args, **kwargs)


	__setitem__ = dict.__setitem__
	__getitem__ = dict.__getitem__


	def parse(self, filename, force=False, ignore_IOError=True):
		section = None
		try:
			fo = open(filename)
		except IOError:
			if ignore_IOError:
				return False
			raise

		for line in fo:
			results = self.r_section.match(line)
			if results:
				section = results.group(1)
				continue
			results = self.r_extract.match(line)
			if results:
				if section is None:
					raise KeyError, 'not in a section'
				elif section not in self:
					self[section] = _IHIHI(())

				self[section][results.group('key')] = results \
					.group('value').rstrip()

		return True





if __name__ == '__main__':
	import tempfile

	tmp = tempfile.NamedTemporaryFile(bufsize=0)
	tmp.write('[My section]\nfoodir: $dir/whatever\ndir=frob\n')
	tmp.write('key = "value" ; a comment')

	conf = IHIHINI(tmp.name)
	tmp.close()

	for section in conf:
		print '%s:' % section
		for k in conf[section]:
			print '\t%s = %s' % (k, conf[section].get_unicode(k))
