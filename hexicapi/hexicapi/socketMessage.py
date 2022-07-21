import socket, time
from hexicapi.verinfo import __version__, __title__, __author__, __license__, __copyright__
from hexicapi.encryption import *
working = []
enc_private = None
enc_public = None
def recv_all(the_socket:socket.socket, packet_size=1024, skip=False, enc=None):
    menc = enc or enc_private
    while the_socket in working: pass
    working.append(the_socket)
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
    working.remove(the_socket)
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
def send_all(the_socket:socket.socket, data, skip=False, enc=None):
    menc = enc or enc_public
    if menc and not skip:
        try:
            data = menc.encrypt(data,
            padding.OAEP(
              mgf=padding.MGF1(algorithm=hashes.SHA256()),
              algorithm=hashes.SHA256(),
              label=None
        ))
        except Exception as e: print(f"ERROR: {e}")
    while the_socket in working: pass
    working.append(the_socket)
    if not type(data) in [bytes, bytearray]:
        raise data_not_bytes(f"Data is not of type bytes / bytearray, type: {type(data)}")
        return -1
    length = str(len(data))
    while len(length) < 16:
        length = '0' + length
    the_socket.send(length.encode('utf-8'))
    the_socket.send(data)
    working.remove(the_socket)
def set_encryption_key(key):
    global enc_public
    enc_public = key

def set_decryption_key(key):
    global enc_private
    enc_private = key