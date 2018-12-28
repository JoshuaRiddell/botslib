import time
import sys

from microWebSrv import MicroWebSrv


def main(wlan):
    global calibrate_ws
    global controller_ws

    # init the bot
    bot = BOTS.Bot()
    bot.set_wlan(wlan)
    time.sleep(1)
    bot.update_display_status()

    # bot.servo.reset_position()

    # init spider controller
    sp = spider.Spider(bot)
    sp.xyz(0, 0, 0)

    # time.sleep(1)

    # sp.xyz(0, 0, 0)

    # time.sleep(1)

    # sp.rpy(0.1, 0, 0)

    # time.sleep(3)

    # sp.rpy(0, 0, 0)
    

    calibrate_ws = SocketHandlers.Calibrate(bot)
    # controller_ws = SocketHandlers.Controller(sp)
    setup_web_server(accept_socket_cb)


    # for v in r:
    #     update(-20, v-20, -70)

    # for v in r:
    #     update(v-20, 20, -70)

    # for v in r:
    #     update(20, 20-v, -70)

    # for v in r:
    #     update(20-v, -20, -70)

    # time.sleep(1)
    # bot.servo.reset_position()

    # if bot.user_sw.pressed():
    #     boot_menu()

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

        [bot, sp] = main(wlan)

    except Exception as e:
        sys.print_exception(e)
        bot.deinit()
