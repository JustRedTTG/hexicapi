import hexicapi.server as server

server.ip = "127.0.0.1" # Set the server ip
server.port = 8181 # Set the server port

server.make_world('example', (20, 50), None, {'description': "Welcome to the example world!"})
server.make_world('wonder', (33, 33), None, {'description': "A secondary place of wonder!"})


@server.app
def example(Client: server.Iden, message):
    # Make sure to return or skip any further client chat if worlds handler returned successful
    if server.worlds_handler(Client, message): return
    elif message == 'world_list': # The Client wants to know the worlds available
        Client.send_objects(*server.worlds.keys()) # Send worlds.keys()
    # We don't need much for worlds


server.allowGuest['example'] = True # Allow guest login, aka no password

server.run()