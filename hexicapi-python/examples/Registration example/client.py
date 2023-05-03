import hexicapi.client as client
from random import randint

# All versions beyond hexicapi 1.0.728 allow you to instantly set up a basic array of on call functions
client.basic_on_calf() # Note: provide False if you don't want the colorama colors to the text

client.ip = "127.0.0.1" # Set the server ip
client.port = 8181 # Set the server port

username = input("Username: ")
password = input("Password: ")

client.register(username, password) # Register

Client = client.run('example', username, password) # Connect

Client.disconnect() # Disconnect, because we're a nice client