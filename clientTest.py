#Server File
import time
import socket
import threading
import sys
import json
from connection_obj import *
from organisation import *
from session import *
# from Encryption import encrypt_message
import re
import random
import string
# from serverTest import *
import base64
from casEncrypt import *
class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    messagetosend = "this is empty"
    typed = "typed text "
    typedsplit = []
    registered = False
    onlineColleagues = None
    sessions = []

    def sendOverSocket(self, dicttosend):
        json_object = json.dumps(dicttosend, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))

    def askKey(self):
        askdict = {"keyrequest":self.typedsplit[1]}
        json_object = json.dumps(askdict, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))

    def getCurrentlyOnline(self):
        askdict = {"getCurrentlyOnline":'dummy'}
        json_object = json.dumps(askdict, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))
    
    def getOrgConnection(self):
        askdict = {"communicateWithOrg":self.typedsplit[1]}
        json_object = json.dumps(askdict, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))
    
    def messageOrg(self):
        print('Messaging org!')
        session = None
        for s in self.sessions:
            if s.orgName == self.typedsplit[1] or s.orgID == self.typedsplit[1]:
                print('Found session!: ')
                print(s)
                session = s
        if session is None:
            print('Session was not found, no message sent')
        else:
            #TODO ENCRYPT USING RECEIVED KEY
            dicttosend = {"messageOrg":{
                "sessionID":session.id,
                "orgName": session.orgName,
                "orgID": session.orgID,
                "message": "encrypted: "+self.typedsplit[2]
            }}
            self.sendOverSocket(dicttosend)


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
            if(self.typedsplit[0]== "GETONLINE" and self.registered):
                print("asking who's online")
                self.getCurrentlyOnline()
            if(self.typedsplit[0]== "GETORGCONNECTION" and self.registered):
                print("Getting org connection")
                self.getOrgConnection()
            if(self.typedsplit[0]== "MESSAGEORG" and self.registered):
                self.messageOrg()
    
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

    def setEmployeeContact(self, dict):
        print('Setting employee contact lmao')
        self.sessions.append(Session(dict))
        print('Sessions: ')
        print(self.sessions)
        

    def __init__(self, jsonfile):
        f = open (jsonfile, encoding='utf-8') 
        self.data = json.loads(f.read()) 
        print(self.data)
        self.myEncrypt = MyEncrypt()

        # self.key = RSA.generate(1024, random_generator)
        

        self.sock.connect((self.data['server']['ip'],int(self.data['server']['port'])))
        
        myPersonDict = self.data['person']
        myPersonDict['keys'] = myPersonDict['keys'].pop('private', None)
        myPersonDict['key'] = myPersonDict.pop('keys')
        # myPersonDict['key'] = base64.b64encode(self.key.publickey().exportKey(format='PEM', passphrase=None, pkcs=1)).decode('ascii')
        myPersonDict['key'] = self.myEncrypt.getPubKeyB64()
        finalPersonDict = {}
        finalPersonDict['person'] = myPersonDict
        
        print('-------------My personal dict:-------------')
        print(finalPersonDict)


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
            
            elif 'online' in datadict:
                #TODO DO SOMETHING WITH THE RETURNED EMPLOYEES
                print('THESE ARE YOUR ONINE COLLEAGUES:')
                print(datadict)
                self.onlineColleagues = datadict['online']

            elif 'registered' in datadict:
                self.registered = True

            elif 'received' in datadict:
                print(datadict['received'])
            
            elif 'employeeContact' in datadict:
                print('Received employeeContact!')
                # print(datadict)
                self.setEmployeeContact(datadict['employeeContact'])
            

            else:
                print(datadict)

            # except:
            #     print(data)
            #     datadict = {}
            # print(datadict)