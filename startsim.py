import os, sys, logging, time, json
from collections import namedtuple
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

def get_options():
    import optparse
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-c', '--cfg', help='config file')
    opt_parser.add_option('-s', '--savefile', help='save stats')
    return opt_parser.parse_args()

from sumowrapper import Simulation, Vehicle, State
from intersection.agent import Agent

Stats = namedtuple('Stats', ['time', 'distance', 'velocity', 'accel', 'step'])

def simulation_loop(configFilename, saveFilename, world, main_frame):
    simulation = Simulation()
    simulation.start(configFilename)
    simulation.state
    first_time = True
    while simulation.min_expected_number > 0 and simulation.state != State.STOPPED:
        while simulation.state == State.PAUSED:
            time.sleep(0.5)
        start_time = time.time()
        simulation.step()
        if simulation.step_count % 1000 == 0:
            print("Step execution time %f" % (time.time() - start_time))
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


        for car_id, agent in world.agents.iteritems():
            agent.update(simulation)
        
        if simulation.step_count % 1 == 1:
            once = True
            for car_id, agent in world.agents.iteritems():
                ustart_time = time.time()
                agent.update(simulation)
                if once and simulation.step_count % 1000 == 0:
                    print("Update execution time %f" % (time.time() - ustart_time))
                sstart_time = time.time()
                simulation.stats.setdefault(car_id, []).append(Stats(
                        time = simulation.time,
                        distance = agent.vehicle.distance, 
                        velocity = agent.vehicle.speed,
                        accel = agent.vehicle.accel,
                        step = simulation.step_count))
                if once and simulation.step_count % 1000 == 0:
                    print("stats execution time %f" % (time.time() - sstart_time))
                    once = False
        if main_frame:
            main_frame.update()
        if simulation.step_count % 1000 == 0:
            print("Loop execution time %f" % (time.time() - start_time))
    simulation.close()
    if saveFilename:
        print("Saving %s" % saveFilename)
        json.dump(simulation.stats, open(saveFilename,'w'))
    return simulation.stats

from threading import Thread
from PyQt5.QtWidgets import QApplication
from gui.app import MainWindow

if __name__ == "__main__":
    (options, args) = get_options()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('log.txt')
    fh.setLevel(logging.INFO)
    #logger.addHandler(fh)
    app = QApplication(sys.argv)
    Simulation.sumo_binary = 'sumo-gui'
    mainWindow = MainWindow()
    mainWindow.loadWorld(options.cfg)
    mainWindow.show()
    sim = Thread(target=simulation_loop, args=(options.cfg, options.savefile, mainWindow.world, mainWindow))
    sim.start()
    sys.exit(app.exec_())


