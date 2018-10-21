import time
import sys

from microWebSrv import MicroWebSrv


def main():
    global calibrate_ws
    global controller_ws

    bot = BOTS.Bot()
    sp = spider.Spider(bot)

    # calibrate_ws = SocketHandlers.Calibrate(bot)
    # controller_ws = SocketHandlers.Controller(sp)
    # setup_web_server(accept_socket_cb)

    r = range(40)
    update = sp.body_xyz

    while True:
        for v in r:
            update(-20, v-20, -70)

        for v in r:
            update(v-20, 20, -70)

        for v in r:
            update(20, 20-v, -70)

        for v in r:
            update(20-v, -20, -70)

        time.sleep(5)

    # time.sleep(1)
    # bot.servo.reset_position()

    # if bot.user_sw.pressed():
    #     boot_menu()

    print(bot.battery.read())

    return [bot, sp]

# def boot_menu():
#     title = "Boot Menu"
#     options = ["Servo Calib"]

#     while True:
#         pass


def accept_socket_cb(webSocket, httpClient):
    global calibrate_ws
    global controller_ws

    if (httpClient.GetRequestPath() == "/calibrate"):
        webSocket.RecvTextCallback = calibrate_ws.socket_text_recv_cb
    if (httpClient.GetRequestPath() == "/controller"):
        webSocket.RecvTextCallback = controller_ws.socket_text_recv_cb


if __name__ == '__main__':
    wlan = setup_wlan()

    try:
        import BOTS
        import spider
        import SocketHandlers

        [bot, spider] = main()

    except Exception as e:
        sys.print_exception(e)
        bot.deinit()
