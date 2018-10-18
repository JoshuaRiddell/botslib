from . import servo
from . import battery
from . import tft

class Bot(object):

    def __init__(self):
        self.battery = battery.Battery(35)

        print("Hello world.")

        self.peripherals = [self.battery]

    def deinit(self):
        print("Deiniting all peripherals...")
        for peripheral in peripherals:
            self.peripherals.deinit()