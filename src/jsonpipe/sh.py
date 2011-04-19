import re

import calabash
import simplejson

import jsonpipe as jp


__all__ = ['jsonpipe', 'jsonunpipe', 'select', 'search_attr']


jsonpipe = calabash.source(jp.jsonpipe)


@calabash.sink
def jsonunpipe(stdin, *args, **kwargs):
    """Calabash wrapper for :func:`jsonpipe.jsonunpipe`."""

    yield jp.jsonunpipe(stdin, *args, **kwargs)


@calabash.sink
def select(stdin, path, pathsep='/'):

    r"""
    Select only lines beginning with the given path.

    This effectively selects a single JSON object and all its sub-objects.

        >>> obj = {'a': 1, 'b': {'c': 3, 'd': 4}}
        >>> list(jsonpipe(obj))
        ['/\t{}',
        '/a\t1',
        '/b\t{}',
        '/b/c\t3',
        '/b/d\t4']
        >>> list(jsonpipe(obj) | select('/b'))
        ['/b\t{}',
        '/b/c\t3',
        '/b/d\t4']
        >>> list(jsonpipe(obj) | select('/b') | jsonunpipe())
        [{'b': {'c': 3, 'd': 4}}]
    """

    path = re.sub(r'%s$' % re.escape(pathsep), r'', path)
    return iter(stdin |
                calabash.common.grep(r'^%s[\t%s]' % (
                    re.escape(path),
                    re.escape(pathsep))))


@calabash.sink
def search_attr(stdin, attr, value, pathsep='/'):

    r"""
    Search stdin for an exact attr/value pair.

    Yields paths to objects for which the given pair matches. Example:

        >>> obj = {'a': 1, 'b': {'a': 2, 'c': {'a': "Hello"}}}
        >>> list(jsonpipe(obj) | search_attr('a', 1))
        ['/']
        >>> list(jsonpipe(obj) | search_attr('a', 2))
        ['/b']
        >>> list(jsonpipe(obj) | search_attr('a', "Hello"))
        ['/b/c']

    Multiple matches will result in multiple paths being yielded:

        >>> obj = {'a': 1, 'b': {'a': 1, 'c': {'a': 1}}}
        >>> list(jsonpipe(obj) | search_attr('a', 1))
        ['/', '/b', '/b/c']
    """

    return iter(stdin |
                # '...path/attribute\tvalue' => 'path'.
                calabash.common.sed(r'^(.*)%s%s\t%s' % (
                    re.escape(pathsep),
                    re.escape(attr),
                    re.escape(simplejson.dumps(value))),
                    r'\1', exclusive=True) |
                # Replace empty strings with the root pathsep.
                calabash.common.sed(r'^$', pathsep))
