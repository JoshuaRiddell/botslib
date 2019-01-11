import bots
import utime

class Calibrate(object):
    "Websocket handler for servo calibration page"

    current_id = 0
    def __init__(self, bot):
        self.current_id = 0
        self.bot = bot

    def socket_text_recv_cb(self, webSocket, msg):
        msg_id = msg[0]
        value = msg[1:]

        if msg_id == 'i':
            # index change command
            # send angle of new index back to client
            webSocket.SendText("a" + str(round(self.bot.servo.get_deg(int(value)))))
            self.current_id = int(value)
        elif msg_id == 'a':
            # angle command, set angle of servo
            self.bot.servo.set_deg_raw(self.current_id, float(value))
        elif msg_id == 'w':
            # write command, get all servo positions and write them as zero positions
            zero_points = self.bot.servo.get_all()
            ids = [x for x in range(bots.NUM_SERVOS)]

            rows = [[str(a), str(b)] for a, b in zip(ids, zero_points)]

            with open(bots.SERVO_CALIBRATION_FILE, 'w') as fd:
                for row in rows:
                    fd.write(",".join(row) + "\n")


class Controller(object):
    "Websocket handler for walking controller web page"

    def __init__(self, spider):
        self.spider = spider

    def socket_text_recv_cb(self, webSocket, msg):
        msg_id = msg[0]
        value = msg[1:]

        if msg_id == "a":
            # angle command so update walk controller with rates
            axes = value.split(',')
            
            x_rate = float(axes[0]) * 20
            y_rate = float(axes[1]) * -20
            z = float(axes[2])
            roll = (float(axes[6]) - float(axes[5])) / 4
            pitch = float(axes[4]) / 4
            yaw_rate = float(axes[3]) / 6

            self.spider.z = z
            self.spider.update_walk_rates(x_rate, y_rate, yaw_rate)
        elif msg_id == "s":
            # start walk command
            self.spider.start_walk()
        elif msg_id == "x":
            # stop walk command
            self.spider.stop_walk()
        

