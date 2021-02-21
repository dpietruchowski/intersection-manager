import math, pdb
import logging
from collections import namedtuple

MotionPoint = namedtuple('MotionPoint', ['t', 'v', 'd'])

def accel_distance(v_init, v_final, accel, decel):
    a = accel if v_init < v_final else decel
    if a == 0:
        return 0
    return float(v_final + v_init)*abs(v_final - v_init) / (2 * a)

def accel_time(v_init, v_final, accel, decel):
    a = accel if v_init < v_final else decel
    if a == 0:
        return 0
    return float(abs(v_final - v_init)) / a

def accel_time_for_distance(v_init, distance, accel, decel, f):
    if f == 0:
        return distance / v_init
    a = accel if f == 1 else decel
    if a == 0:
        return distance / v_init
    b = 2 * v_init
    c = -2 * distance
    delta = b**2 - 4 * a * c
    if delta < 0:
        logging.debug("Delta is lower than 0: %f" % delta)

    if delta <= 0:
        v = float(-b) / (2 * a)
        return 0 if v < 0 else v

    sqrtDelta = math.sqrt(delta)
    t1 = float(-b - sqrtDelta) / (2*a)
    t2 = float(-b + sqrtDelta) / (2*a)
    # check first solution
    if t1 > 0:
        return t1
    # check second solution
    if t2 > 0:
        return t2
    return 0



def motion_factor(velocity, v_final):
    f = 0 if abs(v_final - velocity) < 0.01 else -1 if v_final < velocity else 1
    return f

def motion_params(velocity, v_init, v_final, accel, decel):
    f1 = motion_factor(velocity, v_init)
    f2 = motion_factor(velocity, v_final)
    a2 = 0 if f1 == 0 else decel if f1 == 1 else accel
    a3 = 0 if f2 == 0 else accel if f2 == 1 else decel
    t2 = 0 if a2 == 0 else abs(f1) * abs(v_init - velocity) / a2
    t3 = 0 if a3 == 0 else abs(f2) * abs(v_final - velocity) / a3
    return f1, f2, a2, a3, t2, t3

def motion_distance(velocity, time, v_init, v_final, accel, decel):
    f1, f2, a2, a3, t2, t3 = motion_params(velocity, v_init, v_final, accel, decel)
    if t2 + t3 > time:
        return 0
    return velocity * time + f1 * ((a2 * t2**2) / 2) + f2 * ((a3 * t3**2) / 2)

def motion_time(velocity, distance, v_init, v_final, accel, decel):
    f1, f2, a2, a3, t2, t3 = motion_params(velocity, v_init, v_final, accel, decel)
    d2 = accel_distance(v_init, velocity, accel, decel)
    d3 = accel_distance(velocity, v_final, accel, decel)
    if d2 < 0 or d3 < 0:
        logging.debug('d2 = %f, d3 = %f' % (d2, d3))
        return 0
    dist_left = distance - d2 - d3
    if dist_left < 0:
        v_sqrt = (2*distance*a2*a3 + v_init**2 * a3 + v_final**2 * a2) / (a2 + a3)
        v = math.sqrt(v_sqrt)
        f1, f2, a2, a3, t2, t3 = motion_params(v, v_init, v_final, accel, decel)
        return t2 + t3
    if velocity == 0.0:
        return 0
    t = dist_left / velocity
    return t + t2 + t3
    

def motion_points(velocity, time, v_init, v_final, accel, decel):
    f1, f2, a2, a3, t2, t3 = motion_params(velocity, v_init, v_final, accel, decel)
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
        return -float(c) / b

    delta = b**2 - 4 * a * c

    if delta < 0:
        logging.debug("Delta is lower than 0: %f" % delta)

    if delta <= 0:
        v = float(-b) / (2 * a)
        return 0 if v < 0 else v

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

    def calc_accel_distance_time(self):
        return accel_distance(self.v_init, self.v_final, self.accel, self. decel), accel_time(self.v_init, self.v_final, self.accel, self. decel)

    def calc_max_final_velocity(self, distance):
        v_sqrt = self.v_init**2 + 2 * distance * self.accel
        velocity = math.sqrt(v_sqrt)
        return velocity

    def calc_motion_points(self, velocity, time):
        return motion_points(velocity, time,
            self.v_init, self.v_final, self.accel, self.decel)

    def calc_velocity(self, distance, time):
        d1 = self.calc_distance(self.v_init, time)
        d2 = self.calc_distance(self.v_final, time)
        d_diff = abs(self.v_final - self.v_init) * 0.005
        d1, d2 = min(d1, d2), max(d1, d2)
        f1, f2 = 0, 0
        if abs(d1 - d2) < d_diff:
            return self.v_final
        elif 0 < distance < d1:
            f1, f2 = 1, 1
        elif d1 <= distance <= d2:
            f1 = -1 if self.v_init < self.v_final else 1
            f2 = 1 if self.v_init < self.v_final else -1
        elif d2 < distance:
            f1, f2 = -1, -1

        if f1 == 0 and f2 == 0:
            return self.v_final
        return motion_velocity(time, distance, self.v_init, self.v_final, self.accel, self.decel, f1, f2)
    
    def calc_distance(self, velocity, time):
        return motion_distance(velocity, time, self.v_init, self.v_final, self.accel, self.decel)

    def calc_time(self, velocity, distance):
        return motion_time(velocity, distance, self.v_init, self.v_final, self.accel, self.decel)

    def calc_params(self, velocity):
        return motion_params(velocity, self.v_init, self.v_final, self.accel, self.decel)