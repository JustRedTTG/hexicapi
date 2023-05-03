import threading,traceback
from hexicapi.socketMessage import *
from hexicapi.verinfo import __version__
from hexicapi.client import Client
from random import randint
from hexicapi.save import save, load
from hexicapi.encryption import *
from hexicapi.registrator import *
import hexicapi.redlogger as logg
private_key, public_key = None, None
silent = False
log = True
ltar = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
identifier = 0
BUFFER_SIZE = 1024
FILE_SERVING_SIZE = 32768
ip = "localhost"
port = 81
    #webport=80
    #webpage=web.mainPage
#variables
ipbans = []
connections = []
rooms = []
free = []
s = None
#
allowGuest = {'registration':True}
apps = []
shadows = []
app_disconnect_handle={}
#
console = [["Welcome To The Server!","all"]]
worlds = {}

class WorldRoom:
    world: str
    id: str
    knows = {}
    knows_data = {}
    def __init__(self, world, id):
        self.world = world
        self.id = id
    def disconnect(self):
        worlds[self.world]['players'].remove(self.id)
        del worlds[self.world]['positions'][self.id]
        del worlds[self.world]['data'][self.id]


class Iden:
    def __init__(self, id, cs):
        self.id = id
        self.socket = cs
        self.thread = True
        self.calldelta = time.time()
        self.username = "Guest"
        self.guest = True
        self.auth = False
        self.app = None
        self.data = None
        self.keyring = None
        self.die = True
        self.room = None
        self.lock = False
        self.admin = False
        self.shadow = False

    def send(self, message):
        try:
            _ = message.decode()
            send_all(self, message,enc=self.key)
        except (AttributeError, UnicodeDecodeError) as e:
            try: send_all(self, message.encode(),enc=self.key)
            except: send_all(self, message,enc=self.key)
        except: # Asume socket falt
            del self.socket
            self.thread = False

    def receive(self, packet_size = BUFFER_SIZE, skip_str=False):
        try: m = recv_all(self, packet_size,enc=private_key)
        except: return False
        if skip_str: return m
        try: return m.decode("utf-8")
        except: return m

    def send_objects(self, *objs):
        self.send(save(None, *objs))

    def receive_objects(self, packet_size = BUFFER_SIZE):
        return load(self.receive(packet_size))

    def datasync(self):
        if self.guest: return
        action.manage_sync(self)

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

    def custom_id(self, id):
        return custom_id(self.username, id, True)

    def elevate_privilege(self):
        return elevate_privilege(self.username)

    def diminish_privilege(self):
        return diminish_privilege(self.username)

    def encrypted_file(self, name, data):
        username_hash = hash256(self.username.encode()).hexdigest()
        return encrypt_file_ring(os.path.join('users',username_hash, name), data, self.keyring)

    def decrypted_file(self, name):
        username_hash = hash256(self.username.encode()).hexdigest()
        return decrypt_file_ring(os.path.join('users', username_hash, name), self.keyring)

class NdenClient(Client):
    app = 'shadow'
    username = f'shadow{randint(111,999)}'
    active = True
    received = None
    received_objects = None
    sent = None
    sent_objects = None
    id = None
    c = None
    authed = False
    def __init__(self):
        pass

    def send(self, message):
        self.sent = message

    def receive(self):
        while not self.received: pass
        temp, self.received = self.received, None
        return temp

    def send_objects(self, *objs):
        self.sent_objects = objs

    def receive_objects(self):
        while not self.received_objects: pass
        temp, self.received_objects = self.received_objects, None

        return temp

    def disconnect(self):
        complete_grid_off(self.c, logg.shadow)

    def heartbeat(self):
        return self.id

    def auth(self, app=None, username=None, password=''):
        if password:
            logg.shadow('Account authentication is not possible for a shadow client', logg.WARNING)
        if username:
            self.username = username
        self.app = app
        self.authed = True


class Nden(Iden):
    def __init__(self, id):
        super().__init__(id, None)
        self.die = False
        self.shadow = True
        self.client = NdenClient()

    def send(self, message):
        self.client.received = message

    def receive(self):
        while not self.client.sent: pass
        temp, self.client.sent = self.client.sent, None
        return temp

    def send_objects(self, *objs):
        self.client.received_objects = objs

    def receive_objects(self):
        while not self.client.sent_objects: pass
        temp, self.client.sent_objects = self.client.sent_objects, None
        return temp

# Make ID for client
def makeID(cs=None):
    global identifier, ltar, free
    num=None
    if len(free)>0:
        num = free[0]
        id = str(connections[num].id.split("'")[0])+"'"
        del free[0]
    else:
        id=str(identifier)+"'"
        identifier+=1
    for r in range(10):
        id+=ltar[randint(0,len(ltar)-1)]
    if num==None:
        num2=len(connections)
    else:
        num2=num
    if cs:
        iden = Iden(id, cs)
    else:
        iden = Nden(id)
    if num == None:
        connections.append(iden)
    else:
        connections[num] = iden
    return id,num2


def is_socket_closed(sock):
    try:
        sock.send("".encode())
        return False
    except:
        return True


def get_allow_guest(app):
    try:
        return allowGuest[app]
    except: return False


die=False
timeout = 3

# Handle Updates
def discon(c):
    if connections[c].id in working: rm_record(connections[c].id)
    else:
        try:
            if connections[c].socket.getsockname() in working: rm_record(connections[c].socket.getsockname())
        except: pass


def complete_grid_off(c, logger):
    ret = True
    if c > len(connections)-1: return False
    if not connections[c].thread: return False
    try:
        if connections[c].app in app_disconnect_handle:
            ret = app_disconnect_handle[connections[c].app](connections[c])
            if ret is None: ret = True
    except Exception:
        if log:
            logger(f"Client disconnect handle, failed.", logg.ERROR)
        ret = False
    if connections[c].room:
        try:
            connections[c].room.disconnect()
        except AttributeError:
            if log:
                logger("Room doesn't have disconnect function or it failed", logg.WARNING)

    discon(c)
    connections[c].thread = False
    console.append([connections[c].username + " disconnected", connections[c].app])
    connections[c].username = "Guest"
    connections[c].auth = False
    connections[c].keyring = None
    connections[c].data = None
    connections[c].app = None
    free.append(c)
    if ret:
        if log:
            logger(f"Client {connections[c].id} disconnected...")
    return ret


def server():
    while not die:
        for c in range(len(connections)):
            if (not connections[c].lock) and connections[c].thread and connections[c].die:
                if is_socket_closed(connections[c].socket) or time.time()-connections[c].calldelta > timeout:
                    complete_grid_off(c, logg.server)
        #print(connections)
        while len(console)>50:
            del console[0]
        clean_working_record()
        time.sleep(1)


def stop():
  global die, s
  die=True
  logg.close_log()
  s.close()


app_handle={'registration':register_handle}

# Handle Clients
def client_handle(cs,c):
    send_all(cs, f"{connections[c].id}\r\n'{__version__}'\r\n{public_key.decode('utf-8')}".encode('utf-8'), skip=True)
    connections[c].key = serialization.load_pem_public_key(
        recv_all(cs, skip=True)
    )
    send_all(cs, b'ok', enc=connections[c].key)
    while connections[c].thread and not die:
        try:
            try:
                m = recv_all(connections[c], BUFFER_SIZE, enc=private_key)
            except:
                break
            if len(m)>0:
                delta=time.time()-connections[c].calldelta
                connections[c].calldelta=time.time()
            try:
                d=m.decode()
                string=True
            except:
                d=m
                string=False
            if d == 'clientGetID':
                send_all(connections[c], connections[c].id.encode(),enc=connections[c].key)
            elif d == 'bye':
                send_all(connections[c], 'see you later!'.encode())
                complete_grid_off(c, logg.client_handle)
                break
            elif d == 'bye_soft':
                send_all(connections[c], 'see you later!'.encode())
                complete_grid_off(c, logg.client_handle_soft)
                break
            elif string and d.split(":")[0] == "auth":
                _, username, password, app = d.split(":")
                if username == '':
                    send_all(connections[c], "guest-declined-no-username".encode(),enc=connections[c].key)
                    break
                id_before = connections[c].id
                accept,guest=action.auth(connections[c],username,str(password),app,get_allow_guest(app))
                if accept and not guest:
                    connections[c].username=username
                    connections[c].app=app
                    connections[c].auth=True
                    connections[c].guest=False
                    send_all(connections[c], "auth-accepted".encode(),enc=connections[c].key)
                    console.append([f"User {username} logged on", app])
                    if log:
                        logg.client_handle_soft(f"Client {id_before} -> {connections[c].id} authenticated!")
                elif accept and guest:
                    no=True
                    for con in connections:
                        if con.username==username:
                            send_all(connections[c], "guest-declined".encode(),enc=connections[c].key)
                            no=False
                            break
                    if no:
                        connections[c].username = username
                        connections[c].app = app
                        connections[c].auth = True
                        send_all(connections[c], "guest-accepted".encode(),enc=connections[c].key)
                        console.append([f"Guest {username} hopped in", app])
                elif guest and not accept:
                    send_all(connections[c], "guest-declined".encode(),enc=connections[c].key)
                else:
                    send_all(connections[c], "auth-declined".encode(),enc=connections[c].key)
            else:
                if connections[c].auth:
                    if connections[c].app in app_handle.keys():
                        connections[c].lock = True
                        try:
                            app_handle[connections[c].app](connections[c],d)
                        except:
                            traceback.print_exc()
                        # Heartbeat the client after app handle, so it doesn't die
                        connections[c].calldelta = time.time()
                        connections[c].lock = False
                elif d!="" and connections[c].thread:
                    print("message: "+d)
                    send_all(connections[c], "request-declined".encode(),enc=connections[c].key)
        except Exception:
            if is_socket_closed(connections[c].socket):
                break
            else:
                connections[c].lock = False
                print("client error occurred")
                traceback.print_exc()
            break

    connections[c].socket.close()

def shadow_handle(c):
    while connections[c].client.active and not die:
        m = connections[c].receive()
        if not connections[c].auth:
            connections[c].auth = True
            connections[c].client.id = connections[c].id
            connections[c].client.c = c
            connections[c].username = connections[c].client.username

        if connections[c].client.app in app_handle.keys():
            app_handle[connections[c].client.app](connections[c], m)

def read():
    global die
    print('==READER : type help==')
    while not die:
        try: inp = input()
        except:
            if log: logg.reader("Detected an interruption.")
            stop()
            break
        if inp == "ipbans":
            for ip in ipbans:
                if ip[1]>=10:
                    t=time.time()-ip[2]
                    pre="seconds"
                    if t>60:
                        t=int(t/60)
                        pre="minutes"
                    if t>60:
                        t=int(t/60)
                        pre="hours"
                    if t>24:
                        t=t/24
                        pre="days"
                    print(ip[0],t,pre)
        elif inp.startswith('unban '):
            i=0
            while i<len(ipbans):
                if ipbans[i][0]==inp.split(" ")[1]:
                    print("unbanned",ipbans[i][0])
                    del ipbans[i]
                i+=1
            save("ipbans",*ipbans)
        elif inp.startswith('ban '):
            ipbans.append([inp.split(" ")[1], 100, time.time()])
            print("banned", inp.split(" ")[1])
            save("ipbans", *ipbans)
        elif inp.startswith('kick '):
            c = inp.split(" ")[1].split("'")[0]
            if not complete_grid_off(int(c), logg.reader):
                logg.reader("Couldn't kick the client")
        elif inp.startswith('op '):
            username = inp.removeprefix('op ')
            if elevate_privilege(username):
                logg.reader(f'Elevated privileges for {username}')
            else:
                logg.reader(f'{username} already has elevated privileges', logg.ERROR)
        elif inp.startswith('unmap '):
            username = inp.removeprefix('unop ')
            if diminish_privilege(username):
                logg.reader(f'Diminished privileges for {username}')
            else:
                logg.reader(f'{username} already has diminished privileges', logg.ERROR)
        elif inp == "kickall":
            c=1
            while c<len(connections):
                if connections[c].thread:
                    complete_grid_off(c, logg.reader)
                c+=1
        elif inp == "users":
            for us in connections:
                if us.thread:
                    print("id:",us.id,",username:",us.username,",Is guest?",us.guest,",auth:",us.auth,",app",us.app,",die?",us.die,",room",us.room)
        elif inp == "freed": print(*free, sep=', ')
        elif inp=="help":
            print("""ipbans - Lists all IP bans.
unban <ip> - Removes ban for IP.
ban <ip> - Bans the IP
kick <id> - Disconnect a client, use the number.
op <username> - Give Admin to account
unop <username> - Remove Admin from account
kickall - Disconnects all clients.
users - Lists all connections.
freed - Lists all free connection slots.
help - Displays this.
stop - Stops the server""")
        elif inp=='stop':
            if log: logg.reader("Stop has been init")
            stop()
        else: continue
        print("~DONE~")


def run(silentQ=False, logQ=True, enable_no_die=False):
    global ipbans, logg, silent, log, s, private_key, public_key
    private_key, public_key = generate_keys()
    set_decryption_key(private_key)
    silent = silentQ
    log = logQ
    if log:
        logg.init()
        logg.silent = silent
    try:
        ipbans = list(load("ipbans"))
    except:
        save("ipbans", *())
        ipbans = []
    # BIND SOCKET TO SERVICE
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if not os.path.exists('users'): os.mkdir('users')
    try:
        s.bind((ip, port))
        print("SERVER running")
    except:
        print("bind failed")
        exit()
    if log:
        logg.connection_acceptor("Connection Successful - " + ip)
    s.listen()
    #
    srthread = threading.Thread(target=server)
    srthread.daemon = True
    srthread.start()
    #
        # if webserver:
        #     rthread = threading.Thread(target=web.RUN, args=(ip, webport,True,webpage))
        #     rthread.daemon = True
        #     rthread.start()
    #
    readthread = threading.Thread(target=read)
    readthread.daemon = True
    readthread.start()
    time.sleep(.05)
    # Process shadows:
    for shadow in shadows:
        thread = threading.Thread(target=shadow_handle, args=(shadow[0],))
        if log:
            logg.connection_acceptor(f"Shadow client with ID {shadow[2]}")
        thread.daemon = True
        thread.start()
        thread = threading.Thread(target=shadow[1], args=(connections[shadow[0]].client,))
        thread.daemon = True
        thread.start()

    # Accept Connections
    while not die:
        try:
            cs, ca = s.accept()
        except: continue

        i = 0
        ban = False
        while i < len(ipbans):
            if ipbans[i][0] == ca[0] and ipbans[i][1] >= 10:
                ban = True
                break
            i += 1
        try:
            m = recv_all(cs, BUFFER_SIZE, skip=True)
            try:
                m.decode()
            except:
                send_all(cs, "welcome".encode("utf-8"), skip=True)
                if not silent:
                    print("creepy", m)
            if ban:
                send_all(cs, str(ipbans[i][2]).encode(), skip=True)
                cs.close()
            elif m.decode("utf-8") == "stop" and die:
                send_all(cs, "bye!".encode(), skip=True)
                cs.close()
            elif m.decode("utf-8") == "clientGetID":
                id, c = makeID(cs)
                thread = threading.Thread(target=client_handle, args=(cs, c))
                if log:
                    logg.connection_acceptor(f"Client on {ca[0]} with ID {id}")
                thread.daemon = True
                thread.start()
            elif m.decode("utf-8") == "clientGetID_NODIE" and enable_no_die:
                id, c = makeID(cs)
                connections[c].die = False
                thread = threading.Thread(target=client_handle, args=(cs, c))
                if log:
                    logg.connection_acceptor(f"NO DIE Client on {ca[0]} with ID {id}",logg.WARNING)
                thread.daemon = True
                thread.start()
            elif "GET / HTTP/1.1" in m.decode("utf-8"):
                # print("Web interupt")
                cs.send('HTTP/1.0 403 Forbidden\r\n'.encode())
                cs.close()
            else:
                i = 0
                al = True
                ba = 0
                while i < len(ipbans):
                    if ipbans[i][0] == ca[0]:
                        al = False
                        ipbans[i][1] += 1
                        ba = ipbans[i][1]
                        break
                    i += 1
                if al:
                    ipbans.append([ca[0], 1, time.time()])
                    ba = 1
                save("ipbans", *ipbans)
                try:
                    if log:
                        logg.connection_acceptor(f"unknown host attempted connection from IP: {ca[0]} ; ban counter: {ba}")
                except:
                    if log:
                        logg.connection_acceptor(f"unknown host attempted connection, ban counter: {ba}")
                if log:
                    logg.connection_acceptor("message: " + m.decode("utf-8"))
                cs.send(str('please login ' + str(ba) + ' - atm=' + str(
                    time.time())).encode())
                cs.close()
        except Exception:
            traceback.print_exc()
            pass
    print("server stopping...")
    s.close()


def app(f): app_handle[f.__name__] = f


def app_disconnect(f): app_disconnect_handle[f.__name__] = f

def shadow(f):
    id, c = makeID()
    shadows.append([c, f, id])

def worlds_handler(Client: Iden, message: str):
    if message.startswith('worlds:join:'):
        world = message.split(':')[2]
        if not world in worlds.keys():
            Client.send('not ok')
            return
        worlds[world]['players'].append(Client.id)
        worlds[world]['positions'][Client.id] = worlds[world]['defaults']['position']
        worlds[world]['data'][Client.id] = worlds[world]['defaults']['data']
        Client.send('ok')
        Client.receive()
        Client.send_objects(worlds[world])
        Client.room = WorldRoom(world, Client.id)
    elif message == 'worlds:position':
        if Client.room and Client.room.world in worlds.keys():
            Client.send('ok')
        else:
            Client.send('not ok')
            return
        data = Client.receive_objects()[0]
        if 'position' in data.keys():
            worlds[Client.room.world]['positions'][Client.id] = data['position']
        if 'data' in data.keys():
            worlds[Client.room.world]['data'][Client.id] = data['data']
        response_positions = {}
        response_data = {}
        if data['all_data']:
            for id in worlds[Client.room.world]['players']:
                response_positions[id] = worlds[Client.room.world]['positions'][id]
                response_data[id] = worlds[Client.room.world]['data'][id]
        else:
            for id in worlds[Client.room.world]['players']:
                if (not id in Client.room.knows.keys()) or Client.room.knows[id] != worlds[Client.room.world]['positions'][id]:
                    response_positions[id] = worlds[Client.room.world]['positions'][id]
                    Client.room.knows[id] = response_positions[id]
                if (not id in Client.room.knows_data.keys()) or Client.room.knows_data[id] != worlds[Client.room.world]['data'][id]:
                    response_data[id] = worlds[Client.room.world]['data'][id]
                    Client.room.knows_data[id] = response_data[id]
        for key in Client.room.knows.keys():
            if not key in worlds[Client.room.world]['players']:
                response_positions[key] = None
                response_data[key] = None
                Client.room.knows[key]
                Client.room.knows_data[key]
        Client.send_objects(response_positions, response_data)
    else: return False
    return True

def make_world(name: str, default_position: tuple, default_data: any = None, other: dict = {}):
    global worlds
    worlds[name] = {
        'players': [],
        'positions': {},
        'data': {},
        'defaults': {
            'position': default_position,
            'data': default_data
        }
    }
    if not other: return
    for key, value in other.items():
        worlds[name][key] = value