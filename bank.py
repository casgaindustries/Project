
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
        #*Init bank accounts in original json
        self.initBankAccounts(self.data['users'])
        
        #* Register at central server
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

            if 'pubkey' in datadict:
                print('Received pubkey')

            else:
                print(datadict)
            print(' ')
            
    
    def sendOverSocket(self, dicttosend):
        json_object = json.dumps(dicttosend, indent = 4)   
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
            if(self.typedsplit[0] == "SEND"):
                print('Send message detected')
                self.sendOverSocket({'bank': "or not"})
            if(self.typedsplit[0]== "GETONLINE"):
                print("asking who's online")
                self.sendOverSocket({"cool" : "story m8"})
    
    def initBankAccounts(self, d):
        print("initializing bank accouts:")
        for u in d:
            self.bankAccounts.append(BankAccount(u))
        print(self.bankAccounts)
        