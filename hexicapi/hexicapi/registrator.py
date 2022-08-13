import base64
import os
from cryptography.fernet import Fernet
from hashlib import sha256 as hash256
from hexicapi.verinfo import *
from hexicapi.socketMessage import *
from hexicapi.save import save, load

def password_completer(password:str):
    if len(password)==32: return base64.urlsafe_b64encode(password)
    if len(password)>32: return base64.urlsafe_b64encode(password[32:])
    while len(password)<32: password += '-'
    return base64.urlsafe_b64encode(password.encode('utf-8'))
def encrypt(data, password):
    f = Fernet(password_completer(password))
    return f.encrypt(data)
def encrypt_ring(data, password):
    f = Fernet(password)
    return f.encrypt(data)
def decrypt(data, password):
    f = Fernet(password_completer(password))
    return f.decrypt(data)
def decrypt_ring(data, password):
    f = Fernet(password)
    return f.decrypt(data)

def register_handle(Client, message):
    if message == "check_username":
        username_hash = hash256(Client.username.encode('utf-8')).hexdigest()
        for i in os.listdir('users'):
            if i == username_hash:
                Client.send("not_ok")
                return
        Client.send("ok")
    elif message == "register":
        username_hash = hash256(Client.username.encode('utf-8')).hexdigest()
        for i in os.listdir('users'):
            if i == username_hash:
                Client.send("no")
                return
        Client.send("ready")
        os.mkdir(f'users/{username_hash}')
        password = Client.receive()
        if type(password) != str:
            Client.send('not_ok')
            return
        password_hash = hash256(password.encode('utf-8')).hexdigest()
        with open(f'users/{username_hash}/credential', 'wb') as f: f.write(password_hash.encode('utf-8'))
        Client.send('ready')
        save(f'users/{username_hash}/savedata', {})
        try:
            with open(f'users/{username_hash}/savedata', 'rb+') as f:
                data = f.read()
                f.seek(0)
                f.write(encrypt(data, password))
        except: os.remove(f'users/{username_hash}/savedata')
    else: Client.send("not_ok")





class action:
    def manage_sync(client):
        username_hash = hash256(client.username.encode('utf-8')).hexdigest()
        if os.path.exists(f'users/{username_hash}/savedata'):  # Check for save data
            with open(f'users/{username_hash}/savedata', 'rb') as f:
                data = decrypt_ring(f.read(), client.keyring)  # Read and decrypt the data
                data = load(data)[0]
        else:  # No save data
            data = save(None, {})  # Make a crude empty save
            with open(f'users/{username_hash}/savedata', 'wb') as f:
                f.write(encrypt_ring(data, client.keyring))  # Write down the encrypted data
            data = {}
        data[client.app] = client.data
        data = save(None, data)
        with open(f'users/{username_hash}/savedata', 'wb') as f:
            f.write(encrypt_ring(data, client.keyring))  # Write down the encrypted data
    def auth(client,username,password,app,ag=False):
        username_hash = hash256(username.encode('utf-8')).hexdigest()
        password_hash = hash256(password.encode('utf-8')).hexdigest()
        if username == '': return False, False # Decline the client entirely, how dare they provide an empty username!
        if os.path.exists(f"users/{username_hash}/credential") and password != '':
            with open(f"users/{username_hash}/credential",'r') as f: # Open the credential file
                file_hash = f.read() # Read the credential file's internally stored hash
                if file_hash==password_hash: # Check for matching hashes
                    client.keyring = password_completer(password)
                    if os.path.exists(f'users/{username_hash}/savedata'): # Check for save data
                        with open(f'users/{username_hash}/savedata', 'rb') as f:
                            data = decrypt(f.read(), password) # Read and decrypt the data
                            try: client.data = load(data)[0][app] # Get the app data
                            except: client.data = None # Empty data
                    else: # No save data
                        client.data = None # Empty data
                        data = save(None, {}) # Make a crude empty save
                        with open(f'users/{username_hash}/savedata', 'wb') as f:
                            f.write(encrypt(data, password)) # Write down the encrypted data
                    return True, False # Return Accepted login!
                else: return False, False # Decline guest, because they impersonate a user
        else:
            if password == '': return ag, True # Allow guest, according to app settings
            else: return False, False # Decline auth, because a password and username were attempted




