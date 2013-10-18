########
Examples
########

Getting started
###############

Attempt to load a system-wide configuration file, whose settings will be
overwritten by a user preferences files.

Missing files are silently ignored.

.. code:: python

   from ihih import IHIH

   conf = IHIH(
      (
         '/etc/example.conf',
         os.path.join(os.path.expanduser('~'), '.example.conf')
      ),
      debug='1'
   )

   if conf.get_float('debug', errors='ignore'):
      print 'i am running in debug mode'

Reloading the conf
##################

Assuming `conf` is a :class:`~ihih.IHIH` instance.

.. code:: python

   # reload on SIGHUP
   import signal

   signal.signal(signal.SIGHUP, lambda s, f: conf.reload())

Configuration format
####################

By default, :class:`~ihih.IHIH` parse files using the following rules:

* the key is before the first ``=`` character
* the value is everything after the first ``=`` character
* the value might be empty
* key and value have their leading and trailing spaces stripped
* values can be quoted (between ``'`` or ``"``)
* quoted values have their quotes automatically removed (ie: ``"my value"``
  becomes ``my value``)
* single quotes are considered as a character
* lines not matching the key / separator / value are ignored
* comments (beginning with a ``#`` or ``//``) are ignored and deleted from the
  value except if they are escaped or quoted
* specials characters (``\'"#/``) can be escaped by prefixing them with a
  backslash (``\``) to not be treated specially
* other (non-special) characters preceded by the escape character are not
  treated specially and the escape character is preserved

By default, :class:`~ihih.IHIHI` parse files accordingly the following rules:

* same-same than :class:`~ihih.IHIH`
* add dollar (``$``) in the special character list
* every word prefixed by a non-escaped dollar and not embraced by
  single-quotes (``'``) is considered as a variable
* strings beginning with ``${`` and ending with ``}`` are also variables,
  this let you define variables containing non-word characters such as dots
  hyphens, or spaces
* variables interpolation is done when using the variable, this let you define
  (or change) the variable content later
* when a variable is not found, it resolve as an empty string
* variable recursion resolve to an empty string

Which mean that it could parse, to a certain extent
(see :ref:`single-line_only`), subset of:

* shell script
* `Postfix <http://www.postfix.org/>`_ main.cf
* Python
* INI (will ignore the sections)

That could be convenient if you have to share a configuration file between
scripts, given you pay attention to respect both formats.

Examples of configuration files
===============================

Parsing a shell script:

.. code:: bash

   # as in shell
   FOO="bar"
   FOOBAR=foo-$FOO   # resolve as: foo-bar
   FOOBAR="foo-$FOO" # resolve as: foo-bar
   FOOBAR='foo-$FOO' # resolve as: foo-$FOO
   BAR=${FOO}        # resolve as: bar
   ABC="a" 'b' c     # resolve as: a b c
   C=hello # world   # resolve as: hello
   D=hello \# world  # resolve as: hello # world

   # different
   DATE=$(date)      # resolve as: $(date)

Parsing a main.cf:

.. code::

   smtpd_banner = $myhostname ESMTP
   myhostname = foo.example.net

Parsing some Python:

.. code:: python

   # same
   a = 'AA'
   b = "BB"

   # notably different
   c = 'A' "B"     # resolve as: A B
   d = c           # resolve as: c

Parsing an INI file:

.. code:: ini

   [uwsgi]                       # ignored
   http-socket = :9090
   processes = 4

   # different
   URL = localhost${http-socket} # resolve as: localhost:9000
