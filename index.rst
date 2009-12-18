.. couchdb-pythonviews documentation master file, created by
   sphinx-quickstart on Fri Dec 18 13:26:07 2009.

couchdb-pythonviews -- A Python View Server for CouchDB
=======================================================

.. module:: couchdbviews
   :synopsis: CouchDB View Server Module.
.. moduleauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>
.. sectionauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>

This module implements a CouchDB View Server for Python.

.. toctree::
   :maxdepth: 3

.. _installation:

Installation
------------

`couchdb-pythonviews` requires `setuptools <http://pypi.python.org/pypi/setuptools>`_. If you do not have it installed already you will want to::

   $ curl -O http://peak.telecommunity.com/dist/ez_setup.py
   $ python ez_setup.py

The view server line protocol is 100% JSON so installing an optimized JSON parser significantly improves performance. couchdb-pythonviews checks for JSON libraries in this order; jsonlib2, simplejson, json. If you have one of the optimized libraries installed (jsonlib2 or simplejson with C speedups) it will use it.