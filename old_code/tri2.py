from PCA9685 import Servo
from math import pi, radians, sqrt, asin, acos, atan, tan, cos, atan, sin
import time


robot=Servo(27,26)
def hypot(x,y):
  return sqrt(x*x + y*y)

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
  

  
a0 = 26.5  
a1 = 48
a2 = 67  
  
def cal_angles(x, y, z):
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

def rotate_x(rads, x, y, z):
  x = (  (x + 24) * cos(rads)  ) - 24
  z =  z - (  (x+24) * sin(rads)   )
  return (x,y,z)
  
  
  
try:
 rads = -pi/8
 while True:
  
  while rads < pi/8:
	leg_l = rotate_x(rads, 50,35,70)
	leg_r = rotate_x(-rads, 50,35,70)
	body_position[0] = cal_angles(leg_l[0], leg_l[1], leg_l[2])    
	body_position[1] = cal_angles(leg_r[0], leg_r[1], leg_r[2])    
	body_position[2] = cal_angles(leg_l[0], -leg_l[1], leg_l[2])   
	body_position[3] = cal_angles(leg_r[0], -leg_r[1], leg_r[2])    
	update()
	time.sleep(0.001)
	rads+=0.005
  while rads > -pi/8:
	leg_l = rotate_x(rads, 45,30,70)
	leg_r = rotate_x(-rads, 45,30,70)
	body_position[0] = cal_angles(leg_l[0], leg_l[1], leg_l[2])    
	body_position[1] = cal_angles(leg_r[0], leg_r[1], leg_r[2])    
	body_position[2] = cal_angles(leg_l[0], -leg_l[1], leg_l[2])   
	body_position[3] = cal_angles(leg_r[0], -leg_r[1], leg_r[2])    
	update()
	time.sleep(0.001)
	rads-=0.005	

finally: 
  body_position = [[0, 0, 0], [0,0, 0], [0, 0, 0], [0, 0, 0]]
  update()  
  robot.deinit()