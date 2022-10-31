import hexicapi.client as client
from random import randint

# All versions beyond hexicapi 1.0.728 allow you to instantly set up a basic array of on call functions
client.basic_on_calf() # Note: provide False if you don't want the colorama colors to the text

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