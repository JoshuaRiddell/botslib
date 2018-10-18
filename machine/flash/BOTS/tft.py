import display
from time import sleep
from machine import PWM
from struct import pack

# constants used for accessing registers on screen
_SWRESET = const(0x01) # Software Reset 
_SLPOUT = const(0x11) # Sleep Out
_COLMOD = const(0x3A) # Colour Mode
_DISPON = const(0x29) # Display On
_MADCTL = const(0x36) # Memory Data Access
_CASET = const(0x2A) # Column Address Set
_PASET = const(0x2B) # Page Address Set

class Tft(display.TFT):
    "Bots specific TFT wrapper for display library."

    def __init__(self, backlight_pin, default_brightness=30):
        super().__init__()
        self.backlight = PWM(backlight_pin, freq=200, duty=default_brightness)

    def init(self, tft_type, **kwargs):
        super().init(tft_type, **kwargs)

        self.tft_writecmd(_SWRESET)  #Software Rest
        sleep(0.2)
        self.tft_writecmd(_SLPOUT)  #sleep out
        sleep(0.2)
        self.tft_writecmddata(_COLMOD, bytearray([0x05])) #set 16 bit color
        self.tft_writecmd(_DISPON)  #Display on
        self.tft_writecmddata(_MADCTL, bytearray([0b10110000])) #this is orienation for my screen
        self.tft_writecmddata(_CASET, pack(">HH", 0, 159)) #set width from 0 to 159
        self.tft_writecmddata(_PASET, pack(">HH", 0, 127)) #set height from  0 to 127

    def brightness(self, percentage):
        self.backlight.duty(percentage)

    def deinit(self):
        pass
        # self.backlight.deinit()
