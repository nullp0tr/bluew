import select
import subprocess
import time
from queue import Queue, Empty
from threading import Thread


def enq_o(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


class Bluew(object):
    def __init__(self):
        try:
            self.btctl = subprocess.Popen(['bluetoothctl'],
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          close_fds=True,
                                          bufsize=1,
                                          universal_newlines=True)
        except FileNotFoundError:
            raise FileNotFoundError('You need bluez and bluetoothctl installed!')

        self.queue = Queue()
        self.thread_ = Thread(target=enq_o, args=(self.btctl.stdout, self.queue))
        self.thread_.daemon = True
        self.thread_.start()
        self.poller = select.poll()
        self.poller.register(self.btctl.stdout, select.POLLIN)

    def _clear_queue(self):
        with self.queue.mutex:
            self.queue.queue.clear()

    def _check_answer(self, good, bad):
        answer = self._get_answer()
        for line in answer:
            for gd in good:
                if gd in line:
                    return True, gd
            for bd in bad:
                if bd is not None and bd in line:
                    return False, bd
        return False

    def _get_answer(self):
        answer = []
        while True:
            try:
                line = self.queue.get_nowait()
            except Empty:
                break
            else:
                answer.append(line)
        return answer

    def info(self, mac_):
        answer_ = {}
        while answer_ == {}:
            self._write_command('info ' + mac_)
            answer = self._get_answer()
            answer_ = self.strip_info(answer)
            if answer_ != {}:
                break
        return answer_

    def _write_command(self, command):
        self._clear_queue()
        self.btctl.stdout.flush()
        self.btctl.stdin.write(command + '\n\r')
        self.btctl.stdout.flush()

    def _write_command_check_answer(self, command, good, bad, timeout=10):
        self._write_command(command)
        answer = False
        start_time = time.time()
        end_time = time.time()
        timed_out = end_time > start_time + timeout
        while answer is False and not timed_out:
            answer = self._check_answer(good, bad)
            end_time = time.time()
            timed_out = end_time > start_time + timeout
        if timed_out:
            return False, 'Timed out'
        return answer

    def connect(self, mac_):
        info = self.info(mac_)
        if info['Connected'] == 'yes':
            return True, "Already connected"
        good = [mac_ + ' Connected: yes', 'Connection successful']
        bad = ['Failed to connect', 'Device ' + mac_ + ' not available']
        answer = self._write_command_check_answer("connect " + mac_, good, bad)
        return answer

    def disconnect(self, mac_):
        info = self.info(mac_)
        if info['Connected'] == 'no':
            return True, "Already disconnected"
        good = [mac_ + ' Connected: no', 'Successful disconnected']
        bad = ['Device ' + mac_ + ' not available', ]
        answer = self._write_command_check_answer("disconnect " + mac_, good, bad)
        return answer

    def pair(self, mac_):
        info = self.info(mac_)
        if info['Paired'] == 'yes':
            return True, "Already paired"
        good = [mac_ + ' Paired: yes', ]
        bad = ['Failed to pair', ]
        answer = self._write_command_check_answer("pair " + mac_, good, bad)
        return answer

    def select_attribute(self, mac_, attribute):
        info = self.info(mac_)
        name = info['Name']
        good = [name + ':' + '/' + attribute, ]
        bad = [None, ]
        answer = self._write_command_check_answer(
            "select-attribute /org/bluez/hci0/dev_" + mac_.replace(':', '_') + "/" + attribute + "\n\r",
            good,
            bad
        )
        return answer

    def write(self, data):
        good = ['Attempting to write', ]
        bad = ['Missing data argument', 'No attribute selected', 'Invalid value at index 0']
        answer = self._write_command_check_answer(
            "write " + data,
            good,
            bad
        )
        return answer

    # Not working yet
    def read(self):
        good = ['Attempting to read', ]
        bad = ['No attribute selected', ]
        answer = self._write_command_check_answer(
            "read",
            good,
            bad
        )
        return answer

    def notify(self, status):
        self.btctl.stdin.write("notify " + status + "\n\r")
        self.btctl.stdin.flush()

    @staticmethod
    def strip_info(answer):
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
            'LegacyPairing',
        )
        answer_ = {}
        for i, line_ in enumerate(answer):
            for attr in attributes:
                if attr in line_:
                    line_ = line_.strip('\n')
                    line_ = line_.strip('\t')
                    line_ = line_.split(' ', 1)[1]
                    if attr == 'Device' and len(line_) != 17:
                        break
                    answer_[attr] = line_
        if len(answer_) < len(attributes) - 2:
            return {}
        return answer_
