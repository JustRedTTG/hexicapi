import threading,traceback
from hexicapi.socketMessage import *
from hexicapi.verinfo import *
from random import randint
from hexicapi.save import save, load
from hexicapi.encryption import *
from hexicapi.registrator import *
private_key, public_key = generate_keys()
set_decryption_key(private_key)
silent=False
log = True
logg = None
ltar = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
identifier=0
BUFFER_SIZE = 1024
ip="localhost"
port=81
    #webport=80
    #webpage=web.mainPage
#variables
ipbans=[]
connections = []
rooms = []
free = []
s = None
#
allowGuest={'registration':True}
apps=[]
app_disconnect={}
#
console=[["Welcome To The Server!","all"]]

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
    def send(self, message):
        try:
            _ = message.decode()
            send_all(self.socket, message,enc=self.key)
        except:
            try: send_all(self.socket, message.encode(),enc=self.key)
            except: send_all(self.socket, message,enc=self.key)
    def receive(self, packet_size = BUFFER_SIZE):
        try: m = recv_all(self.socket, packet_size,enc=private_key)
        except: return False
        try: return m.decode("utf-8")
        except: return m
    def send_objects(self, *objs):
        self.send(save(None, *objs))
    def receive_objects(self, packet_size = BUFFER_SIZE):
        return load(self.receive(packet_size))
    def datasync(self):
        if self.guest: return
        action.manage_sync(self)
# Make ID for client
def makeID(cs):
    global identifier,ltar,free
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
    iden = Iden(id, cs)
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
# Handle Updates
def discon(c):
    if connections[c].socket in working: working.remove(connections[c].socket)
def server():
    while not die:
        for c in range(len(connections)):
            if connections[c].thread and connections[c].die:
                if is_socket_closed(connections[c].socket) or time.time()-connections[c].calldelta > 3:
                    ret = True
                    try:
                        ret = app_disconnect[connections[c].app](connections[c])
                        if ret == None:
                            ret = True
                    except:
                        pass
                    discon(c)
                    connections[c].thread=False
                    console.append([connections[c].username + " disconnected",connections[c].app])
                    connections[c].username = "Guest"
                    connections[c].auth = False
                    connections[c].keyring = None
                    connections[c].data = None
                    connections[c].app = None
                    free.append(c)
                    if ret:
                        if log:
                            logg.server(f"Client {connections[c].id} disconnected...")
        #print(connections)
        while len(console)>50:
            del console[0]
        time.sleep(1)

def stop():
  global die, s
  die=True
  logg.close_log()
  s.close()

app_handle={'registration':register_handle}
# Handle Clients
def client_handle(cs,c):
    send_all(cs, f"{connections[c].id}\r\n{public_key.decode('utf-8')}".encode('utf-8'), skip=True)
    connections[c].key = serialization.load_pem_public_key(
        recv_all(cs, skip=True),
        backend=default_backend()
    )
    while connections[c].thread and not die:
        try:
            try:
                m = recv_all(cs, BUFFER_SIZE, enc=private_key)
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
                send_all(cs, connections[c].id.encode(),enc=connections[c].key)
            elif string and d.split(":")[0] == "auth":
                _, username, password,app = d.split(":")
                if username == '':
                    send_all(cs, "guest-declined-no-username".encode(),enc=connections[c].key)
                    break
                accept,guest=action.auth(connections[c],username,str(password),app,get_allow_guest(app))
                if accept and not guest:
                    connections[c].username=username
                    connections[c].app=app
                    connections[c].auth=True
                    connections[c].guest=False
                    send_all(cs, "auth-accepted".encode(),enc=connections[c].key)
                    console.append([f"User {username} logged on", app])
                elif accept and guest:
                    no=True
                    for con in connections:
                        if con.username==username:
                            send_all(cs, "guest-declined".encode(),enc=connections[c].key)
                            no=False
                            break
                    if no:
                        connections[c].username = username
                        connections[c].app = app
                        connections[c].auth = True
                        send_all(cs, "guest-accepted".encode(),enc=connections[c].key)
                        console.append([f"Guest {username} hopped in", app])
                elif guest and not accept:
                    send_all(cs, "guest-declined".encode(),enc=connections[c].key)
                else:
                    send_all(cs, "auth-declined".encode(),enc=connections[c].key)
            else:
                if connections[c].auth:
                    if connections[c].app in app_handle.keys():
                        app_handle[connections[c].app](connections[c],d)
                elif d!="" and connections[c].thread:
                    print("message: "+d)
                    send_all(cs, "request-declined".encode(),enc=connections[c].key)
        except Exception:
            if is_socket_closed(cs):
                break
            else:
                print("client error occurred")
                traceback.print_exc()
            break

    cs.close()

def read():
    global die
    while not die:
        try: inp = input()
        except:
            if log: logg.reader("Detected an interruption.")
            stop()
        if inp=="ipbans":
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
        elif "unban " in inp:
            i=0
            while i<len(ipbans):
                if ipbans[i][0]==inp.split(" ")[1]:
                    print("unbanned",ipbans[i][0])
                    del ipbans[i]
                i+=1
            save("ipbans",*ipbans)
        elif "ban " in inp:
            ipbans.append(inp.split(" ")[1])
            print("banned", ipbans[i][0])
            save("ipbans", *ipbans)
        elif inp=="kickall":
            c=1
            while c<len(connections):
                if connections[c].thread:
                    connections[c].thread=False
                    console.append([connections[c].username + " disconnected", connections[c].app])
                    connections[c].username = "Guest"
                    connections[c].auth = False
                    connections[c].app = None
                    free.append(c)
                    if log:
                        logg.reader(f"Client {connections[c].id} disconnected...")
                c+=1
        elif inp=="users":
            for us in connections:
                if us.thread:
                    print("id:",us.id,",username:",us.username,",Is guest?",us.guest,",auth:",us.auth,",app",us.app,",die?",us.die,",room",us.room)
        elif inp=="freed":
            print(*free)
        elif inp=="help":
            print("""ipbans - Lists all IP bans.
unban <ip> - Removes ban for IP.
ban <ip> - Bans the IP
kickall - Disconnects all clients.
users - Lists all connections.
freed - Lists all free connection slots.
help - Displays this.
stop - Stops the server""")
        elif inp=='stop':
            if log: logg.reader("Stop has been init")
            stop()
        else: return
        print("~DONE~")

def run(silentQ=False, logQ=True, enable_no_die=False):
    global ipbans, logg, silent, log, s
    silent = silentQ
    log = logQ
    if log:
        import hexicapi.redlogger as logg
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
def app_disconnect(f): app_disconnect[f.__name__] = f

class user:
    pass