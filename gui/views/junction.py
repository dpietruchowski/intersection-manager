from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class JunctionView(QWidget):
    def __init__(self, parent = None):
        super(QWidget, self).__init__(parent)
        self.comboBoxJunctions = QComboBox()
        self.spinBoxTime = QSpinBox()
        self.spinBoxTime.setRange(0, 10000000)
        self.junctionWidget = JunctionWidget()
        self.carListWidget = QListWidget()

        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        topLayout.setSpacing(6)
        topLayout.addWidget(self.comboBoxJunctions)
        topLayout.addWidget(self.spinBoxTime)
        topLayout.addStretch(10)
        mainLayout.addLayout(topLayout)
        botLayout = QHBoxLayout()
        botLayout.addWidget(self.junctionWidget)
        botLayout.addWidget(self.carListWidget)
        mainLayout.addLayout(botLayout)
        self.setLayout(mainLayout)

        self.spinBoxTime.valueChanged.connect(self.onTimeChanged)
        self.carListWidget.currentRowChanged.connect(self.onCarChanged)

    def setJunctionsComboBox(self, junctionIds):
        self.comboBoxJunctions.clear()
        for id in junctionIds:
            self.comboBoxJunctions.addItem(id)

    def setJunction(self, junction):
        self.junctionWidget.junction = junction
        self.junctionWidget.update()

    def onTimeChanged(self):
        self.junctionWidget.time = self.spinBoxTime.value()
        self.junctionWidget.update()

    def onCarChanged(self):
        item = self.carListWidget.currentItem()
        agent = self.world.agents[item.text()]
        if not agent:
            return
        self.junctionWidget.agent = agent
        junction, lane, distance = agent.next_reg_point 
        if not junction:
            return
        registration_point, arrival_point = agent.junctions[junction.id]
        arrival_time = int(arrival_point.t / agent.step_length)
        self.spinBoxTime.setValue(arrival_time)


    def add_agent(self, agent_id):
        item = QListWidgetItem(str(agent_id))
        #item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        #item.setCheckState(Qt.Unchecked)
        self.carListWidget.addItem(item)

    def delete_agent(self, agent_id):
        items = self.carListWidget.findItems(agent_id, Qt.MatchExactly)
        if not items: return     
        for item in items:
            self.carListWidget.takeItem(self.carListWidget.row(item))


class JunctionWidget(QWidget):
    def __init__(self, parent = None):
        super(QWidget, self).__init__(parent)
        self.junction = None
        self.agent = None
        self.time = 0
        self.setMinimumSize(500, 500)

    def paintEvent(self, event):        
        painter = QPainter()
        painter.begin(self)
        painter.save()
        painter.fillRect(event.rect(), Qt.white)
        if not self.junction:
            painter.restore()
            painter.end()
            return
        pen = QPen()
        pen.setCosmetic(True)
        pen.setWidthF(2)
        painter.setPen(pen)

        xscale = (event.rect().width())/(self.junction.area.rect.width() + 0.01)
        yscale = (event.rect().height())/(self.junction.area.rect.height() + 0.01)
        xoffset = self.junction.area.rect.left()
        yoffset = self.junction.area.rect.bottom()
        painter.setTransform(QTransform().scale(xscale, -yscale).translate(-xoffset, -yoffset))
        self.draw(painter)
        painter.restore()
        painter.end()

    def heightForWidth(self, w):
        return w
    
    def hasHeightForWidth(self):
        return True

    def draw(self, painter):
        self.junction.draw(painter)
        if self.junction.manager:
            manager = self.junction.manager
            brush = QBrush(QColor(100,100,100,100))
            for cell in self.junction.area.range():
                if manager.is_cell_registered(self.time, cell):
                    painter.fillRect(self.junction.area.get_cellRect(cell), brush)

        if not self.agent or not self.agent.curr_junction_point:
            return
        junction, lane, distance = self.agent.curr_junction_point 
        if not junction or junction != self.junction: 
            return
        car_distance = self.agent.prev_state.distance - distance
        car_distance += self.agent.prev_state.length/2
        if car_distance > -self.agent.prev_state.length/2:
            polygon = lane.get_bounding_polygon_for_dist(car_distance)
            if polygon:
                painter.save()
                painter.drawPolygon(polygon)
                painter.restore()