import os, sys, logging, time
from collections import namedtuple
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

def get_options():
    import optparse
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-c', '--cfg', help='config file')
    return opt_parser.parse_args()

from sumowrapper import Simulation, Vehicle, State
from intersection.agent import Agent

Stats = namedtuple('Stats', ['time', 'distance', 'velocity', 'accel'])

def simulation_loop(configFilename, world, main_frame):
    simulation = Simulation()
    simulation.start(configFilename)
    simulation.state
    first_time = True
    while simulation.min_expected_number > 0 and simulation.state != State.STOPPED:
        while simulation.state == State.PAUSED:
            time.sleep(0.5)
        simulation.step()
        Agent.step_length = simulation.time / simulation.step_count
        if first_time:
            logging.info('Simulation started. Step length: %f' % Agent.step_length)
            if main_frame:
                main_frame.setSimulation(simulation)
            first_time = False
        
        car_id_list = simulation.vehicles.id_list
        agent_id_list = world.agents.keys()

        to_add_id_list = list(set(car_id_list) - set(agent_id_list))
        if main_frame:
            main_frame.add_agents(to_add_id_list)
        for car_id in to_add_id_list:
            world.agents[car_id] = Agent(Vehicle(car_id), world)

        to_delete_id_list = list(set(agent_id_list) - set(car_id_list))
        if main_frame:
            main_frame.delete_agents(to_delete_id_list)
        for car_id in to_delete_id_list:
            del world.agents[car_id]
        
        for car_id, agent in world.agents.items():
            agent.update(simulation)
            simulation.stats.setdefault(car_id, []).append(Stats(
                    time = simulation.time,
                    distance = agent.vehicle.distance, 
                    velocity = agent.vehicle.speed,
                    accel = agent.vehicle.accel))
        if main_frame:
            main_frame.update()
    simulation.close()
    return simulation.stats

from threading import Thread
from PyQt5.QtWidgets import QApplication
from gui.app import MainWindow

if __name__ == "__main__":
    (options, args) = get_options()
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    fh = logging.FileHandler('log.txt')
    fh.setLevel(logging.WARNING)
    #logger.addHandler(fh)
    app = QApplication(sys.argv)
    Simulation.sumo_binary = 'sumo'
    mainWindow = MainWindow()
    mainWindow.loadWorld(options.cfg)
    mainWindow.show()
    sim = Thread(target=simulation_loop, args=(options.cfg, mainWindow.world, mainWindow))
    sim.start()
    sys.exit(app.exec_())


