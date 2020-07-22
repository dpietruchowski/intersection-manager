from intersection.agent import Agent
from intersection.world import World
from collections import namedtuple
from startsim import simulation_loop
from sumowrapper import Simulation

import unittest
import logging

class Vehicle:
    def __init__(self):
        self.speed_mode = 1
        self.max_speed = 55
        self.speed = 10
        self.distance = 0
        self.accel = 10
        self.decel = 5
        self.route_id = 'r1'
        self.road_id = 'r2'

WorldMock = namedtuple('World', 'routes')

def findStatForTime(stats, time):
    for stat in stats:
        if stat.time >= time:
            return stat
    return None

class TestAgent(unittest.TestCase):
    def assertNear(self, value, expected, diff=0.05):
        self.assertTrue(abs(value - expected) < diff, 
                'value: %f, expected: %f, diff: %f' % (value, expected, abs(value - expected)))

    @unittest.skip
    def test_straight_accel(self):
        Simulation.sumo_binary = 'sumo'
        world = World()
        world.load_net('configs/straight/straight.net.xml')
        world.load_routes('configs/straight/straight.rou.xml')
        Agent.max_accel = 2.6
        Agent.max_decel = 4.5
        Agent.default_speed = 10
        stats = simulation_loop('configs/straight/straight.sumocfg', world)
        stat3_85 = findStatForTime(stats['vehicle_0'], 3.85)
        self.assertNear(stat3_85.time, 3.85)
        self.assertNear(stat3_85.distance, 19.27)
        self.assertNear(stat3_85.velocity, 10)


    def test_agent_new(self):
        Simulation.sumo_binary = 'sumo'
        world = World()
        world.load_net('configs/new/new.net.xml')
        world.load_routes('configs/new/new.rou.xml')
        Agent.max_accel = 2.6
        Agent.max_decel = 4.5
        Agent.default_speed = 10
        stats = simulation_loop('configs/new/new.sumocfg', world)
        stat3_85 = findStatForTime(stats['vehicle_0'], 3.85)


    
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.disabled = True
    unittest.main(exit=True)