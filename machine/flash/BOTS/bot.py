from machine import I2C

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

SPLASH_JPG = "/flash/BOTS/assets/bots160x120.jpg"

class Bot(object):
    "Class to handle all Bot board peripherals."

    def __init__(self):
        "Initialise all peripherals."
        
        self.battery = battery.Battery(BATTERY_SENSE)

        self.i2c = I2C(0, sda=I2C_SDA, scl=I2C_SCL)

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
        
        # self.servo = servo.Servo(i2c)

        print("Hello world.")

    def deinit(self):
        "Deinit all peripherals."

        print("Deiniting all peripherals...")
        self.battery.deinit()
        self.i2c.deinit()
        self.tft.deinit()
        # self.servo.deinit()
