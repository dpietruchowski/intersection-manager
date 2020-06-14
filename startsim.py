import os, sys
import optparse
from CarAgent import CarAgent

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    print(os.environ['SUMO_HOME'])
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-c', '--cfg', help='config file')
    return opt_parser.parse_args()

sumo_binary = 'sumo-gui'
    
def main():
    (options, args) = get_options()
    print(options.cfg)
    traci.start([sumo_binary, '-c', options.cfg])
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1
        for carID in traci.vehicle.getIDList():
            if not carID in cars:
                cars[carID] = CarAgent(carID)
                cars[carID].setSpeed(3)
                traci.vehicle.setSpeedMode(carID, 0)
            print(traci.vehicle.getSpeed(carID))
        for routeID in traci.route.getIDList():
            print("edge: " + str(traci.route.getEdges(routeID)))
            
    traci.close()


if __name__ == "__main__":
    main()


