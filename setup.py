#!/usr/bin/python
import os
import sys

try:
	from setuptools import setup
except ImportError:
	import warnings
	warnings.warn('setuptools not found, falling back to distutils')
	from distutils.core import setup

sys.path.insert(0, os.path.dirname(__file__))
import ihih





home = 'https://github.com/romain-dartigues/python-ihih'

setup(
	name='ihih',
	version=ihih.__version__,
	description='Configuration parsers with lazy parameters evaluation',
	long_description=open('README.rst').read(),
	author='Romain Dartigues',
	license='BSD 3-Clause License',
	keywords='conf config configuration parser',
	url=home,
	download_url=home,
	classifiers=(
		'Development Status :: 4 - Beta',
		'Environment :: Plugins',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.5',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Topic :: Software Development :: Libraries :: Python Modules',
	),
	py_modules=('ihih',),
)
