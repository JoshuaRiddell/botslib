import display
from machine import I2C, PWM, ADC, Pin, Timer
from time import sleep, sleep_us
from struct import pack
from math import pi, floor, degrees, radians
from os import listdir

try:
    import cbots
    CBOTS_LOADED = True
except ImportError:
    # does not exist
    CBOTS_LOADED = False

# pin definitions
BATTERY_SENSE = const(35)
I2C_SDA = const(27)
I2C_SCL = const(26)
BOOT_PIN = const(0)
USER_PIN = const(25)

# TFT definitions
TFT_WIDTH = const(160)
TFT_HEIGHT = const(128)
MISO = const(19)
MOSI = const(21)
CLK = const(18)
CS = const(5)
BACKLIGHT_PIN = const(23)

# battery low voltage cutoff threshold
LVC = 6.4

# servos definitions
NUM_SERVOS = const(16)

# paths
ASSETS_PATH = "/flash/assets"
SPLASH_JPG = ASSETS_PATH + "/bots160x120.jpg"
STATUS_JPG = ASSETS_PATH + "/bots_man.jpg"

SERVO_CALIBRATION_FILE = "calib.csv"

class Bot(object):
    "Class to handle all Bot board peripherals."

    def __init__(self, status_update_timer=0, status_update_rate=1000, use_cbots=False):
        "Initialise all peripherals."
        
        # momentary switches on the board
        self.boot_sw = Switch(BOOT_PIN)
        self.user_sw = Switch(USER_PIN)

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

        # init battery voltage measurement
        self.battery = Battery(BATTERY_SENSE)

        # init i2c
        self.i2c = I2C(0, sda=I2C_SDA, scl=I2C_SCL, speed=1000000)
        self.servo = Servo(self.i2c)

        # set wlan to be none at first
        self.wlan = None

        # setup periodic timer for status image updating
        self.update_display_status(initial=True)
        self.status_tm = Timer(status_update_timer)
        self.status_tm.init(
            period=status_update_rate,
            mode=self.status_tm.PERIODIC,
            callback=lambda timer: self.update_display_status()
        )

        if use_cbots:
            self.setup_cbots()
    
    def setup_cbots(self):
        "Setup required configuration for use of cbots library."
        if not CBOTS_LOADED:
            raise ValueError("cbots_used set to true but cbots library was not found.")

        # tell them the i2c object we are using
        cbots.set_i2c(self.i2c)

        # set the servo calibration
        cbots.set_servo_zero_pos(self.servo.zero_pos)

        # change our write servo function to be the c implementations
        self.servo.set_rad = cbots.set_servo_rad

    def set_wlan(self, wlan):
        # save the ap object for later if we want to display the status
        self.wlan = wlan

    def update_display_status(self, initial=False):
        "Show the status of the bot on the TFT display."

        if initial:
            self.tft.image(0, 0, STATUS_JPG)

        batt = self.battery.read()
        if batt < LVC:
            col = self.tft.RED
        else:
            col = self.tft.GREEN

        self.tft.text(25, 40, "BATT " + str(batt) + "V  ", color=col)

        if self.wlan is None:
            self.tft.text(25, 55, "IP     NO CONNECT", color=self.tft.RED)
        else:
            self.tft.text(25, 55, "IP     " +
                        str(self.wlan.ifconfig()[0]), color=self.tft.GREEN)

    def deinit(self):
        "Deinit all peripherals."

        print("Deiniting all peripherals (apart from networking)...")
        self.battery.deinit()
        self.servo.deinit()
        self.i2c.deinit()
        self.tft.deinit()
        self.boot_sw.deinit()
        self.user_sw.deinit()

    def __del__(self):
        self.deinit()


class Switch(Pin):
    def __init__(self, pin):
        super().__init__(pin, self.IN, self.PULL_UP)

    def pressed(self):
        return not self.value()


class Battery(ADC):
    "Define the battery class as an extension of the ADC."

    def __init__(self, pin):
        "Setup the ADC pin for reading battery voltage."
        super().__init__(pin)
        self.atten(self.ATTN_11DB)

    def read(self):
        "Read pin voltage and scale to battery voltage."

        voltage = super().read()*0.0057
        voltage = floor(voltage*100)/100
        return voltage


class Servo(object):
    "Class for handling PWM servo driver through the PCA9685 chip."

    rad2off = 200/(pi/2)
    maximum_angle = 1.5708

    zero_pos = [0] * NUM_SERVOS
    current_pos = [0] * NUM_SERVOS

    def __init__(self, i2c, slave=0x40):
        # save i2c things for later
        self.slave = slave
        self.i2c = i2c

        # try and load calibration file
        if not SERVO_CALIBRATION_FILE in listdir('.'):
            print("No calibration.csv found, using 0 calibration.")
        else:
            self.load_calib_from_file(SERVO_CALIBRATION_FILE)
        
        # init the PWM generating chip
        self._init_pca()

    def load_calib_from_file(self, filename):
        with open(filename, 'r') as fd:
            for line in fd.readlines():
                vals = line.strip().split(',')

                vals[0] = int(vals[0])
                vals[1] = float(vals[1])

                self.zero_pos[vals[0]] = vals[1]

    def set_calib(self, zero_pos):
        self.zero_pos = zero_pos[:]

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
        for servo in range(NUM_SERVOS):  # set all servos to popsition 0
            self.set_rad(servo, 0)

    def get_all(self):
        return self.current_pos

    def get_rad(self, servo):
        return self.current_pos[servo]

    def get_deg(self, servo):
        return degrees(self.get_rad(servo))

    def set_deg_raw(self, servo, angle):
        "Set the position of servo index to angle in degrees."
        self.set_rad_raw(servo, radians(angle))

    def set_rad_raw(self, servo, angle):

        self.current_pos[servo] = angle

        on_time = servo * 200
        off_time = (servo * 200) + 340 - (int(angle * self.rad2off))
        self.i2c.writeto_mem(self.slave, 0x06 + (servo*4),
                             pack('<HH', on_time, off_time))

    def set_rad(self, servo, angle):
        "Set the position of servo index to angle in radians."
        angle += self.zero_pos[servo]

        if (abs(angle) > self.maximum_angle):
            print("servo index: " + str(servo) + ", out of range")
            return
        
        self.current_pos[servo] = angle

        on_time = servo * 200
        off_time = (servo * 200) + 340 - (int(angle * self.rad2off))
        self.i2c.writeto_mem(self.slave, 0x06 + (servo*4),
                             pack('<HH', on_time, off_time))

    def set_deg(self, servo, angle):
        "Set the position of servo index to angle in degrees."
        self.set_rad(servo, radians(angle))

    def deinit(self):
        # write 0 ontime to all servos to turn them off
        for servo in range(NUM_SERVOS):
            self.i2c.writeto_mem(self.slave, 0x06 + (servo*4),
                                 pack('<HH', 0, 0))


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
