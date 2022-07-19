import socket, time
from hexicapi.verinfo import __version__, __title__, __author__, __license__, __copyright__
working = []
def recv_all(the_socket:socket.socket, packet_size=1024):
    while the_socket in working:
        pass
    working.append(the_socket)
    data = the_socket.recv(16).decode('utf-8')
    try:
        data_length = int(data)
    except:
        return data.encode('utf-8')
    data = b''
    while len(data) < data_length:
        data += the_socket.recv(packet_size)
    working.remove(the_socket)
    return data
class data_not_bytes(Exception):
    pass
def send_all(the_socket:socket.socket, data):
    while the_socket in working:
        pass
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