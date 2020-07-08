import os, sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    print(os.environ['SUMO_HOME'])
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

def get_options():
    import optparse
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-c', '--cfg', help='config file')
    return opt_parser.parse_args()

import traci
sumo_binary = 'sumo-gui'

from intersection.agent import Agent

def simulation(configFilename, world):
    agents = {}
    step = 0
    traci.start([sumo_binary, '-c', configFilename])
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1
        Agent.stepLength = traci.simulation.getTime()/step 
        carIDs = traci.vehicle.getIDList()
        for carID in carIDs:
            if not carID in agents:
                agent = Agent(carID, world)
                agents[carID] = agent
        for carID in agents.keys():
            if not carID in carIDs:
                del agents[carID]
        
        for carID, agent in agents.items():
            agent.update()
    traci.close()

from threading import Thread
from PyQt5.QtWidgets import QApplication
from gui.app import MainWindow

if __name__ == "__main__":
    (options, args) = get_options()
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.loadWorld(options.cfg)
    mainWindow.show()
    sim = Thread(target=simulation, args=(options.cfg, mainWindow.world,))
    sim.start()
    sys.exit(app.exec_())


