import traci
import math
from collections import namedtuple

Registration = namedtuple('Registration', ['t', 'v'])

class Agent:
    step_length = 0.1
    def __init__(self, id, world):
        self.id = id
        self.route = world.routes[traci.vehicle.getRouteID(self.id)]
        self.junctions = {} #[id].time/velocity
        traci.vehicle.setSpeedMode(self.id, 1)

    def register_next(self):
        pass

    def register_all(self):
        pass

    def update(self):
        distance, lane, junction = self.route.get_next_junction(traci.vehicle.getRoadID(self.id))
        if not junction or not junction.manager:
            traci.vehicle.setSpeed(self.id, 10)
            return

        if junction.id in self.junctions:
            v = self.junctions[junction.id].v
            if traci.vehicle.getAcceleration(self.id) > 0:
                print v, traci.vehicle.getSpeed(self.id), traci.simulation.getTime(), traci.vehicle.getAcceleration(self.id)
            return

        time, v = self.calc_fastest_time_v(distance)
        print time
        manager = junction.manager
        begin_time = int(math.ceil(time / self.stepLength))
        end_time = int(math.ceil((time + lane.length / v) / self.stepLength))
        self.junctions[junction.id] = Registration(t=begin_time, v=v)

        manager.register(lane, self.id, begin_time, end_time)
        traci.vehicle.setSpeed(self.id, v)

    def calc_speed(self, time, distance):
        dist_left = distance - traci.vehicle.getDistance(self.id)
        timeLeft = time - traci.simulation.getTime()
        if dist_left <= 0 or timeLeft <= 0:
            return 0
        return dist_left/timeLeft

    #calc time at intersection, v(t)
    def calc_fastest_time_v(self, distance):
        dist_left = distance - traci.vehicle.getDistance(self.id)
        if dist_left <= 0:
            return 0
        curr_time = traci.simulation.getTime()
        a = traci.vehicle.getAccel(self.id)
        v_max = traci.vehicle.getMaxSpeed(self.id)
        v = traci.vehicle.getSpeed(self.id)
        delta_v = v_max - v

        print (delta_v**2)/(2*a*dist_left)
        timeLeft = dist_left / v_max + (delta_v**2)/(2*a*dist_left)
        return curr_time + timeLeft, v_max
