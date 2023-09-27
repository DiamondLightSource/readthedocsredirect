readthedocsredirect
===================

An empty docs project to help with redirecting docs from readthedocs to github.io

Usage
-----

This needs to be run inside DLS

First of all install the deps::

    $ pipenv install

Then create a new branch, named after the project you wish to redirect::

    $ git checkout -b <myproject>

Modify the ``docs/index.rst`` file and replace the ``<organization>`` and ``<project>`` tags with the appropriate ones::

    $ sed -i 's/<organization>/myorganization/' docs/index.rst
    $ sed -i 's/<project>/myproject/' docs/index.rst

Commit the modified file and push the branch::

    $ git add docs/index.rst
    $ git commit -m "Modified index.rst"
    $ git push -u origin <myproject>

Then check the help::

    $ pipenv run python readthedocsredirect.py -h

Now run it with the name of the project (and optionally github repo and org)::

    $ pipenv run python readthedocsredirect.py myproject
    https://myproject.readthedocs.io should now redirect to https://myorganization.github.io/myproject/

How it works
------------

This project builds an index.html whose entire contents is some Javascript that
replaces the current URL with the intended redirect URL.

This used to be simpler, but readthedocs now requires several configuration files and
settings, which means there must be some per-project configuration of this redirector.
