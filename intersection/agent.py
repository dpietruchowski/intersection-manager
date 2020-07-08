import traci
import math

class Agent:
    stepLength = 0.1
    def __init__(self, id, world):
        self.id = id
        self.route = world.routes[traci.vehicle.getRouteID(self.id)]
        self.junctions = {} #[id].time/velocity
        traci.vehicle.setSpeedMode(self.id, 1)

    def registerNext(self):
        pass

    def registerAll(self):
        pass

    def update(self):
        distance, lane, junction = self.route.getNextJunction(traci.vehicle.getRoadID(self.id))
        if not junction or not junction.manager:
            traci.vehicle.setSpeed(self.id, 10)
            return
        if junction.id in self.junctions:
            return

        time, v = self.calcFastestTimeAndV(distance)
        print time
        manager = junction.manager
        beginTime = int(math.ceil(time / self.stepLength))
        endTime = int(math.ceil((time + lane.length / v) / self.stepLength))
        self.junctions[junction.id] = beginTime
        manager.register(lane, self.id, beginTime, endTime)
        traci.vehicle.setSpeed(self.id, v)

    def calcSpeed(self, time, distance):
        distLeft = distance - traci.vehicle.getDistance(self.id)
        timeLeft = time - traci.simulation.getTime()
        if distLeft <= 0 or timeLeft <= 0:
            return 0
        return distLeft/timeLeft

    def calcFastestTimeAndV(self, distance):
        distLeft = distance - traci.vehicle.getDistance(self.id)
        if distLeft <= 0:
            return 0
        currTime = traci.simulation.getTime()
        a = traci.vehicle.getAccel(self.id)
        vMax = traci.vehicle.getMaxSpeed(self.id)
        v = traci.vehicle.getSpeed(self.id)
        deltaV = vMax - v

        print (deltaV**2)/(2*a*distLeft)
        timeLeft = distLeft / vMax + (deltaV**2)/(2*a*distLeft)
        return currTime + timeLeft, vMax
