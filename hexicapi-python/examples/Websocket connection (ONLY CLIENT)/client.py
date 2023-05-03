import hexicapi.client as c
from hexicapi.connectors import WebsocketConnector

c.HOST = 'wss://..................'
# You can use with cloudflare access / cloudflare tunnel / zero trust
# or any other HTTP/HTTP TCP websocket server hooked up using hexic api!
c.basic_on_calf()

client = c.run('ping', 'guest', connector=WebsocketConnector)

client.send('Hi')
print(client.receive())

client.disconnect()