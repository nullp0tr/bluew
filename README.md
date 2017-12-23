[![Build Status](https://travis-ci.org/nullp0tr/bluew.svg?branch=master)](https://travis-ci.org/nullp0tr/Bluew)
[![codecov](https://codecov.io/gh/nullp0tr/bluew/branch/master/graph/badge.svg)](https://codecov.io/gh/nullp0tr/bluew)
[![version](https://img.shields.io/badge/version-0.3.0-green.svg)](https://img.shields.io/badge/version-0.2.0-green.svg)

```
                ########  ##       ##     ## ######## ##      ##
                ##     ## ##       ##     ## ##       ##  ##  ##
  Bluetooth     ##     ## ##       ##     ## ##       ##  ##  ##
  Made          ########  ##       ##     ## ######   ##  ##  ##
  Simple.       ##     ## ##       ##     ## ##       ##  ##  ##
                ##     ## ##       ##     ## ##       ##  ##  ##
                ########  ########  #######  ########  ###  ###  
```


# Bluew
Bluetooth made simple.

### What's bluew?
Bluew started as just a wrapper for bluetoothctl, the client that comes with bluez 5. There are
some nice python bluetooth libraries out there, but they either didn't offer the easiness of bluetoothctl
or didn't nicely support having multiple connections.


Bluew tries to offer both multiple connections and an easy API,
that's heavily influenced by the Requests library.

By now bluew has moved on from wrapping bluetoothctl, and has it's own engine/backend which
talks directly to bluez using the D-Bus API.


### How to install?

`pip3 install git+https://github.com/nullp0tr/bluew.git`

With sudo:

`sudo -H pip3 install git+https://github.com/nullp0tr/bluew.git`

### API
This is a list of the currently supported API calls:
- pair
- trust
- untrust
- info
- read_attribute
- write_attribute
- notify
- stop_notify
- get_devices
- get_controllers
- get_services
- get_chrcs
- remove

### TODO for 0.4.0 release

- 90% Test coverage.
- Better handling of bluez errors.
- Better documentation.
- Connect using advertising UUID instead of just mac.

### Changelog:
##### #0.3.0:
- Changed from the blctl engine to DBusted (Implemented on top of dbus).
- Added notify, stop_notify.
- Added get_devices, get_controllers.
- Added get_services, get_chrcs.
- Added remove
- Much more...
