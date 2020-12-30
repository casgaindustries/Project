class BankAccount:
    def __init__(self,data):
        self.id = data['id']
        self.roles = data['roles']
        self.balance = data['balance']

    def __str__(self):
        return "Bank account: %s,  %s, %s \n" % (self.id, self.roles,self.balance)

    def __repr__(self):
        return self.__str__()