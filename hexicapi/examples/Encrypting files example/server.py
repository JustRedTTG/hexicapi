import hexicapi.server as server

server.ip = "127.0.0.1" # Set the server ip
server.port = 8181 # Set the server port

# Make a preloaded user that the client can interact with
server.forced_register('Example', 'password', True)


@server.app
def example(Client: server.Iden, message):
    Client.send('ok')
    Client.encrypted_file('test.enc', Client.receive().encode())
    data = Client.decrypted_file('test.enc')
    Client.send(data)


server.run()