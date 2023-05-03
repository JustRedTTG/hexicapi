import hexicapi.server as server

server.ip = "127.0.0.1" # Set the server ip
server.port = 8181 # Set the server port

# Make a preloaded user that the client can interact with
server.forced_register('Example', 'password')

game_data = {
    'level': 0,
    'money': 50
}


@server.app
def example(Client: server.Iden, message):
    if message == 'check_save_data':
        Client.send_objects(Client.data)
    elif message == 'init_save_data':
        Client.data = game_data.copy()
        Client.datasync()
        Client.send('ok')


server.run()