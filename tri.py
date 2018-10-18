from PCA9685 import Servo
from math import pi, radians, sqrt, asin, acos, atan, tan, cos, atan
import time


a1 = 48
a2 = 67
diff =  a2**2 - a1**2 
de90 = pi/2

def set_degrees (servo, degrees):
  robot.set_servo(radians(degrees), servo) 

calbration = ((0.8, 0.1, -0.5), (-0.7, 0.1, 0.25),(-0.8, -0.1, 0.4), (0.7, -0.1, -0.7))
body_direction = ((-1, -1, 1), (1, 1, -1), (-1, 1, -1), (1, -1, 1))
body_servo = ((2,1,0), (13, 14, 15), ( 6, 5, 4), (9, 10, 11))
body_position = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]

def update():
  for joint in range(3):
    for leg in range (4):
	  robot.set_servo(body_position[leg][joint] * body_direction[leg][joint]+ calbration[leg][joint], body_servo[leg][joint] )

def hypot(x,y):
  return sqrt(x*x + y*y)
	  
def angles(x, y, z):  
  theda9 = atan(y/x)
  x = hypot(x,y)
  xcal = x- 26.5
  l = hypot(xcal,z)  
  t1 = (l**2 - diff)/ (2 * l) 
  if t1 < a1 :
    theda3 = asin(t1/a1) + asin((l-t1)/a2) - de90
    theda4 = acos(t1/a1) - atan(z/xcal)
  else : 
    
	theda3 = de90
	theda4 = -atan(y/xcal)
  return (theda9, theda4, theda3 )


try:
  
    
finally: robot.deinit() #deinit the I2C bus