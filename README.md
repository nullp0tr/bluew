[![Build Status](https://travis-ci.org/nullp0tr/bluew.svg?branch=master)](https://travis-ci.org/nullp0tr/Bluew)
[![codecov](https://codecov.io/gh/nullp0tr/bluew/branch/master/graph/badge.svg)](https://codecov.io/gh/nullp0tr/bluew)
# bluew
Bluew is a python wrapper for Bluetoothctl, the official client from the linux bluetooth stack Bluez.

### Why need Bleuew?
Bluetoothctl is already an awesome tool on it's own, but it wasn't made to be automated, 
and so the main goal of bluew is to literally automate tasks/tests which you'd do with bluetoothctl 
without using one of the awesome but more verbose python bluetooth stacks. It also allows you to connect and 
talk to multiple bluetooth devices without much hassle.

### How to install?

`pip3 install git+https://github.com/nullp0tr/bluew.git`

With sudo:

`sudo -H pip3 install git+https://github.com/nullp0tr/bluew.git`
### How to use?
Bluew has an api that almost exactly matches bluetoothctl's, so all you have to do to connect and disconnect for example is:
```
>>> from bluew import Bluew
>>> bl = Bluew()
>>> bl.connect('xx:xx:xx:xx:xx')
(True, 'Connection successful')
>>> bl.disconnect('xx:xx:xx:xx:xx')
(True, 'Successful disconnected')
>>>
```
As easy that!

### Status
Some functions of Bluetoothctl aren't ready yet, but they're all gonna be added soon.

### Test coverage
More tests are getting added, but currently most tests can't run on travis, because bluew uses Bluez 5 and so far I hadn't any success installing that on the travis VMs.