.. _api:

The Basic Bluew API
===================

.. module:: bluew


This document covers the basic one-time API calls you can make with bluew.


Main Interface
--------------

The following 10 functions are accessible directly from bluew.

.. autofunction:: connect
.. autofunction:: disconnect
.. autofunction:: trust
.. autofunction:: distrust
.. autofunction:: pair
.. autofunction:: remove
.. autofunction:: get_devices
.. autofunction:: info
.. autofunction:: read_attribute
.. autofunction:: write_attribute


Exceptions
----------

.. autoexception:: bluew.errors.BluewError
.. autoexception:: bluew.errors.DeviceNotAvailable
.. autoexception:: bluew.errors.PairError
.. autoexception:: bluew.errors.ReadWriteNotifyError
.. autoexception:: bluew.errors.InvalidArgumentsError
.. autoexception:: bluew.errors.NoControllerAvailable
.. autoexception:: bluew.errors.ControllerSpecifiedNotFound
.. autoexception:: bluew.errors.ControllerNotReady


Bluew Connection
----------------

.. _sessionapi:

.. autoclass:: Connection
    :inherited-members:

