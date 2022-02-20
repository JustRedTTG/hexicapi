import socket

ip = "localhost"
port = 81
functions={
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
def on_calf(f):
    functions[f.__name__] = f

def calf(name):
    f = functions[name]
    if f != None:
        if type(f) == list:
            f[0](f[1])
        else:
            f()

def disconnect_socket(s):
    try:
        s.send('bye'.encode())
    except:
        pass
    s.close()

def run(app,username,password='',autoauth=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    calf('connecting')
    try:
        s.connect((ip,port))
    except:
        calf('connection_fail')
        return
    calf('connection_success')
    s.send("clientGetID".encode("utf-8"))
    id = s.recv(1024).decode("utf-8")
    calf('handshake')
    if autoauth:
        calf('authenticating')
        try:
            s.send(str('auth:' + username + ':' + password + ':' + app).encode())
            auth_result = s.recv(1024).decode('utf-8')
        except:
            calf('disconnect')
        if auth_result == 'auth-declined' or auth_result == 'guest-declined':
            calf('authentication_fail')
        else:
            calf('authentication_success')
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
                self.info['socket'].send("clientGetID".encode("utf-8"))
                id = self.info['socket'].recv(1024).decode("utf-8")
            except:
                id=''
            if id == self.info['id']:
                calf('heartbeat')
            else:
                calf('heartbeat_error')
            return id
        def disconnect(self):
            disconnect_socket(self.info['socket'])
            calf('disconnect')
        def send(self, message):
            try:
                _ = message.decode()
                try:
                    self.info['socket'].send(message)
                except Exception as e:
                    print(e)
                    return False
            except:
                try:
                    self.info['socket'].send(message.encode())
                except:
                    try:
                        self.info['socket'].send(message)
                    except Exception as e:
                        print(e)
                        return False
            return True
        def receive(self, size = 1024):
            try:
                m = self.info['socket'].recv(size)
            except:
                return False
            try:
                return m.decode("utf-8")
            except:
                return m
        def auth(self, app, username, password=''):
            calf('authenticating')
            auth_result = 'auth-declined'
            try:
                s.send(str('auth:' + username + ':' + password + ':' + app).encode())
                auth_result = s.recv(1024).decode('utf-8')
            except:
                calf('disconnect')
            if auth_result == 'auth-declined' or auth_result == 'guest-declined':
                calf('authentication_fail')
            else:
                calf('authentication_success')
    return Client()
