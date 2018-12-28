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

    # bot.servo.reset_position()

    # init spider controller
    sp = spider.Spider(bot)
    sp.xyz(0, 0, 50)
# 
    dt = 0.1
    freq = 1

    for i in range(600):
        t0 = time.time()

        t = i * dt

        x = 10 * cos(t * 2 * pi * freq)
        y = 10 * cos(t * 2 * pi * freq + pi/2)

        for j in range(4):
            z = 200 * cos(-t * 2 * pi * freq - 3*pi/4 - pi/2 * j) - 170
            z = max(0, z)
            sp.legs[j][2] = -35 + z

            if z > 20:
                sp.legs[j][1] = sp.legs0[j][1] + 10

            sp.legs[j][1] -= 3

        sp.xyz(x, y, 50)

        time.sleep(dt - (time.time() - t0))

# 
    calibrate_ws = SocketHandlers.Calibrate(bot)
    # controller_ws = SocketHandlers.Controller(sp)
    setup_web_server(accept_socket_cb)

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
