.. couchdb-wsgi documentation master file, created by
   sphinx-quickstart on Mon Aug 17 21:05:22 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

couchdb-wsgi -- WSGI compliant adapter for CouchDB external processes
=====================================================================

.. module:: couchdb_wsgi
   :synopsis: WSGI compliant adapter for CouchDB external processes.
.. moduleauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>
.. sectionauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>

Module allows `WSGI <http://www.python.org/dev/peps/pep-0333/>`_ compliant applications to run inside a CouchDB external process.

.. toctree::
   :maxdepth: 3

.. _installation:

Installation
------------

`couchdb-wsgi` requires `setuptools <http://pypi.python.org/pypi/setuptools>`_ . If you do not have it installed already you will want to::

   $ curl -O http://peak.telecommunity.com/dist/ez_setup.py
   $ python ez_setup.py

Now you can install couchdb-wsgi::

   $ easy_install couch-wsgi

The source code is publicly `available on github <http://github.com/mikeal/couchdb-wsgi>`_. Tickets should be logged on the `github issues tracker <http://github.com/mikeal/couchdb-wsgi/issues>`_. 

The process for code contributions is for users to `fork the repository on github <http://help.github.com/forking/>`_, push modifications to their public fork, and then send `mikeal <http://github.com/mikeal>`_ a `pull request <http://github.com/guides/pull-requests>`_.

.. _couchdb-external-processes:

CouchDB External Proccesses
---------------------------

CouchDB includes support for assigning an external process handler to a given REST namespace in CouchDB databases. `This is documented on the CouchDB wiki <http://wiki.apache.org/couchdb/ExternalProcesses>`_.

Put simply, CouchDB invokes a shell call to the configured script and writes JSON request objects to stdin and takes JSON response objects in stdout. 

couchdb-wsgi provides a WSGI compliant adapter for this external process interface so that you can run wsgi applications and modern Python web frameworks.

Example::
   
   #!/usr/bin/python
   import couchdb_wsgi
   
   def application(environ, start_response):
       start_response('200 Ok', [('content-type', 'text/plain')])
       return ['Hello World']
   
   couchdb_wsgi.CouchDBWSGIHandler(application).run()

Using with Django
-----------------

Django's WSGI support is detailed `in their documentation for Apache support via mod_wsgi <http://docs.djangoproject.com/en/dev/howto/deployment/modwsgi/#basic-configuration>`_.

Example::

   #!/usr/bin/python
   import os, sys
   import couchdb_wsgi

   django_project = os.path.join(os.path.dirname(__file__), 'mysite')
   sys.path.append(django_project)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

   import django.core.handlers.wsgi

   application = django.core.handlers.wsgi.WSGIHandler()

   couchdb_wsgi.CouchDBWSGIHandler(application).run()


:mod:`couchdb_wsgi` --- WSGI compliant adapter for CouchDB external processes.
==============================================================================

.. class:: CouchDBWSGIHandler(application)

   *application* is a WSGI application callable.
   
   .. attribute:: application
   
      WSGI application callable passed during instantiation.
   
   .. method:: run()
      
      Starts the handler.
      
   .. method:: requests()
   
      Iterator. Yields request dictionaries.
   
   .. method:: handle_request(request)
   
      Creates a :class:`CouchDBWSGIRequest` instance for the given request and calls the application
      callable with :attr:`CouchDBWSGIRequest.environ` and :meth:`CouchDBWSGIRequest.start_response`.
      
      Method also converts the response and request handler to a CouchDB external process JSON object.

.. class:: CouchDBWSGIRequest(request)

   *request* is a request dictionary from CouchDB
   
   .. attribute:: request
   
      The request dictionary passed during instantiation.
   
   .. attribute:: environ
   
      Property. WSGI environ dictionary for this request.
   
   .. method:: start_response(status, headers)
   
      WSGI compliant start_response method.
      
   .. attribute:: code
   
      Status code integer parsed from the status string sent to :meth:`start_response`.
      
   .. attribute:: headers
   
      Dictionary parsed form the headers array sent to :meth:`start_response`.
   