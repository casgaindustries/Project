class Session:
    id = None
    orgName = None
    orgID = None
    key = None

    def __init__(self, dict):
        self.id = dict['sessionID']
        self.orgID = dict['orgID']
        self.orgName  = dict['orgName']
        self.key = dict['key']

    def __str__(self):
        # print(self.id," ",self.name, " ", self.employees)
        return "Session id: %s, orgName:  %s, orgID %s, key %s" % (self.id, self.orgName, self.orgID, self.key[:12])

    def __repr__(self):
        return self.__str__()