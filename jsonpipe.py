# -*- coding: utf-8 -*-

import os.path as p
import sys

import argparse
import simplejson


__all__ = ['jsonpipe']
__version__ = '0.0.4'


def jsonpipe(obj, pathsep='/', path=()):

    r"""
    Generate a jsonpipe stream for the provided (parsed) JSON object.

    This generator will yield output as UTF-8-encoded bytestrings line-by-line.
    These lines will *not* be terminated with line ending characters.

    The provided object can be as complex as you like, but it must consist only
    of:

    *   Dictionaries (or subclasses of `dict`)
    *   Lists or tuples (or subclasses of the built-in types)
    *   Unicode Strings (`unicode`, utf-8 encoded `str`)
    *   Numbers (`int`, `long`, `float`)
    *   Booleans (`True`, `False`)
    *   `None`

    Please note that, where applicable, *all* input must use either native
    Unicode strings or UTF-8-encoded bytestrings, and all output will be UTF-8
    encoded.

    The simplest case is outputting JSON values (strings, numbers, booleans and
    nulls):

        >>> def pipe(obj): # Shim for easier demonstration.
        ...     print '\n'.join(jsonpipe(obj))
        >>> pipe(u"Hello, World!")
        /	"Hello, World!"
        >>> pipe(123)
        /	123
        >>> pipe(0.25)
        /	0.25
        >>> pipe(None)
        /	null
        >>> pipe(True)
        /	true
        >>> pipe(False)
        /	false

    jsonpipe always uses '/' to represent the top-level object. Dictionaries
    are displayed as ``{}``, with each key shown as a sub-path:

        >>> pipe({"a": 1, "b": 2})
        /	{}
        /a	1
        /b	2

    Lists are treated in much the same way, only the integer indices are used
    as the keys, and the top-level list object is shown as ``[]``:

        >>> pipe([1, "foo", 2, "bar"])
        /	[]
        /0	1
        /1	"foo"
        /2	2
        /3	"bar"

    Finally, the practical benefit of using hierarchical paths is that the
    syntax supports nesting of arbitrarily complex constructs:

        >>> pipe([{"a": [{"b": {"c": ["foo"]}}]}])
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
    separator, :func:`jsonpipe` will raise a :exc:`ValueError`:

        >>> pipe({"a/b": 1})
        Traceback (most recent call last):
        ...
        ValueError: Path separator '/' present in key 'a/b'

    In more complex examples, some output may be written before the exception
    is raised. To mitigate this problem, you can provide a custom path
    separator:

        >>> print '\n'.join(jsonpipe({"a/b": 1}, pathsep=':'))
        :	{}
        :a/b	1

    The path separator should be a bytestring, and you are advised to use
    something you are almost certain will not be present in your dictionary
    keys.
    """

    def output(string):
        return pathsep + pathsep.join(path) + "\t" + string

    if is_value(obj):
        yield output(simplejson.dumps(obj))
        raise StopIteration # Stop the generator immediately.
    elif isinstance(obj, dict):
        yield output('{}')
        iterator = obj.iteritems()
    elif isinstance(obj, (list, tuple)):
        yield output('[]')
        iterator = enumerate(obj)
    else:
        raise TypeError("Unsupported type for jsonpipe output: %r" %
                        type(obj))

    for key, value in iterator:
        # Check the key for sanity.
        key = to_str(key)
        if pathsep in key:
            # In almost any case this is not what the user wants; having
            # the path separator in the key would create ambiguous output
            # so we should fail loudly and as quickly as possible.
            raise ValueError("Path separator %r present in key %r" %
                             (pathsep, key))

        for line in jsonpipe(value, pathsep=pathsep, path=path + (key,)):
            yield line


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


def _get_tests():
    import doctest
    return doctest.DocTestSuite(optionflags=(doctest.ELLIPSIS |
                                             doctest.NORMALIZE_WHITESPACE))


PARSER = argparse.ArgumentParser()
PARSER.add_argument('-s', '--separator', metavar='SEP', default='/',
                    help="Set a custom path component separator (default: /)")
PARSER.add_argument('-v', '--version', action='version',
                    version='jsonpipe v%s' % (__version__,))


def main():
    args = PARSER.parse_args()

    # Load JSON from stdin, preserving the order of object keys.
    json_obj = simplejson.load(sys.stdin,
                               object_pairs_hook=simplejson.OrderedDict)
    for line in jsonpipe(json_obj, pathsep=args.separator):
        print line
