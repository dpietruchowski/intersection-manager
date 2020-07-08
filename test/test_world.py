from intersection.junction import Cell, Lane, Area
from intersection.world import Edge, World

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
        world.loadRoutes('configs/test/test.rou.xml')
        self.assertTrue(world.junctions["gneJ1"])
        self.assertTrue(world.routes['route_0'])
        self.assertTrue(world.routes['route_1'])
        self.assertEqual(world.routes['route_0'].getNextJunction('gneE0').id, 'gneJ1')
        self.assertEqual(world.routes['route_0'].getNextJunction('gneE6').id, 'gneJ8')
        self.assertEqual(world.routes['route_0'].getNextJunction('gneE4'), None)
        self.assertEqual(world.routes['route_1'].getNextJunction('gneE4').id, 'gneJ1')
        self.assertEqual(world.routes['route_1'].getNextJunction('gneE5').id, 'gneJ6')
        self.assertEqual(world.routes['route_1'].getNextJunction('gneE0'), None)
        pass

    
if __name__ == "__main__":
    unittest.main(exit=True)