import hexicapi.server as server

server.ip = "127.0.0.1" # Set the server ip
server.port = 8181 # Set the server port

# Make a preloaded user that the client can interact with
server.forced_register('Example', 'password', True)
server.elevate_privilege('Example') # These privileges can only be set by the server!
# server.diminish_privilege('Example') # Reverse the admin privileges


@server.app
def example(Client: server.Iden, message):
    if message == 'some admin business':
        if Client.admin:
            Client.send('ok')
        else:
            Client.send('not ok')


server.run()