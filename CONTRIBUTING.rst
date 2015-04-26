############
Contributing
############

This document provides guidelines for people who want to contribute to the
`drunken-boat` project.


**************
Create tickets
**************

Please use `drunken-boat bugtracker`_ **before** starting some work:

* check if the bug or feature request has already been filed. It may have been
  answered too!

* else create a new ticket.

* if you plan to contribute, tell us, so that we are given an opportunity to
  give feedback as soon as possible.

* Then, in your commit messages, reference the ticket with some
  ``refs #TICKET-ID`` syntax.


******************
Use topic branches
******************

* Work in branches.

* Please never push in ``master`` directly.

* Prefix your branch with one the following keyword ``feature/`` when
  adding a new feature and ``fix/`` when working on a fix.
  You can also add the ticket ID corresponding to the issue to be explicit.

* If you work in a development branch and want to refresh it with changes from
  master, please `rebase`_ or `merge-based rebase`_, i.e. do not merge master.


***********
Fork, clone
***********

Clone `drunken-boat` repository (adapt to use your own fork):

.. code:: sh

   git clone https://github.com/boblefrag/drunken_boat
   cd drunken_boat

*************
Usual actions
*************

The `setup.py` is the reference card for usual actions in development
environment:

* Install development toolkit with `python setup.py develop`.

* Run tests with `python setup.py test`.

* Build documentation: `python setup.py build_sphinx`

* Release `drunken_boat` project with `zest.releaser`_: ``fullrelease``.

.. rubric:: Notes & references

.. target-notes::

.. _`drunken-boat bugtracker`: https://github.com/boblefrag/drunken-boat/issues
.. _`rebase`: http://git-scm.com/book/en/v2/Git-Branching-Rebasing
.. _`merge-based rebase`: http://git-scm.com/book/en/v2/Git-Branching-Rebasing
.. _`zest.releaser`: https://pypi.python.org/pypi/zest.releaser/
