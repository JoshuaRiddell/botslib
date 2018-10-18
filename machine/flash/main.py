import time
import network
import sys

SSID = "Robot_Spider"
USER = "micro"
PASSWORD = "python"

def main(bot):

    print(bot.battery.read())

    # create an instance of the I2C bus
    I2C_bus = I2C(0, sda=27, scl=26)

    # create instance of the servo driver
    robot = Servo(I2C_bus)

    # setup screen
    tft = display.TFT()
    tft.init(tft.GENERIC, width=160, height=128, miso=19,
             mosi=21, clk=18, cs=5, dc=22, color_bits=16)
    tft_setup(tft)
    # adjust value of duty to change backlight
    backlight = PWM(23, freq=200, duty=25)

    # load animation images from pic directory
    for pic in range(1, 55):
        tft.image(0, 0, 'pic/'+str(pic)+'.jpg')
    time.sleep(0.5)

    # clear screen with black colour
    tft.clear(0x000000)

    # place open worm inage at bottom of screen
    tft.image(0, 88, 'open_worm.jpg')

    # display data on screen
    tft.text(20, 10, "BATTERY = "+str(read_battery())+"v")
    tft.text(18, 25, "IP = " + str(ap_if.ifconfig()[0]))


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
    while network.ftp.status()[0] != 2:time.sleep(0.1)

    # print status
    print ("FTP status ", network.ftp.status())
    print ("Telnet status ", network.telnet.status())


if __name__ == '__main__':
    setup_ap()

    try:
        import BOTS.bot as bot
        bot = bot.Bot()
        main(bot)
    except Exception as e:
        sys.print_exception(e)
    finally:
        bot.deinit()
