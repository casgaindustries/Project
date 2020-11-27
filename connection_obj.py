import json

class ConnectionObj:
    id = None
    name = None
    key = None
    messagesToReceive = []

    #The actual connection object which python understands:
    c= None

    def __init__(self,id,name,key,c):
        print('ait bro niewe connec')
        self.id = id
        self.name = name
        self.key = key
        self.c = c
    
    def send(self, message):
        json_object = json.dumps(message, indent = 4)
    
        self.c.send(bytes(json_object, encoding = 'utf-8'))

    def __str__(self):
        return "%s,  %s, %s...." % (self.id, self.name, self.key[0:10])

    def __repr__(self):
        return self.__str__()