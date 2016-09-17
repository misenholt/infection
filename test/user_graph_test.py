'''
Created on Sep 13, 2016

@author: Max
'''
import unittest
from models.user_graph import CoachingGraph, GraphViolation, User
from _collections import defaultdict


class UserGraphTest(unittest.TestCase):


    def setUp(self):
        self.testGraph = CoachingGraph()
        self.testUser1 = User('test user I')
        self.testUser2 = User('test user II')


    def tearDown(self):
        pass


    def testGraph_addUser(self):
        self.testGraph.addUser(self.testUser1)
        self.assertEqual(len(self.testGraph.users), 1)
        
        with self.assertRaises(GraphViolation):
            self.testGraph.addUser(self.testUser1)
        self.assertEqual(len(self.testGraph.users), 1)
        
        self.testGraph.addUser(self.testUser2)
        self.assertEqual(len(self.testGraph.users), 2)
        


    def testGraph_addRelationship(self):
        #Both users not in graph
        with self.assertRaises(GraphViolation):
            self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
            
        #coachee not in graph
        self.testGraph.addUser(self.testUser1)
        with self.assertRaises(GraphViolation):
            self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        
        #coach not in graph    
        with self.assertRaises(GraphViolation):
            self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser1.UUID)
        
        #both users in graph    
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.assertEqual(len(self.testGraph.coaches.keys()), 1) 
        self.assertEqual(len(self.testGraph.coaches[self.testUser1.UUID]), 1) 
        
        #self reference
        with self.assertRaises(GraphViolation):
            self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser1.UUID)
            
        #slightly more complex graph
        self.testUser3 = User('test user III')
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testUser4 = User('test user IV')
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.assertEqual(len(self.testGraph.coaches.keys()), 2) #there should be 2 coaches in this graph
        self.assertEqual(len(self.testGraph.coaches[self.testUser1.UUID]), 2) #testUser1 should be in the coaches relationship with 2 coachees
        
        #disconnected graph
        self.testUser5 = User('test user V')
        self.testGraph.addUser(self.testUser5)
        self.testUser6 = User('test user VI')
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.assertEqual(len(self.testGraph.coaches.keys()), 3) #there should be 3 coaches in this graph
        
    def testInfect_disconnected(self):
        '''
        disconnected graph with a branch
        '''
        self.testUser1 = User('test user I', 1.0)
        self.testUser2 = User('test user II', 1.0)
        self.testUser3 = User('test user III', 1.0)
        self.testUser4 = User('test user IV', 1.0)
        self.testUser5 = User('test user V', 1.0)
        self.testUser6 = User('test user VI', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        
        self.testGraph.total_infection(self.testUser1.UUID, 1.1)
        self.assertEqual(self.testUser1.siteVersion, 1.1)
        self.assertEqual(self.testUser2.siteVersion, 1.1)
        self.assertEqual(self.testUser3.siteVersion, 1.1)
        self.assertEqual(self.testUser4.siteVersion, 1.1)
        self.assertEqual(self.testUser5.siteVersion, 1.0)
        self.assertEqual(self.testUser6.siteVersion, 1.0)
        
    def testInfect_upstream(self):
        '''
        upstream infection
        '''
        self.testUser1 = User('test user I', 1.0)
        self.testUser2 = User('test user II', 1.0)
        self.testUser3 = User('test user III', 1.0)
        self.testUser4 = User('test user IV', 1.0)
        self.testUser5 = User('test user V', 1.0)
        self.testUser6 = User('test user VI', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        
        self.testGraph.total_infection(self.testUser3.UUID, 1.1)
        self.assertEqual(self.testUser1.siteVersion, 1.1)
        self.assertEqual(self.testUser2.siteVersion, 1.1)
        self.assertEqual(self.testUser3.siteVersion, 1.1)
        self.assertEqual(self.testUser4.siteVersion, 1.1)
        self.assertEqual(self.testUser5.siteVersion, 1.0)
        self.assertEqual(self.testUser6.siteVersion, 1.0)
        
    def testInfect_looping(self):
        '''
        graph with a loop
        '''
        self.testUser1 = User('test user I', 1.0)
        self.testUser2 = User('test user II', 1.0)
        self.testUser3 = User('test user III', 1.0)
        self.testUser4 = User('test user IV', 1.0)
        self.testUser5 = User('test user V', 1.0)
        self.testUser6 = User('test user VI', 1.0)
        self.testUser7 = User('test user VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.testGraph.addCoachingRelationship(self.testUser6.UUID, self.testUser7.UUID)
        self.testGraph.addCoachingRelationship(self.testUser7.UUID, self.testUser5.UUID)
        
        self.testGraph.total_infection(self.testUser5.UUID, 1.1)
        self.assertEqual(self.testUser1.siteVersion, 1.0)
        self.assertEqual(self.testUser2.siteVersion, 1.0)
        self.assertEqual(self.testUser3.siteVersion, 1.0)
        self.assertEqual(self.testUser4.siteVersion, 1.0)
        self.assertEqual(self.testUser5.siteVersion, 1.1)
        self.assertEqual(self.testUser6.siteVersion, 1.1)
        self.assertEqual(self.testUser7.siteVersion, 1.1)
        
    def testInfect_looping_branching(self):
        '''
        graph with a loop and a branch off it
        '''
        self.testUser1 = User('test user I', 1.0)
        self.testUser2 = User('test user II', 1.0)
        self.testUser3 = User('test user III', 1.0)
        self.testUser4 = User('test user IV', 1.0)
        self.testUser5 = User('test user V', 1.0)
        self.testUser6 = User('test user VI', 1.0)
        self.testUser7 = User('test user VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser5.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.testGraph.addCoachingRelationship(self.testUser6.UUID, self.testUser7.UUID)
        self.testGraph.addCoachingRelationship(self.testUser7.UUID, self.testUser5.UUID)
        
        self.testGraph.total_infection(self.testUser6.UUID, 1.1)
        self.assertEqual(self.testUser1.siteVersion, 1.1)
        self.assertEqual(self.testUser2.siteVersion, 1.1)
        self.assertEqual(self.testUser3.siteVersion, 1.1)
        self.assertEqual(self.testUser4.siteVersion, 1.1)
        self.assertEqual(self.testUser5.siteVersion, 1.1)
        self.assertEqual(self.testUser6.siteVersion, 1.1)
        self.assertEqual(self.testUser7.siteVersion, 1.1)
        
    def testInfect_singleton(self):
        '''
        infection of a disconnected node
        '''
        self.testUser1 = User('test user I', 1.0)
        self.testUser2 = User('test user II', 1.0)
        self.testUser3 = User('test user III', 1.0)
        self.testUser4 = User('test user IV', 1.0)
        self.testUser5 = User('test user V', 1.0)
        self.testUser6 = User('test user VI', 1.0)
        self.testUser7 = User('test user VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        
        self.testGraph.total_infection(self.testUser7.UUID, 1.1)
        self.assertEqual(self.testUser1.siteVersion, 1.0)
        self.assertEqual(self.testUser2.siteVersion, 1.0)
        self.assertEqual(self.testUser3.siteVersion, 1.0)
        self.assertEqual(self.testUser4.siteVersion, 1.0)
        self.assertEqual(self.testUser5.siteVersion, 1.0)
        self.assertEqual(self.testUser6.siteVersion, 1.0)
        self.assertEqual(self.testUser7.siteVersion, 1.1)
        
    def testGetSpanningTree(self):
        '''
        graph with a loop and a branch off it
        '''
        self.testUser1 = User('I', 1.0)
        self.testUser2 = User('II', 1.0)
        self.testUser3 = User('III', 1.0)
        self.testUser4 = User('IV', 1.0)
        self.testUser5 = User('V', 1.0)
        self.testUser6 = User('VI', 1.0)
        self.testUser7 = User('VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser5.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.testGraph.addCoachingRelationship(self.testUser6.UUID, self.testUser7.UUID)
        self.testGraph.addCoachingRelationship(self.testUser7.UUID, self.testUser5.UUID)
        
        self.testGraph.virtualRootUser = User('R')
        self.testGraph.users[self.testGraph.virtualRootUser.UUID] = self.testGraph.virtualRootUser
        self.testGraph.spanningIs_coached_by = {} #dict of coacheeID:coachID
        self.testGraph.spanningCoaches = defaultdict(set) #dict of coachID:{coacheeIDs}
        self.testGraph.getSpanningTree()
        
        self.assertEqual(len(self.testGraph.users.keys()), len(self.testGraph.spanningIs_coached_by.keys()) + 1)

        self.assertEqual(set(self.testGraph.users.keys()), set(self.testGraph.spanningIs_coached_by.keys()) | {self.testGraph.virtualRootUser.UUID})
        
        edgeSet = {
            (self.testUser1.UUID, self.testUser2.UUID),
            (self.testUser1.UUID, self.testUser4.UUID),
            (self.testUser5.UUID, self.testUser6.UUID),
            (self.testUser2.UUID, self.testUser3.UUID),
            (self.testUser2.UUID, self.testUser5.UUID),
            (self.testUser6.UUID, self.testUser7.UUID),
            (self.testGraph.virtualRootUser.UUID, self.testUser1.UUID)
            }

        for coacheeID, coachID in self.testGraph.spanningIs_coached_by.items():
            self.assertIn((coachID, coacheeID), edgeSet)
             
        for coachID, coacheeID in edgeSet:
            self.assertIn((coacheeID, coachID), self.testGraph.spanningIs_coached_by.items())
              
        self.assertEqual(len(self.testGraph.users.keys()), len(self.testGraph.spanningIs_coached_by.keys()) + 1)
        self.assertEqual(set(self.testGraph.users.keys()), set(self.testGraph.spanningIs_coached_by.keys()) | {self.testGraph.virtualRootUser.UUID})
        
    def testGetSpanningTree_rootless_loop(self):
        '''
        graph with a loop and a branch off it
        '''
        self.testUser1 = User('I', 1.0)
        self.testUser2 = User('II', 1.0)
        self.testUser3 = User('III', 1.0)
        self.testUser4 = User('IV', 1.0)
        self.testUser5 = User('V', 1.0)
        self.testUser6 = User('VI', 1.0)
        self.testUser7 = User('VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
 
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.testGraph.addCoachingRelationship(self.testUser6.UUID, self.testUser7.UUID)
        self.testGraph.addCoachingRelationship(self.testUser7.UUID, self.testUser5.UUID)
          
        self.testGraph.virtualRootUser = User('Virtual Root')
        self.testGraph.users[self.testGraph.virtualRootUser.UUID] = self.testGraph.virtualRootUser
        self.testGraph.spanningIs_coached_by = {} #dict of coacheeID:coachID
        self.testGraph.spanningCoaches = defaultdict(set) #dict of coachID:{coacheeIDs}
        self.testGraph.getSpanningTree()
         
        edgeSet = {
            (self.testUser1.UUID, self.testUser2.UUID),
            (self.testUser1.UUID, self.testUser4.UUID),
            (self.testUser2.UUID, self.testUser3.UUID),
            (self.testGraph.virtualRootUser.UUID, self.testUser1.UUID)
        }
         
        optionalEdgeSet = {            
            (self.testUser5.UUID, self.testUser6.UUID),
            (self.testUser7.UUID, self.testUser5.UUID),
            (self.testUser6.UUID, self.testUser7.UUID)
        }
         
        optionalRootEdgeSet = {
            (self.testGraph.virtualRootUser.UUID, self.testUser5.UUID),
            (self.testGraph.virtualRootUser.UUID, self.testUser6.UUID),
            (self.testGraph.virtualRootUser.UUID, self.testUser7.UUID)
        }
         
        for coacheeID, coachID in self.testGraph.spanningIs_coached_by.items():
            self.assertTrue(
                (coachID, coacheeID) in edgeSet | optionalEdgeSet | optionalRootEdgeSet
            )
             
        for coachID, coacheeID in edgeSet:
            self.assertIn((coacheeID, coachID), self.testGraph.spanningIs_coached_by.items())
             
        c = 0
        for coachID, coacheeID in optionalEdgeSet:
            if not (coacheeID, coachID) in self.testGraph.spanningIs_coached_by.items(): c += 1
        self.assertEqual(c, 1)
 
        d = 0
        for coachID, coacheeID in optionalRootEdgeSet:
            if (coacheeID, coachID) in self.testGraph.spanningIs_coached_by.items(): d += 1
        self.assertEqual(d, 1)
             
         
    def testSetSubtreeSizes(self):
        '''
        graph with a loop and a branch off it
        '''
        self.testUser1 = User('I', 1.0)
        self.testUser2 = User('II', 1.0)
        self.testUser3 = User('III', 1.0)
        self.testUser4 = User('IV', 1.0)
        self.testUser5 = User('V', 1.0)
        self.testUser6 = User('VI', 1.0)
        self.testUser7 = User('VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser5.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.testGraph.addCoachingRelationship(self.testUser6.UUID, self.testUser7.UUID)
        self.testGraph.addCoachingRelationship(self.testUser7.UUID, self.testUser5.UUID)
        
        self.testGraph.virtualRootUser = User('R')
        self.testGraph.users[self.testGraph.virtualRootUser.UUID] = self.testGraph.virtualRootUser
        self.testGraph.spanningIs_coached_by = {} #dict of coacheeID:coachID
        self.testGraph.spanningCoaches = defaultdict(set) #dict of coachID:{coacheeIDs}
        self.testGraph.getSpanningTree()
        self.testGraph.setSubtreeSizes(self.testGraph.virtualRootUser.UUID)
        
        sizeDict = {
                    self.testGraph.virtualRootUser.UUID: 8, 
                    self.testUser1.UUID: 7, 
                    self.testUser2.UUID: 5, 
                    self.testUser3.UUID: 1, 
                    self.testUser4.UUID: 1, 
                    self.testUser5.UUID: 3, 
                    self.testUser6.UUID: 2, 
                    self.testUser7.UUID: 1
                    }
        
        for userID, user in self.testGraph.users.items():
            self.assertEqual(user.subtreeSize, sizeDict[userID])  
        
    def testSelectSubtree(self):
        '''
        graph with a loop and a branch off it
        '''
        self.testUser1 = User('I', 1.0)
        self.testUser2 = User('II', 1.0)
        self.testUser3 = User('III', 1.0)
        self.testUser4 = User('IV', 1.0)
        self.testUser5 = User('V', 1.0)
        self.testUser6 = User('VI', 1.0)
        self.testUser7 = User('VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser5.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.testGraph.addCoachingRelationship(self.testUser6.UUID, self.testUser7.UUID)
        self.testGraph.addCoachingRelationship(self.testUser7.UUID, self.testUser5.UUID)
         
        self.testGraph.virtualRootUser = User('R')
        self.testGraph.users[self.testGraph.virtualRootUser.UUID] = self.testGraph.virtualRootUser
        self.testGraph.spanningIs_coached_by = {} #dict of coacheeID:coachID
        self.testGraph.spanningCoaches = defaultdict(set) #dict of coachID:{coacheeIDs}
        self.testGraph.getSpanningTree()
        self.testGraph.setSubtreeSizes(self.testGraph.virtualRootUser.UUID)
             
        '''
        Test starts here
        '''
        self.assertEqual(self.testGraph.selectSubtree(3), self.testUser5.UUID)
        self.assertEqual(self.testGraph.selectSubtree(4), self.testUser5.UUID)
        self.assertEqual(self.testGraph.selectSubtree(5), self.testUser2.UUID)
        rootID = self.testGraph.selectSubtree(1)
        self.assertTrue(
            rootID == self.testUser3.UUID or 
            rootID == self.testUser4.UUID or 
            rootID == self.testUser7.UUID
            )
          
    def testInfectSubtree_size3(self):
        '''
        graph with a loop and a branch off it
        '''
        self.testUser1 = User('I', 1.0)
        self.testUser2 = User('II', 1.0)
        self.testUser3 = User('III', 1.0)
        self.testUser4 = User('IV', 1.0)
        self.testUser5 = User('V', 1.0)
        self.testUser6 = User('VI', 1.0)
        self.testUser7 = User('VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser5.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.testGraph.addCoachingRelationship(self.testUser6.UUID, self.testUser7.UUID)
        self.testGraph.addCoachingRelationship(self.testUser7.UUID, self.testUser5.UUID)
         
        self.testGraph.virtualRootUser = User('R')
        self.testGraph.users[self.testGraph.virtualRootUser.UUID] = self.testGraph.virtualRootUser
        self.testGraph.spanningIs_coached_by = {} #dict of coacheeID:coachID
        self.testGraph.spanningCoaches = defaultdict(set) #dict of coachID:{coacheeIDs}
        self.testGraph.getSpanningTree()
        self.testGraph.setSubtreeSizes(self.testGraph.virtualRootUser.UUID)
                 
        self.testGraph.infectSubtree(1.1, self.testGraph.selectSubtree(3))
         
        self.assertEqual(self.testUser1.siteVersion, 1.0)
        self.assertEqual(self.testUser2.siteVersion, 1.0)
        self.assertEqual(self.testUser3.siteVersion, 1.0)
        self.assertEqual(self.testUser4.siteVersion, 1.0)
        self.assertEqual(self.testUser5.siteVersion, 1.1)
        self.assertEqual(self.testUser6.siteVersion, 1.1)
        self.assertEqual(self.testUser7.siteVersion, 1.1)
         
    def testInfectSubtree_size4(self):
        '''
        graph with a loop and a branch off it
        '''
        self.testUser1 = User('I', 1.0)
        self.testUser2 = User('II', 1.0)
        self.testUser3 = User('III', 1.0)
        self.testUser4 = User('IV', 1.0)
        self.testUser5 = User('V', 1.0)
        self.testUser6 = User('VI', 1.0)
        self.testUser7 = User('VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser5.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.testGraph.addCoachingRelationship(self.testUser6.UUID, self.testUser7.UUID)
        self.testGraph.addCoachingRelationship(self.testUser7.UUID, self.testUser5.UUID)
         
        self.testGraph.virtualRootUser = User('R')
        self.testGraph.users[self.testGraph.virtualRootUser.UUID] = self.testGraph.virtualRootUser
        self.testGraph.spanningIs_coached_by = {} #dict of coacheeID:coachID
        self.testGraph.spanningCoaches = defaultdict(set) #dict of coachID:{coacheeIDs}
        self.testGraph.getSpanningTree()
        self.testGraph.setSubtreeSizes(self.testGraph.virtualRootUser.UUID)
                 
        self.testGraph.infectSubtree(1.1, self.testGraph.selectSubtree(4))
         
        self.assertEqual(self.testUser1.siteVersion, 1.0)
        self.assertEqual(self.testUser2.siteVersion, 1.0)
        self.assertEqual(self.testUser3.siteVersion, 1.0)
        self.assertEqual(self.testUser4.siteVersion, 1.0)
        self.assertEqual(self.testUser5.siteVersion, 1.1)
        self.assertEqual(self.testUser6.siteVersion, 1.1)
        self.assertEqual(self.testUser7.siteVersion, 1.1)
         
    def testInfectSubtree_size5(self):
        '''
        graph with a loop and a branch off it
        '''
        self.testUser1 = User('I', 1.0)
        self.testUser2 = User('II', 1.0)
        self.testUser3 = User('III', 1.0)
        self.testUser4 = User('IV', 1.0)
        self.testUser5 = User('V', 1.0)
        self.testUser6 = User('VI', 1.0)
        self.testUser7 = User('VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser5.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.testGraph.addCoachingRelationship(self.testUser6.UUID, self.testUser7.UUID)
        self.testGraph.addCoachingRelationship(self.testUser7.UUID, self.testUser5.UUID)
         
        self.testGraph.virtualRootUser = User('R')
        self.testGraph.users[self.testGraph.virtualRootUser.UUID] = self.testGraph.virtualRootUser
        self.testGraph.spanningIs_coached_by = {} #dict of coacheeID:coachID
        self.testGraph.spanningCoaches = defaultdict(set) #dict of coachID:{coacheeIDs}
        self.testGraph.getSpanningTree()
        self.testGraph.setSubtreeSizes(self.testGraph.virtualRootUser.UUID)
                 
        self.testGraph.infectSubtree(1.1, self.testGraph.selectSubtree(5))
         
        self.assertEqual(self.testUser1.siteVersion, 1.0)
        self.assertEqual(self.testUser2.siteVersion, 1.1)
        self.assertEqual(self.testUser3.siteVersion, 1.1)
        self.assertEqual(self.testUser4.siteVersion, 1.0)
        self.assertEqual(self.testUser5.siteVersion, 1.1)
        self.assertEqual(self.testUser6.siteVersion, 1.1)
        self.assertEqual(self.testUser7.siteVersion, 1.1)
         
    def testLimitedInfection(self):
        '''
        graph with a loop and a branch off it
        '''
        self.testUser1 = User('I', 1.0)
        self.testUser2 = User('II', 1.0)
        self.testUser3 = User('III', 1.0)
        self.testUser4 = User('IV', 1.0)
        self.testUser5 = User('V', 1.0)
        self.testUser6 = User('VI', 1.0)
        self.testUser7 = User('VII', 1.0)
        self.testGraph.addUser(self.testUser1)
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addUser(self.testUser5)
        self.testGraph.addUser(self.testUser6)
        self.testGraph.addUser(self.testUser7)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser5.UUID)
        self.testGraph.addCoachingRelationship(self.testUser5.UUID, self.testUser6.UUID)
        self.testGraph.addCoachingRelationship(self.testUser6.UUID, self.testUser7.UUID)
        self.testGraph.addCoachingRelationship(self.testUser7.UUID, self.testUser5.UUID)
        
        self.testGraph.limited_infection(1.1, 5)
         
        self.assertEqual(self.testUser1.siteVersion, 1.0)
        self.assertEqual(self.testUser2.siteVersion, 1.1)
        self.assertEqual(self.testUser3.siteVersion, 1.1)
        self.assertEqual(self.testUser4.siteVersion, 1.0)
        self.assertEqual(self.testUser5.siteVersion, 1.1)
        self.assertEqual(self.testUser6.siteVersion, 1.1)
        self.assertEqual(self.testUser7.siteVersion, 1.1)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'UserGraphTest.testName']
    unittest.main()