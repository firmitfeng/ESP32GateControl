from os import uname
import machine
from machine import Pin
import network
# import utime
import usocket
import _thread

import mfrc522

from led import Led
from btn_switch import BtnSwitch
from keydb import KeyDB

IS_DEBUG = True

LED_PIN = 25
BTN_PIN = 22
DELAY_PIN = 21
BEEPER = 5

wlan = None
ip = ''
port = 10000
ssid = "1615"
passwd = "0.123456"


def resolved():
    '''
    刷卡验证成功、按钮、收到开门指令后，显示提示、开门动作
    '''

    if IS_DEBUG:
        print('\nAuthorization success.')
    led.blink()
    beeper.blink()
    delay.toogle()


def rejected():
    '''
    验证失败后，提示
    '''

    if IS_DEBUG:
        print('\nAuthorization error.')
    beeper.blink(3)


def timing(time_str):
    '''
    服务器校准时间
    '''
    time_list = [int(i) for i in time_str.split('-')]
    # init((year, month, mday, weekday, hour, minute, second, unknow[maybe ms, tzinfo]))
    rtc.init((time_list[0], time_list[1], time_list[2], 0, time_list[3],
              time_list[4], time_list[5], 0))
    print('timing commplete')
    print('Now is ' + getNowStr())


def getNowStr():
    # rtc.datetime return (year, month, mday, weekday, hour, minute, second, unknow[maybe ms])
    return '{0}-{1}-{2} {4}:{5}:{6} '.format(*rtc.datetime())
    # utime.localtime() return  (year, month, mday, hour, minute, second, weekday, yearday)
    # return '{}-{}-{} {}:{}:{} '.format(*utime.localtime())


def parse_data(data, sep='|'):
    return data.decode('utf-8').split(sep)


def convert_data(data):
    return data.encode('utf-8')


def init_wlan():
    global wlan
    global ip
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, passwd)
        while not wlan.isconnected():
            pass
        print('network config:', wlan.ifconfig())
    ip = wlan.ifconfig()[0]


def udp_ser(ip, port):
    # Create DGRAM UDP socket
    print('Init UDP server...')
    print(ip, port)
    s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
    s.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
    s.bind((ip, port))
    try:
        print('UDP server is ok!')
        while True:
            data, client_addr = s.recvfrom(1024)
            print('receive:', data, 'from:', client_addr)
            data_p = parse_data(data)
            if data_p[0] == u'timing':
                timing(data_p[1])
            elif data_p[0] == u'now':
                data = ''
            elif data_p[0] == u'put' and len(data_p) > 1:
                key_db.put(data_p[1])
                key_db.save()
            elif data_p[0] == u'remove' and len(data_p) > 1:
                key_db.remove(data_p[1])
                key_db.save()
            elif data_p[0] == u'empty':
                key_db.empty()
                key_db.save()
            elif data_p[0] == u'open':
                resolved()
            elif data_p[0] == u'reboot':
                print('got cmd: reboot udp server')
                raise Exception('reboot')
            elif data_p[0] == u'test':
                rejected()

            s.sendto(convert_data(getNowStr()) + data, client_addr)
    except Exception as e:
        print('Some error in UDP Server')
        import sys
        sys.print_exception(e)
        if (s):
            s.sendto(
                convert_data(getNowStr() + 'UDP Server error. msg: ' +
                             str(e) + '\nrecived: ') + data, client_addr)
    finally:
        s.close()
        print('UDP Server is closed.')
        print('Rebooting UDP server...')
        # create udp server thread
        _thread.start_new_thread(udp_ser, (ip, port))
        _thread.exit()


print('Init Electrical Lock with ESP32/ESP8622...')

# init rtc
rtc = machine.RTC()

# init mfrc reader
if uname()[0] == 'esp8266':
    rdr = mfrc522.MFRC522(0, 2, 4, 5, 14)
elif uname()[0] == 'esp32':
    rdr = mfrc522.MFRC522(18, 23, 19, 4, 2)
else:
    raise RuntimeError("Unsupported platform")

# init led, button etc
led = Led(LED_PIN, debug=IS_DEBUG)
btn = BtnSwitch(BTN_PIN, debug=IS_DEBUG)
delay = Led(DELAY_PIN, name='DELAY', debug=IS_DEBUG)
beeper = Led(BEEPER, name='BEEPER', debug=IS_DEBUG)

# init Key DB
key_db = KeyDB()

# init wlan
init_wlan()

lock = _thread.allocate_lock()

# create udp server thread
_thread.start_new_thread(udp_ser, (ip, port))

print('Complete.')

beeper.blink()

print("")
print("Working...")
print("")

try:
    while True:
        open_status = False

        # reading card
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                card_uid = raw_uid[0] + raw_uid[1] * 256 + raw_uid[2] * 100000
                if IS_DEBUG:
                    print("\nNew card detected")
                    print(card_uid)
                if key_db.query(card_uid):
                    open_status = True
                else:
                    rejected()

        # button press
        if btn.is_pressed():
            open_status = True
            if IS_DEBUG:
                print('\nKey Pressed', btn.pin_no)

        if open_status:
            resolved()

except KeyboardInterrupt:
    print("Bye")
