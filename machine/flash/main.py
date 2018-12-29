import time
import sys

from machine import Timer
from math import sin, cos, pi
from microWebSrv import MicroWebSrv


def main(wlan):
    global calibrate_ws
    global controller_ws

    # init the bot
    bot = BOTS.Bot()
    bot.set_wlan(wlan)
    bot.update_display_status()

    if bot.user_sw.pressed():
        return None, None

    # init spider controller
    sp = spider.Spider(bot)

    # setup web server
    calibrate_ws = SocketHandlers.Calibrate(bot)
    controller_ws = SocketHandlers.Controller(sp)
    setup_web_server(accept_socket_cb)

    # stand up
    sp.xyz(0, 0, 50)

    dt = 50

    # walk with slow dt
    sp.walk_dt = dt / 1000.
    sp.walk_leg_freq = 0.5
# 
    sp.begin_walk()

    tm = Timer(0)
    tm.init(period=dt, mode=tm.PERIODIC, callback=lambda timer: sp.update_walk(controller_ws.x_rate, controller_ws.y_rate, controller_ws.yaw_rate))
    
    input("Press enter to stop walking...")
    tm.deinit()

    # sp.end_walk()

    # for i in range(100):
    #     sp.update_walk(, controller_ws.y_rate, 0)

    return [bot, sp]


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
