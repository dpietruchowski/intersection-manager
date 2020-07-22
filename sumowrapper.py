import os
import sys
import pdb

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    print(os.environ['SUMO_HOME'])
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

class Vehicle(object):
    def __init__(self, id_):
        self.id_ = id_

    @property
    def accel(self):
        return traci.vehicle.getAcceleration(self.id_)

    @property
    def distance(self): #m
        return traci.vehicle.getDistance(self.id_)

    @property
    def road_id(self):
        return traci.vehicle.getRoadID(self.id_)

    @property
    def route_id(self):
        return traci.vehicle.getRouteID(self.id_)

    @property
    def max_accel(self): #m/s^2
        return traci.vehicle.getAccel(self.id_)

    @max_accel.setter
    def max_accel(self, value): #m/s^2
        traci.vehicle.setAccel(self.id_, value)

    @property
    def max_decel(self): #m/s^2
        return traci.vehicle.getDecel(self.id_)

    @max_decel.setter
    def max_decel(self, value): #m/s^2
        traci.vehicle.setDecel(self.id_, value)

    @property
    def speed(self): #m/s
        return traci.vehicle.getSpeed(self.id_)

    @speed.setter
    def speed(self, value): #m/s
        traci.vehicle.setSpeed(self.id_, value)

    @property
    def max_speed(self): #m/s
        return traci.vehicle.getMaxSpeed(self.id_)

    @max_speed.setter
    def max_speed(self, value): #m/s
        traci.vehicle.setMaxSpeed(self.id_, value)

    @property
    def speed_mode(self):
        return traci.vehicle.getSpeedMode(self.id_)

    @max_speed.setter
    def speed_mode(self, value):
        traci.vehicle.setSpeedMode(self.id_, value)


class Vehicles(object):
    def __len__(self):
        return traci.vehicle.getIDCount()

    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError
        return Vehicle(id_list[index])

    @property
    def id_list(self):
        return traci.vehicle.getIDList()


class Simulation(object):
    sumo_binary = 'sumo-gui'
    def __init__(self):
        self.step_count = 0
        self.vehicles = Vehicles()

    def start(self, configFilename):
        traci.start([self.sumo_binary, '-c', configFilename])

    def step(self):
        traci.simulationStep()
        self.step_count += 1

    def close(self):
        traci.close()

    @property
    def min_expected_number(self):
        return traci.simulation.getMinExpectedNumber()

    @property
    def time(self): #s
        return traci.simulation.getTime()