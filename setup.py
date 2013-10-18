#!/usr/bin/python
import distutils.core
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import ihih





distutils.core.setup(
	name='ihih',
	version=ihih.__version__,
	description='Configuration parsers with lazy parameters evaluation',
	long_description=open('README.rst').read(),
	author='Romain Dartigues',
	license='BSD 3-Clause License',
	keywords='conf config configuration parser',
	url='https://github.com/romain-dartigues/python-ihih',
	classifiers=(
		'Development Status :: 4 - Beta',
		'Environment :: Plugins',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Software Development :: Libraries :: Python Modules',
	),
	py_modules=('ihih',),
)
