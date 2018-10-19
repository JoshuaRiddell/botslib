import display
from machine import I2C, PWM, ADC
from time import sleep, sleep_us
from struct import pack
from math import pi, floor

BATTERY_SENSE = const(35)
I2C_SDA = const(27)
I2C_SCL = const(26)

TFT_WIDTH = const(160)
TFT_HEIGHT = const(128)
MISO = const(19)
MOSI = const(21)
CLK = const(18)
CS = const(5)
BACKLIGHT_PIN = const(23)

ASSETS_PATH = "/flash/BOTS/assets"
SPLASH_JPG = ASSETS_PATH + "/bots160x120.jpg"
STATUS_JPG = ASSETS_PATH + "/bots_man.jpg"


class Bot(object):
    "Class to handle all Bot board peripherals."

    def __init__(self):
        "Initialise all peripherals."

        # init the tft and display splash screen
        self.tft = Tft(BACKLIGHT_PIN)
        self.tft.init(self.tft.GENERIC,
                      width=TFT_WIDTH,
                      height=TFT_HEIGHT,
                      miso=MISO,
                      mosi=MOSI,
                      clk=CLK,
                      cs=CS,
                      dc=22,
                      color_bits=16)
        self.tft.image(0, 0, SPLASH_JPG)

        # init battery adc measurement
        self.battery = Battery(BATTERY_SENSE)

        # init i2c
        self.i2c = I2C(0, sda=I2C_SDA, scl=I2C_SCL, speed=1000000)
        self.servo = Servo(self.i2c)

    def set_ap_if(self, ap_if):
        # save the ap object for later
        self.ap_if = ap_if

    def update_display_status(self):
        # finally show the tft status screen
        self.tft.image(0, 0, STATUS_JPG)

        self.tft.text(25, 7, "BATTERY = " +
                      str(self.battery.read())+"V", color=self.tft.RED)
        self.tft.text(25, 22, "IP = " +
                      str(self.ap_if.ifconfig()[0]), color=self.tft.RED)

    def deinit(self):
        "Deinit all peripherals."

        print("Deiniting all peripherals (apart from networking)...")
        self.battery.deinit()
        self.servo.deinit()
        self.i2c.deinit()
        self.tft.deinit()


class Battery(ADC):
    "Define the battery class as an extension of the ADC."

    def __init__(self, pin):
        "Setup the ADC pin for reading battery voltage."
        super().__init__(pin)
        self.atten(self.ATTN_11DB)

    def read(self):
        "Read pin voltage and scale to battery voltage."

        voltage = super().read()*0.0057
        voltage = floor(voltage*10)/10
        return voltage


class Servo:
    "Class for handling PWM servo driver through the PCA9685 chip."

    rad2off = 200/(pi/2)
    maximum_angle = 1.22173

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
        if (abs(angle) > self.maximum_angle):
            return

        on_time = servo * 200
        off_time = (servo * 200) + 340 - (int(angle * self.rad2off))
        self.i2c.writeto_mem(self.slave, 0x06 + (servo*4),
                             pack('<HH', on_time, off_time))

    def set_deg(self, servo, angle):
        "Set the position of servo index to angle in degrees."
        self.set_rad(servo, angle*pi/180)

    def deinit(self):
        self.reset_position()


# constants used for accessing registers on screen
_SWRESET = const(0x01)  # Software Reset
_SLPOUT = const(0x11)  # Sleep Out
_COLMOD = const(0x3A)  # Colour Mode
_DISPON = const(0x29)  # Display On
_MADCTL = const(0x36)  # Memory Data Access
_CASET = const(0x2A)  # Column Address Set
_PASET = const(0x2B)  # Page Address Set


class Tft(display.TFT):
    "Bots specific TFT wrapper for display library."

    def __init__(self, backlight_pin, default_brightness=30):
        super().__init__()
        self.backlight = PWM(backlight_pin, freq=200, duty=default_brightness)

    def init(self, tft_type, **kwargs):
        super().init(tft_type, **kwargs)

        self.tft_writecmd(_SWRESET)  # Software Rest
        sleep(0.2)
        self.tft_writecmd(_SLPOUT)  # sleep out
        sleep(0.2)
        self.tft_writecmddata(_COLMOD, bytearray([0x05]))  # set 16 bit color
        self.tft_writecmd(_DISPON)  # Display on
        # this is orienation for my screen
        self.tft_writecmddata(_MADCTL, bytearray([0b10110000]))
        self.tft_writecmddata(_CASET, pack(">HH", 0, 159)
                              )  # set width from 0 to 159
        # set height from  0 to 127
        self.tft_writecmddata(_PASET, pack(">HH", 0, 127))

    def brightness(self, percentage):
        self.backlight.duty(percentage)

    def deinit(self):
        super().deinit()
        self.backlight.deinit()
