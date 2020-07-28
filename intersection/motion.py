import math
import logging
from collections import namedtuple

MotionPoint = namedtuple('MotionPoint', ['t', 'v', 'd'])

def accel_distance(v_init, v_final, accel):
    return abs(float(v_final + v_init)*(v_final - v_init) / (2 * accel))

def accel_time(v_init, v_final, accel):
    return abs(float(v_final - v_init) / accel)

def motion_factor(velocity, v_final):
    f = -1 if v_final < velocity else 0 if v_final == velocity else 1
    return f

def motion_params(velocity, time, v_init, v_final, accel, decel):
    f1 = motion_factor(velocity, v_init)
    f2 = motion_factor(velocity, v_final)
    a2 = decel if f1 == 1 else accel
    a3 = accel if f2 == 1 else decel
    t2 = abs(f1) * abs(v_init - velocity) / a2
    t3 = abs(f2) * abs(v_final - velocity) / a3
    return f1, f2, a2, a3, t2, t3

def motion_distance(velocity, time, v_init, v_final, accel, decel):
    f1, f2, a2, a3, t2, t3 = motion_params(velocity, time, v_init, v_final, accel, decel)
    if t2 + t3 > time:
        return 0
    return velocity * time + f1 * ((a2 * t2**2) / 2) + f2 * ((a3 * t3**2) / 2)

def motion_points(velocity, time, v_init, v_final, accel, decel):
    f1, f2, a2, a3, t2, t3 = motion_params(velocity, time, v_init, v_final, accel, decel)
    if t2 + t3 > time:
        return []
    
    motion_points = []
    motion_points.append(MotionPoint(t = 0, v = v_init, d = 0))
    d = t2 * velocity + f1 * float(a2 * t2**2) / 2 
    motion_points.append(MotionPoint(t = t2, v = velocity, d = d))
    d += velocity * (time - (t2 + t3))
    motion_points.append(MotionPoint(t = time - t3, v = velocity, d = d))
    d += t3 * velocity + f2 * float(a3 * t3**2) / 2
    motion_points.append(MotionPoint(t = time, v = v_final, d = d))
    return motion_points

def max_motion_distance(time, v_init, v_final, accel, decel, f1, f2):
    accel_1 = decel if f1 == 1 else accel
    accel_2 = accel if f2 == 1 else decel
    a = (1.0/2) * (float(f1) / accel_1 + float(f2) / accel_2)
    b = time - (float(f1 * v_init) / accel_1 + float(f2 * v_final) / accel_2)
    c = (1.0/2) * (float(f1* v_init**2) / accel_1 + float(f2 * v_final**2) / accel_2)
    delta = b**2 - 4 * a * c
    distance  = -delta / (4 * a)
    velocity = -b / (2 * a)
    if velocity < 0 or distance < 0:
        return 0, 0
    return velocity, distance

def motion_velocity(time, distance, v_init, v_final, accel, decel, f1, f2):
    accel_1 = decel if f1 == 1 else accel
    accel_2 = accel if f2 == 1 else decel
    a = (1.0/2) * (float(f1) / accel_1 + float(f2) / accel_2)
    b = time - (float(f1 * v_init) / accel_1 + float(f2 * v_final) / accel_2)
    c = (1.0/2) * (float(f1* v_init**2) / accel_1 + float(f2 * v_final**2) / accel_2) - distance

    if a == 0:
        return -float(b) / c

    delta = b**2 - 4 * a * c

    if delta < 0:
        logging.warning("Delta is lower than 0: %f" % delta)
        return
    elif delta == 0:
        return float(-b) / (2 * a)

    sqrtDelta = math.sqrt(delta)
    v1 = float(-b - sqrtDelta) / (2*a)
    v2 = float(-b + sqrtDelta) / (2*a)

    d1 = motion_distance(v1, time, v_init, v_final, accel, decel)
    if abs(d1 - distance) < 0.01 and v1 > 0:
        return v1

    d2 = motion_distance(v2, time, v_init, v_final, accel, decel)
    if abs(d2 - distance) < 0.01 and v2 > 0:
        return v2

    return 0

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

class Motion:
    def __init__(self, v_init, v_final, accel, decel):
        self.v_init = v_init
        self.v_final = v_final
        self.accel = accel
        self.decel = decel

    def calc_accel_distance_time(self, velocity):
        return accel_distance(self.v_init, velocity, self.accel), accel_time(self.v_init, velocity, self.accel)

    def calc_decel_distance_time(self, velocity):
        return accel_distance(self.v_final, velocity, self.decel), accel_time(self.v_final, velocity, self.decel)

    def calc_motion_points(self, velocity, time):
        return motion_points(velocity, time,
            self.v_init, self.v_final, self.accel, self.decel)

    def calc_velocity(self, time, distance):
        d1 = motion_distance(self.v_init, time, self.v_init, self.v_final, self.accel, self.decel)
        d2 = motion_distance(self.v_final, time, self.v_init, self.v_final, self.accel, self.decel)
        if 0 < distance < d1:
            return motion_velocity(time, distance, self.v_init, self.v_final, self.accel, self.decel, 1, 1)
        elif d1 <= distance <= d2:
            f1 = -1 if self.v_init < self.v_final else 1
            f2 = 1 if self.v_init < self.v_final else -1
            return motion_velocity(time, distance, self.v_init, self.v_final, self.accel, self.decel, f1, f2)
        elif d2 < distance:
            return motion_velocity(time, distance, self.v_init, self.v_final, self.accel, self.decel, -1, -1)
        return 0

    def calc_max_distance(self, time, v_max):
        v1, d1 = max_motion_distance(time, self.v_init, self.v_final, self.accel, self.decel, -1, -1)

        d_accel, t_accel = self.calc_accel_distance_time(v1)
        d_decel, t_decel = self.calc_decel_distance_time(v1)
        if t_accel + t_decel < time:
            return min(v_max, v1)

        v = max(self.v_final, self.v_init)
        d_max = motion_distance(v, time, self.v_init, self.v_final, self.accel, self.decel)
        if d_max > 0:
            return d_max

        v = min(self.v_final, self.v_init)
        d_max = motion_distance(v, time, self.v_init, self.v_final, self.accel, self.decel)
        
        return d_max