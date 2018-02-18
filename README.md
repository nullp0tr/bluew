[![Build Status](https://travis-ci.org/nullp0tr/bluew.svg?branch=master)](https://travis-ci.org/nullp0tr/Bluew)
[![codecov](https://codecov.io/gh/nullp0tr/bluew/branch/master/graph/badge.svg)](https://codecov.io/gh/nullp0tr/bluew)
[![version](https://img.shields.io/badge/version-0.3.3-green.svg)](https://img.shields.io/badge/version-0.2.0-green.svg)

![logo](bluew_logo.png)

Bluetooth made simple.

### What's bluew?
Bluew started as just a wrapper for bluetoothctl, the client that comes with bluez 5. There are
some nice python bluetooth libraries out there, but they either didn't offer the easiness of bluetoothctl
or didn't nicely support having multiple connections.


Bluew tries to offer both multiple connections and an easy API,
that's heavily influenced by the Requests library.

By now bluew has moved on from wrapping bluetoothctl, and has it's own engine/backend which
talks directly to bluez using the D-Bus API.


### How to install?'

`pip3 install bluew`

Globally with sudo:

`sudo -H pip3 install bluew`


Unfortunately since DBusted (bluew's current backend) is using python-dbus, 
you also need to install the following packages from your system package manager.

##### Ubuntu:
`sudo apt-get install python-gi python3-dbus libdbus-1-dev libdbus-glib-1-dev`

We're currently looking for more native alternatives.

If you've managed to install bluew, congratulations, you passed the biggest 
obstacle in using it. From now it should be a smooth ride.

### Documentation
Complete documentation is currenly under construction,
but you can access the draft under https://nullp0tr.github.io/bluew/

### Simple use:
If you just wanna do something quickly 
like connecting to a device, disconnecting, 
trusting, reading an attribute from it, or writing to one, 
you can do that in the following way.
```python
>>> import bluew
```
##### Pair:
```python
>>> mac = 'xx:xx:xx:xx:xx'
>>> bluew.pair(mac)
```
##### Trust:
```python
>>> bluew.trust(mac)
```
##### Distrust:
```python
>>> bluew.distrust(mac)
```
##### Info:
```python
>>> dev = bluew.info(mac)
>>> dev.Trusted
True
>>> dev.Paired
True
```
##### Reading an attribute (service/characteristic):
```python
>>> uuid = 'someuuid'
>>> bluew.read_attribute(mac, uuid)
[b'x0', b'x0']
```
##### Writing an attribute:
```python
>>> bluew.write_attribute(mac, uuid, [0x3, 0x1, 0x1])
>>> bluew.read_attribute(mac, uuid)
[b'x03', b'x01', b'x01']
```
##### Scan and get devices around:
```python
>>> bluew.get_devices()
```
##### Get bluetooth controllers available:
```python
>>> bluew.get_controllers()
```
##### Remove device (distrust and unpair):
```python
>>> bluew.remove(mac)
```

### More advanced use:
If you have a more advanced usage in mind than just pairing with 
a device or reading an attribute quickly YOU SHOULD use bluew.Connection, 
for example:
```python
>>> from bluew import Connection
>>> mac = "xx:xx:xx:xx:xx"
>>> with Connection(mac) as con:
>>>     con.pair()
>>>     con.write_attribute(attr1, data)
>>>     con.notify(attr2, handler)
```
`bluew.Connection` supports all the functions already shown above and used 
directly from bluew except for `get_devices()` and `get_controllers` and offers 
even more functions like:
- get_services
- get_chrcs
- notify
- stop_notify

### Flags:
You can pass to any function/class imported from bluew the following flags:
##### keep_alive:
- *default*: True
- *possible*: False
- *usage*: Keep connection alive after Connection object is closed, or after a 
command is executed.
##### timeout:
- *default*: 5 (seconds)
- *possible*: N : float
- *usage*: Time allowed to find the device, also used with get_devices() for duration
of scanning. You can't pass this to Connection methods yet.
##### cntrl:
- *default*: None
- *possible*: 'hciN'; N being an integer
- *usage*: Controller you'd like to use for the operations, if None is left there's
currently no guarantee which controller would be picked.

### TODO for 0.4.0 release

- 90% Test coverage.
- Better handling of bluez errors.
- Fully automated hand-free pairing.
- Better documentation.
- Connect using advertising UUID instead of just mac.

