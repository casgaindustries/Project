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

def get_random_string():
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(10))

# Client class that can communicate via an org or as a personal account.
class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    messagetosend = "this is empty"
    typed = "typed text "
    typedsplit = []
    registered = False
    onlineColleagues = None
    sessions = []
    # employeeSessions = []

    # Sends dict to server as json
    def sendOverSocket(self, dicttosend):
        json_object = json.dumps(dicttosend, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))

    # Asks the key of other client to the server
    def askKey(self):
        askdict = {"keyrequest":self.typedsplit[1]}
        json_object = json.dumps(askdict, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))

    # Asks the key of bank to the server
    def askBankKey(self):
        askdict = {"bankkeyrequest":self.typedsplit[1]}
        json_object = json.dumps(askdict, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))

    # Ask the bank who is currently online in the clients' org
    def getCurrentlyOnline(self):
        askdict = {"getCurrentlyOnline":'dummy'}
        json_object = json.dumps(askdict, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))
    
    # Asks the server to set up a connection with an org
    def getOrgConnection(self):
        askdict = {"communicateWithOrg":self.typedsplit[1]}
        json_object = json.dumps(askdict, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))
    
    # Messages org given sessionID retreived before
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
            enmes = self.myEncrypt.encryptStringToB64(self.typedsplit[2],session.key)
            dicttosend = {"messageOrg":{
                "sessionID":session.id,
                "orgName": session.orgName,
                "orgID": session.orgID,
                "message": enmes
            }}
            self.sendOverSocket(dicttosend)
    
    # Message other client via this client's org
    def messageViaOrg(self):
        employeeSession = None
        for eses in self.employeeSessions:
            print('Employeesessions:')
            print(eses)
            if eses.id == self.typedsplit[1]:
                employeeSession = eses
        
        print('Will try to message client via org')
        dicttosend = {'messageViaOrg':{
            'sessionID':self.typedsplit[1],
            'mes':self.myEncrypt.encryptStringToB64(self.typedsplit[2],employeeSession.pubKey)
        }}
        self.sendOverSocket(dicttosend)

    # Send add or sub or add command to bank
    def sendToBank(self,d):
        partToEncrypt = None
        if(self.typedsplit[2] == "ADD"):
            print("sending add command")
            partToEncrypt = {
                "type": "ADD",
                "from": self.typedsplit[3],
                "to": self.typedsplit[4],
                "amt": int(self.typedsplit[5])
                # "key": self.myEncrypt.getPubKeyB64()

            }

        elif self.typedsplit[2] == "SUB":
            print("sending sub command")
            partToEncrypt = {
                "type": "SUB",
                "from": self.typedsplit[3],
                "amt": int(self.typedsplit[4])
                # "key": self.myEncrypt.getPubKeyB64()
            }

        if(partToEncrypt is None):
            print("The part to encrypt was none")
            return

        print('parttoencrypt:')
        print(partToEncrypt)
        print(type(partToEncrypt))
        ptejson = json.dumps(partToEncrypt)
        ptencrypted = self.myEncrypt.encryptStringToB64(ptejson,d['bankpubkey']['key'])
        

        dicttosend = {"sendToBank":{
            "id":d['bankpubkey']['id'],
            "mes":ptencrypted
        }}
        self.sendOverSocket(dicttosend)

    #__________________________________________________________________________________________________________________
    #__________________________________________________________________________________________________________________
    # Handles keyboard input from user, please look here for what to type!
    #__________________________________________________________________________________________________________________
    #__________________________________________________________________________________________________________________
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
            #____________________________________
            #_____SEND [name/ID] [message]
            #____________________________________
            if(self.typedsplit[0] == "SEND" and self.registered):
                print('Send message detected')
                self.askKey()
            # #____________________________________
            # #____________________________________
            # #____________________________________          
            # if(self.typedsplit[0] == "BANKKEY" and self.registered):
            #     print('Asking bank key')
            #     self.askBankKey()
            #____________________________________
            #______GETONLINE
            #____________________________________
            if(self.typedsplit[0]== "GETONLINE" and self.registered):
                print("asking who's online")
                self.getCurrentlyOnline()
            #____________________________________
            #_______GETORGCONNECTION [name/ id]
            #____________________________________
            if(self.typedsplit[0]== "GETORGCONNECTION" and self.registered):
                print("Getting org connection")
                self.getOrgConnection()
            #____________________________________
            #_______ (You need to have established an org connection with the previous command first!)
            #_______MESSAGEORG [orgid/ orgname] [message]
            #____________________________________
            if(self.typedsplit[0]== "MESSAGEORG" and self.registered):
                self.messageOrg()
            #____________________________________
            #________MESSAGEVIAORG [sessionID] [message]
            #____________________________________
            if(self.typedsplit[0]== "MESSAGEVIAORG" and self.registered):
                self.messageViaOrg()
            #____________________________________
            #________SENDTOBANK [bankname/ bankid] [ADD] [from_acc_id] [to_acc_id] [amt]
            #________SENDTOBANK [bankname/ bankid] [SUB] [from_acc_id] [amt]
            #____________________________________
            if(self.typedsplit[0]=="SENDTOBANK" and self.registered):
                self.askBankKey()
    
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
        self.employeeSessions = []
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
        #___________________________________________________________________________
        #_________________________ This while loop receives messages from the server and does the appropriate action
        #___________________________________________________________________________


        while True:
            data = self.sock.recv(6000)
            if not data:
                break
            
            # try:
            datadict = json.loads(data)

            #___________________________________________________________________________
            #_________________________ If a pubkey is received, this encrypts the previously typed message and sends it to the right person
            #___________________________________________________________________________
            if 'pubkey' in datadict:
                print('unecrtyped message:')
                print(' '.join(self.typedsplit[2:]))
                print('key: $s',datadict['pubkey']['key'])
                # en = encrypt_message(self.messagetosend,datadict['pubkey']['key'])
                # en =  "act like this is encrypted"
                unen = ' '.join(self.typedsplit[2:])
                en = self.myEncrypt.encryptStringToB64(unen,datadict['pubkey']['key'])
                print('encrypted message: ')
                print(en)
                
                # message = {"message":{"rec": datadict['pubkey']['id'], "mes": en}}
                message = {"message":{"rec": datadict['pubkey']['id'], "mes": en, "mesid": get_random_string() }}
                print(message)
                json_object = json.dumps(message, indent = 4)   
                # self.sock.send(bytes(f))
                self.sock.send(bytes(json_object, encoding = 'utf-8'))
            
            #___________________________________________________________________________
            #_________________________ If a bank's pubkey is received, this encrypts the previously typed message and sends it to that bank
            #___________________________________________________________________________
            elif 'bankpubkey' in datadict:
                print('Received pubkey for bank:')
                print(datadict)
                self.sendToBank(datadict)
                

            #___________________________________________________________________________
            #_________________________ If a message is received, this decrypts it and prints it
            #___________________________________________________________________________
            elif 'message' in datadict:
                print('received a message from ',datadict['message']['senderName'],':')
                # print("\'",datadict['message']['mes'],"\'")
                # print('corresponding dict: ',datadict)

                enmes = datadict['message']['mes']
                mes = self.myEncrypt.decryptB64(enmes)
                # print('Unencrypted text:')
                print(mes)
                self.sock.send(bytes(json.dumps({"received":datadict}, indent = 4), encoding = 'utf-8'))
            
            #___________________________________________________________________________
            #_________________________This can be received after typing GETONLINE, prints your online collegues
            #___________________________________________________________________________
            elif 'online' in datadict:
                #TODO DO SOMETHING WITH THE RETURNED EMPLOYEES
                print('THESE ARE YOUR ONINE COLLEAGUES:')
                print(datadict)
                self.onlineColleagues = datadict['online']

            #___________________________________________________________________________
            #_________________________Confirms that you have been registered
            #___________________________________________________________________________
            elif 'registered' in datadict:
                self.registered = True
            #___________________________________________________________________________
            #_________________________Can be received after sending message, confirms that somehting was received
            #___________________________________________________________________________
            elif 'received' in datadict:
                print(datadict['received'])
            
            #___________________________________________________________________________
            #_________________________After the server makes a session with an employee, this is received by the  user here, and put in their array.
            #___________________________________________________________________________
            elif 'employeeContact' in datadict:
                print('Received employeeContact!')
                # print(datadict)
                self.setEmployeeContact(datadict['employeeContact'])
            
            #___________________________________________________________________________
            #_________________________If you receive a message via your org, this sets a new session and decrypts that message
            #___________________________________________________________________________
            elif 'messageThroughOrg' in datadict:
                print(datadict)
                print('Message for your Org '+datadict['messageThroughOrg']['orgName']+' from sessionID: '+datadict['messageThroughOrg']['sessionID'])
                self.employeeSessions.append(EmployeeSession(datadict['messageThroughOrg']['sessionID'],datadict['messageThroughOrg']['senderKey']))
                #! fake :
                # self.employeeSessions.append(EmployeeSession('coolsesID',datadict['messageThroughOrg']['senderKey']))

                print(self.myEncrypt.decryptB64(datadict['messageThroughOrg']['message']))

            #___________________________________________________________________________
            #_________________________When you receive a message from an org, this encrypts it and prints it.
            #___________________________________________________________________________
            elif 'MessageFromOrg' in datadict:
                print(datadict)
                d = datadict['MessageFromOrg']
                print('Received a message form org: '+d['orgName'])
                print(self.myEncrypt.decryptB64(d['mes']))

            

            else:
                print(datadict)
            print(' ')
            # except:
            #     print(data)
            #     datadict = {}
            # print(datadict)