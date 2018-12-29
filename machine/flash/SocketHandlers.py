import BOTS
import utime

class Calibrate(object):

    current_id = 0

    def __init__(self, bot):
        self.current_id = 0
        self.bot = bot

    def socket_text_recv_cb(self, webSocket, msg):
        msg_id = msg[0]
        value = msg[1:]

        if msg_id == 'i':
            webSocket.SendText("a" + str(round(self.bot.servo.get_deg(int(value)))))
            self.current_id = int(value)
        elif msg_id == 'a':
            self.bot.servo.set_deg_raw(self.current_id, float(value))
        elif msg_id == 'w':
            zero_points = self.bot.servo.get_all()
            ids = [x for x in range(BOTS.NUM_SERVOS)]

            rows = [[str(a), str(b)] for a, b in zip(ids, zero_points)]

            with open(BOTS.SERVO_CALIBRATION_FILE, 'w') as fd:
                for row in rows:
                    fd.write(",".join(row) + "\n")

class Controller(object):
    def __init__(self, spider):
        self.spider = spider
        self.x_rate = 0
        self.y_rate = 0
        self.yaw_rate = 0

    def socket_text_recv_cb(self, webSocket, msg):
        # old_time = utime.ticks_us()
        msg_id = msg[0]
        value = msg[1:]

        if msg_id == "a":
            axes = value.split(',')
            
            self.x_rate = float(axes[0]) * 20
            self.y_rate = float(axes[1]) * 20
            self.yaw_rate = float(axes[2]) / 5.

        