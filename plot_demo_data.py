import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QCheckBox
from PyQt5.QtChart import QChart, QChartView, QLineSeries
import sys

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 680, 500)

        data = np.loadtxt('triangle.tsv');
        t = data[:,0]
        ch1 = data[:,7]
        ch2 = data[:,8]
        
        view1 = self.create_linechart(t,ch1)
        view2 = self.create_linechart(t,ch2)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        toolbar = QHBoxLayout()
        
        createPlot = QPushButton("create plot")
        createPlot.clicked.connect(self.doPlot)
        toolbar.addWidget(createPlot)
        
        lay = QVBoxLayout(central_widget)
        lay.addLayout(toolbar)

        lay1 = QHBoxLayout()
        lay1.addWidget(view1, stretch=1)
        cb1 = QCheckBox("Show")
        lay1.addWidget(cb1)
        lay.addLayout(lay1)

        lay2 = QHBoxLayout()
        lay2.addWidget(view2, stretch=1)
        cb2 = QCheckBox("Show")
        lay2.addWidget(cb2)
        lay.addLayout(lay2)

    def doPlot(self):
        print("Plot")

    def create_linechart(self,t,data):
        series = QLineSeries()
        for i,j in zip(t,data):
            series.append(i,j)

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chartview = QChartView(chart)
        return chartview


if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec_())
