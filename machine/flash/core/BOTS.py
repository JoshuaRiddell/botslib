import time
from ustruct import pack
from math import pi, floor
from machine import ADC


#setup analog to digital converter to read bat voltage
bat=ADC(35)
bat.atten(bat.ATTN_11DB)

def read_battery(): 
  voltage = bat.read()*0.0057
  voltage = floor(voltage*10)/10 
  return voltage 
  
  
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


class Servo:
  def __init__(self, i2c_bus, slave=0x40):    
	self.slave = slave	
	self.i2c = i2c_bus    
	self.i2c.writeto_mem(slave, 0x00, b'\x10') #set mode1 to sleep    
	time.sleep_us(5)    
	prescale = int((25000000/ (4096*50))+0.5)    
	self.i2c.writeto_mem(slave, 0xfe, pack('B',prescale)) #setprescale    
	self.i2c.writeto_mem(slave, 0x00, b'\xa1') #set mode1 	
	time.sleep_us(5)    
	self.step = 200/(pi/2) #step size for radians	
	for servo in range(16):  #set all servos to popsition 0    
	  on_time = servo*220      
	  off_time = on_time + 340	  
	  self.i2c.writeto_mem(self.slave, 0x06 + (servo*4), pack('<HH', on_time, off_time))

  #servo positions r set in radians not degress
  def set_servo(self, pos, servo):
	off_time = (servo * 220) + 340 - (int(pos * self.step))     
	self.i2c.writeto_mem(self.slave, 0x08 + (servo*4), pack('<H',off_time))
	
