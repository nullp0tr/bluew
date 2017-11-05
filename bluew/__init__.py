"""
Bluew is a python wrapper for Bluetoothctl.
Author: Ahmed Alsharif
License: MIT
"""

import subprocess
import time
from queue import Queue, Empty
from threading import Thread


def enq_o(out, queue, handler=None, eof=b''):
    """
    Add lines from Bluetoothctl to the queue,
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


def expect(good, bad, response):
    """
    A function to test a list of lines,
    for specific answers, returns False
    if noting expected is received.
    :param good: What to expect with (True, reason).
    :param bad: What to expect with (False, reason).
    :param response: List of lines.
    :return: (True || False, "expected") or False
    """
    for line in response:
        for goodie in good:
            if goodie in line:
                return True, goodie
        for baddie in bad:
            if baddie is not None and baddie in line:
                return False, baddie
    return False


class Bluew(object):
    """
    Bluew is a python wrapper for bluetoothctl.
    """

    def __init__(self, handler=None, clean_q=True, blctl_bin='bluetoothctl'):
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

    def _parse_scanned_devices(self, found_devices):
        if found_devices is None:
            return

        def _handler(line):
            if 'NEW' in line:
                mac_addr = line.split(' ')[2]
                found_devices.append(mac_addr)

        self._thread = Thread(
            target=enq_o, args=(self.btctl.stdout, self._queue, _handler))
        self._thread.daemon = True
        self._thread.start()

    def _reload_thread(self):
        self._thread = Thread(
            target=enq_o, args=(self.btctl.stdout, self._queue, None))
        self._thread.daemon = True
        self._thread.start()

    def _clear_queue(self):
        if self._clean_q:
            with self._queue.mutex:
                self._queue.queue.clear()

    def _get_response(self, timeout=0.2, ignore_empty=False):
        response = []
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
                response.append(line)
        return response

    def _write_command(self, command):
        self._clear_queue()
        self.btctl.stdout.flush()
        self.btctl.stdin.write(command + '\n\r')
        self.btctl.stdout.flush()

    def _write_command_check_response(self, command, good, bad, timeout=20):
        self._write_command(command)
        response = False
        start_time = time.time()
        while response is False and not timed_out(start_time, timeout):
            response = expect(good, bad,
                              response=self._get_response())
        if response is False:
            return False, 'Timed out'
        return response

    def info(self, mac_, timeout=10):
        """
        Bluetoothctl info command.
        :param mac_: Device mac address.
        :param timeout:
        :return: Tuple with (True || False, Reason).
        """
        info_data = {}
        good = ['Device ' + mac_ + '\n']
        bad = ['Device ' + mac_ + ' not available']
        self._write_command('info ' + mac_)
        start_time = time.time()
        not_big_enough = True
        while not_big_enough and not timed_out(start_time, timeout):
            resp_data = self._get_response()

            res = expect(good, bad, resp_data)
            if isinstance(res, tuple) and res[0] is False:
                break

            def merge_dicts(first, second):
                """
                merges two dicts together and returns a third one.
                :param first: a dict
                :param second: another dict
                :return: a dict with both first and second dict
                """
                third = first.copy()
                third.update(second)
                return third

            info_data = merge_dicts(
                strip_info(resp_data, response_=info_data), info_data)
            not_big_enough = len(info_data) < (len(Bluew.attributes) - 2)
        if not_big_enough:
            info_data = {}
        return info_data

    def connect(self, mac_):
        """
        Bluetoothctl connect command.
        :param mac_: Device mac address.
        :return: Tuple with (True || False, Reason).
        """
        info = self.info(mac_)
        connected = info.get('Connected', '')
        if connected == 'yes':
            return True, "Already connected"
        good = [mac_ + ' Connected: yes', 'Connection successful']
        bad = ['Failed to connect', 'Device ' + mac_ + ' not available']
        response = self._write_command_check_response("connect " + mac_, good,
                                                      bad)
        return response

    def disconnect(self, mac_):
        """
        Bluetoothctl disconnect command.
        :param mac_: Device mac address.
        :return: Tuple with (True || False, Reason).
        """
        info = self.info(mac_)
        connected = info.get('Connected', '')
        if connected == 'no':
            return True, "Already disconnected"
        good = [mac_ + ' Connected: no', 'Successful disconnected']
        bad = ['Device ' + mac_ + ' not available', ]
        response = self._write_command_check_response("disconnect " + mac_,
                                                      good, bad)
        return response

    def pair(self, mac_):
        """
        Bluetoothctl pair command.
        :param mac_: Device mac address.
        :return: Tuple with (True || False, Reason).
        """
        info = self.info(mac_)
        paired = info.get('Paired', '')
        if paired == 'yes':
            return True, "Already paired"
        good = [mac_ + ' Paired: yes', ]
        bad = ['Failed to pair', 'Device ' + mac_ + ' not available']
        response = self._write_command_check_response("pair " + mac_, good,
                                                      bad)
        return response

    def select_attribute(self, mac_, attribute):
        """
        Bluetoothctl select-attribute command.
        :param mac_: Device mac address.
        :param attribute: The attribute to be selected.
        :return: Tuple with (True || False, Reason).
        """
        info = self.info(mac_)
        name = info.get('Name')
        if not name:
            return False, "Can't get device info"

        good = [name + ':' + '/' + attribute, ]
        bad = ['Missing attribute argument', 'No device connected']
        response = self._write_command_check_response(
            "select-attribute /org/bluez/hci0/dev_" + mac_.replace(':', '_') +
            "/" + attribute + "\n\r",
            good,
            bad,
            timeout=15)
        return response

    def write(self, data):
        """
        Bluetoothctl write command. Returns true if write was attempted.
        :param data: Data string, exp: "03 01 01".
        :return: Tuple with (True || False, Reason).
        """
        good = ['Attempting to write', ]
        bad = [
            'Missing data argument', 'No attribute selected',
            'Invalid value at index 0'
        ]
        respone = self._write_command_check_response("write " + data, good,
                                                     bad)
        return respone

    def swrite(self, data, base16=True):
        """
        Safe bluetoothctl write command, which returns true,
        only if write was confirmed, and not just if write was attempted.
        :param data: Data string, exp: "0x03 0x01 0xff".
        :param base16: Data values base. default is 16.
        :return: Tuple with (True || False, Reason).
        """
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

        write_response_status, write_response_reason = self.write(data)
        if not write_response_status:
            return write_response_status, write_response_reason
        read_data = self.read()

        for i, val in enumerate(data__):
            if val != int(read_data[i], base=16):
                return False, "Write was not successful"

        return True, "Write was successful"

    def read(self, timeout=0.2):
        """
        Bluetoothctl read command.
        :return: list with the attribute values
        """
        self._write_command("read")
        response = self._get_response(ignore_empty=True, timeout=timeout)
        response_ = strip_read(response)
        return response_

    def notify(self, on_off_arg):
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
            'No attribute selected'
        ]
        response = self._write_command_check_response(
            "notify " + on_off_arg,
            good,
            bad)
        return response

    def scan(self, on_off_arg, found_devices=None):
        """
        Bluetoothctl scan command
        :param found_devices: list of found devices so far.
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
            'Invalid argument'
        ]
        response = self._write_command_check_response(
            "scan " + on_off_arg,
            good,
            bad
        )

        if response[1] == 'Discovery started':
            self._parse_scanned_devices(found_devices)
        else:
            self._reload_thread()
        return response

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


def strip_info(data, response_=None):
    """
    This function strips device info from bluetoothctl output.
    :param data: a list of lines from bluetoothctl
    :param response_: optional recursive parameter
    :return: dictionary with device info
    """

    if data is None or response_ is None:
        response_ = {}
    for line_ in data:
        for attr in Bluew.attributes:
            if attr in line_:
                line_ = line_.strip('\n')
                line_ = line_.strip('\t')
                line_ = line_.split(' ', 1)[1]
                if attr == 'Device' and len(line_) != 17:
                    break
                response_[attr] = line_
    return response_


def strip_read(output_data):
    """
    This function strips an attribute value line,
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
    """
    This function returns True if it times out
    :param start_time: self explanatory
    :param timeout_time: self explanatory
    :return: True if time is out, else False.
    """
    return time.time() > start_time + timeout_time


class BluewNotifierError(Exception):
    """
    BluewNotifierError a custom exception with the step of error,
    and what caused it.
    """

    def __init__(self, step, reason):
        Exception.__init__(self)
        self.step = step
        self.reason = reason

    def __str__(self):
        return "Error while " + self.step + " because of: " + self.reason


class BluewNotifier(Bluew):
    """
    A Bluew instance to constantly get updates from a bluetooth attribute,
    that supports notifications.
    """

    def __init__(self, mac, attribute,
                 handler=None,
                 data_buff_size=1,
                 **kwargs):
        Bluew.__init__(self, self.notif_handler)
        self.ready = False
        self.handler = handler
        self.data_buff_size = data_buff_size
        # no_connect is used to skip step when testing.
        if kwargs.get('no_connect') is None:
            resp_stat, reason = self.connect(mac)
            if not resp_stat:
                raise BluewNotifierError("connecting", reason)
        # no_select is used to skip step when testing
        if kwargs.get('no_select') is None:
            resp_stat, reason = self.select_attribute(mac, attribute)
            if not resp_stat:
                raise BluewNotifierError("selecting attribute", reason)
        # no_notify is used to skip step when testing
        if kwargs.get('no_notify') is None:
            resp_stat, reason = self.notify('on')
            if not resp_stat:
                raise BluewNotifierError("setting notify", reason)
        self.ready = True
        self.data = []

    def notif_handler(self, line):
        """
        This function is called when Bluetoothctl outputs a line,
        and checks if it's a notification to call the user defined handler,
        on it's value.
        :param line: Bluetoothctl output line
        :return: Nothing
        """
        if self.ready:
            self._clear_queue()

            attr_val = 'Attribute' in line and 'Value: ' in line
            if line.startswith('\x1b[K[\x1b[0;93mCHG\x1b[0m] ') and attr_val:
                strdata = line.split(' ')
                val = strdata[4].split('x')[1].splitlines()[0]
                data = bytearray.fromhex(val)
                self.data.append(
                    abs(int.from_bytes(
                        data, byteorder='big', signed=True)))

            if len(self.data) == self.data_buff_size:
                if self.handler is not None:
                    self.handler(self.data)
                self.data.clear()
