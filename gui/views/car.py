from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy

from car_ui import Ui_Form


def prev_next_iter(iterable):
    prev = None
    for curr in iterable:
        if prev:
            yield prev, curr
        prev = curr

class CarFigure(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.subplot = fig.add_subplot(111)
        super(CarFigure, self).__init__(fig)


class CarView(QWidget):
    def __init__(self, parent = None):
        super(CarView, self).__init__(parent)
        self.figure = CarFigure()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.plotLayout.addWidget(self.figure)
        self.ui.btnRefresh.clicked.connect(self.refresh)

    def update(self, simulation):
        self.simulation = simulation

    def refresh(self):
        self.figure.subplot.cla()
        self.figure.subplot.grid()
        legend_handles = []
        for idx in range(self.ui.carListWidget.count()):
            item = self.ui.carListWidget.item(idx)
            if item.checkState() == Qt.Checked:
                legend_handles.extend(self.plot(self.simulation, item.text()))
        self.figure.subplot.legend(handles=legend_handles)
        self.figure.draw()

    def plot(self, simulation, agent_id):
        listStats = map(list, zip(*simulation.stats[agent_id]))
        legend_handles = []
        if self.ui.s_t.isChecked():
            l, = self.figure.subplot.plot(listStats[0], listStats[1], label='s(t): %s' % agent_id)
            legend_handles.append(l)
        if self.ui.v_t.isChecked():
            l, = self.figure.subplot.plot(listStats[0], listStats[2], label='v(t): %s' % agent_id)
            legend_handles.append(l)

        agent = self.world.agents[agent_id]
        junction, lane, distance = agent.next_reg_point 
        if self.ui.mps_t.isChecked() and junction and junction.id in agent.junctions:
            registration_point, motion_points, arrival_point = agent.junctions[junction.id]
            x = []
            y = []
            for prev, curr in prev_next_iter(motion_points):
                a = abs(prev.v - curr.v) / abs(prev.t - curr.t)
                f = -1 if curr.v < prev.v else 0 if prev.v == curr.v else 1
                s = lambda t : prev.v * t + ((f * a * t**2) / 2)
                step = 0.1
                d = prev.d
                for i in numpy.arange(prev.t, curr.t, step):
                    x.append(i + registration_point.t)
                    y.append(d + s(i - prev.t))
            l, = self.figure.subplot.plot(x, y, label='mps(t): %s' % agent_id)
            legend_handles.append(l)
        if self.ui.mpv_t.isChecked() and junction and junction.id in agent.junctions:
            registration_point, motion_points, arrival_point = agent.junctions[junction.id]
            x = [motion_point.t + registration_point.t for motion_point in motion_points]
            y = [motion_point.v for motion_point in motion_points]
            l, = self.figure.subplot.plot(x, y, label='mpv(t): %s' % agent_id)
            legend_handles.append(l)
        return legend_handles

    def add_agent(self, agent_id):
        item = QListWidgetItem(str(agent_id))
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        self.ui.carListWidget.addItem(item)

    def delete_agent(self, agent_id):
        items = self.ui.carListWidget.findItems(agent_id, Qt.MatchExactly)
        if not items: return     
        for item in items:
            self.ui.carListWidget.takeItem(self.ui.carListWidget.row(item))




