========
jsonpipe
========

Everyone I know prefers to work with JSON over XML, but sadly there is a sore
lack of utilities of the quality or depth of `html-xml-utils`_ and
`XMLStarlet`_ for actually processing JSON data in an automated fashion, short
of writing an *ad hoc* processor in your favourite programming language.

.. _html-xml-utils: http://www.w3.org/Tools/HTML-XML-utils/README
.. _XMLStarlet: http://xmlstar.sourceforge.net/

**jsonpipe** is a step towards a solution: it traverses a JSON object and
produces a simple, line-based textual format which can be processed by all your
UNIX favourites like grep, sed, awk, cut and diff. It may also be valuable
within programming languages---in fact, it was originally conceived as a way of
writing simple test assertions against JSON output without coupling the tests
too closely to the specific structure used.

This implementation (which should be considered the reference) is written in
Python.


Example
=======

A ``<pre>`` is worth a thousand words. For simple JSON values::

    $ echo '"Hello, World!"' | jsonpipe
    /	"Hello, World!"
    $ echo 123 | jsonpipe
    /	123
    $ echo 0.25 | jsonpipe
    /	0.25
    $ echo null | jsonpipe
    /	null
    $ echo true | jsonpipe
    /	true
    $ echo false | jsonpipe
    /	false

The 'root' of the object tree is represented by a single ``/`` character, and
for simple values it doesn't get any more complex than the above. Note that a
single tab character separates the path on the left from the literal value on
the right.

Composite data structures use a hierarchical syntax, where individual
keys/indices are children of the path to the containing object::

    $ echo '{"a": 1, "b": 2}' | jsonpipe
    /	{}
    /a	1
    /b	2
    $ echo '["foo", "bar", "baz"]' | jsonpipe
    /	[]
    /0	"foo"
    /1	"bar"
    /2	"baz"

For an object or array, the right-hand column indicates the datatype, and will
be either ``{}`` (object) or ``[]`` (array). For objects, the order of the keys
is preserved in the output.

The path syntax allows arbitrarily complex data structures::

    $ echo '[{"a": [{"b": {"c": ["foo"]}}]}]' | jsonpipe
    /	[]
    /0	{}
    /0/a	[]
    /0/a/0	{}
    /0/a/0/b	{}
    /0/a/0/b/c	[]
    /0/a/0/b/c/0	"foo"


Caveat: Path Separators
=======================

Because the path components are separated by ``/`` characters, an object key
like ``"abc/def"`` would result in ambiguous output. jsonpipe will throw
an error if this occurs in your input, so that you can recognize and handle the
issue. To mitigate the problem, you can choose a different path separator::

    $ echo '{"abc/def": 123}' | jsonpipe -s '☃'
    ☃	{}
    ☃abc/def	123

The Unicode snowman is chosen here because it's unlikely to occur as part of
the key in most JSON objects, but any character or string (e.g. ``:``, ``::``,
``~``) will do.


Installation
============

**jsonpipe** is written in Python, so is best installed using ``pip``::

    pip install jsonpipe

Note that it probably requires Python v2.5+ for now, although work on
compatibility with previous versions of Python is in progress.


(Un)license
===========

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
software, either in source code form or as a compiled binary, for any purpose,
commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this
software dedicate any and all copyright interest in the software to the public
domain. We make this dedication for the benefit of the public at large and to
the detriment of our heirs and successors. We intend this dedication to be an
overt act of relinquishment in perpetuity of all present and future rights to
this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
