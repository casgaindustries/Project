class ConnectionObj:
    id = None
    name = None
    key = None
    
    #The actual connection object which python understands:
    c= None

    def __init__(self,id,name,key,c):
        print('ait bro niewe connec')
        self.id = id
        self.name = name
        self.key = key
        self.c = c

    def __str__(self):
        return "%s,  %s, %s...." % (self.id, self.name, self.key[0:10])