'''
Created on Sep 13, 2016

@author: Max
'''
from uuid import uuid4
from _collections import defaultdict
from queue import Queue
from operator import itemgetter

class User(object):
    '''
    UUID is set when the user is created and does not change
    siteVersion may be set and changed at any time
    name represents any information attached to the user that does not affect infection
    '''


    def __init__(self, name, version=None):
        '''
        Constructor
        '''
        self.UUID = uuid4() #each user should have a unique ID
        self.tutors = set()
        self.name = name
        if version: self.setVersion(version)
        
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
    self.is_coached_by is a dict of uuid_of_coachee:[uuids_of_coaches[ 
    '''


    def __init__(self):
        self.users = {}
        self.coaches = defaultdict(set)
        self.is_coached_by = defaultdict(list)
            
    def addUser(self, newUser):
        if newUser.UUID in self.users.keys():
            raise GraphViolation('User with ID {} already exists.'.format(newUser.UUID))
        self.users[newUser.UUID] = newUser
        
    def addCoachingRelationship(self, coachID, coacheeID):
        for ID in [coachID, coacheeID]:
            if ID not in self.users.keys():
                raise GraphViolation('User with ID {} does not exist.'.format(ID))
            
        if coachID == coacheeID:
            raise GraphViolation('Self-referential relationship')
            
            
        self.coaches[coachID].add(coacheeID)
        self.is_coached_by[coacheeID].append(coachID)
        
    def total_infection(self, startingUserID, newVersionNumber):
        infectedUsers = set()
        processingQueue = Queue()
        processingQueue.put(startingUserID)
        while not processingQueue.empty():
            currentID = processingQueue.get()
            self.users[currentID].setVersion(newVersionNumber)
            
            #treat relations in both directions identically for infection
            for userID in self.coaches[currentID]:
                if userID in infectedUsers: continue
                infectedUsers.add(userID)   #add users to infected list when they go on the queue to avoid duplicates
                processingQueue.put(userID)
                
            for userID in self.is_coached_by[currentID]:
                if userID in infectedUsers: continue
                infectedUsers.add(userID)
                processingQueue.put(userID)
        

    def limited_infection(self, newVersionNumber, numberToInfect):
        '''
        This algorithm is based on the intuition that our graph will look a lot like a tree.
        That is to say there will be relatively few users with more than one coach and even fewer cycles
        Therefore I have foregone the more robust but heavier algorithms in favour of lighter options.
        
        The second intuition is that the best way to partition a connected component for infection in to select an entire
        subtree of the spanning tree. A heavier option would be to use one of several graph partition algorithms. 
        The reason I am considering these heavier is because we would have to optimize on two variables: 
        both on 'niceness' of the partition and on deviation from desired size.
        
        Therefore the algorithm is as follows:
        1. Create a spanning tree of each connected component
        2. Join the roots of the trees to a virtual root to create a single spanning tree for the graph
        3. Traverse the tree, assigning to each node the number of nodes in the subtree rooted at that node
        4. Select the subtree whose size is nearest to the number of desired infections
        5. Infect that subtree
        '''
        self.virtualRootUser = User('Virtual Root')
        self.users[self.virtualRootUser.UUID] = self.virtualRootUser
        self.spanningIs_coached_by = {} #dict of coacheeID:coachID
        self.spanningCoaches = defaultdict(set) #dict of coachID:{coacheeIDs}
        
        self.getSpanningTree()
        self.setSubtreeSizes(self.virtualRootUser.UUID)
        self.infectSubtree(newVersionNumber, self.selectSubtree(numberToInfect))
        
    def limited_infection_exact(self, newVersionNumber, numberToInfect):
        '''
        not finished implementing, not tested
        '''
        self.virtualRootUser = User('Virtual Root')
        self.users[self.virtualRootUser.UUID] = self.virtualRootUser
        self.spanningIs_coached_by = {} #dict of coacheeID:coachID
        self.spanningCoaches = defaultdict(set) #dict of coachID:{coacheeIDs}
        
        self.getSpanningTree()
        self.setSubtreeSizes(self.virtualRootUser.UUID)
        for s in self.selectSubtree_exact(numberToInfect):
            self.infectSubtree(newVersionNumber, s)
        

    def getSpanningTree(self):
        '''
        Constructing the spanning tree
        The edges are unweighted, so the algorithm is pretty simple.
        However the graph is directed and while the direction may not matter for infection, it probably matters for 'niceness'
        So we are preserving the coach-coachee relationship in the spanning tree, which may not result in a strictly minimal
        spanning tree
        I am also joining the roots to the virtual master root as soon as they are identified for convenience
        '''
        rootUserIDs = self.users.keys() - self.is_coached_by.keys() - {self.virtualRootUser.UUID} #root users are users that are not coachees
#         print('RR', rootUserIDs)
        processingQueue = Queue()
        for rootUserID in rootUserIDs:
            processingQueue.put(rootUserID)
        
        while not processingQueue.empty():
            currentUserID = processingQueue.get()
#             print(currentUserID)
            if currentUserID in self.spanningIs_coached_by.keys():
                continue
            elif currentUserID in rootUserIDs:
                self.spanningIs_coached_by[currentUserID] = self.virtualRootUser.UUID
                self.spanningCoaches[self.virtualRootUser.UUID].add(currentUserID)
            else:
                self.spanningIs_coached_by[currentUserID] = self.is_coached_by[currentUserID][0]
                self.spanningCoaches[self.is_coached_by[currentUserID][0]].add(currentUserID)
                
            for coacheeID in self.coaches[currentUserID]:
                processingQueue.put(coacheeID)
                
        '''
        handling rootless cycles
        '''
        unhandled = self.users.keys() - self.spanningIs_coached_by.keys() - {self.virtualRootUser.UUID}
        while len(unhandled) > 0:           #So long as there are users not in the tree
            newRoot = list(unhandled)[0]    #semirandomly select a root user from the rootless subgraph
            processingQueue = Queue()       #build from the root as before
            processingQueue.put(newRoot)
            while not processingQueue.empty():
                currentUserID = processingQueue.get()
                if currentUserID in self.spanningIs_coached_by.keys():
                    continue
                elif currentUserID == newRoot:
                    self.spanningIs_coached_by[newRoot] = self.virtualRootUser.UUID #attach it to the virtual root
                    self.spanningCoaches[self.virtualRootUser.UUID].add(newRoot)
                else:
                    self.spanningIs_coached_by[currentUserID] = self.is_coached_by[currentUserID][0]
                    self.spanningCoaches[self.is_coached_by[currentUserID][0]].add(currentUserID)
                
                for coacheeID in self.coaches[currentUserID]:
                    processingQueue.put(coacheeID)
                    
            unhandled = self.users.keys() - self.spanningIs_coached_by.keys() - {self.virtualRootUser.UUID}


    def setSubtreeSizes(self, rootID):
        '''
        adding subtree sizes
        this method is called recursively to do a post-order depth-first traversal of the spanning tree
        '''
        size = 1
        for childID in self.spanningCoaches[rootID]:
            self.setSubtreeSizes(childID)
            size += self.users[childID].subtreeSize
        
        self.users[rootID].subtreeSize = size
        
                
    def selectSubtree(self, targetSize):
        ordered = sorted([(user.UUID, user.subtreeSize) for user in self.users.values()], key=itemgetter(1))
        prevSize = 0
        prevID = None
        for ID, size in ordered: #TODO: make this a O(log n) search
            if size < targetSize:
                prevSize = size
                prevID = ID
            elif size == targetSize:
                return ID
            else:   #prevSize < targetSize < size
                if targetSize - prevSize > size - targetSize:
                    return ID
                else:
                    return prevID
                
    def selectSubtree_exact(self, targetSize):
        '''
        not implemented
        implementation idea: search through the subtrees in largest-to-smallest order, finding the largest tree that 
        fits in the difference and adding them until you run out of subtrees or hit the target value.
        This hould work as there are usually many leaves to the spanning tree, but it may not be a very desirable solution.
        
        Also we should switch to a O(log n) search rather than the linear search we are currently using in limited infection
        ''' 
        
    def infectSubtree(self, newVersionNumber, rootID):
        processingQueue = Queue()
        processingQueue.put(rootID)
        while not processingQueue.empty():
            currentUserID = processingQueue.get()
            self.users[currentUserID].setVersion(newVersionNumber)
            for childID in self.spanningCoaches[currentUserID]:
                processingQueue.put(childID)
        
    
class GraphViolation(Exception):
    
    def __init__(self, message):
        self.message = message
        
