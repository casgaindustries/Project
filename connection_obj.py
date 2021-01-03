import json

# Connection object, keeps track of socket, clientID and pubkey
class ConnectionObj:

    def __init__(self,id,name,key,c):
        self.messagesToReceive = []
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
    
    def asdict(self):
        return {'id': self.id, 'name': self.name}