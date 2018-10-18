#constants used for accessing registers on screen
_SWRESET = const(0x01) # Software Reset 
_SLPOUT = const(0x11) # Sleep Out
_COLMOD = const(0x3A) # Colour Mode
_DISPON = const(0x29) # Display On
_MADCTL = const(0x36) # Memory Data Access
_CASET = const(0x2A) # Column Address Set
_PASET = const(0x2B) # Page Address Set

def tft_setup(disp):
 disp.tft_writecmd(_SWRESET)  #Software Rest
 time.sleep(0.2)
 disp.tft_writecmd(_SLPOUT)  #sleep out
 time.sleep(0.2)
 disp.tft_writecmddata(_COLMOD, bytearray([0x05])) #set 16 bit color
 disp.tft_writecmd(_DISPON)  #Display on
 disp.tft_writecmddata(_MADCTL, bytearray([0b10110000])) #this is orienation for my screen
 disp.tft_writecmddata(_CASET, pack(">HH", 0, 159)) #set width from 0 to 159
 disp.tft_writecmddata(_PASET, pack(">HH", 0, 127)) #set height from  0 to 127
