import traceback, pickle

import colorama

from hexicapi.socketMessage import *
from hexicapi.encryption import *
from hexicapi.save import save, load
from hexicapi.verinfo import __version__
BUFFER_SIZE = 1024
FILE_SERVING_SIZE = 32768

ip = "localhost"
port = 81
debug = False

functions={ # print(list(functions)) - > shows all available functions
    'connecting':None,
    'connection_warning':None,
    'connection_fail':None,
    'connection_success':None,
    'authenticating':None,
    'authentication_fail':None,
    'authentication_success':None,
    'handshake':None,
    'disconnect':None,
    'disconnect_soft':None,
    'heartbeat':None,
    'heartbeat_error':None,
    'registering':None,
    'registering_taken':None,
    'registering_complete':None,
    'version_warning':None,
    'version_info':None,
    'version_error':None,
}
auth_states = {
    'auth-declined': "Username or Password didn't get accepted",
    'auth-accepted': "Server accepted the details provided",
    'guest-declined': "Guest username didn't get accepted",
    'guest-declined-no-username': "Username declined because it was blank",
    'guest-accepted': "Server accepted the guest username provided",
    'auth-canceled': "Server cancelled authentication.",
}


def create_lambda_on_calf(text: str, enable_exit: bool = False):
    if enable_exit:
        return lambda reason: [print(x) if x else exit() for x in [text.format(reason=reason, color_reset=colorama.Fore.RESET), None]]
    else:
        return lambda reason: print(text.format(reason=reason))


def basic_on_calf(enable_color = True):
    global functions
    functions['connecting'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTYELLOW_EX if enable_color else ""}Connecting: {{reason}}{colorama.Fore.RESET if enable_color else ""}')
    functions['connection_warning'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTRED_EX if enable_color else ""}Connection error: {{reason}}{colorama.Fore.RESET if enable_color else ""}')
    functions['connection_fail'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTRED_EX if enable_color else ""}Connection error: {{reason}}{colorama.Fore.RESET if enable_color else ""}', True)
    functions['connection_success'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTGREEN_EX if enable_color else ""}Connection successful: {{reason}}{colorama.Fore.RESET if enable_color else ""}')
    functions['authenticating'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTYELLOW_EX if enable_color else ""}Authenticating: {{reason}}{colorama.Fore.RESET if enable_color else ""}')
    functions['authentication_fail'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTRED_EX if enable_color else ""}Authentication error: {{reason}}{colorama.Fore.RESET if enable_color else ""}', True)
    functions['authentication_success'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTGREEN_EX if enable_color else ""}Authentication successful: {{reason}}{colorama.Fore.RESET if enable_color else ""}')
    functions['handshake'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTGREEN_EX if enable_color else ""}Handshake: {{reason}}{colorama.Fore.RESET if enable_color else ""}')
    functions['disconnect'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTCYAN_EX if enable_color else ""}Closing due to disconnect... {{reason}}{colorama.Fore.RESET if enable_color else ""}', True)
    functions['disconnect_soft'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTCYAN_EX if enable_color else ""}Soft disconnect... {{reason}}{colorama.Fore.RESET if enable_color else ""}')
    functions['heartbeat'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTCYAN_EX if enable_color else ""}Heartbeat: {{reason}}{colorama.Fore.RESET if enable_color else ""}')
    functions['heartbeat_error'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTRED_EX if enable_color else ""}Heartbeat error: {{reason}}{colorama.Fore.RESET if enable_color else ""}', True)
    functions['version_warning'] = create_lambda_on_calf(f'{colorama.Fore.YELLOW if enable_color else ""}Version warning: {{reason}}{colorama.Fore.RESET if enable_color else ""}')
    functions['version_info'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTBLACK_EX if enable_color else ""}Version information: {{reason}}{colorama.Fore.RESET if enable_color else ""}')
    functions['version_error'] = create_lambda_on_calf(f'{colorama.Fore.LIGHTRED_EX if enable_color else ""}Version error: {{reason}}{colorama.Fore.RESET if enable_color else ""}', True)


def on_calf(f):
    functions[f.__name__] = f

def calf(name, reason='No reason provided for the cause'):
    f = functions[name]
    if f != None:
        if type(f) == list:
            f[0](f[1], reason)
        else:
            f(reason)

def disconnect_socket(client, softly: bool = False):
    try:
        send_all(client, 'bye_soft'.encode() if softly else 'bye'.encode())
        recv_all(client)
    except:
        pass
    client.socket.close()
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
        self.silent: bool = False

    def heartbeat(self, force_okay: bool = False, silent: bool = True):
        try:
            send_all(self, "clientGetID".encode("utf-8"), enc=self.enc_public)
            id = recv_all(self, BUFFER_SIZE, enc=self.enc_private).decode("utf-8")
        except: id=''
        if id == self.id or force_okay:
            if not silent: calf('heartbeat', "The server responded.")
        else: calf('heartbeat_error', "The server didn't respond with the same id.")
        return id

    def disconnect(self, softly: bool = False, silent: bool = True):
        disconnect_socket(self, softly)
        if softly and not silent:
            calf('disconnect_soft', "User called soft disconnect.")
        elif not softly:
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
        if skip_str: return m
        try: return m.decode("utf-8")
        except Exception:
            if debug: print(traceback.format_exc())
            return m

    def send_objects(self, *objs):
        self.send(save(None, *objs))

    def receive_objects(self, packet_size=BUFFER_SIZE):
        return load(self.receive(packet_size))

    def auth(self, app=None, username=None, password='', silent: bool = False):
        if not silent: calf('authenticating', "Called auth.")
        auth_result = 'auth-declined'
        try:
            send_all(self, f'auth:{username or self.username}:{password}:{app or self.app}'.encode(), enc=self.enc_public)
            auth_result = recv_all(self, BUFFER_SIZE, enc=self.enc_private).decode('utf-8')
        except: calf('disconnect', auth_states['auth-canceled'])
        if auth_result == 'auth-declined' or auth_result == 'guest-declined': calf('authentication_fail', auth_states[auth_result])
        elif not silent: calf('authentication_success', auth_states[auth_result])
        if auth_result == 'auth-accepted':
            self.id = self.heartbeat(True)

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
            data += self.receive(skip_str=True, packet_size=length)
            self.send('ok')
        return data

    def join_world(self, name):
        self.send(f'worlds:join:{name}') # Join request
        if self.receive() == 'not ok': return False # Can't join
        self.send('ready') # Ready to receive world data
        return self.receive_objects()[0] # World dictionary from the server

    def update_world(self, position: tuple = None, data: any = None, all_data: bool = False):
        self.send(f'worlds:position') # Update request
        if self.receive() == 'not ok': return False # Can't access update
        packet = {
            'all_data': all_data
        }
        if position:
            packet['position'] = position
        if data:
            packet['data'] = data
        self.send_objects(packet)
        response_positions, response_data = self.receive_objects()
        return response_positions, response_data

    def handle_world_data(self, positions: dict, datas: dict, position: tuple = None, data: any = None):
        response_positions, response_data = self.update_world(position, data, True)
        for key, value in response_positions.items():
            if not value and key in positions.keys():
                del positions[key]
            elif value:
                positions[key] = value
        for key, value in response_data.items():
            if not value and key in datas.keys():
                del datas[key]
            elif value:
                datas[key] = value

    def reconnect(self, password: str = ''):
        return run(self.app, self.username, password, silent=self.silent)



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
        data = id_enc.split('\r\n')
        id = data[0]
        version = data[1].split("'")[1]
        enc_public = data[2]
        if version != __version__:
            calf('version_warning', f"server: {version} client: {__version__}")
        elif not silent:
            calf('version_info', version)
    except:
        if not version == __version__:
            calf('connection_warning', "probably... banned or version error")
            calf('version_error', f"server: {version} client: {__version__}")
        else:
            calf('connection_fail', "probably... banned or internal error")
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
        cli.auth(password=password, silent=silent)
    cli.silent = silent
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