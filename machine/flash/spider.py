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

Z = const(30)

STATE_STEP_IDLE = const(0)
STATE_STEP_MOVING = const(1)
STATE_STEP_STEPPING = const(2)
STATE_STEP_RETURNING = const(3)

LEG_STEP_THRESHOLD = const(30)

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
        self.end_walk = cspider.end_walk
        self.update_walk = cspider.update_walk
        self.update_walk_rates = cspider.update_walk_rates

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
        

        self.move_time = 0.5
        self.step_time = 0.2
        self.step_period = self.move_time + self.step_time

        self.walk_t = 0
        self.last_step_t = -100
        self.state_t0 = 0

        self.step_state = 0
        self.step_leg = 0

        self.x_rate = 0
        self.y_rate = 0
        self.yaw_rate = 0

        self.decimator = 0
        self.step_lock = 0
    
    def update_walk_rates(self, x_rate, y_rate, yaw_rate):
        self.x_rate = x_rate
        self.y_rate = y_rate
        self.yaw_rate = yaw_rate

    def get_centroid(self):
        # calculate centroid
        x_sum = 0
        y_sum = 0

        for i in range(4):
            if i == self.step_leg:
                continue

            x_sum += self.legs[i][0]
            y_sum += self.legs[i][1]

        centroid_x = x_sum / 3.
        centroid_y = y_sum / 3.

        return [centroid_x, centroid_y]

    def get_next_leg_index(self):
        # find the largest leg index
        max_leg_diff = 0
        max_leg_index = 0
        for i in range(4):
            r = (self.legs[i][0] - self.legs0[i][0])**2 + (self.legs[i][1] - self.legs0[i][1])**2

            if r > max_leg_diff:
                max_leg_diff = r
                max_leg_index = i

        # check if we want to lift the leg
        if max_leg_diff > LEG_STEP_THRESHOLD:
            return max_leg_index
        
        return -1

    @staticmethod
    def sign(x1, y1, x2, y2, x3, y3):
        return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1- y3)

    def cg_in_legs(self):
        ids = list(range(4))
        ids.pop(self.step_leg)

        l = self.legs

        d1 = self.sign(self.x, self.y, l[ids[0]][0], l[ids[0]][1], l[ids[1]][0], l[ids[1]][1])
        d2 = self.sign(self.x, self.y, l[ids[1]][0], l[ids[1]][1], l[ids[2]][0], l[ids[2]][1])
        d3 = self.sign(self.x, self.y, l[ids[2]][0], l[ids[2]][1], l[ids[0]][0], l[ids[0]][1])

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    def update_walk(self):
        # update walk
        x_rate = self.x_rate
        y_rate = self.y_rate
        yaw_rate = self.yaw_rate

        # for interrupt mode
        self.walk_t += self.walk_dt
        t = self.walk_t

        step_state = self.step_state
        state_t = t - self.state_t0

        if step_state == STATE_STEP_IDLE:
            # check if it's been long enough since the last step
            if t - self.last_step_t >= self.step_period:

                step_leg_idx = self.get_next_leg_index()

                if step_leg_idx != -1:
                    self.step_leg = step_leg_idx
                    self.step_state = STATE_STEP_MOVING
                    self.n = 0
                    self.state_t0 = t
            
            # update body position to move towards the centre
            if abs(self.x) < 1:
                self.x = 0
            if abs(self.y) < 1:
                self.y = 0

            self.x -= self.x * (state_t / self.move_time)
            self.y -= self.y * (state_t / self.move_time)

        elif step_state == STATE_STEP_MOVING:
            centroid_x, centroid_y = self.get_centroid()

            # update body position to move towards centroid
            self.x += (centroid_x - self.x) * (state_t / self.move_time)
            self.y += (centroid_y - self.y) * (state_t / self.move_time)

            # self.x = centroid_x
            # self.y = centroid_y

            if self.cg_in_legs():
                self.n += 1

                if self.n > 2:
                    self.step_state = STATE_STEP_STEPPING
                    self.state_t0 = t

        elif step_state == STATE_STEP_STEPPING:
            # lift leg
            # z = 30 * sin(state_t * pi / self.step_time)**2
            # self.legs[self.step_leg][2] = self.legs0[self.step_leg][2] + z
            self.legs[self.step_leg][2] = self.legs0[self.step_leg][2] + 50

            # # if leg is high enough then reset position
            # if z > 20:
            self.legs[self.step_leg][0] = self.legs0[self.step_leg][0]
            self.legs[self.step_leg][1] = self.legs0[self.step_leg][1]

            # keep body on centroid
            # centroid_x, centroid_y = self.get_centroid()
            # self.x = centroid_x
            # self.y = centroid_y

            if state_t >= self.step_time:
                self.step_state = STATE_STEP_IDLE
                self.state_t0 = t
                self.legs[self.step_leg][2] = self.legs0[self.step_leg][2]

        # write leg positions
        for i in range(4):
            if (self.legs[i][2] > 10):
                # leg is lifted so don't move it
                continue

            # apply translational shift to move in the x,y directions
            self.legs[i][0] -= x_rate * self.walk_dt
            self.legs[i][1] -= y_rate * self.walk_dt

            # apply rotational shift to yaw in each direction
            self.legs[i][0], self.legs[i][1] = self.rot2d(yaw_rate*self.walk_dt, self.legs[i][0], self.legs[i][1])

        # write the calculated position to the legs
        self.update_body()
    
    
    def end_walk(self):
        # reset all the legs
        self.legs = [row[:] for row in self.legs0]

        # reset body lean
        self.x = 0
        self.y = 0

        # write to legs
        self.update_body()

    def start_walk(self):
        self.begin_walk(0.05, 0.05)

        self.step_timer.init(
            period=50,
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
