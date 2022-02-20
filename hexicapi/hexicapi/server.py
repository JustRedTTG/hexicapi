import os, sys
import os.path
import socket,threading,traceback
import hexicapi.web as web
from hexicapi.verinfo import __version__, __title__, __author__, __license__, __copyright__
from random import randint
from time import sleep,time
from pgerom import save as pesave
from pgerom import load as peload
logg = None
ltar = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
identifier=0
BUFFER_SIZE = 1024
ip="localhost"
port=81
webport=80
webpage=web.mainPage
#variables
ipbans=[]
connections = []
rooms = []
free = []
#
allowGuest={}
apps=[]
app_disconnect={}
#
console=[["Welcome To The Server!","all"]]

# Make ID for client
def makeID(cs):
    global identifier,ltar,free
    num=None
    if len(free)>0:
        num = free[0]
        id = str(connections[num]["id"].split("'")[0])+"'"
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
    iden = {"id": id, "socket":cs,"thread":True,"calldelta":time(),"username":"Guest","guest":True,"auth":False,"app":None,"data":None,"die":True,"room":None}
    if num == None:
        connections.append(iden)
    else:
        connections[num] = iden
    return id,num2

class action:
    def auth(username,password,app):
        try:
            ag = allowGuest[app]
        except:
            ag=False
        if os.path.exists("users/"+username):
            with open("users/"+username+"/auth") as f:
                f.seek(0)
                if f.read()==password:
                    return True, False
                else:
                    return False,ag
        else:
            if username!="":
                return ag,ag
            else:
                return False,False
    def idname(id):
        with open("users/"+str(id)) as f:
            name = str(f.read())
        return name
    def nameid(name):
        with open("users/"+str(name)+"/id") as f:
            id = int(f.read())
        return id
    def mycon(app):
        con=[]
        for x in console:
            if x[1]==app or x[1]=="all":
                con.append(x)
        return con
def is_socket_closed(sock):
    try:
        sock.send("".encode())
        return False
    except:
        return True
die=False
# Handle Updates
def server():
    while not die:
        for c in range(len(connections)):
            if connections[c]["thread"] and connections[c]["die"]:
                #print(time()-connections[c]["calldelta"])
                if is_socket_closed(connections[c]["socket"]) or time()-connections[c]["calldelta"] > 3:
                    ret = True
                    try:
                        ret = app_disconnect[connections[c]['app']](connections[c])
                        if ret == None:
                            ret = True
                    except:
                        pass
                    connections[c]["thread"]=False
                    console.append([connections[c]["username"] + " disconnected",connections[c]["app"]])
                    connections[c]["username"] = "Guest"
                    connections[c]["auth"] = False
                    connections[c]["app"] = None
                    free.append(c)
                    if ret:
                        print(f"client {connections[c]['id']} disconnected...")
                        logg.log("Client "+connections[c]['id']+" disconnected...")
        #print(connections)
        while len(console)>50:
            del console[0]
        sleep(1)

def stop():
  global die
  die=True
  logg.die=True

app_handle={}
# Handle Clients
def client_handle(cs,c):
    cs.send(connections[c]["id"].encode("utf-8"))
    while connections[c]["thread"] and not die:
        try:
            m = cs.recv(BUFFER_SIZE)
            if len(m)>0:
                delta=time()-connections[c]["calldelta"]
                connections[c]["calldelta"]=time()
            try:
                d=m.decode()
                string=True
            except:
                d=m
                string=False
            if d == "clientGetID":
              cs.send(connections[c]["id"].encode())
            elif d == "bye":
                break
            elif string and d.split(":")[0] == "auth":
                _, username, password,app = d.split(":")
                accept,guest=action.auth(username,password,app)
                if accept and not guest:
                    connections[c]["username"]=username
                    connections[c]["app"]=app
                    connections[c]["auth"]=True
                    cs.send("auth-accepted".encode())
                    console.append(["User "+username+" logged on",app])
                elif accept and guest:
                    no=True
                    for con in connections:
                        if con["username"]==username:
                            cs.send("guest-declined".encode())
                            no=False
                            break
                    if no:
                        connections[c]["username"] = username
                        connections[c]["app"] = app
                        connections[c]["auth"] = True
                        cs.send("guest-accepted".encode())
                        console.append(["Guest " + username + " hopped in",app])
                elif guest and not accept:
                    cs.send("guest-declined".encode())
                else:
                    cs.send("auth-declined".encode())
            else:
                if connections[c]["auth"]:
                    if connections[c]['app'] in app_handle.keys():
                        app_handle[connections[c]['app']](connections[c],d)
                elif d!="" and connections[c]["thread"]:
                    print("message: "+d)
                    cs.send("request-declined".encode())
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
        inp = input()
        if inp=="ipbans":
            for ip in ipbans:
                if ip[1]>=10:
                    t=time()-ip[2]
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
                    print("unbanned "+ipbans[i][0])
                    del ipbans[i]
                i+=1
            pesave("ipbans",*ipbans)
        elif inp=="kickall":
            c=1
            while c<len(connections):
                if connections[c]["thread"]:
                    connections[c]["thread"]=False
                    console.append([connections[c]["username"] + " disconnected", connections[c]["app"]])
                    connections[c]["username"] = "Guest"
                    connections[c]["auth"] = False
                    connections[c]["app"] = None
                    free.append(c)
                    print(f"client {connections[c]['id']} disconnected...")
                    logg.log("Client " + connections[c]['id'] + " disconnected...")
                c+=1
        elif inp=="users":
            for us in connections:
                if us["thread"]:
                    print("id:",us["id"],",username:",us["username"],",Is guest?",us["guest"],",auth:",us["auth"],",app",us["app"],",die?",us["die"],",room",us["room"])
        elif inp=="freed":
            print(*free)
        elif inp=="help":
            print("""ipbans - Lists all IP bans.
unban <ip> - Removes ban for IP.
kickall - Disconnects all clients.
users - Lists all connections.
freed - Lists all free connection slots.
help - Displays this.""")
        print("~DONE~")

def run():
    global ipbans, logg
    import hexicapi.redlogger as logg
    try:
        ipbans = list(peload("ipbans"))
    except:
        pesave("ipbans", *())
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
    logg.log("Connection Successful - " + ip)
    s.listen()
    #
    srthread = threading.Thread(target=server)
    srthread.daemon = True
    srthread.start()
    rthread = threading.Thread(target=web.RUN, args=(ip, webport,True,webpage))
    rthread.daemon = True
    rthread.start()
    #
    readthread = threading.Thread(target=read)
    readthread.daemon = True
    readthread.start()
    # Accept Connections
    while not die:
        cs, ca = s.accept()
        i = 0
        ban = False
        while i < len(ipbans):
            if ipbans[i][0] == ca[0] and ipbans[i][1] >= 10:
                ban = True
                break
            i += 1
        try:
            m = cs.recv(BUFFER_SIZE)
            try:
                m.decode()
            except:
                cs.send("welcome".encode("utf-8"))
                print("creappy", m)
            if ban:
                cs.send(str(ipbans[i][2]).encode())
                cs.close()
            elif m.decode("utf-8") == "stop" and die:
                cs.send("bye!".encode())
                cs.close()
            elif m.decode("utf-8") == "clientGetID":
                id, c = makeID(cs)
                thread = threading.Thread(target=client_handle, args=(cs, c))
                print("Client on " + str(ca[0]) + " with ID " + id)
                logg.log("Client on " + str(ca[0]) + " with ID " + id)
                thread.daemon = True
                thread.start()
            elif m.decode("utf-8") == "clientGetID_NODIE":
                id, c = makeID(cs)
                connections[c]["die"] = False
                thread = threading.Thread(target=client_handle, args=(cs, c))
                print("Client on " + str(ca[0]) + " with ID " + id)
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
                    ipbans.append([ca[0], 1, time()])
                    ba = 1
                pesave("ipbans", *ipbans)
                try:
                    print("unknown host attempted connection from IP: " + ca[0] + ", ban counter: " + str(ba))
                    logg.log("unknown host attempted connection from IP: " + ca[0] + ", ban counter: " + str(ba))
                except:
                    print("unknown host attempted connection, ban counter: " + str(ba))
                    logg.log("unknown host attempted connection, ban counter: " + str(ba))
                print("message: " + m.decode("utf-8"))
                logg.log("message: " + m.decode("utf-8"))
                cs.send(str('please login ' + str(ba) + ' - atm=' + str(
                    time())).encode())
                cs.close()
        except Exception:
            traceback.print_exc()
            pass
    print("server stopping...")
    s.close()

class client:
    def app(f):
        app_handle[f.__name__] = f
    def app_disconnect(f):
        app_disconnect[f.__name__] = f
    def send(client, message):
        try:
            _ = message.decode()
            client['socket'].send(message)
        except:
            try:
                client['socket'].send(message.encode())
            except:
                client['socket'].send(message)
    def receive(client, packet_size = BUFFER_SIZE):
        try:
            data = []
            while True:
                packet = client['socket'].recv(packet_size)
                if not packet:
                    break
                data.append(packet)
            m = b''.join(data)
        except:
            return False
        try:
            return m.decode("utf-8")
        except:
            return m
