from math import atan2, asin, pi, sin, cos, acos, sqrt, degrees
import time

# to allow importing on non micropython systems
try:
    const(10)
except:
    const = lambda x: x

l1 = const(25)
l2 = const(48)
l3 = const(75)
l4 = const(10)

bw = const(47)
bl = const(88)

class Spider(object):

    def __init__(self, bot):
        self.bot = bot
        self.set_servo = bot.servo.set_rad

    def body_xyzrpy(self, x, y, z, roll, pitch, yaw):
        pass

    def body_xyz(self, x, y, z):
        
        self.set_leg(0, 70-x, -50-y, z)
        self.set_leg(1, 70-x, 50-y, z)
        self.set_leg(2, -70-x, 50-y, z)
        self.set_leg(3, -70-x, -50-y, z)
    
    def body_rpy(self, roll, pitch, yaw):
        pass
    
    def set_leg(self, id, x, y, z):
        
        # do coordinate system transformations for different legs
        z = -z
        if id == 0:
            o_r = 1
            t23 = 1
        elif id == 1:
            o_r = -1
            t23 = -1
        elif id == 2:
            x = -x
            y = -y
            o_r = 1
            t23 = 1
        elif id == 3:
            x = -x
            y = -y
            o_r = -1
            t23 = -1

        # do inverse kinematics
        [t1, t2, t3] = self.leg_ik(x,y,z,o_r=o_r,t23=t23)
        t3 = -t3

        # write to servos
        r_id = id*4
        self.set_servo(r_id, t3)
        r_id += 1
        self.set_servo(r_id, t2)
        r_id += 1
        self.set_servo(r_id, t1)

    def leg_ik_deg(self, x, y, z, **kwargs):
        return [degrees(x) for x in self.leg_ik(x,y,z, **kwargs)]

    def leg_ik(self, x, y, z, o_r=1, t23=1):
        t = atan2(y, x) + o_r * pi/2
        u = [cos(t) * l4, sin(t) * l4]

        v1 = [x+u[0], y+u[1]]
        v1_old_mag = sqrt(v1[0]**2 + v1[1]**2)
        v1_factor = l1 / v1_old_mag
        v1_mag = v1_old_mag - l1
        v1 = [v1[0]*v1_factor, v1[1]*v1_factor]

        t1 = atan2(v1[1], v1[0])

        l = sqrt(v1_mag**2 + z**2)

        t_internal = acos((l2**2 + l3**2 - l**2)/(2 * l2 * l3))
        t_depression = atan2(z, v1_mag)
        triangle_upper = asin( l3 * sin(t_internal) / l )

        t2 = t_depression - triangle_upper
        t3 = pi - t_internal

        t2 = t23 * t2
        t3 = t23 * t3

        return [t1, t2, t3]

if __name__ == "__main__":
    bot = None
    spi = Spider(bot)
    print(spi.leg_ik_deg(120, 0, 10))
