from math import atan2, asin, pi, sin, cos, acos, sqrt, degrees

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

    def body_xyz(self, x, y, z, roll, pitch, yaw):
        pass
    
    def body_rpy(self, roll, pitch, yaw):
        pass
    
    def set_leg(self, id, x, y, z):
        [t1, t2, t3] = self.leg_ik(x,y,z)
        self.set_servo(0, t1)
        self.set_servo(1, t2)
        self.set_servo(2, t3)

    def leg_ik_deg(self, x, y, z):
        return [degrees(x) for x in self.leg_ik(x,y,z)]

    def leg_ik(self, x, y, z):
        t = atan2(y, x) + pi/2
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

        return [t1, t2, t3]

if __name__ == "__main__":
    bot = None
    spi = Spider(bot)
    print(spi.leg_ik_deg(120, 0, 10))
