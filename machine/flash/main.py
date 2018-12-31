import time
import sys

from machine import Timer
from math import sin, cos, pi
from microWebSrv import MicroWebSrv

import cbots

import utime


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

    # setup cbots
    cbots.set_i2c(bot.i2c)
    cbots.begin_walk(0.02, 0.8)


    # stand up
    sp.xyz(0, 0, 50)

    # dt = 40

    # walk with slow dt
    # sp.walk_dt = dt / 1000.
    # sp.walk_leg_freq = 0.5

    # sp.begin_walk()

    uw = cbots.update_walk

    tm = Timer(0)
    tm.init(period=20, mode=tm.PERIODIC, callback=lambda timer: uw(controller_ws.x_rate, controller_ws.y_rate, controller_ws.yaw_rate))

    # bot.servo.deinit()
    
    # for i in range(100):
    #     sp.update_walk(0, 0, 0)

    # sp.end_walk()

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
