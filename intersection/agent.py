import math
from collections import namedtuple
from sumowrapper import simulation

Registration = namedtuple('Registration', ['t', 'v'])

class Agent:
    step_length = 0.1
    def __init__(self, vehicle, world):
        self.vehicle = vehicle
        self.route = world.routes[self.vehicle.route_id]
        self.junctions = {} #[id].time/velocity
        self.vehicle.speed_mode = 1

    def register_next(self):
        pass

    def register_all(self):
        pass

    def update(self):
        distance, lane, junction = self.route.get_next_junction(self.vehicle.road_id)
        if not junction or not junction.manager:
            self.vehicle.speed = 10
            return

        if junction.id in self.junctions:
            v = self.junctions[junction.id].v
            if self.vehicle.acceleration > 0:
                print v, self.vehicle.speed, simulation.time, self.vehicle.acceleration
            return

        time, v = self.calc_fastest_time_v(distance)
        print time
        manager = junction.manager
        begin_time = int(math.ceil(time / self.step_length))
        end_time = int(math.ceil((time + lane.length / v) / self.step_length))
        self.junctions[junction.id] = Registration(t=begin_time, v=v)

        manager.register(lane, self.vehicle.id_, begin_time, end_time)
        self.vehicle.speed = v

    def calc_speed(self, time, distance):
        dist_left = distance - self.vehicle.distance
        timeLeft = time - simulation.time
        if dist_left <= 0 or timeLeft <= 0:
            return 0
        return dist_left/timeLeft

    #calc time at intersection, v(t)
    def calc_fastest_time_v(self, distance):
        dist_left = distance - self.vehicle.distance
        if dist_left <= 0:
            return 0
        curr_time = simulation.time
        a = self.vehicle.accel
        v_max = self.vehicle.max_speed
        v = self.vehicle.speed
        delta_v = v_max - v

        print (delta_v**2)/(2*a*dist_left)
        timeLeft = dist_left / v_max + (delta_v**2)/(2*a*dist_left)
        return curr_time + timeLeft, v_max
