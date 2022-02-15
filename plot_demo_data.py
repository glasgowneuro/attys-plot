import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QCheckBox
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
import sys
from plotly.subplots import make_subplots
import plotly.graph_objects as go


class Window(QMainWindow):

    channels = [
        {"name":"ADC 1","unit":"V","idx":7,"min":-2,"max":2},
        {"name":"ADC 2","unit":"V","idx":8,"min":-2,"max":2},
        {"name":"Acc X","unit":"m/s^2","idx":1,"min":-10,"max":10},
        {"name":"Acc Y","unit":"m/s^2","idx":2,"min":-10,"max":10},
        {"name":"Acc Z","unit":"m/s^2","idx":3,"min":-10,"max":10}
    ]
    
    def __init__(self, filename):
        super().__init__()
        self.setGeometry(100, 100, 680, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        toolbar = QHBoxLayout()
        
        createPlot = QPushButton("Create plot page")
        createPlot.clicked.connect(self.doPlot)
        toolbar.addWidget(createPlot)
        
        lay = QVBoxLayout(central_widget)
        lay.addLayout(toolbar)

        self.data = np.loadtxt(filename);
        self.t = self.data[:,0]

        self.doUseCheckboxes = []

        for channel in self.channels:
            ch = self.data[:,channel['idx']]
            view = self.createGraph(self.t,ch,channel)
            layh = QHBoxLayout()
            layh.addWidget(view, stretch=1)
            cb = QCheckBox("Use")
            cb.setChecked(True)
            self.doUseCheckboxes.append(cb)
            layh.addWidget(cb)
            lay.addLayout(layh)

    def doPlot(self):
        r = 0
        for cb in self.doUseCheckboxes:
            if cb.isChecked():
                r = r + 1
        fig = make_subplots(rows=r, cols=1,
                            x_title="t/sec",
                            shared_xaxes=True,
                            vertical_spacing=0.02)

        r = 0
        for channel,cb in zip(self.channels,self.doUseCheckboxes):
            if cb.isChecked():
                r = r + 1
                fig.add_trace(go.Scatter(name=channel['name'],
                                         x=self.t,
                                         y=self.data[:,channel['idx']]),
                              row=r, col=1)
                fig.update_yaxes(title_text=(channel['name']+"/"+channel['unit']), row=r, col=1)

        if r == 0:
            return
        
        fig.update_layout(title_text="Attys data")
        fig.show()


    def createGraph(self,t,data,channel):
        series = QLineSeries()
        for i,j in zip(t,data):
            series.append(i,j)

        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        axisY = QValueAxis();
        axisY.setTitleText(channel['name']+"/"+channel['unit'])
        axisY.setRange(channel['min'],channel['max'])
        chart.setAxisY(axisY)
        axisX = QValueAxis();
        axisX.setTitleText('t/sec')
        axisX.setRange(t[0],t[-1])
        chart.setAxisX(axisX)
        chartview = QChartView(chart)
        return chartview


if __name__ == "__main__":
    filename = "triangle.tsv"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    App = QApplication(sys.argv)
    window = Window(filename)
    window.show()
    sys.exit(App.exec_())
