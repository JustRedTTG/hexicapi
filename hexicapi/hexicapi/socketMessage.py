import socket, time
import traceback

from hexicapi.verinfo import __version__, __title__, __author__, __license__, __copyright__
from hexicapi.encryption import *
working = []
record = []
enc_private = None
enc_public = None
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
    while client_id in working: pass
    working.append(client_id)
    record.append([client_id, time.time()])
    data = the_socket.recv(16).decode('utf-8')
    try:
        data_length = int(data)
    except:
        # if enc_private and not skip:
        #     data = enc_private.decrypt(data,
        #     padding.OAEP(
        #         mgf=padding.MGF1(algorithm=hashes.SHA256()),
        #         algorithm=hashes.SHA256(),
        #         label=None
        # ))
        return data.encode('utf-8')

    data = b''
    while len(data) < data_length:
        data += the_socket.recv(packet_size)
    rm_record(client_id)
    if menc and not skip:
        data = menc.decrypt(data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
    ))
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
    if menc and not skip:
        try:
            data = menc.encrypt(data,
            padding.OAEP(
              mgf=padding.MGF1(algorithm=hashes.SHA256()),
              algorithm=hashes.SHA256(),
              label=None
        ))
        except Exception as e: print(traceback.format_exc())
    while client_id in working: pass
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

def set_encryption_key(key):
    global enc_public
    enc_public = key

def set_decryption_key(key):
    global enc_private
    enc_private = key