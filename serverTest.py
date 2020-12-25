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

import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.Cipher import DES3
random_generator = Random.new().read

def get_random_string():
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(10))
    # print("Random string is:", result_str)

class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    organisations = []
    def __init__(self):
        self.sock.bind(('0.0.0.0',10000))
        self.sock.listen(1)
        self.createOrgsFromFiles(['organisation_1.json','organisation_2.json'])


    def decrypt(self, cypertext, key):
        print('decrypting...') 

    def createOrgsFromFiles(self, files):
        for filename in files:
            f = open (filename, encoding='utf-8') 
            orgdict = json.loads(f.read()) 
            org = Organisation(orgdict)
            self.organisations.append(org)
        if(True):
            print('Created orgs: ')
            print(self.organisations)
            print(" ")

    def registerPerson(self,datadict,c):
        persondata = datadict['person']
        newconnection = ConnectionObj(persondata['id'],persondata['name'],persondata['key'],c)
        self.connections.append(newconnection)
        newconnection.send({"registered":{}})
        print(self.connections)
        return newconnection
    
    def retreiveKeyRequest(self,datadict,newconnection):
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
    
    def sendMessage(self,datadict,newconnection):
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
    
    def confirmReceived(self,datadict,connection):
        print('this dict was received:')
        print(datadict)
        connection.messagesToReceive.remove(datadict['received'])
        sender = next(connection for connection in self.connections if connection.id == datadict['received']['message']['senderID'])
        stringtosend = "Your message saying \"",datadict['received']['message']['mes'],"\" was received:"
        if sender is not None:
            sender.send({"received":stringtosend})

    def getCurrentlyOnlineMyOrg(self,newconnection):
        #First check in which org this person is located
        myOrg = None
        for org in self.organisations:
            if any(em.id == newconnection.id for em in org.employees):
                print(' ')
                print('Your org is: ' )
                print(org)
                print(' ')
                myOrg = org
        if(myOrg is None):
            print('No org found for this user!')
            return 
        online = []
        for em in myOrg.employees:
            for connection in self.connections:
                if(connection.id == em.id and connection.id != newconnection.id):
                    online.append(connection)
        print('These people are online in your company:')
        print(online)
        onlinedictarray = []
        for connection in online:
            onlinedictarray.append(connection.asdict())
        onlineDict = {"online":onlinedictarray}
        print(onlineDict)

        newconnection.send(onlineDict)

    def getOrg(self,orgString):
        #Gets the employees currently online given a company ID or name
        theOrg = None
        for org in self.organisations:
            if (org.id==orgString or org.name==orgString):
                theOrg=org
                print("Org found: "+org.name)
        if(theOrg is None):
            print("There was no org found for this string: "+orgString)
        elif(theOrg.employees == []):
            print("There are no employees online for this org!")
        return theOrg  
    
    #method which returns employee and connection object related to session id
    def getConnectionAndEmployee(self, org, sessionID):
        em = None
        for e in org.employees:
            print(e.id + " has the following sessions:")
            print(e.mySessions)
            for s in e.mySessions:
                if(s == sessionID):
                    em = e
                    print(e.id + "Had the correct session id...")
        
        con = None
        for conn in self.connections:
            if conn.id == em.id:
                con = conn
        
        return con, em

    def getOnlineInOrg(self,org):
        online = []
        for em in org.employees:
            for connection in self.connections:
                if(connection.id == em.id):
                    online.append(em)
        print('These people are online in your company:')
        print(online)
        return(online)
        
    def createOrgSession(self,newconnection,datadict):
        print('Creating a new session between: '+datadict['communicateWithOrg']+" and "+ newconnection.name)
        org = self.getOrg(datadict['communicateWithOrg'])
        sessionID = get_random_string()
        print("Session ID: ", sessionID)
        onlineInOrg = self.getOnlineInOrg(org)
        connectionBuddy = random.choice(onlineInOrg)
        connectionBuddy.mySessions.append(sessionID)
        ###! just to test
        print('----------THE TEST STATEMENT-------')
        for e in org.employees:
            print(e)
        ##! 
        connectionBuddyCon = None
        for conn in self.connections:
            if conn.id == connectionBuddy.id:
                print('Found connection obj for buddy')
                connectionBuddyCon = conn
                break

        print(connectionBuddy)
        #TODO return dict/json with key of the recipient employee and the session id
        returndict = {"employeeContact":{
            "key":connectionBuddyCon.key,
            "sessionID":sessionID,
            "orgID":org.id,
            "orgName":org.name
        }}
        newconnection.send(returndict)

    def messageOrg(self,newconnection,datadict):
        d = datadict['messageOrg']
        org = self.getOrg(d['orgID'])
        con, em = self.getConnectionAndEmployee(org,d['sessionID'])
        print('messaging: Connection object, Employee object' )
        print(con)
        print(em)

        dicttosend = {"messageThroughOrg":{
            "orgID":d['orgID'],
            "orgName": d['orgName'],
            "sessionID":d['sessionID'],
            "senderID": newconnection.id,
            "senderName": newconnection.name,
            "senderKey": newconnection.key,
            "message": d['message']
        }}

        con.send(dicttosend)

    def myHandler(self,c,a):
        newconnection = None
        
        while True:
            try:
                data = c.recv(6000)
                datadict = None
                try:
                    datadict = json.loads(data)
                except:
                    print(data)
                    datadict = {}

                if 'person' in datadict and newconnection is None:
                    newconnection = self.registerPerson(datadict,c)

                elif 'keyrequest' in datadict and newconnection is not None:
                    self.retreiveKeyRequest(datadict,newconnection)

                elif 'message' in datadict and newconnection is not None:
                    self.sendMessage(datadict,newconnection)
                  
                elif 'received' in datadict and newconnection is not None:
                    self.confirmReceived(datadict,newconnection)
                
                elif 'getCurrentlyOnline' in datadict and newconnection is not None:
                    self.getCurrentlyOnlineMyOrg(newconnection)
                
                elif 'communicateWithOrg' in datadict and newconnection is not None:
                    self.createOrgSession(newconnection,datadict)

                elif 'messageOrg' in datadict and newconnection is not None:
                    self.messageOrg(newconnection,datadict)
                
                else:
                    print('this json was not recognized:')
                    print(datadict)
            
                if not data:
                    print(str(a[0])+ ':' + str(a[1]), "disconnected")
                    self.connections.remove(newconnection)
                    newconnection.c.close()
                    break
            except Exception as e:
                print(e)
                print(str(a[0])+ ':' + str(a[1]), "disconnected")
                self.connections.remove(newconnection)
                newconnection.c.close()
                break
            
    def keepResending(self, dict, receiver):
        # time.sleep(5)
        #TODO set this to the correct limit for the sender
        limit = 5
        i = 0
        while(dict in receiver.messagesToReceive and i<limit):
            i = i+1
            print('sending dict again, because no response has come back')
            receiver.send(dict)
            #TODO set this to the correct timeouttime set by the sender
            time.sleep(5)
        if(not i<limit):
            print('gave up sending the dict to receiver')
        else:
            print('receiver confirmed the message')

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

        # self.key = RSA.generate(1024, random_generator)
        

        self.sock.connect((self.data['server']['ip'],int(self.data['server']['port'])))
        
        myPersonDict = self.data['person']
        myPersonDict['keys'] = myPersonDict['keys'].pop('private', None)
        myPersonDict['key'] = myPersonDict.pop('keys')
        # myPersonDict['key'] = base64.b64encode(self.key.publickey().exportKey(format='PEM', passphrase=None, pkcs=1)).decode('ascii')
        # myPersonDict['key'] = self.key.publickey()
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

if (len(sys.argv) > 1):
    client = Client(sys.argv[1])
else:
    server = Server()
    server.run()

