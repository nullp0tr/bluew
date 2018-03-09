"""
This is an SDK for the Myo Gesture Control Armband.
"""


from bluew.rapid import RapidAPI, Read, Write, Notify


CONTROL_SERVICE = 'd5060401-a904-deb9-4748-2c7f4a124842'
BATTERY_CHRC = '00002a19-0000-1000-8000-00805f9b34fb'
EMG_CHAR1 = 'd5060405-a904-deb9-4748-2c7f4a124842'
EMG_CHAR2 = 'd5060305-a904-deb9-4748-2c7f4a124842'
EMG_CHAR3 = 'd5060205-a904-deb9-4748-2c7f4a124842'
EMG_CHAR4 = 'd5060105-a904-deb9-4748-2c7f4a124842'
IMU_CHAR = 'd5060402-a904-deb9-4748-2c7f4a124842'
ALL_EMG_CHRCS = (EMG_CHAR1, EMG_CHAR2, EMG_CHAR3, EMG_CHAR4)
VIB_STRONG = [0x3, 0x1, 0x1]
EMG_MODE = [0x1, 0x3, 0x3, 0x1, 0x2]


class Myo(RapidAPI):
    """
    Myo armband API
    """
    battery_level = Read(BATTERY_CHRC)
    vibrate = Write(CONTROL_SERVICE, accept=[VIB_STRONG])
    set_mode = Write(CONTROL_SERVICE, accept=[EMG_MODE])
    subscribe_to_emg = Notify(ALL_EMG_CHRCS)


def main():
    myo = Myo('D4:D4:76:6D:97:63')
    print(myo.battery_level)
    myo.vibrate(VIB_STRONG)
    myo.set_mode(EMG_MODE)
    stop_notify = myo.subscribe_to_emg(lambda vals: print(vals))
    stop_notify()
    myo.con.close()


if __name__ == '__main__':
    main()
