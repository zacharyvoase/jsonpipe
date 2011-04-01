========
Examples
========

This file enumerates some common patterns for working with jsonpipe output. The
examples here use the file ``example.json``, which can be found in the root of
this repo. Basic familiarity with the UNIX shell, common utilities and regular
expressions is assumed.


Simple Selection
================

In Python::

    >>> json[12]['user']['screen_name']
    u"ManiacasCarlos"

On the command-line, just grep for the specific path you're looking for::

    $ jsonpipe < example.json | grep -P '^/12/user/screen_name\t'
    /12/user/screen_name	"ManiacasCarlos"

The pattern used here is terminated with ``\t``, because otherwise we'd get
sub-components of the ``screen_name`` path if it were an object, and we'd also
pick up any keys which started with the string ``screen_name`` (so we might get
``screen_name_123`` and ``screen_name_abc`` if those keys existed).


Extracting Entire Objects
=========================

In Python::

    >>> json[12]['user']
    {... u'screen_name': u'ManiacasCarlos', ...}

On the command-line, grep for the path again but terminate with ``/`` instead
of ``\t``::

    $ jsonpipe < example.json | grep -P '^/12/user/'
    ...
    /12/user/profile_use_background_image	true
    /12/user/protected	false
    /12/user/screen_name	"ManiacasCarlos"
    /12/user/show_all_inline_media	false
    ...

You can also filter for either a simple value *or* an entire object by
terminating the pattern with a character range::

    $ jsonpipe < example.json | grep -P '^/12/user[/\t]'
    /12/user	{}
    /12/user/contributors_enabled	false
    /12/user/created_at	"Mon Jan 31 20:42:31 +0000 2011"
    /12/user/default_profile	false
    ...


Searching Based on Equality or Patterns
=======================================

Find users with a screen name beginning with a lowercase 'm'::

    $ jsonpipe < example.json | grep -P '/user/screen_name\t"m'
    /0/user/screen_name	"milenemagnus_"
    /11/user/screen_name	"mommiepreneur"
    /14/user/screen_name	"mantegavoadora"

