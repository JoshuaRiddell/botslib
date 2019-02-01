from machine import Timer
from math import atan2, asin, pi, sin, cos, acos, sqrt, degrees

# safe import of cspider library
try:
    import cspider
    CSPIDER_LOADED = True
except ImportError:
    CSPIDER_LOADED = False

# definitions for link lengths
L1 = const(25)
L2 = const(48)
L3 = const(75)
L4 = const(10)  # offset of foot to leg axis

# body length and width to leg pivot points
BW = const(47)
BL = const(88)

# desired stance width and length when legs are centred
STANCE_WIDTH = const(140)
STANCE_LENGTH = const(180)
STANCE_HEIGHT = const(35)

# states for walking state machine
STATE_STEP_IDLE = const(0)
STATE_STEP_LEANING = const(1)
STATE_STEP_STEPPING = const(2)

class Spider(object):
    "Spider robot controller."

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

        # single variable functions
        self.set_x = cspider.set_x
        self.set_y = cspider.set_y
        self.set_z = cspider.set_z
        self.set_roll = cspider.set_roll
        self.set_pitch = cspider.set_pitch
        self.set_yaw = cspider.set_yaw

        # pass through legs0 stance coordinates
        cspider.set_legs0(self.legs0)

    def set_x(self, x):
        self.x = x
        self.update_body()

    def set_y(self, y):
        self.y = y
        self.update_body()

    def set_z(self, z):
        self.z = z
        self.update_body()

    def set_roll(self, roll):
        self.roll = roll
        self.update_body()

    def set_pitch(self, pitch):
        self.pitch = pitch
        self.update_body()

    def set_yaw(self, yaw):
        self.yaw = yaw
        self.update_body()

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
        "Get required coordinates for each leg and set the leg to those coordinates."
        [x, y, z] = self.body_to_leg(0)
        self.set_leg(0, x, -y, z)

        [x, y, z] = self.body_to_leg(1)
        self.set_leg(1, x, y, z)

        [x, y, z] = self.body_to_leg(2)
        self.set_leg(2, -x, y, z)

        [x, y, z] = self.body_to_leg(3)
        self.set_leg(3, -x, -y, z)

    def body_to_leg(self, idx):
        "Transform the leg coordinates based on the current body position."
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
        "Do leg inverse kinematics and write the results to the servos."
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
        "Convert x,y,z leg coordinates to joint angles."
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

    def begin_walk(self, dt, move_time, step_time, step_period, step_thresh, scaling_factor):
        "Initialise all walking variables."
        # walk timing properties
        self.walk_dt = dt
        self.walk_t = 0

        # moving and stepping times (seconds)
        self.move_time = move_time
        self.step_time = step_time
        self.step_period = step_period

        # distance threshold to cause leg stepping
        self.step_thresh = step_thresh

        # step state times
        self.last_step_t = -100
        self.state_t0 = 0

        # step state and current leg id
        self.step_state = STATE_STEP_IDLE
        self.step_leg = 0
        self.scaling_factor = scaling_factor

        # initialise walking rates
        self.x_rate = 0
        self.y_rate = 0
        self.yaw_rate = 0

    def update_walk_rates(self, x_rate, y_rate, yaw_rate):
        "Update walking rate values for next update."
        self.x_rate = x_rate
        self.y_rate = y_rate
        self.yaw_rate = yaw_rate

    def get_centroid(self):
        "Get centroid of legs currently on the ground."
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
        "Get next leg to be lifted. Returns leg index. Returns -1 if no leg needs to be lifted"

        # find the leg which is farthest from leg resting position
        max_leg_diff = 0
        max_leg_index = 0
        for i in range(4):
            # cartesian distance to legs0 position
            r = sqrt((self.legs[i][0] - self.legs0[i][0])**2 + (self.legs[i][1] - self.legs0[i][1])**2)

            if r > max_leg_diff:
                max_leg_diff = r
                max_leg_index = i

        # check if we want to lift the leg
        if max_leg_diff > self.step_thresh:
            return max_leg_index
        
        # we don't want to lift any legs
        return -1

    @staticmethod
    def sign(x1, y1, x2, y2, x3, y3):
        "Sign function for use in calculating if a point is inside a triangle."
        return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1- y3)

    def cg_in_legs(self, centroid_x, centroid_y):
        """Check if the current CG (self.x,self.y) is inside stability base of the 3 legs
        currently on the ground.
        """

        # get list of IDs not including stepping leg
        ids = list(range(4))
        ids.pop(self.step_leg)

        # shrink the triangle down by scaling factor for margin of error
        l = self.legs
        l_shrink = []
        for lid in ids:
            c = [
                centroid_x + self.scaling_factor * (centroid_x - l[lid][0]),
                centroid_y + self.scaling_factor * (centroid_y - l[lid][1]),
            ]
            l_shrink.append(c)

        # see if point is inside leg coordinates
        d1 = self.sign(self.x, self.y, l_shrink[0][0], l_shrink[0][1], l_shrink[1][0], l_shrink[1][1])
        d2 = self.sign(self.x, self.y, l_shrink[1][0], l_shrink[1][1], l_shrink[2][0], l_shrink[2][1])
        d3 = self.sign(self.x, self.y, l_shrink[2][0], l_shrink[2][1], l_shrink[0][0], l_shrink[0][1])

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    def update_walk_state_machine(self, t):
        # get current state
        step_state = self.step_state
        state_t = t - self.state_t0

        if step_state == STATE_STEP_IDLE:
            # check if it's been long enough since the last step
            if t - self.last_step_t >= self.step_period:

                step_leg_idx = self.get_next_leg_index()

                if step_leg_idx != -1:
                    self.last_step_t = t
                    self.step_leg = step_leg_idx
                    self.step_state = STATE_STEP_LEANING
                    self.n = 0
                    self.state_t0 = t
            
            # update body position to move towards the centre
            if abs(self.x) < 1:
                self.x = 0
            if abs(self.y) < 1:
                self.y = 0

            self.x -= self.x * (state_t / self.move_time)
            self.y -= self.y * (state_t / self.move_time)

        elif step_state == STATE_STEP_LEANING:
            centroid_x, centroid_y = self.get_centroid()

            # update body position to move towards centroid
            self.x += (centroid_x - self.x) * (state_t / self.move_time)
            self.y += (centroid_y - self.y) * (state_t / self.move_time)

            if self.cg_in_legs(centroid_x, centroid_y):
                self.step_state = STATE_STEP_STEPPING
                self.state_t0 = t

        elif step_state == STATE_STEP_STEPPING:
            sl = self.legs[self.step_leg]
            sl0 = self.legs0[self.step_leg]

            # lift leg
            sl[2] = sl0[2] + 50

            # reset position
            sl[0] = sl0[0]
            sl[1] = sl0[1]

            if state_t >= self.step_time:
                self.step_state = STATE_STEP_IDLE
                self.state_t0 = t
                sl[2] = sl0[2]

    def update_walk_transformations(self, t):
        # write leg positions
        xr = self.x_rate
        yr = self.y_rate
        yawr = self.yaw_rate

        for i in range(4):
            if (self.legs[i][2] > 10):
                # leg is lifted so don't move it
                continue

            # apply translational shift to move in the x,y directions
            self.legs[i][0] -= xr * self.walk_dt
            self.legs[i][1] -= yr * self.walk_dt

            # apply rotational shift to yaw in each direction
            self.legs[i][0], self.legs[i][1] = self.rot2d(yawr * self.walk_dt, self.legs[i][0], self.legs[i][1])


    def update_walk(self):
        "Periodic walk update function. Handles stepping and body translation."

        # calculate new time
        self.walk_t += self.walk_dt
        t = self.walk_t

        self.update_walk_state_machine(t)
        self.update_walk_transformations(t)
        self.update_body()
        
    def end_walk(self):
        # reset all the legs
        self.legs = [row[:] for row in self.legs0]

        # reset body lean
        self.x = 0
        self.y = 0

        # write to legs
        self.update_body()

    def start_walk(self, dt=0.05, move_time=0.5, step_time=0.5, step_period=0.6, step_thresh=30, scaling_factor=0.1):

        self.begin_walk(dt, move_time, step_time, step_period, step_thresh, scaling_factor)

        self.step_timer.init(
            period=int(dt*1000),
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
