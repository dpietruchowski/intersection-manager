import math
import logging
from collections import namedtuple

MotionPoint = namedtuple('MotionPoint', ['t', 'v', 'd'])

def calc_accel_motion_distance(v_init, v_final, accel):
    return float(v_final + v_init)*(v_final - v_init) / (2 * accel)

def calc_accel_motion_time(v_init, v_final, accel):
    return float(v_final - v_init) / accel

def calc_accel_motion_distance_time(v_init, v_final, accel):
    return calc_accel_motion_distance(v_init, v_final, accel), \
        calc_accel_motion_time(v_init, v_final, accel)


def calc_accel_motion_max_distance(time, v_init, v_final, accel, decel):
    a = (-1.0/2) * (1.0 / accel + 1.0 / decel)
    b = time + float(v_init) / accel + float(v_final) / decel
    c = (-1.0/2)*(float(v_init**2) / accel + float(v_final**2) / decel)
    return (4 * a * c - b**2) / (4 * a)

def calc_accel_motion_fastest_time(distance, v_init, v_final, accel, decel):
    a = (-1.0/2) * (1.0 / accel + 1.0 / decel)
    b = float(v_init) / accel + float(v_final) / decel
    c = (-1.0/2) * (float(v_init**2) / accel + float(v_final**2) / decel + 2 * distance)

    sqrtBPrim = math.sqrt(4 * a * c)
    t1 = sqrtBPrim - b
    t2 = -sqrtBPrim - b
    
    # check first solution
    if t1 > 0:
        return t1

    # check second solution
    if t2 > 0:
        return t2


def calc_motion_points_for_distance(v_init, v_max, v_final, accel, decel, distance):
    v_final = min(v_final, v_max)
    accel_dist, accel_time = calc_accel_motion_distance_time(v_init, v_max, accel)
    decel_dist, decel_time = calc_accel_motion_distance_time(v_final, v_max, decel)
    points = [MotionPoint(t = 0, v = v_init, d = 0)]
    if accel_dist + decel_dist > distance:
        return
    else:
        t_max = float(distance - (accel_dist + decel_dist)) / v_max
        d = accel_dist
        points.append(MotionPoint(t = accel_time, v = v_max, d = d))
        d += v_max * t_max
        points.append(MotionPoint(t = accel_time + t_max, v = v_max, d = d))
        d += decel_dist
        points.append(MotionPoint(t = accel_time + t_max + decel_time, v = v_final, d = d))

    return points

def calc_accel_motion_velocity(time, distance, v_init, v_final, accel, decel):
    a = (-1.0/2) * (1.0 / accel + 1.0 / decel)
    b = time + float(v_init) / accel + float(v_final) / decel
    c = (-1.0/2) * (float(v_init**2) / accel + float(v_final**2) / decel + 2 * distance)

    delta = b**2 - 4 * a * c

    if delta < 0:
        logging.warning("Delta is lower than 0: %f" % delta)
        return
    elif delta == 0:
        return float(-b) / (2 * a)

    sqrtDelta = math.sqrt(delta)
    v1 = float(-b - sqrtDelta) / (2*a)
    v2 = float(-b + sqrtDelta) / (2*a)

    # check first solution
    t_accel = calc_accel_motion_time(v_init, v1, accel)
    t_decel = calc_accel_motion_time(v_final, v1, decel)
    if t_accel + t_decel < time:
        return v1

    # check second solution
    t_accel = calc_accel_motion_time(v_init, v2, accel)
    t_decel = calc_accel_motion_time(v_final, v2, decel)
    if t_accel + t_decel < time:
        return v2



class Motion:
    def __init__(self, v_init, v_final, accel, decel):
        self.v_init = v_init
        self.v_final = v_final
        self.accel = accel
        self.decel = decel

    def calc_accel_distance_time(self, v_max):
        return calc_accel_motion_distance_time(self.v_init, v_max, self.accel)

    def calc_decel_distance_time(self, v_max):
        return calc_accel_motion_distance_time(self.v_final, v_max, self.decel)

    def calc_motion_points(self, distance, v_max):
        return calc_motion_points_for_distance(self.v_init , v_max, self.v_final, 
                self.accel, self.decel, distance)

    def calc_velocity(self, time, distance):
        return calc_accel_motion_velocity(time, distance, self.v_init, self.v_final, 
                self.accel, self.decel)

    def calc_max_distance(self, time):
        return calc_accel_motion_max_distance(time, self.v_init, self.v_final, self.accel, self.decel)

    def calc_min_velocity_for_distance(self, time):
        distance = self.calc_max_distance(time)
        return self.calc_velocity(time, distance)

    def calc_fastest_time(self, distance):
        return calc_accel_motion_fastest_time(distance, self.v_init, self.v_final, self.accel, self.decel)