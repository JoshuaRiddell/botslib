from machine import Pin, SPI
import time
from ustruct import pack, unpack
from array import array


SWRESET = 0x01
SLPIN = 0x10
SLPOUT = 0x11
PTLON = 0x12
NORON = 0x13
INVOFF = 0x20
INVON = 0x21
DISPOFF = 0x28
DISPON = 0x29
CASET = 0x2A
RASET = 0x2B
RAMWR = 0x2C
RAMRD = 0x2E
PTLAR = 0x30
MADCTL = 0x36
COLMOD = 0x3A
FRMCT1 = 0xB1
FRMCT2 = 0xB2
FRMCT3 = 0xB3
INVCTR = 0xB4
DISSET = 0xB6
PWRCT1 = 0xC0
PWRCT2 = 0xC1
PWRCT3 = 0xC2
PWRCT4 = 0xC3
PWRCT5 = 0xC4
VMCTR1 = 0xC5
PWRCT6 = 0xFC
GAMCTP = 0xE0
GAMCTN = 0xE1


dc = Pin(22, Pin.OUT)
spi = SPI(1, sck=18, miso=19, mosi=21, cs=5, baudrate = 26000000)


data_SNESS = Pin(27, Pin.IN)
latch = Pin(26, Pin.OUT)
clock = Pin(25, Pin.OUT)

text_file = open ("text.fnt", "rb")
text_buff = bytearray(735)
text_buff = text_file.read(736)
text_file.close

def read_SNESS():
  while True :
    buttons= [1] * 8
    latch.value(0)   
    clock.value(1)
    latch.value(1)
    time.sleep_us(1)
    latch.value(0)
    for loops in range(8):
      buttons [loops] = data_SNESS.value()
      clock.value(0)
      clock.value(1)
    return buttons

def send_spi(data, is_data):
    dc.value(is_data)
    spi.write(data)
  
  
def init():
  send_spi(bytearray([SWRESET]), False)
  time.sleep(0.2)
  send_spi(bytearray([SLPOUT]), False)
  time.sleep(0.2)
  send_spi(bytearray([COLMOD]), False)
  send_spi(bytearray([0x05]),True)
  send_spi(bytearray([DISPON]), False)
  send_spi(bytearray([MADCTL]), False)
  send_spi(bytearray([0b11111000]),True)
  send_spi(bytearray([CASET]),False)            # set Column addr command 
  send_spi(pack(">HH", 0, 159), True)  # x_end 
  send_spi(bytearray([RASET]),False)            # set Row addr command        
  send_spi(pack(">HH", 0, 127), True) 


def set_window(x0, y0, width, height):	      
    x1=x0+width-1
    y1=y0+height-1		
    send_spi(bytearray([0x2A]),False)            # set Column addr command		
    send_spi(pack(">HH", x0, x1), True)  # x_end 
    send_spi(bytearray([0x2B]),False)            # set Row addr command        
    send_spi(pack(">HH", y0, y1), True)  # y_end        
    send_spi(bytearray([0x2C]),False)

def fill_screen(colour):
  send_spi(bytearray([RAMWR]), False)
  for i in range (64):
    send_spi(pack('<H',colour)*320,True)

def load_image(file):
  send_spi(bytearray([RAMWR]), False)
  chunk_size = 1024
  BMP_file = open(file , "rb")
  data = BMP_file.read(54)
  data = BMP_file.read(chunk_size)
  while len(data)>0 :
      send_spi(data,True)
      data = BMP_file.read(chunk_size)
  BMP_file.close()

def dump_data(data):
  send_spi(bytearray([RAMWR]), False)
  send_spi(data, True)


def put_text(xpos, ypos, scale, text_graphics): 

	#bk = self.bit24_to_bit16(background_colour)
	#fg = self.bit24_to_bit16(foreground_colour)
	#color = (pack('>H',0x1f1f), pack('>H',0xf0f0))
	
	for counter, charter in enumerate(text_graphics):      
	  pos = 0
	  set_window(xpos + (8*scale* counter), ypos, 8* scale, 8 * scale)
	  buff = bytearray(128*scale**2) 
	  send_spi(bytearray([RAMWR]), False)	
	  letter = []
	  for i in range(8): 
	    letter.append(text_buff[(ord(charter)-32)*8+i])
	  coun = -1
	  for lines in reversed(letter):	    
		coun +=1		
		for times in range(scale):        
		  mask = 0b10000000        
		  for bits in range(8) :		    
			if mask & lines > 0 : 
			  buff[pos:pos+scale*2] = array('B', [0xf0,0xf0]*scale)
			  pos += scale*2		    
			else :			   
			   possi = xpos*2 + ypos*320 + counter*16*scale + bits*2*scale + coun*320*scale + times*320
			   buff[pos:pos+scale*2] = buffy [possi:possi+scale*2]  
			   pos += scale*2 		    
			mask = mask >> 1
	  send_spi(buff, True)    
	return (xpos, ypos, len(text_graphics) * 8 * scale, 8 * scale)

def restore_image(box):     
	chunk_size = box[2] * 2     
	set_window(box[0], box[1], box[2], box[3])
	send_spi(bytearray([RAMWR]), False)    
	for looping in range (box[3]):
	  possi  = box[0] * 2 + (box[1] + looping) * 160*2      
	  data = buffy[possi:possi+chunk_size]    
	  send_spi(data,True) 	


	

	
init()

buffy = bytearray(40960)
BMP_file = open('bot16.bmp' , "rb")
BMP_file.seek(54)
buffy = BMP_file.read(40960)

dump_data(buffy)

BMP_file.close()
	
size = 1
x=0
y=0
blah = put_text(x,y,1,'BOTS')
chnage = False

try: 
  while True:
   buttons = read_SNESS()
   if not buttons[2]:     
	 size-=1
	 if size < 1 : size = 1
	 chnage = True	 
   if not buttons[3]:     
	 size+=1
	 if size > 4: size = 4
	 chnage = True
   if not buttons[7]:      
	 x+=(5+size)
	 chnage = True
   if not buttons[6]:      
	 x-=(5+size)
	 if x < 0: x=0
	 chnage = True
   if not buttons[5]:      
	 y-=(5+size)
	 if y < 0: y =0
	 chnage = True
   if not buttons[4]:      
	 y+=(5+size)
	 chnage = True
   if chnage:     
	 restore_image(blah)     
	 blah = put_text(x,y,size,'BOTS')
	 time.sleep(0.1)
	 chnage = False


#

finally:
  del buffy
  del text_buff
  spi.deinit()
