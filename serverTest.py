#Server File
import time
import socket
import threading
import sys
import json
from connection_obj import *
from Encryption import encrypt_message
import re
import random
import string
def get_random_string():
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(10))
    # print("Random string is:", result_str)

class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    def __init__(self):
        self.sock.bind(('0.0.0.0',10000))
        self.sock.listen(1)

    def handler(self,c,a):
        while True:
            data = c.recv(6000)
            for connection in self.connections:
                print( 'newdadta')
                print(data)
                connection.send(bytes(data))
            if not data:
                print(str(a[0])+ ':' + str(a[1]), "disconnected")
                self.connections.remove(c)
                c.close()
                break
    
    def decrypt(self, cypertext, key):
        print('decrypting...')

    def myHandler(self,c,a):
        newconnection = None
        while True:
            # try:
                data = c.recv(6000)
                datadict = None
                try:
                    datadict = json.loads(data)
                except:
                    print(data)
                    datadict = {}
                # print(datadict)
                #! Check and establish new connection if you receive 'person' json
                #! Then add it to connections list
                if 'person' in datadict and newconnection is None:
                    persondata = datadict['person']
                    newconnection = ConnectionObj(persondata['id'],persondata['name'],persondata['key'],c)
                    self.connections.append(newconnection)
                    newconnection.send({"registered":{}})
                    print(self.connections)

                elif 'keyrequest' in datadict and newconnection is not None:
                    print('received a keyrequest?:')
                    print(datadict)
                    recipientstring = datadict['keyrequest']
                    recipient = None
                    for con in self.connections:
                        # if con.id is recipientstring or con.name is recipientstring:
                        # print(con.id)
                        # print(recipientstring)
                        if con.id == recipientstring or con.name == recipientstring:
                            #TODO build check for multiple people of same name
                            print('this recipient matches!')
                            recipient = con
                    if recipient is not None:
                        newconnection.send({"pubkey":{"id":recipient.id,"key":recipient.key}})

                
                elif 'message' in datadict and newconnection is not None:
                    #* We never decrypt the message here!
                    messagedata = datadict['message']
                    #! First: figure out who the receiver is:
                    print('datadict w message:')
                    print(datadict)
                    recipientstring = messagedata['rec']
                    recipient = None
                    for con in self.connections:
                        # if con.id is recipientstring or con.name is recipientstring:
                        print(con.id)
                        print(recipientstring)
                        if con.id == recipientstring:
                            #TODO build check for multiple people of same name
                            print('this recipient matches!')
                            recipient = con
                    if recipient is None:
                        print('this recipient was not found:')
                        print(messagedata)
                    else:
                        dicttosend = dict(messagedata)
                        # dicttosend['message'].pop('rec', None)
                        dicttosend['senderName'] = newconnection.name
                        dicttosend['senderID'] = newconnection.id
                        print('trying to send this: ')
                        newdicttosend  = {"message":dicttosend}
                        print(newdicttosend)
                        print('to: ')
                        print(recipient.id)
                        # recipient.send(newdicttosend)

                        #! for now we send stuff twice
                        #* Start a new thread that keeps trying to send the message to the receiver
                        recipient.messagesToReceive.append(newdicttosend)
                        iThread = threading.Thread(target = self.keepResending(newdicttosend,recipient))
                        iThread.deamon = True
                        iThread.start()
                        
                
                elif 'received' in datadict and newconnection is not None:
                    print('received')
                    newconnection.messagesToReceive.remove(datadict['received'])
                else:
                    print('this json was not recognized:')
                    print(datadict)
            

                if not data:
                    print(str(a[0])+ ':' + str(a[1]), "disconnected")
                    self.connections.remove(newconnection)
                    newconnection.c.close()
                    break
            # except Exception as e:
            #     print(e)
            #     print(str(a[0])+ ':' + str(a[1]), "disconnected")
            #     self.connections.remove(newconnection)
            #     newconnection.c.close()
            #     break
            
    def keepResending(self, dict, receiver):
        # time.sleep(5)
        while(dict in receiver.messagesToReceive):
            print('That dict is definitly not received.')
            receiver.send(dict)
            time.sleep(5)

        
        print('That dict is received')

    def run(self):
        while True:
            #connection is c, cliens' adres is a
            c, a = self.sock.accept()
            cThread = threading.Thread(target = self.myHandler, args = (c,a))
            cThread.daemon = True
            cThread.start()
            #! self.connections.append(c), we want to add this later!
            # print(self.connections)
            print(str(a[0])+ ':' + str(a[1]), "connected")


class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    messagetosend = "this is empty"
    typed = "typed text "
    typedsplit = []
    registered = False
    def askKey(self):
        askdict = {"keyrequest":self.typedsplit[1]}
        json_object = json.dumps(askdict, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))

    def handleInput(self):
        while True:
            # self.sock.send(bytes(input(""),'utf-8'))
            self.typed = input("")
            self.typedsplit = self.typed.split()
            temp = [self.typedsplit[0]]
            reststring = ' '.join(self.typedsplit[1:])
            temp2 = re.findall("\[(.*?)\]", reststring)
            temp = temp + temp2
            self.typedsplit = temp
            print('input:  ')
            for e in self.typedsplit:
                print(e)
            if(self.typedsplit[0] == "SEND" and self.registered):
                print('Send message detected')
                self.askKey()

    
    def testloop(self):
         while True:
            self.typed = input("")

            

            #!!!!!!!!!!!! TEST 
            # f = open ('messagetest1.json', encoding='utf-8') 
            f = open ('keyreq1.json', encoding='utf-8') 
            data = json.loads(f.read())
            json_object = json.dumps(data, indent = 4)   
            # self.sock.send(bytes(f))
            self.sock.send(bytes(json_object, encoding = 'utf-8'))
            # self.sock.send(data)
            #!!!!!!!!!!!!!!!!

    def __init__(self, jsonfile):
        f = open (jsonfile, encoding='utf-8') 
        self.data = json.loads(f.read()) 
        print(self.data)

        

        self.sock.connect((self.data['server']['ip'],int(self.data['server']['port'])))
        
        myPersonDict = self.data['person']
        myPersonDict['keys'] = myPersonDict['keys'].pop('private', None)
        myPersonDict['key'] = myPersonDict.pop('keys')
        finalPersonDict = {}
        finalPersonDict['person'] = myPersonDict        
        myPersonJson = json.dumps(finalPersonDict).encode('utf-8')
        # myPersonJson = json.dumps(myPersonDict)

        # print(myPersonJson)
            
        # self.sock.send(bytes(myPersonJson, 'utf-8'))
        self.sock.sendall(myPersonJson)

        iThread = threading.Thread(target = self.handleInput)
        iThread.deamon = True
        iThread.start()

        while True:
            data = self.sock.recv(6000)
            if not data:
                break
            
            # try:
            datadict = json.loads(data)

            if 'pubkey' in datadict:
                print('unecrtyped message:')
                print(' '.join(self.typedsplit[2:]))
                print('key: $s',datadict['pubkey']['key'])
                # en = encrypt_message(self.messagetosend,datadict['pubkey']['key'])
                en =  "act like this is encrypted"
                en = ' '.join(self.typedsplit[2:])
                print('encrypted message: ')
                print(en)
                # message = {"message":{"rec": datadict['pubkey']['id'], "mes": en}}
                message = {"message":{"rec": datadict['pubkey']['id'], "mes": en, "mesid": get_random_string() }}
                print(message)
                json_object = json.dumps(message, indent = 4)   
                # self.sock.send(bytes(f))
                self.sock.send(bytes(json_object, encoding = 'utf-8'))
            
            elif 'message' in datadict:
                #TODO DECRYPT THIS WHEN IT IS ACTUALLY ENCRYPTED
                print('received a message from ',datadict['message']['senderName'],':')
                print("\'",datadict['message']['mes'],"\'")
                print('corresponding dict: ',datadict)
                self.sock.send(bytes(json.dumps({"received":datadict}, indent = 4), encoding = 'utf-8'))

            elif 'registered' in datadict:
                self.registered = True

            else:
                print(datadict)

            # except:
            #     print(data)
            #     datadict = {}
            # print(datadict)

if (len(sys.argv) > 1):
    client = Client(sys.argv[1])
else:
    server = Server()
    server.run()

