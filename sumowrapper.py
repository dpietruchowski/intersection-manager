import os, sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    print(os.environ['SUMO_HOME'])
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

class Vehicle:
    def __init__(self, id_):
        self.id_ = id_

    @property
    def acceleration(self):
        return traci.vehicle.getAcceleration(self.id_)

    @property
    def distance(self):
        return traci.vehicle.getDistance(self.id_)

    @property
    def accel(self):
        return traci.vehicle.getAccel(self.id_)

    @property
    def road_id(self):
        return traci.vehicle.getRoadID(self.id_)

    @property
    def route_id(self):
        return traci.vehicle.getRouteID(self.id_)

    @accel.setter
    def accel(self, value):
        return traci.vehicle.setAccel(self.id_, value)

    @property
    def speed(self):
        return traci.vehicle.getSpeed(self.id_)

    @speed.setter
    def speed(self, value):
        return traci.vehicle.setSpeed(self.id_, value)

    @property
    def max_speed(self):
        return traci.vehicle.getMaxSpeed(self.id_)

    @max_speed.setter
    def max_speed(self, value):
        return traci.vehicle.setMaxSpeed(self.id_, value)

    @property
    def speed_mode(self):
        return traci.vehicle.getSpeedMode(self.id_)

    @max_speed.setter
    def speed_mode(self, value):
        return traci.vehicle.setSpeedMode(self.id_, value)


class Vehicles:
    def __len__(self):
        return traci.vehicle.getIDCount()

    def __getitem__(self):
        if index >= len(self):
            raise IndexError
        return Vehicle(id_list[index])

    @property
    def id_list(self):
        return traci.vehicle.getIDList()


class Simulation:
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
    def time(self):
        return traci.simulation.getTime()

simulation = Simulation()