####
ihih
####

:abbr:`ihih (I Hate INI hacks)` is an attempt to provide simple
configuration parsers (for Python) with a dictionary-like interface.

It try to be flexible and let you alter the syntax by sub-classing it.

More informations can be found in the docs directory or
`online <https://p0d.org/python-ihih/>`_.

Features
########

"flat" configuration file format
================================

Flat by opposition to, "nested" (like JSON, nginx, ...)
and "section" (INI files, ...).

Simple key / value system
=========================

Simple, obvious, supporting the features you are used to (ignore blank lines
and spaces, support comments, automatic unquoting, ...).

Lazy value interpolation
========================

Example::

   my_banner   = $myhostname MY-PROGRAM
   my_hostname = server.example.net
  
Dictionary-like interface
=========================

Example:

.. code:: pycon

   >>> print conf['my_banner']
   server.example.net MY-PROGRAM

Configuration precedence
========================

In the following example, user configuration file will take precedence over
system-wide configuration file:

.. code:: python

   conf = IHIH(
      (
         '/etc/example.conf',
         os.path.join(os.path.expanduser('~'), '.example.conf')
      )
   )

Default on the initialization
=============================

Example:

.. code:: python

   conf = IHIH(
      '/etc/example.conf',
      {'lang': 'en', 'TZ': 'UTC'}
   )
