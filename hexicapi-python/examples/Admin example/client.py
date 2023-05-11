import hexicapi.client as client

# All versions beyond hexicapi 1.0.728 allow you to instantly set up a basic array of on call functions
client.basic_on_calf() # Note: provide False if you don't want the colorama colors to the text

client.HOST = "127.0.0.1:8181" # Set the server host

Client = client.run('example', 'Example', 'password') # Connect

Client.send('some admin business') # Request some admin business
if Client.receive() == 'ok': # Check if we succeeded
    print('YAY, the server is accepting admin business from us')
else:
    print('\nThe server is not accepting admin business from us\n')

Client.disconnect() # Disconnect, because we're a nice client