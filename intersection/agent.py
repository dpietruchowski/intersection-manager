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

Registration = namedtuple('Registration', ['registration_point', 'arrival_point'])
JunctionPoint = namedtuple('JunctionPoint', ['junction', 'lane', 'distance'])

class State:
    def __init__(self):
        self.speed = 0
        self.road_id = 0
        self.valid = False

    def save(self, vehicle):
        self.length = vehicle.length
        self.distance = vehicle.distance
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
        self.vehicle.speed_mode = 6
        self.vehicle.max_accel = self.max_accel
        self.vehicle.max_decel = self.max_decel
        distance, lane, junction = self.route.get_next_junction(self.vehicle.road_id)
        self.next_reg_point = JunctionPoint(junction=junction, lane=lane, distance=distance)
        self.curr_junction_point = None


    def motion(self, v_final):
        return Motion(self.vehicle.speed, v_final, self.max_accel, self.max_decel)

    def register(self, simulation):
        distance, lane, junction = self.next_reg_point.distance, self.next_reg_point.lane, self.next_reg_point.junction
        dist_left = self.calc_distance_left(distance)
        v_junction = junction.v_max
        v_final = self.motion(v_junction).calc_max_final_velocity(dist_left)
        v_final = min(v_junction, v_final)
        time = self.calc_fastest_time(dist_left, v_final)
        if time <= 0:
            logging.warning('Registering not possible')
            return

        arrival_time = time + simulation.time

        begin_time = int(round(arrival_time / Agent.step_length))
        end_time = int(round((arrival_time + (lane.length + self.vehicle.length) / v_final) / Agent.step_length))
        manager = junction.manager
        begin_time, end_time = manager.register(lane, self.vehicle.id_, begin_time, end_time)

        arrival_time = begin_time * Agent.step_length
        registration_point = MotionPoint(t = simulation.time, v = self.vehicle.speed, d = self.vehicle.distance)
        arrival_point = MotionPoint(t = arrival_time, v = v_final, d = distance - self.vehicle.length)
        self.junctions[junction.id] = Registration(registration_point, arrival_point)
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
                if abs(time_diff) > 0.05:
                    logging.warning('[%s] Car is in wrong time on the intersection Diff: %f' % (self.vehicle.id_, time_diff))
                v_diff = arrival_point.v - self.vehicle.speed
                if abs(v_diff) > 0.5:
                    logging.warning('[%s] Car has wrong v on the intersection Diff: %f' % (self.vehicle.id_, v_diff))
            
            if junction and not self.curr_junction_point:
                junction_point = JunctionPoint(junction=junction, lane=lane, distance=distance)
                if self.is_on_junction(junction_point):
                    self.curr_junction_point = junction_point
            distance, lane, junction = self.route.get_next_junction(self.vehicle.road_id)
            self.next_reg_point = JunctionPoint(junction=junction, lane=lane, distance=distance)
        distance, lane, junction = self.next_reg_point.distance, self.next_reg_point.lane, self.next_reg_point.junction
        
        if self.curr_junction_point:
            self.vehicle.speed = self.curr_junction_point.junction.v_max
            if not self.is_on_junction(self.curr_junction_point):
                self.curr_junction_point = None
        elif not junction or not junction.manager:
            self.vehicle.speed = self.vehicle.max_speed
        elif junction.id in self.junctions:
            success = self.update_velocity(simulation)
            if not success:
                success = self.update_velocity(simulation)
                self.register(simulation)
                self.update_velocity(simulation)
        else:
            self.register(simulation)
            self.update_velocity(simulation)

        if junction and junction.manager:
            junction.manager.set_time(simulation.step_count - 1)
        self.prev_state.save(self.vehicle)

    def update_velocity(self, simulation):
        distance, junction = self.next_reg_point.distance, self.next_reg_point.junction
        if not junction.id in self.junctions:
            return
        if self.vehicle.id_ == 'vehicle_3.0':
            aa = "aa"
        arrival_point = self.junctions[junction.id].arrival_point
        time_left = arrival_point.t - simulation.time
        dist_left = self.calc_distance_left(distance)
        velocity = self.calc_velocity(dist_left, time_left, arrival_point.v)
        time = self.calc_time(dist_left, velocity, arrival_point.v)
        #time = int(round(time / Agent.step_length)) * Agent.step_length
        if time > time_left + Agent.step_length:
            logging.warning('[%f][%s] Car wont be at time on the intersection. Reregister. (%f)' % (simulation.time,
                    self.vehicle.id_, time_left - time))
            return False
        else:
            pass
            self.vehicle.speed = velocity
            return True

    def calc_velocity(self, distance, time, v_final):
        motion = self.motion(v_final)
        return motion.calc_velocity(distance, time)

    def calc_fastest_time(self, distance, v_final):
        motion = self.motion(v_final)
        return motion.calc_time(self.vehicle.max_speed, distance)

    def calc_time(self, distance, velocity, v_final):
        motion = self.motion(v_final)
        return motion.calc_time(velocity, distance)

    def calc_distance_left(self, distance):
        return distance - self.vehicle.distance - self.vehicle.length

    def is_on_junction(self, junction_point):
        d_diff = junction_point.junction.v_max * Agent.step_length
        is_front_after = self.vehicle.front_distance > junction_point.distance - d_diff
        is_back_before = self.vehicle.back_distance < junction_point.distance + junction_point.lane.length + d_diff 
        return is_front_after and is_back_before


#    def calc_motion_points_for_arrival(self, arrival_point, simulation):
#        dist_left = self.calc_distance_left(arrival_point.d)
#        time_left = arrival_point.t - simulation.time
#        return self.calc_motion_points(dist_left, time_left, arrival_point.v)

#    def calc_motion_points(self, distance, time, v_final):
#        motion = self.motion(v_final)
#        velocity = motion.calc_velocity(distance, time)
#        if not velocity:
#            return
#        motion_points = motion.calc_motion_points(velocity, time)
#        return motion_points

#    def follow_motion_points(self, simulation, registration_point, motion_points):
#        curr_point = None
#        next_point = None
#        for curr_motion_point, next_motion_point in prev_next_iter(motion_points):
#            if curr_motion_point.t + registration_point.t >= simulation.time - self.step_length:
#                curr_point = curr_motion_point
#                next_point = next_motion_point
#                break
#
#        if not curr_point or not next_point:
#            return
#
#        if abs(curr_motion_point.t + registration_point.t - simulation.time) <= self.step_length:
#            self.vehicle.speed = next_point.v
#
#        return curr_point

        

