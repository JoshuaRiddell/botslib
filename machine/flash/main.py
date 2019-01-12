import sys
import networking

def main(wlan):
    global calibrate_ws
    global controller_ws

    # init the bot
    bot = bots.Bot(use_cbots=True)
    bot.set_wlan(wlan)

    # don't go any further if the user button is pressed
    # use this if you locked up the device using subsequent code
    if bot.user_sw.pressed():
        return None, None

    # init spider controller
    sp = spider.Spider(bot, use_cspider=True)

    # setup web server
    calibrate_ws = socket_handlers.Calibrate(bot)
    controller_ws = socket_handlers.Controller(sp)
    networking.setup_web_server(accept_socket_cb)

    # stand up
    sp.xyz(0, 0, 40)

    return [bot, sp]


def accept_socket_cb(webSocket, httpClient):
    global calibrate_ws
    global controller_ws

    if (httpClient.GetRequestPath() == "/calibrate"):
        webSocket.RecvTextCallback = calibrate_ws.socket_text_recv_cb
    if (httpClient.GetRequestPath() == "/controller"):
        webSocket.RecvTextCallback = controller_ws.socket_text_recv_cb


if __name__ == '__main__':
    wlan = networking.setup_wlan()

    # do all of this inside a try except
    # in this way if there are errors then the ftp server doesn't crash
    try:
        import bots
        import spider
        import socket_handlers

        [bot, sp] = main(wlan)

    except Exception as e:
        sys.print_exception(e)
        bot.deinit()
