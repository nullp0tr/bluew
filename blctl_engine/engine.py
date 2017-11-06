"""
blctl_engine.engine
~~~~~~~~~~~~~~~~~~~

This module provides a default engine for bluew,
BlctlEngine which basically just wraps Bluetoothctl
from Bluez +5.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""

import subprocess
import time
from queue import Queue, Empty
from threading import Thread

import bluew.responses as responses
from bluew.engine import EngineBluew


class BlctlEngine(EngineBluew):
    """A EngineBluew using Bluetoothctl."""

    def __init__(self, blctl_bin='bluetoothctl',
                 handler=None, clean_q=True,
                 *args, **kwargs):

        name = "BlctlEngine"
        version = "0.0.1"
        kwargs['name'] = name
        kwargs['version'] = version

        super().__init__(*args, **kwargs)

        try:
            self.btctl = subprocess.Popen(
                [blctl_bin],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True,
                bufsize=1,
                universal_newlines=True)
        except FileNotFoundError:
            raise FileNotFoundError(
                'You need to have bluez ' + blctl_bin + ' installed!')

        self._queue = Queue()
        self._thread = Thread(
            target=enq_o, args=(self.btctl.stdout, self._queue, handler))
        self._thread.daemon = True
        self._thread.start()
        self._clean_q = clean_q

    def _clear_queue(self):
        if self._clean_q:
            with self._queue.mutex:
                self._queue.queue.clear()

    def _get_blctl_output(self, timeout=0.5, ignore_empty=False):
        output = []
        start_time = time.time()
        received_input = False
        while not timed_out(start_time, timeout):
            try:
                line = self._queue.get_nowait()
                received_input = True
            except Empty:
                if ignore_empty:
                    if received_input:
                        start_time = time.time()
                        received_input = False
                else:
                    break
            else:
                output.append(line)
        return output

    def _write_command(self, command):
        self._clear_queue()
        self.btctl.stdout.flush()
        self.btctl.stdin.write(command + '\n\r')
        self.btctl.stdout.flush()

    def _write_command_get_result(self, command, good, bad, timeout=20):
        self._write_command(command)
        result = False
        start_time = time.time()
        while result is False and not timed_out(start_time, timeout):
            result = expect(good, bad,
                            data=self._get_blctl_output(ignore_empty=True))
        if result is False:
            return False, 'Timed out'
        return result

    def _info(self, mac_, timeout=10):
        """
        Bluetoothctl info command.
        :param mac_: Device mac address.
        :param timeout:
        :return: Tuple with (True || False, Reason).
        """

        info_data = {}
        good = ['Device ' + mac_ + '\n']
        bad = ['Device ' + mac_ + ' not available',
               'Missing device address argument']
        self._write_command('info ' + mac_)
        start_time = time.time()
        not_big_enough = True
        while not_big_enough and not timed_out(start_time, timeout):
            resp_data = self._get_blctl_output()

            res = expect(good, bad, resp_data)
            if isinstance(res, tuple) and res[0] is False:
                return {}

            info_data = merge_dicts(
                strip_info(resp_data, response_=info_data), info_data)
            not_big_enough = len(info_data) < (len(BlctlEngine.attributes) - 2)
        if not_big_enough:
            info_data = {}
        return info_data

    def info(self, mac):
        """

        :param mac: MAC address of bluetooth device.
        :return: bluew.responses.Response
        """

        info_data = self._info(mac)
        if info_data:
            return responses.InfoSucceededResponse(info_data)
        return responses.InfoFailedResponse()

    def connect(self, mac):
        """Bluetoothctl connect command.

        :param mac: Device mac address.
        :return: Tuple with (True || False, Reason).
        """
        info = self._info(mac)
        connected = info.get('Connected', '')
        if connected == {}:
            return responses.ConnectFailedResponse()
        if connected == 'yes':
            return responses.ConnectedAlreadyResponse()

        good = [mac + ' Connected: yes', 'Connection successful']
        bad = ['Failed to connect', 'Device ' + mac + ' not available']
        result = self._write_command_get_result("connect " + mac,
                                                good,
                                                bad)
        if result[0] is True:
            return responses.ConnectSucceededResponse()

        return responses.ConnectFailedResponse()

    def _remove(self, mac):
        """
        Bluetoothctl remove command.
        :param mac: Device mac address.
        :return: Tuple with (True || False, Reason).
        """
        good = ['Device has been removed', ]
        bad = ['Device ' + mac + ' not available',
               "Missing device address argument"]
        result = self._write_command_get_result("remove " + mac,
                                                good,
                                                bad)
        return result

    def disconnect(self, mac):
        """
        Bluetoothctl disconnect command.
        :param mac: Device mac address.
        :return: Tuple with (True || False, Reason).
        """
        info = self._info(mac)
        connected = info.get('Connected', '')
        if connected == 'no':
            return responses.DisconnectedAlreadyResponse()

        good = [mac + ' Connected: no', 'Successful disconnected']
        bad = ['Device ' + mac + ' not available', ]
        result = self._write_command_get_result("disconnect " + mac,
                                                good, bad)
        if result[0] is True:
            return responses.DisconnectSucceededResponse()

        return responses.DisconnectFailedResponse()

    def pair(self, mac):
        """
        :param mac: MAC address of device.
        :return: bluew.responses.Response
        """

        info = self._info(mac)
        paired = info.get('Paired', '')
        if paired == 'yes':
            return responses.PairedAlreadyResponse()
        good = [mac + ' Paired: yes', ]
        bad = ['Failed to pair', 'Device ' + mac + ' not available']
        result = self._write_command_get_result("pair " + mac, good,
                                                bad)
        if result[0] is True:
            return responses.PairSucceededResponse()

        return responses.PairFailedResponse()

    def _select_attribute(self, mac, attribute):
        """
        :param mac: MAC address of device
        :param attribute: The attribute to be selected.
        :return: Tuple with (True || False, Reason).
        """
        info = self._info(mac)
        name = info.get('Name')
        if not name:
            return False, "Can't get device info"

        good = [name + ':' + '/' + attribute, ]
        bad = ['Missing attribute argument', 'No device connected']
        result = self._write_command_get_result(
            "select-attribute /org/bluez/hci0/dev_" + mac.replace(':', '_') +
            "/" + attribute + "\n\r",
            good,
            bad,
            timeout=15)
        return result

    def _write(self, data):
        """
        :param data: Data string, exp: "03 01 01".
        :return: Tuple with (True || False, Reason).
        """
        good = ['Attempting to write', ]
        bad = ['Missing data argument',
               'No attribute selected',
               'Invalid value at index 0']
        result = self._write_command_get_result("write " + data,
                                                good,
                                                bad)
        return result

    def write_attribute(self, mac, attribute, data):
        """
        Safe bluetoothctl write command, which returns true,
        only if write was confirmed, and not just if write was attempted.
        :param mac: MAC address of bluetooth device.
        :param attribute: attribute to be overwritten.
        :param data: Data string, exp: "0x03 0x01 0xff".
        :param base16: Data values base. default is 16.
        :return: Tuple with (True || False, Reason).
        """

        base16 = True

        data_ = data.split(' ')
        data__ = []
        for val in data_:
            if base16 and 'x' in val:
                base = 16
            elif not base16 and 'x' not in val:
                base = 10
            else:
                raise ValueError(
                    "Base is not correct, if using base 10 set base16 to False"
                )
            data__.append(int(val, base))

        result = self._select_attribute(mac, attribute)
        if result[0] is False:
            return responses.WriteFailedResponse()

        write_response_status, write_response_reason = self._write(data)
        if not write_response_status:
            return write_response_status, write_response_reason
        read_data = self._read()

        read_data_integers = hexlist_to_intlist(read_data)
        if validate_write_data(data__, read_data_integers):
            return responses.WriteFailedResponse()

        return responses.WriteSucceededResponse()

    def _read(self, timeout=0.4):
        self._write_command("read")
        blctl_output = self._get_blctl_output(ignore_empty=True,
                                              timeout=timeout)
        result = strip_read(blctl_output)
        return result

    def read_attribute(self, mac, attribute):
        """Bluetoothctl read command.

        :return: list with the attribute values
        """

        self._select_attribute(mac, attribute)
        result = self._read()
        if not result:
            return responses.ReadFailedResponse()
        return responses.ReadSucceededResponse(result)

    def _devices(self, timeout=0.8):
        """Bluetoothctl devices command.

        :return: list with devices.
        """
        self._write_command("devices")
        result = self._get_blctl_output(ignore_empty=True, timeout=timeout)
        response_ = strip_devices(result)
        return response_

    def _notify(self, on_off_arg):
        """
        Bluetoothctl notify command.
        :param on_off_arg: string, either "on" or "off".
        :return: Tuple with (True || False, Reason).
        """
        good = [
            'Notify started',
            'Notify stopped',
        ]
        bad = [
            'Failed to start notify',
            'Failed to stop notify',
            'No attribute selected',
            'Missing on/off argument'
        ]
        result = self._write_command_get_result(
            "notify " + on_off_arg,
            good,
            bad)
        return result

    def _scan(self, on_off_arg):
        """Bluetoothctl scan command.

        :param on_off_arg: string, either "on" or "off".
        :return: Tuple with (True || False, Reason).
        """
        good = [
            'Discovery started',
            'Discovery stopped'
        ]
        bad = [
            'Failed to start discovery',
            'Failed to stop discovery',
            'Invalid argument',
            'Missing on/off argument'
        ]
        result = self._write_command_get_result(
            "scan " + on_off_arg,
            good,
            bad
        )

        return result

    attributes = (
        'Device',
        'Name',
        'Alias',
        'Class',
        'Icon',
        'Paired',
        'Trusted',
        'Blocked',
        'Connected',
        'LegacyPairing',)


def enq_o(out, queue, handler=None, eof=b''):
    """Add lines from Bluetoothctl to the queue,
    and pass each line to a handler if provided.

    :param out: stdout
    :param queue: data queue
    :param handler: function that get's called with each line.
    :param eof: end of file
    :return: Nothing
    """

    for line in iter(out.readline, eof):
        if handler is not None:
            handler(line=line)
        queue.put(line)
    out.close()


def expect(good, bad, data):
    """A function to test a list of lines,
    for specific answers, returns False
    if noting expected is received.

    :param good: What to expect with (True, reason).
    :param bad: What to expect with (False, reason).
    :param data: List of lines.
    :return: (True || False, "expected") or False
    """

    for line in data:
        for goodie in good:
            if goodie in line:
                return True, goodie
        for baddie in bad:
            if baddie is not None and baddie in line:
                return False, baddie
    return False


def strip_info(data, response_=None):
    """This function strips device info from bluetoothctl output.

    :param data: a list of lines from bluetoothctl
    :param response_: optional recursive parameter
    :return: dictionary with device info
    """

    if data is None or response_ is None:
        response_ = {}
    for line_ in data:
        for attr in BlctlEngine.attributes:
            if attr in line_:
                line_ = line_.strip('\n')
                line_ = line_.strip('\t')
                line_ = line_.split(' ', 1)[1]
                if attr == 'Device' and len(line_) != 17:
                    break
                response_[attr] = line_
    return response_


def strip_devices(output_data):
    """This function strips devices data.

    :param output_data: output lines from bluetoothctl
    :return: list of devices.
    """

    result = []
    for line in output_data:
        splitted_line = line.split(' ')
        line_starts_correctly = splitted_line[0] == 'Device'
        line_has_enough_attrs = len(splitted_line) >= 3
        if line_starts_correctly and line_has_enough_attrs:
            result.append(splitted_line[1])
    return result


def hexlist_to_intlist(hexlist):
    """This functions turns a list of hex strings to
    a list of integers.

    :param hexlist: A list of strings containing hex numbers.
    :return: A list of integers.
    """

    intlist = [int(val, base=16) for val in hexlist]
    return intlist


def strip_read(output_data):
    """This function strips an attribute value line,
    off everything except for the value.

    :param output_data: output lines from Bluetoothctl
    :return: the value of the attribute
    """

    result = []
    for line in output_data:
        if 'Attribute' in line and 'Value: ' in line:
            result.append(line[-5:-1])
    return result


def timed_out(start_time, timeout_time):
    """This function returns True if time's out

    :param start_time: self explanatory
    :param timeout_time: self explanatory
    :return: True if time is out, else False.
    """

    return time.time() > start_time + timeout_time


def validate_write_data(data_written, data_read):
    """This function validates if data_read contains data_written.

    :param data_written: data written to data_read.
    :param data_read: a list of values.
    :return: True or False
    """

    if data_written != data_read[:len(data_written)]:
        return False
    return True


def merge_dicts(first, second):
    """Merge two dicts together and return a third one.

    :param first: a dict
    :param second: another dict
    :return: a dict with both first and second dict
    """

    third = first.copy()
    third.update(second)
    return third
