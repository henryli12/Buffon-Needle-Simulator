import sys
import numpy as np
import random
import matplotlib
matplotlib.use('QT5AGG')
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QApplication, QMainWindow, QComboBox, QLabel, QRadioButton)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=10, height=10, dpi=100):
        fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class Needle:
    def __init__(self, length):
        self.angle = random.random() * np.pi
        self.center = (random.random() * 5, random.random() * 5)
        self.r = length / 2
        x = self.r * np.cos(self.angle)
        y = self.r * np.sin(self.angle)
        self.start = [self.center[0] + x, self.center[1] + y]
        self.end = [self.center[0] - x, self.center[1] - y]

    def check_cross(self, xpoints):
        for p in xpoints:
            if (self.start[0] <= p <= self.end[0]) or (self.start[0] >= p >= self.end[0]):
                return True
        return False

class Circle:
    def __init__(self, diameter):
        self.center = (random.random() * 5, random.random() * 5)
        self.r = diameter / 2

    def check_cross(self, xpoints):
        for p in xpoints:
            if (self.center[0] - self.r) <= p <= (self.center[0] + self.r):
                return True
        return False

class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.initUI()

    def initUI(self):
        # Set up window
        self.setFixedSize(900, 900)
        self.setWindowTitle("Buffon Needle Simulator")

        # Set up main widget
        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        # Set up layouts
        self.hbox = QHBoxLayout()
        self.hbox.setAlignment(QtCore.Qt.AlignTop)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.vbox.setAlignment(QtCore.Qt.AlignTop)

        self.widget.setLayout(self.vbox)

        # type selection layout
        self.t = 'Needle'
        self.typeSelection = QHBoxLayout()
        self.typeLabel = QLabel('Type: ')
        self.typeSelection.addWidget(self.typeLabel)
        self.needleType = QRadioButton('Needle')
        self.needleType.setChecked(True)
        self.needleType.toggled.connect(lambda:self.changeType(self.needleType))
        self.typeSelection.addWidget(self.needleType)

        self.circleType = QRadioButton('Circle')
        self.circleType.toggled.connect(lambda:self.changeType(self.circleType))
        self.typeSelection.addWidget(self.circleType)

        self.typeSelection.addStretch()

        self.hbox.addLayout(self.typeSelection)


        # iterations label and combo box
        self.selectionSection = QHBoxLayout()
        self.iterationsLabel = QLabel("Amount:")
        self.selectionSection.addWidget(self.iterationsLabel)

        self.iterations = QComboBox()
        self.iterations.addItem('10')
        self.iterations.addItem('100')
        self.iterations.addItem('200')
        self.iterations.addItem('500')
        self.iterations.addItem('1000')
        self.iterations.addItem('2500')
        self.selectionSection.addWidget(self.iterations)

        # length label and combo box
        self.lengthLabel = QLabel("Length/Diameter:")
        self.selectionSection.addWidget(self.lengthLabel)

        self.length = QComboBox()
        self.length.move(150,30)
        self.length.addItem('.1')
        self.length.addItem('.2')
        self.length.addItem('.3')
        self.length.addItem('.4')
        self.length.addItem('.5')
        self.length.addItem('.6')
        self.length.addItem('.7')
        self.length.addItem('.8')
        self.length.addItem('.9')
        self.length.addItem('1')
        self.selectionSection.addWidget(self.length)

        # Start simulation button
        self.start = QPushButton("Start Simulation")
        self.start.clicked.connect(self.simulation)
        self.selectionSection.addWidget(self.start)

        # Pause button
        self.pause = QPushButton('Pause')
        self.pause.setDisabled(True)
        self.pause.clicked.connect(self.pauseAction)
        self.pausing = False
        self.selectionSection.addWidget(self.pause)

        # Cancel button
        self.cancel = QPushButton('Cancel Simulation')
        self.cancel.setDisabled(True)
        self.cancel.clicked.connect(self.cancelAction)
        self.selectionSection.addWidget(self.cancel)

        # Add second row to vbox
        self.vbox.addLayout(self.selectionSection)

        # Stats section
        self.counter = 0
        self.counterLabel = QLabel('Number of Plotted: 0')
        self.counterLabel.setFixedWidth(150)
        self.crossCounter = 0
        self.crossLabel = QLabel('Number of Crossing: 0 (0.0%)')
        self.statsSection = QHBoxLayout()
        self.statsSection.setAlignment(QtCore.Qt.AlignLeft)
        self.statsSection.stretch(1)
        self.statsSection.addWidget(self.counterLabel)
        self.statsSection.addWidget(self.crossLabel)
        self.vbox.addLayout(self.statsSection)

        # Set up canvas
        self.canvas = MplCanvas(self, width=10, height=10, dpi=100)
        self.vbox.addWidget(self.canvas)
        self.canvas.axes.set_ylim([-0.5,5.5])
        self.canvas.axes.set_xlim([-0.5, 5.5])
        x = [0, 1, 2, 3, 4, 5]
        for p in x:
            self.canvas.axes.axvline(p)

        self.show()

    def changeType(self, type):
        if type.text() == 'Needle' and type.isChecked():
            self.t = 'Needle'
        elif type.text() == 'Circle' and type.isChecked():
            self.t = "Circle"
        else:
            return

    def pauseAction(self):
        if self.pausing:
            self.timer.start()
            self.pausing = False
            self.pause.setText('Pause')
        else:
            self.timer.stop()
            self.pausing = True
            self.pause.setText('Resume')

    def cancelAction(self):
        self.timer.stop()
        self.length.setDisabled(False)
        self.iterations.setDisabled(False)
        self.pause.setDisabled(True)
        self.cancel.setDisabled(True)
        self.needleType.setDisabled(False)
        self.circleType.setDisabled(False)

    def simulation(self):
        # Set up for simulation
        self.start.setText('Restart Simulation')
        self.pause.setDisabled(False)
        self.pause.setText('Pause')
        self.cancel.setDisabled(False)
        self.counter = 0
        self.crossCounter = 0
        self.counterLabel.setText('Number of Plotted: 0')
        self.crossLabel.setText('Number of Crossing: 0 (0.0%)')
        self.length.setDisabled(True)
        self.iterations.setDisabled(True)
        self.circleType.setDisabled(True)
        self.needleType.setDisabled(True)
        self.canvas.axes.cla()
        self.xpoints = [0, 1, 2, 3, 4, 5]
        for p in self.xpoints:
            self.canvas.axes.axvline(p)
        cross = mpatches.Patch(color='green', label='Cross')
        miss = mpatches.Patch(color='red', label='Miss')
        self.canvas.axes.legend(handles=[cross, miss], loc='upper right', bbox_to_anchor=(1,1.1))
        self.canvas.axes.set_ylim([-0.5, 5.5])
        self.canvas.axes.set_xlim([-0.5, 5.5])
        self.total = int(self.iterations.currentText())

        # Use timer to repeat plotting needles
        self.timer = QtCore.QTimer()
        self.timer.setInterval(5)
        self.timer.timeout.connect(self.plot)
        self.timer.start()
        self.canvas.draw()

    def plot(self):
        # if finish simulation
        if self.counter == self.total-1:
            self.timer.stop()
            self.pause.setDisabled(True)
            self.length.setDisabled(False)
            self.iterations.setDisabled(False)
            self.cancel.setDisabled(True)
            self.needleType.setDisabled(False)
            self.circleType.setDisabled(False)
            self.start.setText('Start Simulation')

        # Updating ui and variables
        self.counter += 1
        self.counterLabel.setText('Number of Plotted: ' + str(self.counter))

        # Create a new needle and check crossing
        if self.t == 'Needle':
            n = Needle(float(self.length.currentText()))
            if n.check_cross(self.xpoints):
                self.canvas.axes.plot([n.start[0], n.end[0]], [n.start[1], n.end[1]], 'g')
                self.crossCounter += 1
            else:
                self.canvas.axes.plot([n.start[0], n.end[0]], [n.start[1], n.end[1]], 'r')
        elif self.t == 'Circle':
            n = Circle(float(self.length.currentText()))
            if n.check_cross(self.xpoints):
                c = mpatches.Circle((n.center[0],n.center[1]), n.r, color='g')
                self.canvas.axes.add_patch(c)
                self.crossCounter += 1
            else:
                c = mpatches.Circle((n.center[0], n.center[1]), n.r, color='r')
                self.canvas.axes.add_patch(c)
        else:
            print('invalid type')
            return
        self.crossLabel.setText('Number of Crossing: ' + str(self.crossCounter) + ' (' + str(round((self.crossCounter/self.counter)*100,2)) + '%)')
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Gui = Window()
    sys.exit(app.exec_())
