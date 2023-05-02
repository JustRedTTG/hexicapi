import hexicapi.server as s
from hexicapi.server import Nden

s.sock_msg_debug = True
s.port = 5000

@s.app
def ping(client: Nden, msg):
    print(f"msg: {msg}")
    client.send(msg)

s.allowGuest['ping'] = True

s.run()