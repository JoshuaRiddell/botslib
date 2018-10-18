import display, time
from micropython import const
from ustruct import pack
from machine import Pin, ADC, PWM
import network
from PCA9685 import Servo
from math import pi, radians, sqrt, asin, acos, atan, tan, cos, atan, sin, floor, hypot
from microWebSrv import MicroWebSrv


bl = PWM(23, freq=100, duty=0)
switch1 = Pin(25, Pin.IN, Pin.PULL_UP)
switch2 = Pin(0, Pin.IN, Pin.PULL_UP)
bat=ADC(35)
bat.atten(bat.ATTN_11DB)



_SWRESET = const(0x01) # Software Reset
_SLPOUT = const(0x11) # Sleep Out
_COLMOD = const(0x3A) # Colour Mode
_DISPON = const(0x29) # Display On
_MADCTL = const(0x36) # Memory Data Access
_CASET = const(0x2A) # Column Address Set
_PASET = const(0x2B) # Page Address Set

def tft_init(disp):
 disp.tft_writecmd(_SWRESET)  #Software Rest
 time.sleep(0.2)
 disp.tft_writecmd(_SLPOUT)  #sleep out
 time.sleep(0.2)
 disp.tft_writecmddata(_COLMOD, bytearray([0x05])) #set 16 bit color
 disp.tft_writecmd(_DISPON)  #Display on
 disp.tft_writecmddata(_MADCTL, bytearray([0b10110000])) #this is orienation for my screen
 disp.tft_writecmddata(_CASET, pack(">HH", 0, 159)) #set width from 0 to 159
 disp.tft_writecmddata(_PASET, pack(">HH", 0, 127)) #set height from  0 to 127

tft = display.TFT()
tft.init(tft.GENERIC, width=160, height=128, miso=19, mosi=21, clk=18, cs=5, dc=22, color_bits=16)
tft_init(tft)



def _acceptWebSocketCallback(webSocket, httpClient) :
  print("WS ACCEPT")
  webSocket.RecvTextCallback   = _recvTextCallback
  webSocket.RecvBinaryCallback = _recvBinaryCallback
  webSocket.ClosedCallback     = _closedCallback

def _recvTextCallback(webSocket, msg) :
  global roll
  global up_down
  global pitch

  type  = msg[0]
  val = int(msg[2:len(msg)])
  if type == "R": roll = (val - 50) * (pi/8) / 50.0
  if type == "P": pitch = (val - 50) * (pi/8) / 50.0
  if type == "U":  up_down = val//2 +40
	
    

  #webSocket.SendText("Reply for %s" % msg)


def _recvBinaryCallback(webSocket, data) :
  print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket) :
  print("WS CLOSED")
  


calbration = ((0.8, -0.3, -0.6), (-0.7, 0.1, 0.25),(-0.8, 0.1, 0.1), (0.7, -0.1, 0))
body_direction = ((-1, -1, 1), (1, 1, -1), (-1, 1, -1), (1, -1, 1))
body_servo = ((2,1,0), (13, 14, 15), ( 6, 5, 4), (9, 10, 11))
body_position = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
body_cartesian = [[50,35,70],[50,35,70],[50,-35,70],[50,-35,70]]

def update():
  for joint in range(3):
    for leg in range (4):
	  robot.set_servo(body_position[leg][joint] * body_direction[leg][joint]+ calbration[leg][joint], body_servo[leg][joint] ) 

def cal_angles(xyz):
  x = xyz[0]
  y = xyz[1]
  z = xyz[2]
  theda9 = atan(y/x)
  x = hypot(x,y) - 26.5
  l = hypot (x, z)
  if l < 115:
    t1 = (l**2 - 2185) / (2 * l) 
    t2 = l - t1  
    theda4 = acos(t1/48) - atan(z/x)
    theda3 = asin(t1/48) + asin(t2/67)- 1.571
  else:	
	theda3 = 1.571
	theda4 = - atan(z/x)
  return (theda9, theda4, theda3)  

def rotate_x(rads,xyz):
  x=xyz[0]
  y=xyz[1]
  z=xyz[2]
  x = ((x + 24) * cos(rads)) - 24
  z =  z - ((xyz[0]+24) * sin(rads))
  return (x,y,z)
  
def rotate_z(rads,xyz,di):
  x=xyz[0]
  y=xyz[1]
  z=xyz[2]
  y = ((y + di) * cos(rads)) - di
  z =  z - ((xyz[1]+di) * sin(rads))
  return (x,y,z)

def rot_x(rads, body):
	leg0 = rotate_x(rads , body[0])
	leg1 = rotate_x(-rads , body[1])
	leg2 = rotate_x(rads, body[2])
	leg3 = rotate_x(-rads, body[3])
	return (leg0, leg1, leg2, leg3)
	
def rot_y(rads, body):
	leg0 = rotate_z(rads , body[0],45)
	leg1 = rotate_z(rads , body[1],45)
	leg2 = rotate_z(rads, body[2],-45)
	leg3 = rotate_z(rads, body[3],-45)
	return (leg0, leg1, leg2, leg3)

def move_cartesian(body):
	body_position[0] = cal_angles(body[0])    
	body_position[1] = cal_angles(body[1])    
	body_position[2] = cal_angles(body[2])   
	body_position[3] = cal_angles(body[3])    
	update()	
  
def battery(): 
  voltage = bat.read()*0.0057
  voltage = floor(voltage*10)/10 
  return voltage 

def update_status():
  tft.set_bg(0x000000)
  voltage = battery()
  tft.text(40, 0, "BAT "+str(voltage)+"v")
  if not ap_if.active(): tft.text(40,15, 'AP off')
  else: tft.text(40,15, ap_if.ifconfig()[0])
  if not sta_if.isconnected(): tft.text(40,30, 'STA off')
  else: tft.text(40,30, sta_if.ifconfig()[0])
  if voltage < 7:
    tft.rect(10, 60, 150, 40, 0xff0000,0xff0000)


def menu(title, menu_list):
  tft.text(10,60, title)
  tft.set_bg(0xf00000)
  tft.text(25,80, menu_list[0])
  max = len(menu_list) 
  max_item = 1
  for items in range(max):    
	current = len(menu_list[items])
	if current > max_item : max_item = current 
  pos = 0
  old = 1
  new = 1
  old2 = 1
  new2 = 1
  while True :     
	new = switch1.value()
	if old != new and not new:
	  pos +=1
	  if pos > max -1 :  pos = 0
	  tft.text(25,80, menu_list[pos] + " " * (max_item - len(menu_list[pos])))	  
	old = new
	new2 = switch2.value()
	if old2 != new2 and not new2: break	  
	time.sleep(0.1)
  tft.rect(10, 60, 150, 40, 0,0)
  tft.set_bg(0x000000)
  return pos


  
try:
  ap_if = network.WLAN(network.AP_IF)
  sta_if = network.WLAN(network.STA_IF)
  tft.image(0, 0, 'bots160x120.jpg') #load image to test fuctionality 
  bl.duty(20)
  time.sleep(2)
  tft.clear()
  tft.image(0, 0, 'bots_man.jpg')
  update_status()
  pos  = menu( "Choose WiFi Mode", ["Acess Mode", "Station Mode", "Don't Connect"])  

  if pos==0:    
	tft.text(45,80, "Please wait")    
	ap_if.active(True)    
	ap_if.config(essid="Robot_Spider")	
	while not ap_if.active() : time.sleep(0.1)    
	network.telnet.start(user="micro",password="python", timeout=300)    
	network.ftp.start(user="micro",password="python",buffsize=1024,timeout=300)    
	print ("FTP status ", network.ftp.status())     
	print ("Telnet status ", network.telnet.status())    
	update_status()	    
	tft.rect(10, 60, 150, 40, 0,0)
    
  if pos == 1:
    tft.text(45,80, "Please wait") 
    sta_if.active(True)
    sta_if.connect('GingellHome_2.4GHz', 'dynamite')
    sta_if.ifconfig(('192.168.1.115', '255.255.255.0', '192.168.1.1', '192.168.0.1'))
    while not sta_if.isconnected() : time.sleep(0.1)
    network.telnet.start(user="micro",password="python", timeout=300)
    network.ftp.start(user="micro",password="python",buffsize=1024,timeout=300)
    print ("FTP status ", network.ftp.status())
    print ("Telnet status ", network.telnet.status())  
    tft.rect(10, 60, 150, 40, 0,0)
    update_status()
  
  


  roll = 0
  mws = MicroWebSrv()                                    # TCP port 80 and files in /flash/www
  mws.MaxWebSocketRecvLen     = 256                      # Default is set to 1024
  mws.WebSocketThreaded       = False                    # WebSockets without new threads
  mws.AcceptWebSocketCallback = _acceptWebSocketCallback# Function to receive WebSockets
  mws.Start() 

  rads = -pi/8
  time.sleep(2)
  robot=Servo(27,26)
  up_down = 70
  pitch  = 0
  
  while True:     
	body_cartesian = [[50,35,up_down],[50,35,up_down],[50,-35,up_down],[50,-35,up_down]]
	update_status()    
	new_body = rot_x(roll, body_cartesian)
	new_body = rot_y(pitch, new_body)
	move_cartesian(new_body)
	time.sleep(0.1)

  

finally:
  tft.deinit()
  bat.deinit()
  bl.value(0)
  body_position = [[0, 0, 0], [0,0, 0], [0, 0, 0], [0, 0, 0]]
  update()  
  robot.deinit()

