# -*- coding: utf-8 -*-

import sys

import argparse
import simplejson

from pipe import jsonpipe, jsonunpipe


__all__ = ['jsonpipe', 'jsonunpipe']
__version__ = '0.0.8'


def _get_tests():
    import doctest
    import inspect
    import sys
    import unittest

    import jsonpipe.sh

    def _from_module(module, object):
        """Backported fix for http://bugs.python.org/issue1108."""
        if module is None:
            return True
        elif inspect.getmodule(object) is not None:
            return module is inspect.getmodule(object)
        elif inspect.isfunction(object):
            return module.__dict__ is object.func_globals
        elif inspect.isclass(object):
            return module.__name__ == object.__module__
        elif hasattr(object, '__module__'):
            return module.__name__ == object.__module__
        elif isinstance(object, property):
            return True # [XX] no way not be sure.
        else:
            raise ValueError("object must be a class or function")
    finder = doctest.DocTestFinder()
    finder._from_module = _from_module

    suite = unittest.TestSuite()
    for name, module in sys.modules.iteritems():
        if name.startswith('jsonpipe'):
            try:
                mod_suite = doctest.DocTestSuite(
                    module, test_finder=finder,
                    optionflags=(doctest.NORMALIZE_WHITESPACE |
                                 doctest.ELLIPSIS))
            except ValueError:
                continue
            suite.addTests(mod_suite)
    return suite


PARSER = argparse.ArgumentParser()
PARSER.add_argument('-s', '--separator', metavar='SEP', default='/',
                    help="Set a custom path component separator (default: /)")
PARSER.add_argument('-v', '--version', action='version',
                    version='%%(prog)s v%s' % (__version__,))


def main():
    args = PARSER.parse_args()

    # Load JSON from stdin, preserving the order of object keys.
    json_obj = simplejson.load(sys.stdin,
                               object_pairs_hook=simplejson.OrderedDict)
    for line in jsonpipe(json_obj, pathsep=args.separator):
        print line


def main_unpipe():
    args = PARSER.parse_args()

    simplejson.dump(
        jsonunpipe(iter(sys.stdin), pathsep=args.separator,
                   decoder=simplejson.JSONDecoder(
                       object_pairs_hook=simplejson.OrderedDict)),
        sys.stdout)
