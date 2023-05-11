import hexicapi.client as client

# All versions beyond hexicapi 1.0.728 allow you to instantly set up a basic array of on call functions
client.basic_on_calf() # Note: provide False if you don't want the colorama colors to the text

client.HOST = "127.0.0.1:8181" # Set the server host

Client = client.run('example', 'Example', 'password') # Connect

print(f"\nThis is my custom ID: {Client.id}\n")

Client.disconnect() # Disconnect, because we're a nice client