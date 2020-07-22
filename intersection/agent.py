import math, pdb
import logging
from collections import namedtuple
from motion import Motion

Registration = namedtuple('Registration', ['t', 'd', 'v'])

class State:
    def __init__(self):
        self.speed = 0
        self.road_id = 0
        self.valid = False

    def save(self, vehicle):
        self.speed = vehicle.speed
        self.road_id = vehicle.road_id
        self.valid = True

class Agent:
    step_length = 0.1
    default_speed = 10
    max_accel = 2.6
    max_decel = 4.5
    def __init__(self, vehicle, world):
        self.vehicle = vehicle
        self.route = world.routes[self.vehicle.route_id]
        self.junctions = {} #[id].time/distance/v
        self.prev_state = State()
        self.vehicle.speed_mode = 1
        self.vehicle.max_accel = self.max_accel
        self.vehicle.max_decel = self.max_decel

    def motion(self, v_final):
        return Motion(self.vehicle.speed, v_final, self.max_accel, self.max_decel)

    def register_for_dist(self, distance, lane, junction, simulation):
        v = 10
        time = self.calc_time_at_distance(distance, v) #fixme
        if time == 0:
            return
        time += simulation.time
        manager = junction.manager
        begin_time = int(math.ceil(time / self.step_length))
        end_time = int(math.ceil((time + lane.length / v) / self.step_length))
        self.junctions[junction.id] = Registration(t = begin_time, d = distance, v = v)

        logging.info('Time registered at: %f for %s' % (time, self.vehicle.id_))

        manager.register(lane, self.vehicle.id_, begin_time, end_time)
        self.vehicle.speed = v

    def update(self, simulation):
        if self.prev_state.valid and self.prev_state.road_id != self.vehicle.road_id:
            logging.info('Time: %f [%s] changed road %s -> %s' % (simulation.time,
                                                  self.vehicle.id_, 
                                                  self.prev_state.road_id, 
                                                  self.vehicle.road_id))
            logging.info('    %f %f %f' % (self.vehicle.speed, self.vehicle.max_decel, self.vehicle.max_accel))
        distance, lane, junction = self.route.get_next_junction(self.vehicle.road_id)
        if not junction or not junction.manager:
            self.vehicle.speed = self.default_speed
        elif junction.id in self.junctions:
            if not (simulation.time % 1): 
                print (self.vehicle.id_, self.junctions[junction.id])
            time = simulation.time - self.junctions[junction.id].t * self.step_length
            v_final = self.junctions[junction.id].v
            d = self.junctions[junction.id].d
            self.vehicle.speed = self.calc_velocity_for_time(time, d, v_final)
        else:
            self.register_for_dist(distance, lane, junction, simulation)
        self.prev_state.save(self.vehicle)

    def calc_time_at_distance(self, distance, v_final):
        dist_left = distance - self.vehicle.distance
        if dist_left <= 0:
            logging.warning('cannot calc time for distance left: %f' % dist_left)
            return 0
        motion = self.motion(v_final)
        motion_points = motion.calc_motion_points(dist_left, self.vehicle.max_speed)
        if not motion_points:
            time = motion.calc_fastest_time(dist_left)
            return time
        return motion_points[-1].t

    def calc_velocity_for_time(self, time, distance, v_final):
        if time <= 0:
            logging.warning('cannot calc velocity for time: %f' % time)
            return self.default_speed
        dist_left = distance - self.vehicle.distance
        v = self.motion(v_final).calc_velocity(time, dist_left)
        if not v:
            return self.default_speed
        return v
        

