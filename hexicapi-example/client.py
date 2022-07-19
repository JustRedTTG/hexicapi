import hexicapi.client as client

@client.on_calf
def authentication_fail(reason):
    print("authentication error")
    print(reason)
    exit()
@client.on_calf
def connection_fail(reason):
    print('connection error')
    print(reason)
    exit()
@client.on_calf
def disconnect(reason):
    print('closing due to disconnect...')
    print(reason)
    exit()

client.ip = "127.0.0.1" # Set the server ip
client.port = 8181 # Set the server port

Client = client.run('example','guest') # Connect

Client.send('example message from client') # Send a message to the server
message = Client.receive() # Receive a message from the server

print("Received the following from the server :")
print(message) # Print the received message


Client.disconnect() # Disconnect, because we're a nice client