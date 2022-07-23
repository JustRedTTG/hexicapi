import hexicapi.server as server

server.ip = "127.0.0.1" # Set the server ip
server.port = 8181 # Set the server port

objects = [
    {'amount':3, 'type':'fruit', 'name':'Apples'},
    {'amount':5, 'type':'fruit', 'name':'Bananas'},
    {'amount':2, 'type':'vegetable', 'name':'Cucumbers'}
]

@server.app
def example(Client:server.Iden, message):
    if message == 'gimme object':
        Client.send_objects(*objects)

server.allowGuest['example'] = True

server.run()