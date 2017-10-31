from consumers import *
from channels import route

server_routing = [
    route('websocket.connect', ws_connect),
    route('websocket.receive', ws_receive),
    route('websocket.disconnect', ws_disconnect),
]