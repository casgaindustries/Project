#Server File
import time
import socket
import threading
import sys
import json
from connection_obj import *
from organisation import *
from session import *
from bank import*
import re
import random
import string

import base64


from casEncrypt import *
from clientTest import Client

def get_random_string():
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(10))
    # print("Random string is:", result_str)

class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    bankconnections = []
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
    
    def retreiveBankKeyRequest(self,datadict,newconnection):
        print('received a keyrequest for a bank?:')
        print(datadict)
        recipientstring = datadict['bankkeyrequest']
        recipient = None
        for con in self.bankconnections:
            # if con.id is recipientstring or con.name is recipientstring:
            # print(con.id)
            # print(recipientstring)
            if con.id == recipientstring or con.name == recipientstring:
                #TODO build check for multiple people of same name
                print('this recipient matches!')
                recipient = con
        if recipient is not None:
            newconnection.send({"bankpubkey":{"id":recipient.id,"key":recipient.key}})

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
                if(s[0] == sessionID):
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
        connectionBuddy.mySessions.append([sessionID,newconnection.id])
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
    
    def sendToBank(self, datadict, newconnection):
        bank = None
        for b in self.bankconnections:
            if b.id == datadict['sendToBank']['id'] or b.name == datadict['sendToBank']['id']:
                bank = b
        if(bank is None):
            print('No bank found!')
            return

        print('The sending to bank:')
        print(bank.name)

        dicttosend = {
            "userMessage":{
                "userID":newconnection.id,
                "message":datadict['sendToBank']['mes']
            }
        }

        bank.send(dicttosend)

    def messageViaOrg(self, datadict, newconnection):
        print('Messaging via org ')
        
        #awesome loop stacking:
        sessiontuple = None
        organisation = None

        for org in self.organisations:
            for employee in org.employees:
                if employee.id == newconnection.id:
                    for session in employee.mySessions:
                        if session[0]==datadict['messageViaOrg']['sessionID']:
                            print('FOUND session with client!')
                            sessiontuple = session
                            organisation = org
        if sessiontuple is None:
            print('Session not found!')
            return
        
        for con in self.connections:
            if con.id == sessiontuple[1]:
                con.send({'MessageFromOrg':{
                    'orgName':org.name,
                    'sessionID':datadict['messageViaOrg']['sessionID'],
                    'mes':datadict['messageViaOrg']['mes']
                }})

    def registerBank(self,datadict,c):
        bankdata = datadict['bank']
        newconnection = ConnectionObj(bankdata['id'],bankdata['name'],bankdata['key'],c)
        self.bankconnections.append(newconnection)
        newconnection.send({"registered":{}})
        print(self.bankconnections)
        return newconnection

    def handleBankConnection(self,bankconnection, datadict):
        print('using handlebankconneciton')
        

    def myHandler(self,c,a):
        newconnection = None
        bankconnection = None
        while True:
            try:
                data = c.recv(6000)
                datadict = None
                try:
                    datadict = json.loads(data)
                except:
                    print(data)
                    datadict = {}
                
                if(bankconnection is not None):
                    self.handleBankConnection(bankconnection,datadict)

                elif 'person' in datadict and newconnection is None:
                    newconnection = self.registerPerson(datadict,c)

                elif 'bank' in datadict and bankconnection is None:
                    print('Creating new bank connection')
                    bankconnection = self.registerBank(datadict,c)

                elif 'keyrequest' in datadict and newconnection is not None:
                    self.retreiveKeyRequest(datadict,newconnection)
 
                elif 'bankkeyrequest' in datadict and newconnection is not None:
                    self.retreiveBankKeyRequest(datadict,newconnection)

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

                elif 'messageViaOrg' in datadict and newconnection is not None:
                    print(datadict)
                    self.messageViaOrg(datadict,newconnection)
                
                elif 'sendToBank' in datadict and newconnection is not None:
                    print('Received sendToBank from one of the clients')
                    self.sendToBank(datadict, newconnection)
                
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
            print(str(a[0])+ ':' + str(a[1]), "connected")



if (len(sys.argv) > 1):
    if(sys.argv[1] == "client"):
        print('Constructing client')
        client = Client(sys.argv[2])
    elif(sys.argv[1] == "bank"):
        print('Constructing bank')
        bank = Bank(sys.argv[2])
    
    
    
else:
    server = Server()
    server.run()

