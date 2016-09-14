'''
Created on Sep 13, 2016

@author: Max
'''
import unittest
from models.user_graph import CoachingGraph, GraphViolation, User


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
        with self.assertRaises(GraphViolation):
            self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
            
        self.testGraph.addUser(self.testUser1)
        with self.assertRaises(GraphViolation):
            self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
            
        with self.assertRaises(GraphViolation):
            self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser1.UUID)
            
        self.testGraph.addUser(self.testUser2)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser2.UUID)
        
        with self.assertRaises(GraphViolation):
            self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser1.UUID)
            
        
        self.testUser3 = User('test user III')
        self.testGraph.addUser(self.testUser3)
        self.testGraph.addCoachingRelationship(self.testUser2.UUID, self.testUser3.UUID)
        self.testUser4 = User('test user IV')
        self.testGraph.addUser(self.testUser4)
        self.testGraph.addCoachingRelationship(self.testUser1.UUID, self.testUser4.UUID)
        self.assertEqual(len(self.testGraph.coaches.keys()), 2) #there should be 2 coaches in this graph
        self.assertEqual(len(self.testGraph.coaches[self.testUser1.UUID]), 2) #testUser1 should be in the coaches relationship with 2 coachees

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'UserGraphTest.testName']
    unittest.main()