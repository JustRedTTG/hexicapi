import hexicapi.server as server

server.ip = "127.0.0.1" # Set the server ip
server.port = 8181 # Set the server port


@server.app
def example(Client: server.Iden, message):
    print(f"\nReceived the following from the client with an id {Client.id} : ") # Print the client ID
    print(message) # Print the received message

    Client.send("example message from the server") # Send a message back :)


server.allowGuest['example'] = True # Allow guest login, aka no password

@server.shadow
def shadow_client(Client: server.NdenClient):
    # The username can be set, but it's handled by the shadow handler
    Client.auth('example')

    Client.send('example message from client')

    message = Client.receive()

    print("Received the following from the server :")
    print(message)
    Client.disconnect()


server.run()