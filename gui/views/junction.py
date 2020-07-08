from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class JunctionView(QWidget):
    def __init__(self, parent = None):
        super(QWidget, self).__init__(parent)
        self.comboBoxJunctions = QComboBox()
        self.spinBoxTime = QSpinBox()
        self.spinBoxTime.setRange(0, 10000)
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

    def setJunctionsComboBox(self, junctionIds):
        self.comboBoxJunctions.clear()
        for id in junctionIds:
            self.comboBoxJunctions.addItem(id)

    def setCarsListWidget(self, carIds):
        self.carListWidget.clear()
        for id in carIds:
            self.carListWidget.addItem(id)
        for idx in range(self.carListWidget.count()):
             item = self.carListWidget.item(idx)
             item.setFlags(item.flags() | Qt.ItemIsUserCheckable)


    def setJunction(self, junction):
        self.junctionWidget.junction = junction
        self.setCarsListWidget(['car1', 'car2', 'car3'])
        self.junctionWidget.update()

    def onTimeChanged(self):
        self.junctionWidget.time = self.spinBoxTime.value()
        self.junctionWidget.update()


class JunctionWidget(QWidget):
    def __init__(self, parent = None):
        super(QWidget, self).__init__(parent)
        self.junction = None
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
        if not self.junction.manager:
            return

        cellReg = self.junction.manager.cellReg
        brush = QBrush(QColor(100,100,100,100))
        for cell in cellReg.getAllCells(self.time):
            painter.fillRect(self.junction.area.getCellRect(cell), brush)