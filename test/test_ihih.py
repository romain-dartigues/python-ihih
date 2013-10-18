# vim:set fileencoding=utf8:
import unittest
import tempfile


import ihih





class SimpleConf(unittest.TestCase):
	_key = 0

	def setUp(self):
		self.ihih = ihih.IHIH(())


	def key(self, new=False):
		if new:
			self._key+= 1
		return self._key


	def test_value_default(self):
		conf = self.ihih.__class__((), default=1)
		self.assertTrue('default' in conf)
		self.assertEqual(conf, {'default': 1})


	def test_value_simple(self):
		self.ihih[self.key(True)] = 'simple value'
		self.assertEqual(self.ihih[self.key()], 'simple value')


	def test_quoting_simple(self):
		self.ihih[self.key(True)] = '''simple 'quoted' "value"'''
		self.assertEqual(self.ihih[self.key()], 'simple quoted value')


	def test_quoting_interleaved(self):
		self.ihih[self.key(True)] = '''interleaved: 'a"'"'b"'''
		self.assertEqual(self.ihih[self.key()], '''interleaved: a"'b''')


	def test_quoting_escaped(self):
		self.ihih[self.key(True)] = r'''"\"''"'''
		self.assertEqual(self.ihih[self.key()], '"\'\'')
		

	def test_escaping(self):
		self.ihih[self.key(True)] = r'\r\n\0\"\$'
		self.assertEqual(self.ihih[self.key()], r'\r\n\0"\$')


	def test_file_loading(self):
		tmp_a = tempfile.NamedTemporaryFile(bufsize=0)
		tmp_a.write('debug = 1\nvar = x y')

		tmp_b = tempfile.NamedTemporaryFile(bufsize=0)
		tmp_b.write('  debug  =  0 \nfoo = bar # comment\n\n#var = c')

		conf = self.ihih.__class__((tmp_a.name, tmp_b.name))
		self.assertEqual(conf['debug'], '0')
		self.assertEqual(conf['var'],   'x y')
		self.assertEqual(conf['foo'],   'bar')

		tmp_a.close()
		tmp_b.close()


	def test_file_loading_unicode(self):
		tmp = tempfile.NamedTemporaryFile(bufsize=0)
		tmp.write(u'größe = 10.24\nwährung = €'.encode('utf8'))

		conf = self.ihih.__class__(tmp.name)
		self.assertEqual(conf[u'größe'], '10.24')
		self.assertEqual(conf[u'währung'], '\xe2\x82\xac')
		self.assertEqual(conf.get_unicode(u'währung'), u'€')

		tmp.close()


	def test_type_conversion(self):
		f = 1.1
		self.ihih[f] = f
		self.assertEqual(self.ihih[f], str(f))
		self.assertEqual(self.ihih[str(f)], str(f))
		self.assertEqual(self.ihih.get(f), str(f))
		self.assertEqual(self.ihih.get_float(f), f)



class Interpolated(SimpleConf):
	def setUp(self):
		self.ihih = ihih.IHIHI(())


	def test_escaping(self):
		self.ihih[self.key(True)] = r'\r\n\0\"\$'
		self.assertEqual(self.ihih[self.key()], r'\r\n\0"$')


	def test_variable_interpolation(self):
		self.ihih['a'] = r'simple \"value\"'
		self.assertEqual(self.ihih['a'], r'simple "value"')

		self.ihih['b'] = r'\$a=$a=$a'
		self.assertEqual(self.ihih['b'], r'$a=%(a)s=%(a)s' % self.ihih, 'simple interpolation')

		self.ihih['c'] = r'$d $a'
		self.assertEqual(self.ihih['c'], r' %(a)s' % self.ihih, 'interpolation with unknown value')

		self.ihih['d'] = r'd'
		self.assertEqual(self.ihih['c'], r'd %(a)s' % self.ihih, 'interpolation lazy resolution')


	def test_variable_interpolation_recursion(self):
		self.ihih['a'] = r'a'

		self.ihih['b'] = r'\$b=$b'
		self.assertEqual(self.ihih['b'], r'$b=', 'direct recursion')

		self.ihih['c'] = r'd[$d]'
		self.ihih['d'] = r'c[$c]'
		self.assertEqual(self.ihih['c'], r'd[c[]]', 'indirect recursion')
		self.assertEqual(self.ihih['d'], r'c[d[]]', 'indirect recursion')


	def test_variable_boundaries(self):
		self.ihih['a'] = 'var:a'
		self.ihih['{a}'] = 'var:{a}'
		self.ihih['a b'] = 'var:{a b}'
		self.ihih['a_b'] = 'var:a_b'
		self.ihih['a.b'] = 'var:a.b'
		self.ihih['a:b'] = 'var:a:b'

		self.ihih[self.key(True)] = r'$a=${a}'
		self.assertEqual(self.ihih[self.key()], r'%(a)s=%(a)s' % self.ihih)

		self.ihih[self.key(True)] = r'$a_b=${a_b}'
		self.assertEqual(self.ihih[self.key()], r'%(a_b)s=%(a_b)s' % self.ihih)

		self.ihih[self.key(True)] = r'$a.b=${a.b}'
		self.assertEqual(self.ihih[self.key()], r'%(a.b)s=%(a.b)s' % self.ihih)

		self.ihih[self.key(True)] = r'$a:b=${a:b}'
		self.assertEqual(self.ihih[self.key()], r'%(a:b)s=%(a:b)s' % self.ihih)

		self.ihih[self.key(True)] = r'$a b!=${a b}'
		self.assertEqual(self.ihih[self.key()], r'%(a)s b!=%(a b)s' % self.ihih)

		self.ihih[self.key(True)] = r'${{a}}'
		self.assertEqual(self.ihih[self.key()], r'}')

		self.ihih[self.key(True)] = r'${{a\}}=${\{a\}}'
		self.assertEqual(self.ihih[self.key()], r'%({a})s=%({a})s' % self.ihih)


	def test_variable_unicode(self):
		self.ihih[u'größe'] = 10.24
		self.ihih[u'währung'] = u'€'

		self.ihih[self.key(True)] = u'$größe $währung'

		self.assertEqual(self.ihih.get_unicode(self.key()), u'10.24 €')


	def test_variable_quoting(self):
		self.ihih['a'] = 'AA'
		self.ihih['b'] = ''' "[$a]" '[$a]' '''

		self.assertEqual(self.ihih['b'], ' [AA] [$a] ')





if __name__ == '__main__':
	unittest.main()
