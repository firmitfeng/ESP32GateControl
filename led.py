from machine import Pin
from time import sleep, sleep_ms

PNP=0
NPN=1

class Led():

    def __init__(self, pin_no, name='LED', mode=NPN, debug=False):
        self.pin_no = pin_no
        self.debug = debug
        self.name = "%s_%s" % (name, pin_no)
        self.pin = Pin(pin_no, Pin.OUT)
        self.mode = mode
        self.status = False

    def on(self):
        if self.debug:
            print(self.name, 'On')
        self.pin.value(1)
        self.status = True

    def off(self):
        if self.debug:
            print(self.name, 'Off')
        self.pin.value(0)
        self.status = False

    def toogle(self, interval=5):
        self.on()
        sleep(interval)
        self.off()

    def val(self):
        return self.pin.value()

    def blink(self, times=1, interval=0.3, sleep_secs=0.3):
        for i in range(times):
            self.toogle(interval)
            sleep(sleep_secs)

if __name__ == '__main__':
    LED_PIN = 25
    led = Led(LED_PIN, name='Test_LED', debug=True)
    led.blink(3,0.5,0.5)





