import hexicapi.client as client

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
def authentication_success(reason): print(f'Authentication successful: {reason}')

@client.on_calf
def handshake(reason): print(f'Handshake: {reason}')

@client.on_calf
def disconnect(reason):
    print(f'Closing due to disconnect... {reason}')
    exit()

@client.on_calf
def heartbeat(reason): print(f'Heartbeat: {reason}')

@client.on_calf
def heartbeat_error(reason):
    print(f'Heartbeat error: {reason}')
    exit()

client.ip = "127.0.0.1" # Set the server ip
client.port = 8181 # Set the server port

Client = client.run('example','guest') # Connect

Client.send('example message from client') # Send a message to the server
message = Client.receive() # Receive a message from the server

print("Received the following from the server :")
print(message) # Print the received message


Client.disconnect() # Disconnect, because we're a nice client