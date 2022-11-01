import hexicapi.client as client
from random import randint

# All versions beyond hexicapi 1.0.728 allow you to instantly set up a basic array of on call functions
client.basic_on_calf() # Note: provide False if you don't want the colorama colors to the text

client.ip = "127.0.0.1" # Set the server ip
client.port = 8181 # Set the server port

Client = client.run('example',f'guest{randint(111,999)}') # Connect

Client.send('world_list')
worlds = Client.receive_objects()
Client.disconnect(True) # Disconnect, because we're a nice client

print("""Please write the name of the world you wanna join.
Available worlds: """, *worlds, sep='\n')
world_name = input('> ')

# Reconnect
Client = client.run('example',f'guest{randint(111,999)}') # Connect

world = Client.join_world(world_name)
if not world:
    print("Couldn't join the world :(")
    Client.disconnect()

print(f'World: {world}')
print(f"{world_name} description: \n{world['description']}")

positions, datas = {}, {} # Set blank positions and datas
Client.handle_world_data(positions, datas) # Get everything stored into positions and datas

print(f"Positions: {positions}, Data: {datas}") # Print beginning world positions and data

Client.handle_world_data(positions, datas, (60, 60), 'Example string as data') # Update client data

print(f"UPDATED Positions: {positions}, Data: {datas}") # Print updated world positions and data

Client.disconnect() # Disconnect, because we're a nice client