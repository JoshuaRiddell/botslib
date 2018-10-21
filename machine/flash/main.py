import time
import network
import sys
from microWebSrv import MicroWebSrv

def main():
    bot = BOTS.Bot()

    if bot.user_sw.pressed():
        boot_menu()

    print(bot.battery.read())

    # for i in range(70):
    #     bot.servo.set_deg(0, i-35)
    #     bot.servo.set_deg(4, i-35)
    #     bot.servo.set_deg(10, i-35)
    #     bot.servo.set_deg(14, i-35)
    #     time.sleep(0.2)
    #     print(i)

    return bot

def boot_menu():
    title = "Boot Menu"
    options = ["Servo Calib"]

    while True:
        pass

current_id = 0

def accept_socket_cb(webSocket, msg):
    print("accepted")
    webSocket.RecvTextCallback   = socket_text_recv

def socket_text_recv(webSocket, msg):
    global current_id

    print("got : " + msg)

    msg_id = msg[0]
    value = msg[1:]

    if msg_id == 'i':
        webSocket.SendText("a" + str(round(bot.servo.get_deg(int(value)))))
        current_id = int(value)
    elif msg_id == 'a':
        bot.servo.set_deg(current_id, float(value))

def setup_web_server():
    mws = MicroWebSrv()                                    # TCP port 80 and files in /flash/www
    mws.MaxWebSocketRecvLen     = 256                      # Default is set to 1024
    mws.WebSocketThreaded       = False                    # WebSockets without new threads
    mws.AcceptWebSocketCallback = accept_socket_cb # call back function to receive WebSockets
    mws.Start()

if __name__ == '__main__':
    wlan = setup_wlan()

    try:
        setup_web_server()

        import BOTS
        import spider
        bot = main()
        spider = spider.Spider(bot)

        spider.set_leg(0, 120, 0, 10)
        # time.sleep(1)
        # bot.servo.reset_position()

    except Exception as e:
        sys.print_exception(e)
        bot.deinit()
