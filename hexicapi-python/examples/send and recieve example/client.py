import hexicapi.client as client
from random import randint

# All versions beyond hexicapi 1.0.728 allow you to instantly set up a basic array of on call functions
client.basic_on_calf() # Note: provide False if you don't want the colorama colors to the text

client.HOST = "127.0.0.1:8181" # Set the server host

Client = client.run('example',f'guest{randint(111,999)}') # Connect

print() # Padding

Client.send('example message from client') # Send a message to the server
message = Client.receive() # Receive a message from the server

print("Received the following from the server :")
print(message) # Print the received message

print() # Padding

Client.disconnect() # Disconnect, because we're a nice client