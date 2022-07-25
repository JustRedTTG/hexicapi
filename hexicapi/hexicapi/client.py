import traceback, pickle
from hexicapi.socketMessage import *
from hexicapi.encryption import *
from hexicapi.save import save, load
from hexicapi.verinfo import *
BUFFER_SIZE = 1024
FILE_SERVING_SIZE = 2048

ip = "localhost"
port = 81
debug = False

functions={ # print(list(functions)) - > shows all available functions
    'connecting':None,
    'connection_fail':None,
    'connection_success':None,
    'authenticating':None,
    'authentication_fail':None,
    'authentication_success':None,
    'handshake':None,
    'disconnect':None,
    'heartbeat':None,
    'heartbeat_error':None,
    'registering':None,
    'registering_taken':None,
    'registering_complete':None,
}
auth_states = {
    'auth-declined': "Username or Password didn't get accepted",
    'auth-accepted': "Server accepted the details provided",
    'guest-declined': "Guest username didn't get accepted",
    'guest-declined-no-username': "Username declined because it was blank",
    'guest-accepted': "Server accepted the guest username provided",
    'auth-canceled': "Server cancelled authentication.",
}

def on_calf(f):
    functions[f.__name__] = f

def calf(name, reason='No reason provided for the cause'):
    f = functions[name]
    if f != None:
        if type(f) == list:
            f[0](f[1], reason)
        else:
            f(reason)

def disconnect_socket(s):
    try:
        send_all(s, 'bye'.encode())
    except:
        pass
    s.close()
class CLI:
    def __init__(self, id, s):
        self.id = id
        self.socket = s
class Client:
    def __init__(self, ip, port, s, id, enc_private, enc_public, username, app):
        self.ip = ip
        self.port = port
        self.socket = s
        self.id = id
        self.enc_private = enc_private
        self.enc_public = enc_public
        self.username = username
        self.app = app
    def heartbeat(self):
        try:
            send_all(self, "clientGetID".encode("utf-8"), enc=self.enc_public)
            id = recv_all(self, BUFFER_SIZE, enc=self.enc_private).decode("utf-8")
        except: id=''
        if id == self.id: calf('heartbeat', "The server responded.")
        else: calf('heartbeat_error', "The server didn't respond with the same id.")
        return id
    def disconnect(self):
        disconnect_socket(self.socket)
        calf('disconnect', "User called disconnect.")
    def send(self, message):
        if not isinstance(message, str):
            try: send_all(self, message, enc=self.enc_public)
            except: return False
        else:
            try: send_all(self, message.encode(), enc=self.enc_public)
            except Exception:
                if debug: print(traceback.format_exc())
                try: send_all(self, message, enc=self.enc_public)
                except Exception:
                    if debug: print(traceback.format_exc())
                    return False
        return True
    def receive(self, packet_size = BUFFER_SIZE, skip_str=False):
        try: m = recv_all(self, packet_size, enc=self.enc_private)
        except Exception:
            if debug: print(traceback.format_exc())
            return False
        try: return m.decode("utf-8")
        except Exception:
            if debug: print(traceback.format_exc())
            return m
    def send_objects(self, *objs):
        self.send(save(None, *objs))
    def receive_objects(self, packet_size=BUFFER_SIZE):
        return load(self.receive(packet_size))
    def auth(self, app=None, username=None, password=''):
        calf('authenticating', "Called auth.")
        auth_result = 'auth-declined'
        try:
            send_all(self, f'auth: {username or self.username}:{password}:{app or self.app}'.encode(), enc=self.enc_public)
            auth_result = recv_all(self, BUFFER_SIZE, enc=self.enc_private).decode('utf-8')
        except: calf('disconnect', auth_states['auth-canceled'])
        if auth_result == 'auth-declined' or auth_result == 'guest-declined': calf('authentication_fail', auth_states[auth_result])
        else: calf('authentication_success', auth_states[auth_result])
    def send_large(self, data):
        self.send(str(len(data)))
        self.receive()
        if len(data) <= FILE_SERVING_SIZE:
            self.send(data)
            self.receive()
        for i in range(0, len(data), FILE_SERVING_SIZE):
            self.send(data[i:i+FILE_SERVING_SIZE])
            self.receive()
    def receive_large(self):
        length = int(self.receive())
        self.send('ok')
        data = b''
        while len(data) < length:
            data += self.receive(skip_str=True, BUFFER_SIZE=length)
            self.send('ok')
        return data

        

def run(app,username,password='',autoauth=True, silent=False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not silent: calf('connecting', "The client was ran.")
    try:
        s.connect((ip,port))
    except:
        calf('connection_fail', "Couldn't make a connection to the provided port and ip.")
        return
    if not silent: calf('connection_success', "Was able to connect to the server port and ip.")
    send_all(s, "clientGetID".encode("utf-8"))
    id_enc = recv_all(s, BUFFER_SIZE, skip=True).decode('utf-8')
    try:
        id, enc_public = id_enc.split('\r\n')
    except:
        calf('connection_fail', "probably... BANNED")
        return None

    enc_public = enc_public.encode('utf-8')
    enc_public = serialization.load_pem_public_key(
        enc_public
    )
    enc_private, public_key = generate_keys()
    send_all(CLI(id, s), public_key, skip=True)
    recv_all(CLI(id, s), enc=enc_private)
    if not silent: calf('handshake', "Encryption handshake.")

    cli = Client(ip, port, s, id, enc_private, enc_public, username, app)

    if autoauth:
        if not silent: calf('authenticating',"Autoauth was enabled.")
        cli.auth(password=password)
    return cli

def register(username, password):
    calf('registering', 'Begin Registration.')
    Client = run('registration', username, silent=True)
    Client.send("check_username")
    status = Client.receive()
    if status == 'not_ok':
        calf('registering_taken', 'The username is taken')
        Client.disconnect()
        return
    Client.send("register")
    if not Client.receive() == 'ready': return
    Client.send(password)
    if not Client.receive() == 'ready': return
    calf('registering_complete', 'Account created')
