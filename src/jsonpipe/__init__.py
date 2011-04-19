# -*- coding: utf-8 -*-

import sys

import argparse
import simplejson

from pipe import jsonpipe, jsonunpipe


__all__ = ['jsonpipe', 'jsonunpipe']
__version__ = '0.0.5'


def _get_tests():
    import doctest
    return doctest.DocTestSuite(optionflags=(doctest.ELLIPSIS |
                                             doctest.NORMALIZE_WHITESPACE))


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
