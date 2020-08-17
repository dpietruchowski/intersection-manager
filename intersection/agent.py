import math, pdb
import logging
from collections import namedtuple
from motion import Motion, MotionPoint

def prev_next_iter(iterable):
    prev = None
    for curr in iterable:
        if prev:
            yield prev, curr
        prev = curr

Registration = namedtuple('Registration', ['registration_point', 'motion_points', 'arrival_point'])
NextRegPoint = namedtuple('NextJunction', ['junction', 'lane', 'distance'])

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
    default_motion_points = []
    def __init__(self, vehicle, world):
        self.vehicle = vehicle
        self.route = world.routes[self.vehicle.route_id]
        self.junctions = {} #[id].time/distance/v
        self.prev_state = State()
        self.vehicle.speed_mode = 6
        self.vehicle.max_accel = self.max_accel
        self.vehicle.max_decel = self.max_decel
        self.motion_points = self.default_motion_points
        distance, lane, junction = self.route.get_next_junction(self.vehicle.road_id)
        self.next_reg_point = NextRegPoint(junction=junction, lane=lane, distance=distance)
        self.curr_motion_points = self.motion_points

    def motion(self, v_final):
        return Motion(self.vehicle.speed, v_final, self.max_accel, self.max_decel)

    def follow_motion_points(self, simulation, registration_point, motion_points):
        curr_point = None
        next_point = None
        for curr_motion_point, next_motion_point in prev_next_iter(motion_points):
            if curr_motion_point.t + registration_point.t >= simulation.time - self.step_length:
                curr_point = curr_motion_point
                next_point = next_motion_point
                break

        if not curr_point or not next_point:
            return

        if abs(curr_motion_point.t + registration_point.t - simulation.time) <= self.step_length:
            self.vehicle.speed = next_point.v

        return curr_point


    def register(self, distance, lane, junction, simulation):
        dist_left = distance - self.vehicle.distance - self.vehicle.length
        v_junction = 10
        time = self.calc_time(dist_left, v_junction)
        if time <= 0:
            logging.warning('Registering not possible')
            return

        arrival_time = time + simulation.time

        begin_time = int(math.ceil(arrival_time / Agent.step_length))
        end_time = int(math.ceil((arrival_time + lane.length / v_junction) / Agent.step_length))
        manager = junction.manager
        begin_time, end_time = manager.register(lane, self.vehicle.id_, begin_time, end_time)

        arrival_time = begin_time * Agent.step_length
        registration_point = MotionPoint(t = simulation.time, v = self.vehicle.speed, d = self.vehicle.distance)
        arrival_point = MotionPoint(t = arrival_time, v = v_junction, d = distance - self.vehicle.length)
        motion_points = self.calc_motion_points_for_arrival(arrival_point, simulation)
        self.junctions[junction.id] = Registration(registration_point, motion_points, arrival_point)
        logging.debug(repr(self.junctions[junction.id]))
        logging.info('[%s] Registered for {%s} at %f (%d) -> %f (%d).' % (self.vehicle.id_, 
                junction.id, 
                arrival_time, begin_time, 
                end_time * Agent.step_length, end_time))

    def unregister(self, junction):
        pass

    

    def update(self, simulation):
        if self.prev_state.valid and self.prev_state.road_id != self.vehicle.road_id:
            logging.info('[%s] Changed road from {%s} to {%s} at %f (%d). Distance: %f' % (self.vehicle.id_, 
                                                  self.prev_state.road_id, 
                                                  self.vehicle.road_id,
                                                  simulation.time, simulation.step_count, 
                                                  self.vehicle.distance))
            distance, lane, junction = self.next_reg_point.distance, self.next_reg_point.lane, self.next_reg_point.junction
            if junction and junction.id in self.junctions:
                arrival_point = self.junctions[junction.id].arrival_point
                time_diff = arrival_point.t - simulation.time
                if abs(time_diff) > 0.01:
                    logging.warning('[%s] Car is in wrong time on the intersection Diff: %f' % (self.vehicle.id_, time_diff))
            distance, lane, junction = self.route.get_next_junction(self.vehicle.road_id)
            self.next_reg_point = NextRegPoint(junction=junction, lane=lane, distance=distance)
        distance, lane, junction = self.next_reg_point.distance, self.next_reg_point.lane, self.next_reg_point.junction
        if not junction or not junction.manager:
            self.follow_motion_points(simulation, MotionPoint(t=0, v=0, d=0), self.motion_points)
        elif junction.id in self.junctions:
            registration_point = self.junctions[junction.id].registration_point
            arrival_point = self.junctions[junction.id].arrival_point
            time_left = arrival_point.t - simulation.time
            dist_left = arrival_point.d - self.vehicle.distance
            velocity = self.calc_velocity(dist_left, time_left, arrival_point.v)
            time = self.calc_time(dist_left, arrival_point.v)
            if time > time_left:
                logging.warning('[%s] Car wont be at time on the intersection. Reregister. (%f)' % (self.vehicle.id_, time_left - time))
                self.register(distance, lane, junction, simulation)
            else:
                self.vehicle.speed = velocity
        else:
            self.register(distance, lane, junction, simulation)
        self.prev_state.save(self.vehicle)

    def calc_motion_points_for_arrival(self, arrival_point, simulation):
        dist_left = arrival_point.d - self.vehicle.distance
        time_left = arrival_point.t - simulation.time
        return self.calc_motion_points(dist_left, time_left, arrival_point.v)

    def calc_velocity(self, distance, time, v_final):
        motion = self.motion(v_final)
        return motion.calc_velocity(distance, time)

    def calc_motion_points(self, distance, time, v_final):
        motion = self.motion(v_final)
        velocity = motion.calc_velocity(distance, time)
        if not velocity:
            return
        motion_points = motion.calc_motion_points(velocity, time)
        return motion_points

    def calc_fastest_time(self, distance, v_final):
        motion = self.motion(v_final)
        return motion.calc_time(self.vehicle.max_speed, distance)

    def calc_time(self, distance, v_final):
        motion = self.motion(v_final)
        return motion.calc_time(self.vehicle.max_speed, distance)

        

