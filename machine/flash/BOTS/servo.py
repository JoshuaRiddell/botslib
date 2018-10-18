from ustruct import pack
from math import pi
from time import sleep_us


class Servo:
    "Class for handling PWM servo driver through the PCA9685 chip."

    rad2off = 200/(pi/2)

    def __init__(self, i2c, slave=0x40):
        # save i2c things for later
        self.slave = slave
        self.i2c = i2c

        # init the PWM generating chip
        self._init_pca()
        self.reset_position()

    def _init_pca(self):
        "Initialise the PCA9685 chip."
        self.i2c.writeto_mem(self.slave, 0x00, b'\x10')  # set mode1 to sleep
        sleep_us(500)
        prescale = int((25000000 / (4096*50))+0.5)
        self.i2c.writeto_mem(self.slave, 0xfe, pack(
            'B', prescale))  # setprescale
        self.i2c.writeto_mem(self.slave, 0x00, b'\xa1')  # set mode1
        sleep_us(500)

    def reset_position(self):
        "Reset all servo positions to 0 degrees."
        r = range(16)
        f = self.set_rad
        for servo in r:  # set all servos to popsition 0
            f(servo, 0)

    def set_rad(self, servo, angle):
        "Set the position of servo index to angle in radians."
        off_time = 340 - (int(angle * self.rad2off))
        self.i2c.writeto_mem(self.slave, 0x08 + (servo*4),
                             pack('<H', off_time))

    def set_deg(self, servo, angle):
        "Set the position of servo index to angle in degrees."
        self.set_rad(servo, angle*pi/180)

    def deinit(self):
        self.reset_position()
