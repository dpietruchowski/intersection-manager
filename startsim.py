import os, sys
from collections import namedtuple

def get_options():
    import optparse
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-c', '--cfg', help='config file')
    return opt_parser.parse_args()

from sumowrapper import Simulation, Vehicle
from intersection.agent import Agent

Stats = namedtuple('Stats', ['time', 'distance', 'velocity', 'accel'])

def simulation_loop(configFilename, world):
    stats = {}
    agents = {}
    simulation = Simulation()
    simulation.start(configFilename)
    while simulation.min_expected_number > 0:
        simulation.step()
        Agent.stepLength = simulation.time / simulation.step_count
        
        car_id_list = simulation.vehicles.id_list
        agent_id_list = agents.keys()

        to_add_id_list = list(set(car_id_list) - set(agent_id_list))
        for car_id in to_add_id_list:
            agents[car_id] = Agent(Vehicle(car_id), world)

        to_delete_id_list = list(set(agent_id_list) - set(car_id_list))
        for car_id in to_delete_id_list:
            del agents[car_id]
        
        for car_id, agent in agents.items():
            agent.update(simulation)
            stats.setdefault(car_id, []).append(Stats(
                    time = simulation.time,
                    distance = agent.vehicle.distance, 
                    velocity = agent.vehicle.speed,
                    accel = agent.vehicle.accel))
    simulation.close()
    return stats

from threading import Thread
from PyQt5.QtWidgets import QApplication
from gui.app import MainWindow

if __name__ == "__main__":
    (options, args) = get_options()
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.loadWorld(options.cfg)
    mainWindow.show()
    sim = Thread(target=simulation_loop, args=(options.cfg, mainWindow.world,))
    sim.start()
    #sys.exit(app.exec_())


