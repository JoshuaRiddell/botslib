import network
import time
import json
from microWebSrv import MicroWebSrv

def setup_wlan():
    "Create wlan object and start telnet and ftp server"

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

def setup_web_server(accept_socket_cb):
    "Setup http webserver."
    
    mws = MicroWebSrv()
    mws.MaxWebSocketRecvLen = 256
    mws.WebSocketThreaded = False
    mws.AcceptWebSocketCallback = accept_socket_cb
    mws.Start()

