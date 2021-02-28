from queue import Queue
import os

NETWORK = {}

class NetworkNode:
    def __init__(self, name, addr):
        if not os.path.exists(name):
            os.mkdir(name)
        NETWORK[name] = self
        self.name = name
        self.addr = addr
        self.messages = Queue()

    def send_to(self, name, data):
        if name not in NETWORK:
            raise Exception("node " + name + " does not exist")
        
        NETWORK[name].messages.put((self.name, data))

    def recv_from(self):
        name, data = NETWORK[self.name].messages.get_nowait()
        return name, data

    def save_file(self, filename, data):
        filename = os.path.join(self.name, filename)
        with open(filename, 'w') as f:
            #TODO
            pass
