[![Build Status](https://travis-ci.org/nullp0tr/bluew.svg?branch=master)](https://travis-ci.org/nullp0tr/Bluew)
# Bluew

Bluew is a python wrapper for Bluetoothctl, the official client from the linux bluetooth stack Bluez.

### Why need Bleuew?
Bluetoothctl is already an awesome tool on it's own, but it wasn't made to be automated, 
and so the main goal of bluew is to literally automate tasks/tests which you'd do with bluetoothctl 
without using one of the awesome but more verbose python bluetooth stacks. It also allows you to connect and 
talk to multiple bluetooth devices without much hassle.

### How to install?

`git clone https://github.com/nullp0tr/bluew.git`

`cd bluew`

`pip3 install . `
`
### Test coverage
More tests are getting added, but currently most tests can't run on travis, because bluew uses Bluez 5 and so far I hadn't any success installing that on the travis VMs.
