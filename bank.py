from datetime import datetime

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
from bank_account import *

# The bank is a client which can receive and send messages
# It keeps track of all its bank accounts, and can alter their balances
class Bank:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, jsonfile):
        f = open (jsonfile, encoding='utf-8') 
        self.data = json.loads(f.read()) 
        print(self.data)

        self.myEncrypt = MyEncrypt()        
        self.sock.connect((self.data['server']['ip'],int(self.data['server']['port'])))
        
        
        self.id = self.data['id']
        self.name = self.data['name']
        self.bankAccounts = []
        self.initBankAccounts(self.data['users'])
        
        # Register at central server
        bdict = {"bank":{
            "id": self.data['id'],
            "name": self.data['name'],
            "key":self.myEncrypt.getPubKeyB64()
        }}
        self.sendOverSocket(bdict)


        iThread = threading.Thread(target = self.handleInput)
        iThread.deamon = True
        iThread.start()

        while True:
            data = self.sock.recv(6000)
            if not data:
                break
            
            datadict = json.loads(data)

            if 'userMessage' in datadict:
                print('userMessage Detected')
                self.handleUserMessage(datadict)

            else:
                print(datadict)
            print(' ')
            
    # Sends to server
    def sendOverSocket(self, dicttosend):
        json_object = json.dumps(dicttosend, indent = 4)   
        self.sock.send(bytes(json_object, encoding = 'utf-8'))
    
    # Tries to send money from one bank account to the other, sends error if it's impossible
    def tryAdd(self,fromID, toID, amt):
        fromacc = None
        toacc = None
        
        for bacc in self.bankAccounts:
            if bacc.id == fromID:
                fromacc = bacc
            elif bacc.id == toID:
                toacc = bacc
        
        print('-------BEFORE--------')
        print('fromacc:')
        print(fromacc)
        print('toacc')
        print(toacc)

        if(fromacc is None or toacc is None):
            #TODO return error message

            self.sendErrorToUser(fromID,"That account wasn't found")
            return
        
        if(fromacc.balance<amt):
            #TODO return error message
            self.sendErrorToUser(fromID,"You don't have enough funds")
            return
        if(amt<0):
            self.sendErrorToUser(fromID,"You can't transfer a negative amount")
            return
        
        fromacc.balance = fromacc.balance - amt
        toacc.balance = toacc.balance + amt

        f = open("logfile.txt", "a")
        f.write("{0} -- {1}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M"), "Sent "+str(amt)+" from "+str(fromacc.id)+ " to "+str(toacc.id)))
        f.close()

        print('-------AFTER--------')
        print('fromacc:')
        print(fromacc)
        print('toacc')
        print(toacc)

    #Tries to sub from a given account, sends error if not right
    def trySub(self,fromID, amt):
        fromacc = None
        
        for bacc in self.bankAccounts:
            if bacc.id == fromID:
                fromacc = bacc
        
        print('-------BEFORE--------')
        print('fromacc:')
        print(fromacc)
        

        if(fromacc is None):
            #TODO return error message

            self.sendErrorToUser(fromID,"That account wasn't found")
            return
        
        if(fromacc.balance<amt):
            #TODO return error message
            self.sendErrorToUser(fromID,"You don't have enough funds")
            return
        if(amt<0):
            self.sendErrorToUser(fromID,"You can't sub a negative amount")
            return
        
        befbal = fromacc.balance
        fromacc.balance = fromacc.balance - amt

        f = open("logfile.txt", "a")
        f.write("{0} -- {1}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M"), "Subtracted "+str(amt)+" from "+str(fromID)+ ", balance after: "+str(fromacc.balance)))
        f.close()

        print('-------AFTER--------')
        print('fromacc:')
        print(fromacc)

        
        
    # Decrypts message from a user and handles it
    def handleUserMessage(self, datadict):
        d = datadict['userMessage']
        userID = d['userID']
        enmes = d['message']
        mes = self.myEncrypt.decryptB64(enmes)
        # print(mes)
        mesdict = json.loads(mes)
        print(mesdict)

        if(userID is not mesdict['from']):
            print('user not authorised')
            print(userID + ' vs '+mesdict['from'])
            self.sendErrorToUser(userID,"You are not authorised to take money from that account")
            return

        if mesdict['type']=='ADD':
            self.tryAdd(userID,mesdict['to'],mesdict['amt'])
        elif mesdict['type']=='SUB':
            self.trySub(userID, mesdict['amt'])
        
    def sendErrorToUser(self, userID, message):
        dicttosend = {"userError":{
            "userID": userID,
            "mes":message
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
            # print('input:  ')
            # for e in self.typedsplit:
            #     print(e)
            # if(self.typedsplit[0] == "SEND"):
            #     print('Send message detected')
            #     self.sendOverSocket({'bank': "or not"})
            # if(self.typedsplit[0]== "GETONLINE"):
            #     print("asking who's online")
            #     self.sendOverSocket({"cool" : "story m8"})
    
    # inits bank account from bank_config json
    def initBankAccounts(self, d):
        print("initializing bank accouts:")
        for u in d:
            self.bankAccounts.append(BankAccount(u))
        print(self.bankAccounts)
        