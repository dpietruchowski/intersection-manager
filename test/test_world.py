from intersection.junction import Cell, Lane, Area
from intersection.world import Edge, World

import unittest

class TestWorld(unittest.TestCase):
    def testLoading(self):
        world = World()
        world.load_net('configs/test/test.net.xml')
        self.assertTrue(world.junctions["gneJ1"])
        print world.junctions["gneJ1"].lanes
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_3_0"].from_edge, world.edges["gneE0"])
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_3_0"].to_edge, world.edges["gneE6"])
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_2_0"].from_edge, world.edges["gneE0"])
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_2_0"].to_edge, world.edges["gneE5"])
        #self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_1_0"].from_edge, world.edges["gneE4"])
        #self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_1_0"].to_edge, world.edges["gneE6"])
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_0_0"].from_edge, world.edges["gneE4"])
        self.assertEqual(world.junctions["gneJ1"].lanes[":gneJ1_0_0"].to_edge, world.edges["gneE5"])

    def testLoadingRoute(self):
        world = World()
        world.load_net('configs/test/test.net.xml')
        world.load_routes('configs/test/test.rou.xml')
        print world.routes

    def testRoute(self):
        world = World()
        world.load_net('configs/test/test.net.xml')
        world.load_routes('configs/test/test.rou.xml')
        self.assertTrue(world.junctions["gneJ1"])
        self.assertTrue(world.routes['route_0'])
        self.assertTrue(world.routes['route_1'])
        self.assertEqual(world.routes['route_0'].get_next_junction('gneE0')[2].id, 'gneJ1')
        self.assertEqual(world.routes['route_0'].get_next_junction('gneE6')[2], None)
        self.assertEqual(world.routes['route_0'].get_next_junction('gneE4')[2], None)
        self.assertEqual(world.routes['route_1'].get_next_junction('gneE4')[2].id, 'gneJ1')
        self.assertEqual(world.routes['route_1'].get_next_junction('gneE5')[2], None)
        self.assertEqual(world.routes['route_1'].get_next_junction('gneE0')[2], None)
        pass

    
if __name__ == "__main__":
    unittest.main(exit=True)