import hexicapi.server as server

server.ip = "127.0.0.1" # Set the server ip
server.port = 8181 # Set the server port

# Make a preloaded user that the client can interact with
server.forced_register('Example', 'password', True)


@server.app
def example(Client: server.Iden, message): pass # We don't need much in this case


server.run()