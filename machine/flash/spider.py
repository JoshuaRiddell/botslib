from math import atan2, asin, pi, sin, cos, acos, sqrt, degrees
import time

# to allow importing on non micropython systems
try:
    NULL = const(10)
except:
    print("const() not defined. Defining...")
    const = lambda x: x

l1 = const(25)
l2 = const(48)
l3 = const(75)
l4 = const(10)  # offset of foot to leg axis

bw = const(47)
bl = const(88)

class Spider(object):

    def __init__(self, bot):
        self.bot = bot
        self.set_servo = bot.servo.set_rad

        self.x = 0
        self.y = 0
        self.z = 0

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.legs = [
            [130, -50, -35],
            [130, 50, -35],
            [-130, 50, -35],
            [-130, -50, -35],
        ]

        self.body_offsets = [
            [bw/2,  -bl/2],
            [bw/2,  bl/2],
            [-bw/2, -bl/2],
            [-bw/2, bl/2],
        ]

        self.angle_signs = [
            -1, 1,  1,  0,
            1,  1,  1,  0,
            1,  1,  1,  0,
            1,  1,  1,  0,
        ]

    def xyzrpy(self, x, y, z, roll, pitch, yaw):
        self.x = x
        self.y = y
        self.z = z
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

        self.update_body()

    def xyz(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        self.update_body()
    
    def rpy(self, roll, pitch, yaw):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

        self.update_body()
    
    def update_body(self):
        [x, y, z] = self.body_to_leg(0)
        self.set_leg(0, x, y, z)

        # time.sleep(1)

        # [x, y, z] = self.body_to_leg(self.x, -self.y, self.z, self.roll, -self.pitch, self.yaw)
        # self.set_leg(1, x, y, z)

        # time.sleep(1)

        # [x, y, z] = self.body_to_leg(-self.x, -self.y, self.z, -self.roll, -self.pitch, -self.yaw)
        # self.set_leg(2, -x, y, z)

        # time.sleep(1)

        # [x, y, z] = self.body_to_leg(-self.x, self.y, self.z, -self.roll, self.pitch, self.yaw)
        # self.set_leg(3, -x, -y, z)

        # time.sleep(1)

    @staticmethod
    def rot2d(a, x, y):
        "Optimised 2D rotation matrix application."
        sa = sin(a)
        ca = cos(a)
        return [x*ca - y*sa, x*sa + y*ca]

    def body_to_leg(self, idx):
        # get offsets for this leg
        leg = self.legs[idx]
        x = leg[0] - self.y
        y = leg[1] - self.x
        z = leg[2] - self.z

        # apply body rotation
        x, z = self.rot2d(self.roll, x, z)
        z, y = self.rot2d(self.pitch, z, y)
        x, y = self.rot2d(self.yaw, x, y)

        # apply offsets due to frame
        o = self.body_offsets[idx]
        x = x - o[0]
        y = y - o[1]

        return [x, y, z]

    def set_leg(self, id, x, y, z):
        # do inverse kinematics
        t1, t2, t3 = self.leg_ik(x, y, z)

        print((x,y,z))
        print(self.leg_ik_deg(x,y,z))

        # write to servos
        r_id = id*4
        self.set_servo(r_id, t3 * self.angle_signs[r_id])
        r_id += 1
        self.set_servo(r_id, t2 * self.angle_signs[r_id])
        r_id += 1
        self.set_servo(r_id, t1 * self.angle_signs[r_id])

    def leg_ik_deg(self, x, y, z, **kwargs):
        return [degrees(x) for x in self.leg_ik(x,y,z, **kwargs)]

    def leg_ik(self, x, y, z):
        # root angle
        t1 = atan2(y, x)

        # offset from root segment       
        x = x - cos(t1) * l1
        y = y - sin(t1) * l1

        # horiztonal and total distance left
        r = sqrt(x**2 + y**2)
        rt = sqrt(r**2 + z**2)

        # knee angle needed to cover that distance
        tk = acos((l2**2 + l3**2 - rt**2) / (2 * l2 * l3))
        t3 = pi - tk

        # angle of depression to calculate the hip angle
        d = atan2(z, r)
        e = asin(l3 * sin(tk) / rt)
        t2 = e - d

        return [t1, t2, t3]
