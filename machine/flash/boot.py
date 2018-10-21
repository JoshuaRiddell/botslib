# This file is executed on every boot (including wake-boot from deepsleep)
import sys
import gc
import network
import time
import json

def reload(mod):
    "De-allocate module, garbage collect and then reload module."

    mod_name = mod.__name__
    del sys.modules[mod_name]
    gc.collect()
    return __import__(mod_name)

def setup_wlan():
    "create wlan object and start telnet and ftp server"

    with open("/flash/network_config.json") as fd:
        wifi_config = json.load(fd)

    ssid = wifi_config.get("ssid")
    wifimode = wifi_config.get("wifimode")
    passkey = wifi_config.get("passkey")
    user = wifi_config.get("user")
    password = wifi_config.get("password")

    # create wlan object
    if wifimode == "AP":
        wlan = network.WLAN(network.AP_IF)
        wlan.config(essid=ssid)
    elif wifimode == "STA":
        wlan = network.WLAN(network.STA_IF)
        wlan.connect(ssid, passkey)
    else:
        print("Wifi disabled")

    # activate wlan
    wlan.active(True)
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

    return wlan
