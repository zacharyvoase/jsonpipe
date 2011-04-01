# -*- coding: utf-8 -*-

from __future__ import with_statement
import contextlib
import os.path as p
import sys

import argparse
import simplejson


__all__ = ['JSONPiper', 'jsonpipe']

# Read in the version from the VERSION file.
version_filename = p.join(p.dirname(p.dirname(__file__)), 'VERSION')
with open(version_filename) as version_file:
    __version__ = version_file.read().strip()
del version_filename, version_file


class JSONPiper(object):

    u"""
    Class to convert a (parsed) JSON object into a UNIX-friendly text stream.

    You need to initialize your piper with a stream; for practical purposes
    I'll be using `sys.stdout`:

        >>> import sys
        >>> p = JSONPiper(sys.stdout)

    Please note that, where applicable, *all* input must use either native
    Unicode strings or UTF-8-encoded bytestrings, and all output will be UTF-8
    encoded.

    The simplest case is outputting JSON values (strings, numbers, booleans and
    nulls):

        >>> p.write(u"Hello, World!")
        /	"Hello, World!"
        >>> p.write(123)
        /	123
        >>> p.write(0.25)
        /	0.25
        >>> p.write(None)
        /	null
        >>> p.write(True)
        /	true
        >>> p.write(False)
        /	false

    jsonpipe always uses '/' to represent the top-level object. Dictionaries
    are displayed as ``{}``, with each key shown as a sub-path:

        >>> p.write({"a": 1, "b": 2})
        /	{}
        /a	1
        /b	2

    Lists are treated in much the same way, only the integer indices are used
    as the keys, and the top-level list object is shown as ``[]``:

        >>> p.write([1, "foo", 2, "bar"])
        /	[]
        /0	1
        /1	"foo"
        /2	2
        /3	"bar"

    Finally, the practical benefit of using hierarchical paths is that the
    syntax supports nesting of arbitrarily complex constructs:

        >>> p.write([{"a": [{"b": {"c": ["foo"]}}]}])
        /	[]
        /0	{}
        /0/a	[]
        /0/a/0	{}
        /0/a/0/b	{}
        /0/a/0/b/c	[]
        /0/a/0/b/c/0	"foo"

    Because the sole separator of path components is a ``/`` character by
    default, keys containing this character would result in ambiguous output.
    Therefore, if you try to write a dictionary with a key containing the path
    separator, `JSONPiper` will raise a :exc:`ValueError`:

        >>> p.write({"a/b": 1})
        Traceback (most recent call last):
        ...
        ValueError: Path separator '/' present in key 'a/b'

    In more complex examples, some output may be written before the exception
    is raised. To mitigate this problem, you can provide a custom path
    separator:

        >>> colon_p = JSONPiper(sys.stdout, pathsep=':')
        >>> colon_p.write({"a/b": 1})
        :	{}
        :a/b	1

    The path separator should be a bytestring, and it is of course advisable
    that you use something you are almost certain will not be present in your
    dictionary keys.
    """

    def __init__(self, stream, pathsep='/'):
        self.stream = stream
        self.stack = []
        self.pathsep = pathsep

    def write(self, obj):

        """
        Output the provided (parsed) JSON object to this piper's stream.

        The object can be as complex as you like, but it must consist only of:

        *   Dictionaries (or subclasses of `dict`)
        *   Lists or tuples (or subclasses of the built-in types)
        *   Unicode Strings (`unicode`, utf-8 encoded `str`)
        *   Numbers (`int`, `long`, `float`)
        *   Booleans (`True`, `False`)
        *   `None`

        Consult the :class:`JSONPiper` documentation for a full run-down of the
        output format.
        """

        if is_value(obj):
            self._write(simplejson.dumps(obj))
            return

        if isinstance(obj, dict):
            self._write('{}')
            iterator = obj.iteritems()
        elif isinstance(obj, (list, tuple)):
            self._write('[]')
            iterator = enumerate(obj)
        else:
            raise TypeError("Unsupported type for jsonpipe output: %r" % type(obj))

        for key, value in iterator:
            with self.push(key) as sub_writer:
                sub_writer.write(value)

    def _write(self, string):
        """Write a simple string to the output stream at the current path."""

        self.stream.write("%s\t%s\n" % (self.path, string))

    @contextlib.contextmanager
    def push(self, key):

        """
        Context manager to push a key onto the stack and pop it afterwards.

        For now, this will modify the piper inside the `with` block and reverse
        the modification afterwards, but in future it may return a new piper
        object, so you should use the bound variable in the body of your `with`
        block for forwards-compatibility.

        Example:

            >>> import sys
            >>> p = JSONPiper(sys.stdout)
            >>> print p.path
            /
            >>> with p.push('example') as p2:
            ...     print p2.path
            /example
            >>> print p.path
            /
        """

        key = to_str(key)
        if self.pathsep in key:
            # In almost any case this is not what the user wants; because
            # joining the strings with a human-readable character is
            # potentially a lossy process we should fail if
            raise ValueError("Path separator %r present in key %r" %
                    (self.pathsep, key))

        self.stack.append(key)
        try:
            yield self
        finally:
            self.stack.pop()

    @property
    def path(self):
        """The current path in the object tree, as a bytestring."""

        return self.pathsep + self.pathsep.join(self.stack)


def to_str(obj):

    ur"""
    Coerce an object to a bytestring, utf-8-encoding if necessary.

        >>> to_str("Hello World")
        'Hello World'
        >>> to_str(u"H\xe9llo")
        'H\xc3\xa9llo'
    """

    if isinstance(obj, unicode):
        return obj.encode('utf-8')
    elif hasattr(obj, '__unicode__'):
        return unicode(obj).encode('utf-8')
    return str(obj)


def is_value(obj):

    """
    Determine whether an object is a simple JSON value.

    The phrase 'simple JSON value' here means one of:

    *   String (Unicode or UTF-8-encoded bytestring)
    *   Number (integer or floating-point)
    *   Boolean
    *   `None`
    """

    return isinstance(obj, (str, unicode, int, long, float, bool, type(None)))


def jsonpipe(json_obj, stream=None, writer=None):

    """
    Pipe the provided JSON object to the output stream (defaulting to stdout).

    This is just a shortcut for constructing a :class:`JSONPiper`:

        >>> jsonpipe({"a": 1, "b": 2})
        /	{}
        /a	1
        /b	2
    """

    if stream is None:
        stream = sys.stdout
    if writer is None:
        writer = JSONPiper(stream)
    writer.write(json_obj)


def _get_tests():
    import doctest
    return doctest.DocTestSuite(
            optionflags=(doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE))


PARSER = argparse.ArgumentParser()
PARSER.add_argument('-s', '--separator', metavar='SEP', default='/',
        help="Set a custom path component separator (default: /)")
PARSER.add_argument('-v', '--version', action='version',
        version='jsonpipe v%s' % (__version__,))


def main():
    args = PARSER.parse_args()
    json_obj = simplejson.load(sys.stdin,
            object_pairs_hook=simplejson.OrderedDict)
    JSONPiper(sys.stdout, pathsep=args.separator).write(json_obj)
