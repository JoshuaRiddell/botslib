import time
import sys

from math import sin, cos, pi

from microWebSrv import MicroWebSrv


def main(wlan):
    global calibrate_ws
    global controller_ws

    # init the bot
    bot = BOTS.Bot()
    bot.set_wlan(wlan)
    time.sleep(1)
    bot.update_display_status()

    # init spider controller
    sp = spider.Spider(bot)
    sp.xyz(0, 0, 50)

    sp.begin_walk()

    for i in range(100):
        sp.update_walk(0, 20, 0.1)
    
    sp.end_walk()

    calibrate_ws = SocketHandlers.Calibrate(bot)
    controller_ws = SocketHandlers.Controller(sp)
    setup_web_server(accept_socket_cb)

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
