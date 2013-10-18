########
Warnings
########

.. Warning::
   They are usage warning, but you are also encouraged to consult the
   :doc:`known bugs and limitations <BUGS>`.

Still in beta
#############

This library is still β, expect its internal API to change over time.

Please let me know if you use it, your features requests, bugs, etc.

Not extensively tested
######################

Some tests exists in the test/ directory, but it's still missing much.

.. Note::
   I only tested it over Python 2.6.

Default item getter return internal type
########################################

You probably want to favor :meth:`ihih.IHIH.get` over
:meth:`ihih.IHIH.__getitem__` as the latter return the internal type which
might not be suitable for your needs.

Automatic type conversion
#########################

This is a key / value, file-based, configuration system;
so it forces everything as a string.

Just be aware of that.

File opening failure
####################

Missing configuration files will be silently ignored, *but*,
if a configuration file is not readable (permissions errors)
or not a file (dead link or directory), it *will* raise an exception,
as the user should be notified of this error.
