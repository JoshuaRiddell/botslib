import time, display, network
from machine import PWM, I2C, Pin
from math import pi, radians
from microWebSrv import MicroWebSrv
from BOTS import *  #import all custom code for the board


#create instance of acess point
ap_if = network.WLAN(network.AP_IF)

#create an instance of the I2C bus
I2C_bus = I2C(0, sda=27, scl=26)

#create instance of the servo driver
robot = Servo(I2C_bus)


#setup screen
tft = display.TFT()
tft.init(tft.GENERIC, width=160, height=128, miso=19, mosi=21, clk=18, cs=5, dc=22, color_bits=16)
tft_setup(tft)
#adjust value of duty to change backlight
backlight = PWM(23, freq=200, duty=25) 

#load animation images from pic directory
for pic in range(1,55): tft.image(0, 0, 'pic/'+str(pic)+'.jpg')
time.sleep(0.5)

#clear screen with black colour
tft.clear(0x000000)

#place open worm inage at bottom of screen
tft.image(0, 88, 'open_worm.jpg')

#display data on screen
tft.text(20, 10, "BATTERY = "+str(read_battery())+"v")
tft.text(18,25, "IP = " + str(ap_if.ifconfig()[0]))



def _acceptWebSocketCallback(webSocket, httpClient) :
  print("WS ACCEPT")
  webSocket.RecvTextCallback   = _recvTextCallback
  webSocket.RecvBinaryCallback = _recvBinaryCallback
  webSocket.ClosedCallback     = _closedCallback

def _recvTextCallback(webSocket, msg) : 
  robot.set_servo(radians(int(msg)), 0)
  #uncomment next line to send data back
  #webSocket.SendText("data to sedn"))


def _recvBinaryCallback(webSocket, data) :
  print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket) :
  print("WS CLOSED")

mws = MicroWebSrv()                                    # TCP port 80 and files in /flash/www
mws.MaxWebSocketRecvLen     = 256                      # Default is set to 1024
mws.WebSocketThreaded       = False                    # WebSockets without new threads
mws.AcceptWebSocketCallback = _acceptWebSocketCallback # call back function to receive WebSockets
mws.Start()   
  
while True: time.sleep(1)



