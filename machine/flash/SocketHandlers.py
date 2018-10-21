import BOTS

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
