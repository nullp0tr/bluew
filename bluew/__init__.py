"""
Bluew is a python wrapper for Bluetoothctl.
Author: Ahmed Alsharif
License: MIT
"""

import subprocess
import time
from queue import Queue, Empty
from threading import Thread


def enq_o(out, queue, handler=None):
    """
    Add lines from Bluetoothctl to the queue,
     and pass each line to a handler if provided.
    :param out: stdout
    :param queue: data queue
    :param handler: function that get's called with each line.
    :return: Nothing
    """
    for line in iter(out.readline, b''):
        if handler is not None:
            handler(line=line)
        queue.put(line)
    out.close()


class Bluew(object):
    """
    Bluew is a python wrapper for bluetoothctl.
    """

    def __init__(self, handler=None):
        try:
            self.btctl = subprocess.Popen(
                ['bluetoothctl'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True,
                bufsize=1,
                universal_newlines=True)
        except FileNotFoundError:
            raise FileNotFoundError(
                'You need to have bluez (bluetoothctl) installed!')

        self.queue = Queue()
        self.thread_ = Thread(
            target=enq_o, args=(self.btctl.stdout, self.queue, handler))
        self.thread_.daemon = True
        self.thread_.start()

    def _clear_queue(self):
        with self.queue.mutex:
            self.queue.queue.clear()

    def _check_response(self, good, bad, response=None):
        if not response:
            response = self._get_response()
        for line in response:
            for gd in good:
                if gd in line:
                    return True, gd
            for bd in bad:
                if bd is not None and bd in line:
                    return False, bd
        return False

    def _get_response(self, timeout=5, ignore_empty=False):
        response = []
        start_time = time.time()
        while not timed_out(start_time, timeout):
            try:
                line = self.queue.get_nowait()
            except Empty:
                if ignore_empty:
                    pass
                else:
                    break
            else:
                response.append(line)
        self._clear_queue()
        return response

    def _write_command(self, command):
        self._clear_queue()
        self.btctl.stdout.flush()
        self.btctl.stdin.write(command + '\n\r')
        self.btctl.stdout.flush()

    def _write_command_check_response(self, command, good, bad, timeout=10):
        self._write_command(command)
        response = False
        start_time = time.time()
        while response is False and not timed_out(start_time, timeout):
            response = self._check_response(good, bad)
        if response is False:
            return False, 'Timed out'
        return response

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

    def info(self, mac_, timeout=5):
        """
        Bluetoothctl info command.
        :param mac_: Device mac address.
        :param timeout:
        :return: Tuple with (True || False, Reason).
        """
        response_ = {}
        good = ['Device ' + mac_ + '\n']
        bad = ['Device ' + mac_ + ' not available']
        self._write_command('info ' + mac_)

        start_time = time.time()
        while response_ == {} and not timed_out(start_time, timeout):
            response = self._get_response()

            res = self._check_response(good, bad, response=response)
            if isinstance(res, tuple) and res[0] is False:
                break

            response_ = self.strip_info(response)
            if response_ != {}:
                break

        return response_

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
        bad = ['Failed to pair', ]
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
        bad = ['Missing attribute argument', ]
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

    def read(self):
        """
        Bluetoothctl read command.
        :return: list with the attribute values
        """
        self._write_command("read")
        response = self._get_response(ignore_empty=True)
        response_ = self.strip_read(response)
        return response_

    def notify(self, status):
        """
        Bluetoothctl notify command.
        :param status: status string, either "on" or "off".
        :return: Tuple with (True || False, Reason).
        """
        good = [
            'Notify started',
            'Notify stopped',
        ]
        bad = ['Failed to start notify', ]
        response = self._write_command_check_response(
            "notify " + status, good, bad, timeout=15)
        return response

    @staticmethod
    def strip_read(response):
        """
        This function strips an attribute value line,
        off everything except for the value.
        :param response: response is a line from Bluetoothctl
        :return: the value of the attribute
        """
        response_ = []
        for line in response:
            if 'Attribute' in line:
                response_.append(line[-5:-1])
        return response_

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

    @staticmethod
    def strip_info(response):
        """
        This function strips device info from bluetoothctl output.
        :param response: a list of lines from bluetoothctl
        :return: dictionary with device info
        """
        response_ = {}
        for i, line_ in enumerate(response):
            for attr in Bluew.attributes:
                if attr in line_:
                    line_ = line_.strip('\n')
                    line_ = line_.strip('\t')
                    line_ = line_.split(' ', 1)[1]
                    if attr == 'Device' and len(line_) != 17:
                        break
                    response_[attr] = line_
        if len(response_) < len(Bluew.attributes) - 2:
            return {}
        return response_


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
        self.step = step
        self.reason = reason

    def __str__(self):
        return "Error while " + self.step + " because of: " + self.reason


class BluewNotifier(Bluew):
    """
    A Bluew instance to constantly get updates from a bluetooth attribute,
    that supports notifications.
    """

    def __init__(self, mac, attribute, handler=None, data_buff_size=1):
        Bluew.__init__(self, self.notif_handler)
        self.ready = False
        self.handler = handler
        self.data_buff_size = data_buff_size
        resp_stat, reason = self.connect(mac)
        if not resp_stat:
            raise BluewNotifierError("connecting", reason)
        resp_stat, reason = self.select_attribute(mac, attribute)
        if not resp_stat:
            raise BluewNotifierError("selecting attribute", reason)
        resp_stat, reason = self.notify('on')
        if not resp_stat:
            raise BluewNotifierError("setting notify", reason)
        self.ready = True
        self.data = []

    def notif_handler(self, line):
        """
        Thif function get's called when Bluetoothctl outputs a line,
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
                b = bytearray.fromhex(val)
                self.data.append(
                    abs(int.from_bytes(
                        b, byteorder='big', signed=True)))

            if len(self.data) == self.data_buff_size:
                if self.handler is not None:
                    self.handler(self.data)
                self.data.clear()
