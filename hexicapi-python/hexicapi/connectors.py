import traceback
from abc import ABC, abstractmethod
import socket, websocket


class Connector(ABC):
    sockname: tuple

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    def connect(self, address: str) -> None: ...

    def getsockname(self) -> tuple: return self.sockname

    @abstractmethod
    def close(self): ...


class AddressException(Exception): ...

class TCPConnector(Connector):

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, address: str):
        split = address.split(':')
        if len(split) != 2: raise AddressException("Address is missing port entirely")
        if not split[-1]: raise AddressException("Address is missing port after colon")
        if not split[0]: raise AddressException("Address is missing ip before colon")
        self.sockname = (split[0], int(split[1]))
        try:
            self.s.connect(self.sockname)
        except ValueError:
            AddressException("Address port isn't a valid value")

    def send(self, data: bytes): return self.s.send(data)

    def recv(self, buffer_size: int): return self.s.recv(buffer_size)

    def close(self): return self.s.close()

class WebsocketConnector(Connector):
    buffer = []
    def __init__(self):
        self.s = websocket.WebSocket()

    def connect(self, address: str):
        self.sockname = address.split(':')
        if len(self.sockname) < 2: self.sockname.append()
        self.sockname = tuple(self.sockname)
        self.s.connect(address)

    def send(self, data: bytes): return self.s.send_binary(data)

    def recv(self, buffer_size: int):
        if len(self.buffer) < 1: self.buffer.extend(self.s.recv())
        items = self.buffer[0:min(buffer_size, len(self.buffer))]
        del self.buffer[0:min(buffer_size, len(self.buffer))]
        return bytes(items)

    def close(self): return self.s.close()