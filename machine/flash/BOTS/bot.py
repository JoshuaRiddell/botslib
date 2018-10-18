from machine import I2C
from time import sleep

from . import servo
from . import battery
from . import tft

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

    def __init__(self, ap_if):
        "Initialise all peripherals."
        
        # save the ap object for later
        self.ap_if = ap_if

        # init the tft and display splash screen
        self.tft = tft.Tft(BACKLIGHT_PIN)
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
        self.battery = battery.Battery(BATTERY_SENSE)

        # init i2c
        self.i2c = I2C(0, sda=I2C_SDA, scl=I2C_SCL)
        # self.servo = servo.Servo(i2c)

        # finally show the tft status screen
        self.tft.image(0, 0, STATUS_JPG)
        self.update_display_status()

    def update_display_status(self):
        batt_v = self.battery.read()
        self.tft.text(25, 7, "BATTERY = "+str(self.battery.read())+"V", color=self.tft.RED)
        self.tft.text(25, 22, "IP = " + str(self.ap_if.ifconfig()[0]), color=self.tft.RED)

    def deinit(self):
        "Deinit all peripherals."

        print("Deiniting all peripherals (apart from networking)...")
        self.battery.deinit()
        self.i2c.deinit()
        self.tft.deinit()
        # self.servo.deinit()
