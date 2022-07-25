import socket, time
import traceback

from hexicapi.verinfo import __version__, __title__, __author__, __license__, __copyright__
from hexicapi.encryption import *
working = []
record = []
enc_private = None
enc_public = None
sock_msg_debug = False
sock_msg_debug_minimal = False
def enable_sock_debug():
    global sock_msg_debug, sock_msg_debug_minimal
    sock_msg_debug = True
    sock_msg_debug_minimal = True
def enable_sock_debug_minimal():
    global sock_msg_debug_minimal
    sock_msg_debug_minimal = True
def rm_record(cid):
    for item in record:
        if item[0] == cid:
            working.remove(item[0])
            record.remove(item)
            break
def clean_working_record():
    now = time.time()
    for item in record:
        if now-item[1] >= 10:
            if item[0] in working: working.remove(item[0])
            else: print(f'TRYING TO REMOVE {item[0]} in {working}')
            record.remove(item)
def recv_all(client, packet_size=1024, skip=False, enc=None):
    if isinstance(client, socket.socket):
        the_socket = client
        client_id = client.getsockname()
    else:
        the_socket = client.socket
        client_id = client.id
    menc = enc or enc_private
    if sock_msg_debug: print(f"RECV on wait. waiting:{working} record:{record}")
    while client_id in working: pass
    if sock_msg_debug: print("RECV finished waiting.")
    working.append(client_id)
    record.append([client_id, time.time()])
    data = the_socket.recv(16).decode('utf-8')
    try:
        data_length = int(data)
        if sock_msg_debug: print(f"RECV data size: {data_length}")
    except:
        # if enc_private and not skip:
        #     data = enc_private.decrypt(data,
        #     padding.OAEP(
        #         mgf=padding.MGF1(algorithm=hashes.SHA256()),
        #         algorithm=hashes.SHA256(),
        #         label=None
        # ))
        if sock_msg_debug: print(f"RECV data size was wrong: >{data}<")
        return data.encode('utf-8')

    data = b''
    while len(data) < data_length:
        data += the_socket.recv(packet_size)
    rm_record(client_id)
    if menc and not skip:
        if sock_msg_debug: print(f"RECV decrypting the following data: >{data}<")
        try:
            data = menc.decrypt(data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
        ))
        except: pass
    if sock_msg_debug_minimal: print(f"{the_socket.getsockname()[0]} : RECV : >{data}<")
    return data
class data_not_bytes(Exception):
    pass
def send_all(client, data, skip=False, enc=None):
    if isinstance(client, socket.socket):
        the_socket = client
        client_id = client.getsockname()
    else:
        the_socket = client.socket
        client_id = client.id
    menc = enc or enc_public
    if sock_msg_debug: old_data = data
    if sock_msg_debug: print(f"SEND sending data: >{data}< ENCRYPTING...")
    if menc and not skip:
        try:
            data = menc.encrypt(data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
        ))
        except: pass
    if sock_msg_debug: print(f"SEND on wait. waiting:{working} record:{record}")
    while client_id in working: pass
    if sock_msg_debug: print("SEND finished waiting.")
    working.append(client_id)
    record.append([client_id, time.time()])
    if not type(data) in [bytes, bytearray]:
        raise data_not_bytes(f"Data is not of type bytes / bytearray, type: {type(data)}")
        return -1
    length = str(len(data))
    while len(length) < 16:
        length = '0' + length
    rm_record(client_id)
    the_socket.send(length.encode('utf-8'))
    the_socket.send(data)
    if sock_msg_debug: print(f"SEND data size: {length}:{len(length)}")
    if sock_msg_debug_minimal: print(f"{the_socket.getsockname()[0]} : SEND : >{old_data}<")

def set_encryption_key(key):
    global enc_public
    enc_public = key

def set_decryption_key(key):
    global enc_private
    enc_private = key