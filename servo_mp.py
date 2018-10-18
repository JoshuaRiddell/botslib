from PCA9685 import Servo
import time
from math import pi


try:
  robot=Servo(27,26) #PCA9585 is connected to pin 27,26
  #set fir 3 servos to psition -pi/2 (-90 degrees)
  robot.set_servo(-pi/2, 0)
  time.sleep(2)
  robot.set_servo(pi/2, 0)
  

finally: robot.deinit() #deinit the I2C bus