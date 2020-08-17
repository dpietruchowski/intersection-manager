from intersection.agent import Agent
from intersection.world import World
from intersection.motion import MotionPoint, Motion
from collections import namedtuple
from startsim import simulation_loop
from sumowrapper import Simulation

import unittest
import logging
import matplotlib.pyplot as plt

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
    def assertNear(self, value, expected, diff=0.1):
        self.assertTrue(abs(value - expected) < diff, 
                'value: %f, expected: %f, diff: %f' % (value, expected, abs(value - expected)))

    def test_straight_accel(self):
        Simulation.sumo_binary = 'sumo-gui'
        world = World()
        world.load_net('configs/straight/straight.net.xml')
        world.load_routes('configs/straight/straight.rou.xml')
        Agent.max_accel = 2.6
        Agent.max_decel = 4.5
        motion = Motion(0, 10, Agent.max_accel, Agent.max_decel)
        velocity = motion.calc_velocity(distance = 270, time = 200)
        Agent.default_motion_points = motion.calc_motion_points(velocity = velocity, time = 200)
        stats = simulation_loop('configs/straight/straight.sumocfg', world)
        stats_20 = findStatForTime(stats['vehicle_0'], 20)
        listStats = map(list, zip(*stats['vehicle_0']))
        plt.plot(listStats[0], listStats[2])
        listStats = map(list, zip(*Agent.default_motion_points))
        plt.plot(listStats[0], listStats[1])
        plt.show()
        self.assertNear(stats_20.distance, 270)

'''
    def test_straight_accel(self):
        Simulation.sumo_binary = 'sumo-gui'
        world = World()
        world.load_net('configs/straight/straight.net.xml')
        world.load_routes('configs/straight/straight.rou.xml')
        Agent.max_accel = 2.6
        Agent.max_decel = 4.5
        Agent.default_motion_points = [
            MotionPoint(t = 0, v = 0, d = 0),
            MotionPoint(t = 15, v = 15, d = 0),
            MotionPoint(t = 20, v = 15, d = 0),
            MotionPoint(t = 26, v = 10, d = 0)
        ]
        stats = simulation_loop('configs/straight/straight.sumocfg', world)
        stat3_85 = findStatForTime(stats['vehicle_0'], 3.85)
        listStats = map(list, zip(*stats['vehicle_0']))
        plt.plot(listStats[0], listStats[2])
        plt.show()



    def test_agent_new(self):
        Simulation.sumo_binary = 'sumo-gui'
        world = World()
        world.load_net('configs/new/new.net.xml')
        world.load_routes('configs/new/new.rou.xml')
        Agent.max_accel = 2.6
        Agent.max_decel = 4.5
        Agent.default_speed = 10
        stats = simulation_loop('configs/new/new.sumocfg', world)
        listStats = map(list, zip(*stats['vehicle_0']))
        plt.plot(listStats[0], listStats[2])
        plt.show()
'''



    
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.disabled = False
    unittest.main(exit=True)