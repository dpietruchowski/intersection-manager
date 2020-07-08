from PyQt5.QtWidgets import QApplication, QMainWindow
from views.junction import JunctionWidget, JunctionView
from intersection.world import Edge, World

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(QMainWindow, self).__init__(parent)
        self.setWindowTitle("Intersection Manager")
        self.junctionView = JunctionView(self)
        self.setCentralWidget(self.junctionView)
        self.junctionView.comboBoxJunctions.currentTextChanged.connect(self.junctionChanged)

    def setWorld(self, world):
        if not world:
            return
        self.world = world
        self.junctionView.setJunctionsComboBox(self.world.junctions.keys())

    def loadWorld(self, configFilename):
        world = World()
        world.loadNet(configFilename.replace('.sumocfg', '.net.xml'))
        world.loadRoutes(configFilename.replace('.sumocfg', '.rou.xml'))
        self.setWorld(world)

    def junctionChanged(self):
        junctionId = self.junctionView.comboBoxJunctions.currentText()
        self.junctionView.setJunction(self.world.junctions[junctionId])

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.loadWorld('configs/test/test.net.xml')
    mainWindow.show()
    sys.exit(app.exec_())


