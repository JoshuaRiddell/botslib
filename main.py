import network
import time

ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)
ap_if.config(essid="Robot_Spider")

time.sleep(1)

network.telnet.start(user="micro",password="python", timeout=1000)
network.ftp.start(user="micro",password="python",buffsize=1024,timeout=1000)

while network.ftp.status()[0] != 2: time.sleep(0.1)

print ("FTP status ", network.ftp.status())
print ("Telnet status ", network.telnet.status())

#import st_test



  





