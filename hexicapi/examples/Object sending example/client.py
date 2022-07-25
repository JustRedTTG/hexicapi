import hexicapi.client as client
from random import randint

client.sock_msg_debug = True

# Below is a demonstration of all the different call functions
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


Client = client.run('example', 'Daughter') # Connect

Client.send('gimme object')
objects = Client.receive_objects()

for object in objects:
    print(f"We need {object['amount']} {object['name']}.")
    print(f"According to the server, this is a {object['type']}.")

Client.disconnect() # Disconnect, because we're a nice client