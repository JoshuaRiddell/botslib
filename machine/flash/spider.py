from machine import Timer
from math import atan2, asin, pi, sin, cos, acos, sqrt, degrees
import time

try:
    import cspider
    CSPIDER_LOADED = True
except ImportError:
    CSPIDER_LOADED = False

# to allow importing on non micropython systems
try:
    _CONST_TEST_VAR = const(10)
except:
    print("const() not defined. Defining...")
    const = lambda x: x

L1 = const(25)
L2 = const(48)
L3 = const(75)
L4 = const(10)  # offset of foot to leg axis

BW = const(47)
BL = const(88)

STANCE_WIDTH = const(140)
STANCE_LENGTH = const(180)
STANCE_HEIGHT = const(35)

class Spider(object):

    def __init__(self, bot, step_timer=1, use_cspider=False):
        self.bot = bot

        self.step_timer = Timer(step_timer)

        self.legs0 = [
            [STANCE_LENGTH/2, -STANCE_WIDTH/2, -STANCE_HEIGHT],
            [STANCE_LENGTH/2, STANCE_WIDTH/2, -STANCE_HEIGHT],
            [-STANCE_LENGTH/2, STANCE_WIDTH/2, -STANCE_HEIGHT],
            [-STANCE_LENGTH/2, -STANCE_WIDTH/2, -STANCE_HEIGHT],
        ]

        if use_cspider:
            self.setup_cspider()
        else:
            self.setup_spider()
    
    def setup_spider(self):
        self.set_servo = self.bot.servo.set_rad

        self.x = 0
        self.y = 0
        self.z = 0

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.legs = [row[:] for row in self.legs0]


        self.body_offsets = [
            [BW/2,  -BL/2],
            [BW/2,  BL/2],
            [-BW/2, BL/2],
            [-BW/2, -BL/2],
        ]

        #   e   m   r
        self.angle_signs = [
            -1, -1,  -1,  0,
            1,  1,  1,  0,
            -1,  -1,  -1,  0,
            1,  1,  1,  0,
        ]

    def setup_cspider(self):
        "Setup the resources to use cspider library."
        if not CSPIDER_LOADED:
            raise ValueError("use_cspider true but cspider library was not found.")

        # body placement functions
        self.xyz = cspider.xyz
        self.rpy = cspider.rpy
        self.xyzrpy = cspider.xyzrpy
        self.update_body = cspider.update_body

        # walking functions
        self.begin_walk = cspider.begin_walk
        self.update_walk = cspider.update_walk
        self.update_walk_params = cspider.update_walk_params

        # pass through legs0 stance coordinates
        cspider.set_legs0(self.legs0)

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
        self.set_leg(0, x, -y, z)

        [x, y, z] = self.body_to_leg(1)
        self.set_leg(1, x, y, z)

        [x, y, z] = self.body_to_leg(2)
        self.set_leg(2, -x, y, z)

        [x, y, z] = self.body_to_leg(3)
        self.set_leg(3, -x, -y, z)

    def body_to_leg(self, idx):
        # get offsets for this leg
        leg = self.legs[idx]
        x = leg[0] - self.x
        y = leg[1] - self.y
        z = leg[2] - self.z

        # apply body rotation
        x, z = self.rot2d(self.roll, x, z)
        z, y = self.rot2d(self.pitch, z, y)
        x, y = self.rot2d(-self.yaw, x, y)

        # apply offsets due to frame
        o = self.body_offsets[idx]
        x = x - o[0]
        y = y - o[1]

        return [x, y, z]

    def set_leg(self, id, x, y, z):
        # do inverse kinematics
        t1, t2, t3 = self.leg_ik(x, y, z)

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
        x = x - cos(t1) * L1
        y = y - sin(t1) * L1

        # horiztonal and total distance left
        r = sqrt(x**2 + y**2)
        rt = sqrt(r**2 + z**2)

        # knee angle needed to cover that distance
        tk = acos((L2**2 + L3**2 - rt**2) / (2 * L2 * L3))
        t3 = pi - tk

        # angle of depression to calculate the hip angle
        d = atan2(z, r)
        e = asin(L3 * sin(tk) / rt)
        t2 = e + d

        return [t1, t2, t3]

    def begin_walk(self, dt, freq):
        self.walk_leg_freq = freq
        self.walk_dt = dt

        self.walk_t0 = time.time()
        self.walk_t = self.walk_t0

        self.x_rate = 0
        self.y_rate = 0
        self.yaw_rate = 0
    
    def update_walk_rates(self, x_rate, y_rate, yaw_rate):
        self.x_rate = x_rate
        self.y_rate = y_rate
        self.yaw_rate = yaw_rate

    def update_walk(self):
        # update walk
        x_rate = self.x_rate
        y_rate = self.y_rate
        yaw_rate = self.yaw_rate
        
        # for interrupt mode
        self.walk_t += self.walk_dt

        # # wait until dt sconds has elapsed
        # wait_time = self.walk_dt - (time.time() - self.walk_t)
        
        # if wait_time < 0:
        #     print("spider dt too small, {} second overrun".format(wait_time))

        #     # just set the time as current and run as fast as we can
        #     self.walk_t = time.time()
        # else:
        #     time.sleep(wait_time)

        #     # update global time counter
        #     self.walk_t += self.walk_dt

        # get a relative time since we started walking
        t = self.walk_t - self.walk_t0

        # get body position in x,y
        x = 15 * cos(t * 2 * pi * self.walk_leg_freq)
        y = 15 * cos(t * 2 * pi * self.walk_leg_freq + pi/2)

        # write position to body
        self.x = x
        self.y = y

        # write leg positions
        for i in range(4):
            # handle periodic lifting of legs in phase with body lean
            z = 150 * cos(-t * 2 * pi * self.walk_leg_freq - 3*pi/4 - pi/2 * i) - 120
            z = max(0, z)
            self.legs[i][2] = self.legs0[i][2] + z

            # reset leg position when it is high enough
            if z > 20:
                self.legs[i][0] = self.legs0[i][0]
                self.legs[i][1] = self.legs0[i][1]

            # apply translational shift to move in the x,y directions
            self.legs[i][0] -= x_rate * self.walk_dt
            self.legs[i][1] -= y_rate * self.walk_dt

            # apply rotational shift to yaw in each direction
            self.legs[i][0], self.legs[i][1] = self.rot2d(yaw_rate*self.walk_dt, self.legs[i][0], self.legs[i][1])

        # write the calculated position to the legs
        self.update_body()
    

    def end_walk(self):
        # reset all the legs
        self.legs = self.legs0[:][:]

        # reset body lean
        self.x = 0
        self.y = 0

        # write to legs
        self.update_body()

    def start_walk(self):
        self.begin_walk(0.1, 0.1)

        self.step_timer.init(
            period=100,
            mode=self.step_timer.PERIODIC,
            callback=lambda timer: self.update_walk()
        )

    def stop_walk(self):
        self.step_timer.deinit()
        self.end_walk()

    @staticmethod
    def rot2d(a, x, y):
        "Optimised 2D rotation matrix application."
        sa = sin(a)
        ca = cos(a)
        return [x*ca - y*sa, x*sa + y*ca]
