import hexicapi.client as client
from random import randint

client.sock_msg_debug = True

# All versions beyond hexicapi 1.0.728 allow you to instantly set up a basic array of on call functions
client.basic_on_calf() # Note: provide False if you don't want the colorama colors to the text

client.HOST = "127.0.0.1:8181" # Set the server host


Client = client.run('example', 'Daughter') # Connect

Client.send('gimme object')
objects = Client.receive_objects()

for obj in objects:
    print(f"We need {obj['amount']} {obj['name']}.")
    print(f"According to the server, this is a {obj['type']}.")

Client.disconnect() # Disconnect, because we're a nice client