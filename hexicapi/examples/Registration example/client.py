import hexicapi.client as client
from random import randint

# Below is a demonstration of all the different call functions

@client.on_calf
def registering(reason): print(f'Registering {reason}')

@client.on_calf
def registering_taken(reason):
    print(reason)
    exit()

@client.on_calf
def registering_complete(reason): print(f'Registration completed! {reason}')

@client.on_calf
def connecting(reason): print(f'Connecting: {reason}')

@client.on_calf
def connection_fail(reason):
    print(f'Connection error: {reason}')
    exit()

@client.on_calf
def connection_success(reason): print(f'Connection successful: {reason}')

@client.on_calf
def authenticating(reason): print(f'Authenticating: {reason}')

@client.on_calf
def authentication_fail(reason):
    print(f'Authentication error: {reason}')
    exit()

@client.on_calf
def disconnect(reason):
    print(f'Closing due to disconnect... {reason}')
    exit()

client.ip = "127.0.0.1" # Set the server ip
client.port = 8181 # Set the server port

username = input("Username: ")
password = input("Password: ")

client.register(username, password) # Register

Client = client.run('example', username, password) # Connect

Client.disconnect() # Disconnect, because we're a nice client