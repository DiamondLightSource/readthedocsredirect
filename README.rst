readthedocsredirect
===================

An empty docs project to help with redirecting docs from readthedocs to github.io

Usage
-----

This needs to be run inside DLS

First of all install the deps::

    $ pipenv install

Then check the help::

    $ pipenv run python readthedocsredirect.py -h

Now run it with the name of the project (and optionally github repo and org)::

    $ pipenv run python readthedocsredirect.py myproject
    https://myproject.readthedocs.io should now redirect to https://dls-controls.github.io/myproject/master/

How it works
------------

Readthedocs redirects only work on 404, so this replaces the repo with an empty
one (this repo) and then puts in a static redirect from /en/latest/<something> to
https://dls-controls.github.io/myproject/master/<something>.
