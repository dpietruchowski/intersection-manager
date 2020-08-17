from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QToolBar
from views.junction import JunctionWidget, JunctionView
from views.car import CarView
from intersection.world import Edge, World

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(QMainWindow, self).__init__(parent)
        self.setWindowTitle("Intersection Manager")
        self.centralWidget = QStackedWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.toolBar = QToolBar(self)
        self.addToolBar(self.toolBar)
        action = self.toolBar.addAction('<')
        action.triggered.connect(self.prevView)
        action = self.toolBar.addAction('>')
        action.triggered.connect(self.nextView)
        self.carView = CarView(self)
        self.centralWidget.addWidget(self.carView)
        self.junctionView = JunctionView(self)
        self.centralWidget.addWidget(self.junctionView)
        self.junctionView.comboBoxJunctions.currentTextChanged.connect(self.junctionChanged)

    def setWorld(self, world):
        if not world:
            return
        self.world = world
        self.carView.world = world
        self.junctionView.world = world
        self.junctionView.setJunctionsComboBox(self.world.junctions.keys())

    def setSimulation(self, simulation):
        self.carView.simulation = simulation
        self.simulation = simulation

    def loadWorld(self, configFilename):
        world = World()
        world.load_net(configFilename.replace('.sumocfg', '.net.xml'))
        world.load_routes(configFilename.replace('.sumocfg', '.rou.xml'))
        self.setWorld(world)

    def junctionChanged(self):
        junctionId = self.junctionView.comboBoxJunctions.currentText()
        self.junctionView.setJunction(self.world.junctions[junctionId])

    def prevView(self):
        self.centralWidget.setCurrentIndex(self.centralWidget.currentIndex() - 1)

    def nextView(self):
        self.centralWidget.setCurrentIndex(self.centralWidget.currentIndex() + 1)

    def update(self):
        pass

    def add_agents(self, agent_list):
        for agent_id in agent_list:
            self.carView.add_agent(agent_id)
            self.junctionView.add_agent(agent_id)

    def delete_agents(self, agent_list):
        for agent_id in agent_list:
            self.carView.delete_agent(agent_id)
            self.junctionView.delete_agent(agent_id)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.loadWorld('configs/test/test.net.xml')
    mainWindow.show()
    sys.exit(app.exec_())


