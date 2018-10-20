import time
import network
import sys

def main():
    bot = BOTS.Bot()

    print(bot.battery.read())

    # for i in range(70):
    #     bot.servo.set_deg(0, i-35)
    #     bot.servo.set_deg(4, i-35)
    #     bot.servo.set_deg(10, i-35)
    #     bot.servo.set_deg(14, i-35)
    #     time.sleep(0.2)
    #     print(i)

    return bot

if __name__ == '__main__':
    ap_if = setup_ap("Robot_Spider", "micro", "python")

    try:
        import BOTS
        import spider
        bot = main()
        spider = spider.Spider(bot)
    except Exception as e:
        sys.print_exception(e)
        bot.deinit()
