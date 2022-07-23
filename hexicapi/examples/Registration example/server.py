import hexicapi.server as server

server.ip = "127.0.0.1" # Set the server ip
server.port = 8181 # Set the server port

@server.app
def example(Client:dict, message): pass # We don't need much in this case

server.allowGuest['example'] = True # Allow guest login, aka no password

server.run()