import time
import network
import sys

SSID = "Robot_Spider"
USER = "micro"
PASSWORD = "python"


def main():
    bot = BOTS.Bot()

    print(bot.battery.read())

    for i in range(70):
        bot.servo.set_deg(0, i-35)
        bot.servo.set_deg(4, i-35)
        bot.servo.set_deg(10, i-35)
        bot.servo.set_deg(14, i-35)
        time.sleep(0.2)
        print(i)

    return bot


def setup_ap():
    "create access point and start telnet and ftp server"
    # create ap
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    ap_if.config(essid=SSID)

    time.sleep(1)

    # create telnet and ftp
    network.telnet.start(user=USER, password=PASSWORD, timeout=1000)
    network.ftp.start(user=USER, password=PASSWORD,
                      buffsize=1024, timeout=1000)

    # wait for telnet and ftp to be up
    while network.ftp.status()[0] != 2:
        time.sleep(0.1)

    # print status
    print ("FTP status ", network.ftp.status())
    print ("Telnet status ", network.telnet.status())

    return ap_if


if __name__ == '__main__':
    ap_if = setup_ap()

    try:
        import BOTS
        bot = main()
    except Exception as e:
        sys.print_exception(e)
        bot.deinit()
