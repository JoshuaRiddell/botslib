import time
import sys

from microWebSrv import MicroWebSrv


def main():
    global calibrate_ws
    
    bot = BOTS.Bot()

    calibrate_ws = SocketHandlers.Calibrate(bot)
    setup_web_server(accept_socket_cb)

    sp = spider.Spider(bot)

    sp.set_leg(0, 120, 0, 10)
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

    if (httpClient.GetRequestPath() == "/calibrate"):
        webSocket.RecvTextCallback = calibrate_ws.socket_text_recv_cb


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
