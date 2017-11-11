[![Build Status](https://travis-ci.org/nullp0tr/bluew.svg?branch=master)](https://travis-ci.org/nullp0tr/Bluew)
[![codecov](https://codecov.io/gh/nullp0tr/bluew/branch/master/graph/badge.svg)](https://codecov.io/gh/nullp0tr/bluew)
[![version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://img.shields.io/badge/version-0.2.0-green.svg)

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


### How to install?

`pip3 install git+https://github.com/nullp0tr/bluew.git`

With sudo:

`sudo -H pip3 install git+https://github.com/nullp0tr/bluew.git`
### Basic usage:
Bluew offers an easy API, which returns bluew Responses unless a major error happened,
like the engine not supporting a certain API call or a connection error when the device,
is not available.

With device available:

```
>>> import bluew as bl
>>> resp = bl.pair('xx:xx:xx:xx:xx')
>>> resp.has_succeeded
True
>>> resp = bl.info('xx:xx:xx:xx:xx')
>>> resp.has_succeeded
True
>>> resp.data
{'Device': 'xx:xx:xx:xx:xx', 'Trusted': 'yes', 'LegacyPairing': 'no', 'Blocked': 'no', 'Paired': 'yes', 'Alias': 'XXX', 'Name': 'XXXX', 'Connected': 'yes'}

```

When the device is not available for connection it raises a BluewConnectionError:
```
>>> resp = bl.pair('xx:xx:xx')
bluew.connections.BluewConnectionError: Bluew was not able to connect to device.
```
If the device is available and it can connect but it can't pair for some reason,
like the device not being in pair mode, It doesn't raise an exception, but the 
has_succeeded attribute would be set to false.
```
>>> resp = bl.pair('xx:xx:xx:xx:xx')
>>> resp.has_succeeded
False
```
As easy that!

### More advanced usage:
If you use the use the API offered by import bluew, you can do basic bluetooth tasks, but you have to
provide the device MAC address each time, and the connection is terminated as soon as the call returns.
But if you want to have multiple connections and/or keep the connection alive for longer it's better to
use the Connection object.

```
>>> from bluew import Connection
>>> thermostat = Connection('xx:xx:xx:xx:xx')
>>> thermostat.mac
'xx:xx:xx:xx:xx'
>>> # Now you can use the api functions without providing the address each time
>>> r = thermostat.pair()
>>> r.has_succeeded
True
```

### API
This is a list of the currently supported API calls:
- pair
- trust
- info
- read_attribute
- write_attribute

### TODO for 1.0.0 release

- Guarantee 100% code coverage.
- support plugable engines
- Add following calls to the API and to the default engine:
  - notify
  - devices
  - find_attributes
  - find_characteristics
  - block
  - unblock
- Support using both MAC address and UUIDs for calls.
  
### TODO in future
- Add support for more BLE modes.
