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

Map and Reduce
--------------

This section assumes you have some knowledge of how `CouchDB's map and reduce system works <http://wiki.apache.org/couchdb/Introduction_to_CouchDB_views>`_.

This Python view server works a bit differently than the default JavaScript view server in CouchDB. Instead of defining a single function in the design document attribute for a given function the Python view server requires that you use a decorator to call out which function in the Python code is a given function type.::

   @map_function
   def my_map_function(doc):
       emit(doc['type'], 1)

This means that, if you like, you can stick multiple view functions in a single Python file which will sync the code blob to multiple attributes.::

   @map_function
   def my_map_function(doc):
       emit(doc['type'], 1)
       
   @reduce_function
   def my_reduce_function(values, rereduce):
       return sum(values)

This code can now be used as both the map and reduce attributes and inside the view server it will only get compiled once.

Reduce is a special function, it uses the positional argument names to decide what should be passed to it. This means that the **argument names you use in your reduce function matter**. Valid argument names are keys, values, ids, length, and rereduce.::

   @reduce_function
   def mega_reduce(keys, values, ids, length, rereduce):
       # I did *not* need all of these args
       if rereduce:
           return sum(values)
       return length

The Python view server also allows you to write explicit rereduce functions.::

   @reduce_function
   def full_length_reduce(length):
       return length
   
   @rereduce_function
   def full_length_rereduce(values):
       return sum(values)

