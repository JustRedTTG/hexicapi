import hexicapi.client as client

# All versions beyond hexicapi 1.0.728 allow you to instantly set up a basic array of on call functions
client.basic_on_calf() # Note: provide False if you don't want the colorama colors to the text

client.ip = "127.0.0.1" # Set the server ip
client.port = 8181 # Set the server port

print("""This example comes with a default user:
The username is: Example
The password is: password""")
username = input("Username: ")
password = input("Password: ")

Client = client.run('example', username, password) # Connect

Client.disconnect() # Disconnect, because we're a nice client