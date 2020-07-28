import sys
import matplotlib
matplotlib.use('Qt5Agg')
import numpy
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

sys.path.insert(0,'..')
import intersection.motion as mt

def get_function(time, distance, v_init, v_final, accel, decel, f1, f2):
    accel_1 = decel if f1 == 1 else accel
    accel_2 = accel if f2 == 1 else decel
    a = (1.0/2) * (float(f1) / accel_1 + float(f2) / accel_2)
    b = time - (float(f1 * v_init) / accel_1 + float(f2 * v_final) / accel_2)
    c = (1.0/2) * (float(f1* v_init**2) / accel_1 + float(f2 * v_final**2) / accel_2)
    print('a = %f, b = %f, c = %f' % (a,b,c))
    def calc_value(velocity):
        return a*(velocity**2) + b*velocity + c
    return calc_value

class MyPlot(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.vp = fig.add_subplot(131)
        self.dp = fig.add_subplot(132)
        self.ddp = fig.add_subplot(133)
        super(MyPlot, self).__init__(fig)

    def vplot(self, time, distance, v_init, v_final, accel, decel, v):
        f1 = -1 if v_init < v else 0 if v_init == v else 1
        f2 = -1 if v_final < v else 0 if v_final == v else 1
        f = get_function(time, distance, v_init, v_final, accel, decel, f1, f2)
        x = []
        y = []
        for i in numpy.arange(-50, 50, 1):
            x.append(i)
            y.append(f(i))
        self.vp.cla()
        self.vp.grid()
        self.vp.plot(x, y)
        self.vp.axvline(v_init, 0, 1, label='v init', c='g')
        self.vp.axvline(v_final, 0, 1, label='v final', c='r')
        self.vp.axvline(v, 0, 1, label='v', c='m')
        self.vp.legend()
        self.draw()

    def dplot(self, velocity, time, v_init, v_final, accel, decel):
        f1 = -1 if v_init < velocity else 0 if v_init == velocity else 1
        f2 = -1 if v_final < velocity else 0 if v_final == velocity else 1
        a2 = decel if f1 == 1 else accel
        a3 = accel if f2 == 1 else decel
        t2 = abs(f1) * abs(v_init - velocity) / a2
        t3 = abs(f2) * abs(v_final - velocity) / a3
        p1 = (0, v_init)
        p2 = (t2, velocity)
        p3 = (time - t3, velocity)
        p4 = (time, v_final)
        l = [p1, p2, p3, p4]
        x, y = zip(*l)
        self.dp.cla()
        self.dp.grid()
        self.dp.plot(list(x), list(y))
        self.draw()
        return f1, f2, velocity * time + f1 * ((a2 * t2**2) / 2) + f2 * ((a3 * t3**2) / 2)

    def ddplot(self, velocity, time, v_init, v_final, accel, decel):
        x = []
        y = []
        for i in numpy.arange(0, time, 0.1):
            x.append(i)
            y.append(mt.motion_distance(velocity, i, v_init, v_final, accel, decel))
        self.ddp.cla()
        self.ddp.grid()
        self.ddp.plot(x, y)
        self.draw()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.sp_time = QtWidgets.QDoubleSpinBox()
        self.sp_distance = QtWidgets.QDoubleSpinBox()
        self.sp_v = QtWidgets.QDoubleSpinBox()
        self.sp_v_init = QtWidgets.QDoubleSpinBox()
        self.sp_v_final = QtWidgets.QDoubleSpinBox()
        self.sp_accel = QtWidgets.QDoubleSpinBox()
        self.sp_decel = QtWidgets.QDoubleSpinBox()
        self.sp_time.setRange(0.1, 3000.0)
        self.sp_distance.setRange(0.1, 10000.0)
        self.sp_v.setRange(0.0, 200.0)
        self.sp_v_init.setRange(0.0, 200.0)
        self.sp_v_final.setRange(0.0, 200.0)
        self.sp_accel.setRange(0.1, 50.0)
        self.sp_decel.setRange(0.1, 50.0)
        self.my_plot = MyPlot(self, width=5, height=4, dpi=100)
        self.sp_time.valueChanged.connect(self.update)
        self.sp_distance.valueChanged.connect(self.update)
        self.sp_v.valueChanged.connect(self.update)
        self.sp_v_init.valueChanged.connect(self.update)
        self.sp_v_final.valueChanged.connect(self.update)
        self.sp_accel.valueChanged.connect(self.update)
        self.sp_decel.valueChanged.connect(self.update)

        self.sp_accel.setSingleStep(0.1)
        self.sp_decel.setSingleStep(0.1)
        self.sp_v_init.setSingleStep(0.1)
        self.sp_v_final.setSingleStep(0.1)
        self.sp_v.setSingleStep(0.1)
        self.sp_time.setValue(100)
        self.sp_distance.setValue(300)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow('Time', self.sp_time)
        form_layout.addRow('Distance', self.sp_distance)
        form_layout.addRow('V', self.sp_v)
        form_layout.addRow('V init', self.sp_v_init)
        form_layout.addRow('V final', self.sp_v_final)
        form_layout.addRow('Accel', self.sp_accel)
        form_layout.addRow('Decel', self.sp_decel)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.my_plot, 1)

        toolbar = NavigationToolbar2QT(self.my_plot, self)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(toolbar)
        main_layout.addLayout(layout)

        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        self.show()

    def update(self):
        time = self.sp_time.value()
        distance = self.sp_distance.value()
        v = self.sp_v.value()
        v_init = self.sp_v_init.value()
        v_final = self.sp_v_final.value()
        accel = self.sp_accel.value()
        decel = self.sp_decel.value()
        self.my_plot.vplot(time, distance, v_init, v_final, accel, decel, v)
        d = self.my_plot.dplot(v, time, v_init, v_final, accel, decel)
        f1 = get_function(time, distance, v_init, v_final, accel, decel, 1, 1)
        f2 = get_function(time, distance, v_init, v_final, accel, decel, -1, -1)
        v_min = min(v_init, v_final)
        v_max = max(v_init, v_final)
        print ('dg1=%f, dg2=%f' % (f1(v_min), f2(v_max)))
        print ('f1=%d, f2=%d, d=%f' % d)
        self.my_plot.ddplot(v, time, v_init, v_final, accel, decel)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()