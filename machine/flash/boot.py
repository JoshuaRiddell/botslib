# This file is executed on every boot (including wake-boot from deepsleep)
import sys
import gc
import network
import time

sys.path[1] = '/flash/lib'
sys.path.append('/flash/assets')
sys.path.append('/flash/core')


def reload(mod):
    "De-allocate module, garbage collect and then reload module."

    mod_name = mod.__name__
    del sys.modules[mod_name]
    gc.collect()
    return __import__(mod_name)

def setup_ap(ssid, user, password):
    "create access point and start telnet and ftp server"
    # create ap
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    ap_if.config(essid=ssid)

    time.sleep(1)

    # create telnet and ftp
    network.telnet.start(user=user, password=password, timeout=1000)
    network.ftp.start(user=user, password=password,
                      buffsize=1024, timeout=1000)

    # wait for telnet and ftp to be up
    while network.ftp.status()[0] != 2:
        time.sleep(0.1)

    # print status
    print ("FTP status ", network.ftp.status())
    print ("Telnet status ", network.telnet.status())

    return ap_if
