from ustruct import pack
from math import pi

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
