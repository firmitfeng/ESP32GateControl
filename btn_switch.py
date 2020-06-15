from machine import Pin
from time import sleep, sleep_ms

class BtnSwitch():
    
    def __init__(self, pin_no, pull_up_down=Pin.PULL_UP, debug=False):
        self.pin_no = pin_no
        self.pull_up_down = pull_up_down
        self.debug = debug
        self.btn = Pin(pin_no, Pin.IN, pull_up_down)


    def __del__(self):
        pass


    def add_event_detect(self, callback, trigger=Pin.IRQ_RISING):
        self.btn.irq(trigger=trigger, handler=callback)


    def wait_pin_change(self, wait_ms=20):
        # wait for pin to change value 等待引脚改变值
        # it needs to be stable for a continuous 20ms 引脚值需在连续20毫秒内保持稳定
        count = 0

        while count < wait_ms:
            if not self.btn.value():
                count += 1
            else:
                return False
            sleep_ms(1)
        return True

    
    def is_pressed(self):
        return self.wait_pin_change()


if __name__ == '__main__':
    from led import Led

    LED_PIN = 25
    BTN_PIN = 22

    led = Led(LED_PIN)
    btn = BtnSwitch(BTN_PIN)

    try:
        while True:
            btn_motion = False
            if btn.is_pressed():
                print('Key Pressed', btn.pin_no)
                led.blink()
    except KeyboardInterrupt:
        print("Bye")
