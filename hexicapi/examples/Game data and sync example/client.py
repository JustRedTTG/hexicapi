import hexicapi.client as client
from random import randint

# Below is a demonstration of all the different call functions
@client.on_calf
def connecting(reason): print(f'Connecting: {reason}')

@client.on_calf
def connection_fail(reason):
    print(f'Connection error: {reason}')
    exit()

@client.on_calf
def connection_success(reason): print(f'Connection successful: {reason}')

@client.on_calf
def authenticating(reason): print(f'Authenticating: {reason}')

@client.on_calf
def authentication_fail(reason):
    print(f'Authentication error: {reason}')
    exit()

@client.on_calf
def disconnect(reason):
    print(f'Closing due to disconnect... {reason}')
    exit()

client.ip = "127.0.0.1" # Set the server ip
client.port = 8181 # Set the server port


Client = client.run('example', 'Example', 'password') # Connect

Client.send('check_save_data')
save = Client.receive_objects()[0]
if not save:
    print('The account has no save data. Waiting on the server to make one...')
    Client.send('init_save_data')
    Client.receive(2)
    print('Run again to view save data.')
    Client.disconnect()

print(f"The account is on level {save['level']} with {save['money']}$")


Client.disconnect() # Disconnect, because we're a nice client