import traceback, pickle
from hexicapi.socketMessage import *
from hexicapi.verinfo import __version__, __title__, __author__, __license__, __copyright__
BUFFER_SIZE = 1024

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
    'heartbeat_error':None
}
auth_states = {
    'auth-declined': "Username or Password didn't get accepted",
    'auth-accepted': "Server accepted the details provided",
    'guest-declined': "Guest username didn't get accepted",
    'guest-declined-no-username': "Username declined because it was blank",
    'guest-accepted': "Server accepted the guest username provided",
    'auth-canceled': "Server cancelled authentication.",
}

def arbi(bin):
    return pickle.loads(bin)
def arbi_reverse(*args):
    return pickle.dumps(args)

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

def run(app,username,password='',autoauth=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    calf('connecting', "The client was ran.")
    try:
        s.connect((ip,port))
    except:
        calf('connection_fail', "Couldn't make a connection to the provided port and ip.")
        return
    calf('connection_success', "Was able to connect to the server port and ip.")
    send_all(s, "clientGetID".encode("utf-8"))
    id = recv_all(s, BUFFER_SIZE).decode("utf-8")
    calf('handshake', "First handshake.")
    if autoauth:
        calf('authenticating',"Autoauth was enabled.")
        try:
            send_all(s, str('auth:' + username + ':' + password + ':' + app).encode())
            auth_result = recv_all(s, BUFFER_SIZE).decode('utf-8')
        except:
            calf('disconnect', auth_states['auth-canceled'])
        if auth_result == 'auth-declined' or auth_result == 'guest-declined' or auth_result == 'guest-declined-no-username':
            calf('authentication_fail', auth_states[auth_result])
        else:
            calf('authentication_success', auth_states[auth_result])
    class Client:
        info = {
            'ip':ip,
            'port':port,
            'socket':s,
            'id':id,
            'username':username,
            'app':app
        }
        def heartbeat(self):
            try:
                send_all(self.info['socket'], "clientGetID".encode("utf-8"))
                id = recv_all(self.info['socket'], BUFFER_SIZE).decode("utf-8")
            except:
                id=''
            if id == self.info['id']:
                calf('heartbeat', "The server responded.")
            else:
                calf('heartbeat_error', "The server didn't respond with the same id.")
            return id
        def disconnect(self):
            disconnect_socket(self.info['socket'])
            calf('disconnect', "User called disconnect.")
        def send(self, message):
            try:
                _ = message.decode()
                try:
                    send_all(self.info['socket'], message)
                except Exception as e:
                    print(e)
                    return False
            except:
                try:
                    send_all(self.info['socket'], message.encode())
                except Exception:
                    if debug:
                        print(traceback.format_exc())
                    try:
                        send_all(self.info['socket'], message)
                    except Exception:
                        if debug:
                            print(traceback.format_exc())
                        return False
            return True
        def receive(self, packet_size = BUFFER_SIZE):
            try:
                m = recv_all(self.info['socket'], packet_size)
            except Exception:
                if debug:
                    print(traceback.format_exc())
                return False
            try:
                return m.decode("utf-8")
            except Exception:
                if debug:
                    print(traceback.format_exc())
                return m
        def auth(self, app=None, username=None, password=''):
            calf('authenticating', "Called auth.")
            auth_result = 'auth-declined'
            try:
                send_all(s, str('auth:' + username or self.info['username'] + ':' + password + ':' + app or self.info['app']).encode())
                auth_result = recv_all(s, BUFFER_SIZE).decode('utf-8')
            except:
                calf('disconnect', auth_states['auth-canceled'])
            if auth_result == 'auth-declined' or auth_result == 'guest-declined':
                calf('authentication_fail', auth_states[auth_result])
            else:
                calf('authentication_success', auth_states[auth_result])
    return Client()
