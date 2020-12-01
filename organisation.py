
#! For now the only roles in an org are moderator and employee
class Organisation:
    name = None
    id = None
    employees = []

    def __init__(self, orgdict):
        self.name = orgdict['name']
        self.id = orgdict['id']
        self.setEmployees(orgdict['employees'])

    def setEmployees(self, employeesdict):
        self.employees = []
        for e in employeesdict:
            self.employees.append(Employee(e['id'],e['roles']))

    def printEmployees(self):
        for e in self.employees:
            print(e)

    def getAllEmployees(self):
        return self.employees

    def getAllOnlineEmployees(self, connectedList):
        print('getallonineemployes')
    
    def __str__(self):
        # print(self.id," ",self.name, " ", self.employees)
        return "%s,  %s, %s" % (self.id, self.name, self.employees)

    def __repr__(self):
        return self.__str__()
    


class Employee:
    id = None
    myRoles = []
    
    def __init__(self,id,roles):
        self.id = id
        self.myRoles = roles
        
    
    def __str__(self):
        return "%s,  %s" % (self.id, self.myRoles)

    def __repr__(self):
        return self.__str__()