#!/usr/bin/python
'''ihih - simple configuration parsers with dictionary-like interface

:Source code: `GitHub project <https://github.com/romain-dartigues/python-ihih>`_
:License: `BSD 3-Clause <http://opensource.org/licenses/BSD-3-Clause>`_
'''





import re
import os





__version__ = '0.1.1.dev'





class IHIH(dict):
	'''IHIH - simple configuration parser

	One key/value pair per line.
	'''
	encoding = 'utf8'
	'''define the encoding'''

	_escape = r'(?<!\\)(?:\\\\)*'
	'''regexp definition of the escape sequence'''

	_escaped_chars = r'[\\\'\"\#/\\]'
	'''regexp definition of characters to unconditionally un-escape'''

	_escaped = r'(?:\\)(?P<char>%s)'

	_comment = r'(\s*%(escape)s(?:\#|//))'
	'''regexp definition of an in-line comment'''

	_separator = r'\='
	'''regexp definition of key/value separator

	Must be a fixed-width expression.'''

	_extract = r'''^\s*
		(?P<key>.+?)
		\s*%(separator)s\s*
		(?P<value>.*)'''
	'''extract ``key = [value]`` on a single line'''

	_quote = r'["\']'
	'''define what a quote might be'''

	_quoted = r'%(escape)s(?P<quote>%(quote)s)(?P<value>.*?)%(escape)s(?P=quote)'
	'''how to find a quoted value'''


	def __init__(self, filenames, *args, **kwargs):
		'''attempt to parse a list of filenames

		Parameters:

		- `filenames` -- if is a string, it is treated as a single
		  file, otherwise it is treated as an iterable
		- other parameters are passed to the :py:class:`dict` constructor
		'''
		dict.__init__(self, *args, **kwargs)

		self._comment = self._comment % {
			'escape': self._escape,
		}
		self.r_comment = re.compile(self._comment)
		self.r_extract = re.compile(
			self._extract % {
				'separator': self._separator,
			},
			re.X
		)
		self.r_quoted = re.compile(
			self._quoted % {
				'escape': self._escape,
				'quote': self._quote,
			}
		)
		self.r_escaped = re.compile(
			self._escaped % self._escaped_chars
		)

		if isinstance(filenames, basestring):
			self.__source = (os.path.realpath(filenames),)
		else:
			self.__source = tuple(
				os.path.realpath(filename)
				for filename in filenames
			)

		self.__mtime = {}

		return self.reload()


	def reload(self, force=False):
		'''call :meth:`parse` on each configuration file'''
		for filename in self.__source:
			self.parse(filename, force)


	def parse(self, filename, force=False):
		'''parse a configuration file

		.. Note::
		   `filename` should be an absolute path.
		'''
		try:
			mtime = os.stat(filename).st_mtime
		except:
			# file not found
			return False

		if mtime <= self.__mtime.get(filename, 0) and not force:
			# file did not change
			return None

		for i, line in enumerate(open(filename)):
			results = self.r_extract.match(line)
			if results:
				self[results.group('key')] = results \
					.group('value').rstrip()

		self.__mtime[filename] = mtime

		return True


	def _unescape(self, value, quote=None):
		'''remove escape prefix on "known escape"

		See :attr:`_escaped_chars`.

		This method attempt to utf8 encode :py:func:`unicode` objects.
		'''
		data = bytearray()
		escaped = None
		prev = 0

		if isinstance(value, unicode):
			enc = lambda s: s.encode(self.encoding)
		else:
			enc = lambda s: s

		for escaped in self.r_escaped.finditer(value):
			if escaped.start() > prev:
				data+= enc(value[prev:escaped.start()])

			data+= enc(escaped.group('char'))
			prev = escaped.end()

		if escaped and escaped.end() < len(value):
			data+= enc(value[escaped.end():])

		elif not escaped:
			data+= enc(value)

		return data


	def _handle_fragment(self, fragment, quote=None):
		'''handle a fragment of a value

		Provided to help on subclassing.'''
		return self._unescape(fragment, quote)


	def _comment_at(self, value):
		'return the position of the begining of a comment'
		comment = self.r_comment.search(value)
		return comment and comment.start()


	def _parse_value(self, value, data):
		'''parse the "value" part of a "key / value"

		This function handle the quoted parts and the comments.

		Parameters:

		- `value` (:py:func:`basestring` instance): value to parse
		- `data`: instance supporting ``+=`` operator
		'''
		quoted = None
		prev = 0

		for quoted in self.r_quoted.finditer(value):
			if quoted.start() > prev:
				# unquoted part before a quoted fragment
				comment_at = self._comment_at(
					value[prev:quoted.start()]
				)
				data+= self._handle_fragment(
					value[
						prev
						:
						quoted.start()
						if comment_at is None
						else comment_at
					]
				)
				if comment_at is not None:
					break

			# quoted fragment
			data+= self._handle_fragment(
				quoted.group('value'),
				quoted.group('quote')
			)
			prev = quoted.end()

		if quoted and quoted.end() < len(value):
			# there is unquoted string after the quoted one
			data+= self._handle_fragment(
				value[
					quoted.end()
					:
					self._comment_at(value[quoted.end():])
				]
			)

		elif not quoted:
			# nothing was quoted
			data+= self._handle_fragment(
				value[:self._comment_at(value)]
			)

		return data


	def _cast_str(self, value):
		'''return a string representation of `value`'''
		if type(value) is str:
			return value
		if isinstance(value, unicode):
			return value.encode(self.encoding)
		return str(value)


	def __contains__(self, key):
		'''True if self contains `key`

		.. Note::
		   The `key` will be casted as :py:func:`str`
		   (see: :meth:`_cast_str`).
		'''
		return dict.__contains__(self, self._cast_str(key))


	def __setitem__(self, key, value):
		'''set item `key` to `value`

		.. Note::
		   Both variables will be casted as :py:func:`str`
		   (see: :meth:`_cast_str`).
		'''
		return dict.__setitem__(
			self,
			self._cast_str(key),
			self._parse_value(
				value
				if isinstance(value, basestring)
				else str(value),
				bytearray()
			)
		)


	def __getitem__(self, key):
		'''return `key` value as internal type

		You probably want to use one of the following:
		:meth:`get_str`, :meth:`get_unicode`, :meth:`get_float`.

		.. Note::
		   The `key` will be casted as :py:func:`str`
		   (see: :meth:`_cast_str`).
		'''
		return dict.__getitem__(self, self._cast_str(key))


	def __delitem__(self, key):
		'''delete `key` from dict

		.. Note::
		   The `key` will be casted as :py:func:`str`
		   (see: :meth:`_cast_str`).
		'''
		return dict.__delitem__(self, self._cast_str(key))


	def get_str(self, key, default=None):
		'''return `key` value as :py:func:`str`
		or `default` if not found

		.. Note::
		   The `key` will be casted as :py:func:`str`
		   (see: :meth:`_cast_str`).
		'''
		if key in self:
			return str(self[key])
		return default


	get = get_str
	'''alias to :meth:`get_str`'''


	def get_unicode(self, key, default=None, errors='strict'):
		'''return `key` value as :py:func:`unicode` or `default`
		if not found

		The `errors` parameter is passed to :py:meth:`str.decode`.

		.. Note::
		   The `key` will be casted as :py:func:`str`
		   (see: :meth:`_cast_str`).
		'''
		if key in self:
			return self[key].decode(self.encoding, errors)
		return default


	def get_float(self, key, default=None, errors='strict'):
		'''return `key` value as :py:func:`float` or `default`
		if not found

		If `errors` is "ignore", return `default` value instead of
		raising :py:exc:`~exceptions.TypeError` on failure.

		.. Note::
		   The `key` will be casted as :py:func:`str`
		   (see: :meth:`_cast_str`).
		'''
		if key in self:
			try:
				return float(self[key])
			except:
				if errors != 'ignore':
					raise
		return default



class IHIHI(IHIH):
	'''IHIH Interpolate - :class:`IHIH` with variable interpolation
	'''

	_variable = r'%(escape)s\$(?P<value>\w+|%(escape)s\{(?P<unquoted>.+?)%(escape)s\})'
	'''regexp definition of a "variable"'''

	_escaped_chars = r'[\\\'\"\#/\\\$\{\}]'

	def __init__(self, *args, **kwargs):
		self.r_variable = re.compile(
			self._variable % {'escape': self._escape},
			re.UNICODE
		)

		return super(IHIHI, self).__init__(*args, **kwargs)


	def __setitem__(self, key, value):
		return dict.__setitem__(
			self,
			self._cast_str(key),
			self._parse_value(
				value
				if isinstance(value, basestring)
				else str(value),
				[]
			)
		)


	def _handle_fragment(self, fragment, quote=None):
		'''search for variables in `fragment`'''
		var = None
		data = []
		prev = 0

		if quote in (None, '"'):
			for var in self.r_variable.finditer(fragment):
				if var.start() > prev:
					data.append((
						self._unescape(
							fragment[prev:var.start()],
							quote
						),
						False
					))

				data.append((
					self._unescape(
						var.group('unquoted')
						if var.group('unquoted')
						else var.group('value')
					),
					True
				))

				prev = var.end()

		if var and var.end() < len(fragment):
			data.append((self._unescape(fragment[var.end():], quote), False))

		elif not prev:
			data = ((self._unescape(fragment, quote), False),)

		return data


	def __getitem__(self, key, path=None):
		'''return `key` value as internal type
		with interpolated variables

		For more informations, see: :meth:`~IHIH.__getitem__`.
		'''
		if path is None:
			path = []
		path.append(key)
		data = super(IHIHI, self).__getitem__(key)
		value = bytearray()

		for sub, is_variable in data:
			if is_variable:
				if sub not in self:
					continue
				if sub in path:
					value+= self._recursive(sub)

				else:
					value+= self.__getitem__(sub, path)
			else:
				value+= sub

		path.remove(key)
		return value


	def _recursive(self, value):
		'''recursive variable handler

		Default: empty string

		You can overwrite this function when subclassing
		and chose to return a unexpended version of the variable,
		raise an error or make a single, non recursive, lookup.
		'''
		return ''
