import hashlib
import socket
import bytestream

class message:
    def __init__(self, payload):
        self.magic = bytestream.bytestream("F9BEB4D9")
        #self.command = bytestream.bytestream("000000000000000000000000")
        self.command = bytestream.bytestream("747800000000000000000000")
        #self.command = bytestream.bytestream("000000000000000000000000")
        self.length = bytestream.fromunsigned(len(payload))

        first_hasher = hashlib.new('sha256')
        first_hasher.update(payload.decode())
        second_hasher = hashlib.new('sha256')
        second_hasher.update(first_hasher.digest())
        hashed = bytestream.bytestream(second_hasher.hexdigest())

        self.checksum = hashed.peek(4)
        self.payload = payload

    def encode(self):
        encoded = bytestream.bytestream("")
        encoded += self.magic
        encoded += self.command
        encoded += self.length
        encoded += self.checksum
        encoded += self.payload
        return encoded

    def decode(self):
        return self.encode().decode()

class client:
    def __init__(self, cdict, server):
        self.cdict = cdict
        self.server = server
        hostport = cdict['addr'].split(":")
        self.host = hostport[0]
        self.port = int(hostport[1])
        hostportlocal = cdict['addrlocal']
        self.localhost = hostportlocal[0]
        self.localport = int(hostportlocal[1])

    def sendMessage(self, msg):
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s = socket.create_connection((self.host, self.port),1)
        s.send(msg.decode())
        data = s.recv(1024)
        s.close()
        return data
        
    def sendTransaction(self, trans):
        return self.sendMessage(message(trans.encode()))
        
class clients:
    def __init__(self, server):
        self.server = server
        self.refresh()

    def refresh(self):
        self.clients = []
        cdicts = self.server("getpeerinfo")
        for cdict in cdicts:
            self.clients.append(client(cdict, self.server))

    def sendMessage(self, msg):
        results = []
        for c in self.clients:
            try:
                results.append(c.sendMessage(msg))
            except socket.error or socket.timeout:
                results.append(None)
        return results
                

    def sendTransaction(self, trans):
        return self.sendMessage(message(trans.encode()))
        
        
        
