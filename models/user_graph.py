'''
Created on Sep 13, 2016

@author: Max
'''
from uuid import uuid4
from _collections import defaultdict

class User(object):
    '''
    UUID is set when the user is created and does not change
    siteVersion may be set and changed at any time
    name represents any information attached to the user that does not affect infection
    '''


    def __init__(self, name):
        '''
        Constructor
        '''
        self.UUID = uuid4() #each user should have a unique ID
        self.tutors = set()
        self.name = name
        
    def setVersion(self, version):
        self.siteVersion = version
    
class CoachingGraph(object):
    '''
    We are using the canonical definition of a graph as 
    a set of vertices (users) and a set of edges (coaching relationships)
    
    coaching relationships have two types: coaches, and is_coached_by
    both relationships have an arity of zero or more
    
    self.users is a dict of uuid:User
    self.coaches is a dict of uuid_of_coach:{uuids_of_coachees}
    self.is_coached_by is a dict of uuid_of_coachee:{uuids_of_coaches} 
    '''


    def __init__(self, params):
        self.users = {}
        self.coaches = defaultdict(set)
        self.is_coached_by = defaultdict(set)
            
    def addUser(self, newUser):
        if newUser.UUID in self.users.keys():
            raise DuplicateUser(newUser.UUID)
        self.users[newUser.UUID] = newUser
        
    def addCoachingRelationship(self, coachID, coacheeID):
        for ID in [coachID, coacheeID]:
            if ID not in self.users.keys():
                raise NonexistentUser(ID)
            
        self.coaches[coachID].add(coacheeID)
        self.is_coached_by[coacheeID].add(coachID)
    
class DuplicateUser(Exception):
    
    def __init__(self, userID):
        self.userID = userID
        self.message = 'User with ID {} already exists.'.format(self.userID)
        
class NonexistentUser(Exception):
    
    def __init__(self, userID):
        self.userID = userID
        self.message = 'User with ID {} does not exist.'.format(self.userID)
