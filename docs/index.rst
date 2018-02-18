.. bluew documentation master file, created by
   sphinx-quickstart on Tue Feb 13 19:06:58 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Bluew: Bluetooth made simple
=================================

Release v\ |release|.


**Bluew** is a simple no boiler-plate bluetooth library, that handles all the
nifty details for you in the background so you can focus on writing programs.

-------------------

**How simple are we talking?**::

    >>> import bluew
    >>> bluew.write_attribute(mac="XX:XX:XX:XX:XX",
    ...                       attribute="7aabf8d2-14c9-11e8-b642-0ed5f89f718b",
    ...                       data=[0x03, 0x03, 0x01])

That was all you'd need to do to write to a BLE characteristic on a device.


**Bluew** aims to make communicating with bluetooth devices and specially BLE
powered devices as easy as possible, but taking out all the distractions and
offering a finely tuned interface that has enough to do everything you'd need,
without clogging your source program with boiler-plate code.


Useful Features
---------------

 - Connect, Pair and Trust
 - Read and Write Characteristics
 - Notify with Callbacks
 - Get Available Devices
 - Get Available Controllers
 - Pick your Controller/Adapter of Choice
 - Get Characteristics and Services of a Device
 - Keep-Alive or Disconnect when done



User Guide
----------

Information about the bluew API and how to use it. Bluew has basically two ways
of usage. You can either make a direct call like bluew.connect(..) or
bluew.read_attribute(..) or you can create a Connection object.

.. toctree::
   :maxdepth: 2

   api
