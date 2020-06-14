from intersection.junction import Cell, Lane, Area
from intersection.world import Edge, World
from PyQt5.QtCore import *

import unittest

class TestWorld(unittest.TestCase):
    def testLoading(self):
        world = World()
        world.loadNet('configs/test/test.net.xml')
        self.assertTrue(world.junctions["gneJ1"])
        print world.junctions["gneJ1"].lanes
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_3_0"].fromEdge, world.edges["gneE0"])
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_3_0"].toEdge, world.edges["gneE6"])
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_2_0"].fromEdge, world.edges["gneE0"])
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_2_0"].toEdge, world.edges["gneE5"])
        #self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_1_0"].fromEdge, world.edges["gneE4"])
        #self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_1_0"].toEdge, world.edges["gneE6"])
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_0_0"].fromEdge, world.edges["gneE4"])
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_0_0"].toEdge, world.edges["gneE5"])

    def testLoadingRoute(self):
        world = World()
        world.loadNet('configs/test/test.net.xml')
        world.loadRoutes('configs/test/test.rou.xml')
        print world.routes

    def testRoute(self):
        world = World()
        world.loadNet('configs/test/test.net.xml')
        self.assertTrue(world.junctions["gneJ1"])
        pass

    
if __name__ == "__main__":
    unittest.main(exit=True)