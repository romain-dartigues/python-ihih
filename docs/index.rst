############################################
:mod:`ihih` --- simple configuration parsers
############################################

.. topic:: Overview

   :abbr:`ihih (I Hate INI hacks)` is an attempt to provide simple
   configuration parsers (for Python) with a dictionary-like interface.

   It try to be flexible and let you alter the syntax by sub-classing it.

Why?
####

Because I Hate :abbr:`INI (initialization)` files.
I don't need sections, i think :py:mod:`ConfigParser` is a pain to use...

And also because in my opinion configuration files should not be *executed*
(ie: i feel bad having a Python file as a configuration system, sure it is
*flexible*, but, you know... [if you don't, you probably don't need this]).

.. toctree::
   :maxdepth: 2

   api
   examples
   warnings
   BUGS

Indices and tables
##################

* :ref:`genindex`
