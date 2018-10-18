from microWebSrv import MicroWebSrv
import time



def _acceptWebSocketCallback(webSocket, httpClient) :
  print("WS ACCEPT")
  webSocket.RecvTextCallback   = _recvTextCallback
  webSocket.RecvBinaryCallback = _recvBinaryCallback
  webSocket.ClosedCallback     = _closedCallback

def _recvTextCallback(webSocket, msg) :
  print(msg)
  type  = msg[0]
  val = int(msg[2:len(msg)]) 
  print(type,val)
  webSocket.SendText("Reply for %s" % msg)


def _recvBinaryCallback(webSocket, data) :
  print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket) :
  print("WS CLOSED")
  

mws = MicroWebSrv()                                    # TCP port 80 and files in /flash/www
mws.MaxWebSocketRecvLen     = 256                      # Default is set to 1024
mws.WebSocketThreaded       = False                    # WebSockets without new threads
mws.AcceptWebSocketCallback = _acceptWebSocketCallback# Function to receive WebSockets
mws.Start() 



while True: time.sleep(0.1)


