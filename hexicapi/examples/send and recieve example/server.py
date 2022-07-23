import hexicapi.server as server

server.ip = "127.0.0.1" # Set the server ip
server.port = 8181 # Set the server port

@server.app
def example(Client:dict, message):
    """{
    'id': "index'10 characters",
    'socket': socket,
    'thread': boolean - if the client is active,
    'calldelta': last time of call,
    'username': 'guest',
    'guest': boolean - if the client is a guest,
    'auth': boolean - if the client is authenticated,
    'app': 'A string - the app name',
    'data': None - user used variable,
    'die': boolean - if the client should expire,
    'room': None - user used variable
    }"""
    print(f"\nReceived the following from the client with an id {Client.id} : ") # Print the client ID
    print(message) # Print the received message

    Client.send("example message from the server") # Send a message back :)

server.allowGuest['example'] = True # Allow guest login, aka no password

server.run()