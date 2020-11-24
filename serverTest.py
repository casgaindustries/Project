#Server File
import socket
import threading
import sys
import json

class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    def __init__(self):
        self.sock.bind(('0.0.0.0',10000))
        self.sock.listen(1)

    def handler(self,c,a):
        while True:
            data = c.recv(2024)
            for connection in self.connections:
                connection.send(bytes(data))
            if not data:
                print(str(a[0])+ ':' + str(a[1]), "disconnected")
                self.connections.remove(c)
                c.close()
                break
    
    def run(self):
        while True:
            #connection is c, cliens' adres is a
            c, a = self.sock.accept()
            cThread = threading.Thread(target = self.handler, args = (c,a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            # print(self.connections)
            print(str(a[0])+ ':' + str(a[1]), "connected")


class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def sendMsg(self):
        while True:
            self.sock.send(bytes(input(""),'utf-8'))
    
    def __init__(self, jsonfile):
        f = open (jsonfile, encoding='utf-8') 
        self.data = json.loads(f.read()) 
        print(self.data)

        

        self.sock.connect((self.data['server']['ip'],int(self.data['server']['port'])))
        
        myPersonDict = self.data['person']
        myPersonDict['keys'] = myPersonDict['keys'].pop('private', None)
        myPersonDict['key'] = myPersonDict.pop('keys')
        # myPersonDict['person'] = myPersonDict
        
        myPersonJson = json.dumps(myPersonDict)

        print(myPersonJson)
            
        self.sock.send(bytes(myPersonJson, 'utf-8'))

        iThread = threading.Thread(target = self.sendMsg)
        iThread.deamon = True
        iThread.start()

        while True:
            data = self.sock.recv(2048)
            if not data:
                break
            print(data)

if (len(sys.argv) > 1):
    client = Client(sys.argv[1])
else:
    server = Server()
    server.run()

    