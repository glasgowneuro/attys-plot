import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
import sys
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import scipy.signal as signal


class AttysData:
    
    channels = [
        {"name":"ADC 1","unit":"V","idx":7,"min":-2,"max":2},
        {"name":"ADC 2","unit":"V","idx":8,"min":-2,"max":2},
        {"name":"Acc X","unit":"m/s^2","idx":1,"min":-10,"max":10},
        {"name":"Acc Y","unit":"m/s^2","idx":2,"min":-10,"max":10},
        {"name":"Acc Z","unit":"m/s^2","idx":3,"min":-10,"max":10},
        {"name":"Mag X","unit":"gauss","idx":4,"min":-100E-6,"max":100E-6},
        {"name":"Mag Y","unit":"gauss","idx":5,"min":-100E-6,"max":100E-6},
        {"name":"Mag Z","unit":"gauss","idx":6,"min":-100E-6,"max":100E-6}
    ]

    def __init__(self,filename):
        self.data = np.loadtxt(filename);
        self.t = self.data[:,0]
        self.fs = 1/(self.t[1]-self.t[0])


class BandstopBox(QComboBox):
    items = [
        ["BS off",0],
        ["BS 50Hz",50],
        ["BS 60Hz",50]
    ]

    def __init__(self):
        super().__init__()
        for i in self.items:
            self.addItem(i[0])

    def process(self,data,fs):
        f = self.items[self.currentIndex()][1]
        if f == 0:
            return data
        f1 = f - 2
        f2 = f + 2
        b,a = signal.butter(4, [f1/fs*2,f2/fs*2], 'stop')
        return signal.lfilter(b,a,data)

class HighpassBox(QComboBox):
    items = [
        ["HP off",0],
        ["HP 0.1Hz",0.1],
        ["HP 0.2Hz",0.2],
        ["HP 0.5Hz",0.5],
        ["HP 1Hz",1],
        ["HP 2Hz",2],
        ["HP 5Hz",5],
        ["HP 10Hz",10],
    ]

    def __init__(self):
        super().__init__()
        for i in self.items:
            self.addItem(i[0])

    def process(self,data,fs):
        f = self.items[self.currentIndex()][1]
        if f == 0:
            return data
        b,a = signal.butter(4, f/fs*2, 'high')
        return signal.lfilter(b,a,data)

class LowpassBox(QComboBox):
    items = [
        ["LP off",0],
        ["LP 1Hz",1],
        ["LP 2Hz",2],
        ["LP 5Hz",5],
        ["LP 10Hz",10],
        ["LP 20Hz",20],
        ["LP 50Hz",50],
        ["Rectifier + LP 1Hz",-1],
        ["Rectifier + LP 2Hz",-2],
        ["Rectifier + LP 5Hz",-5],
    ]

    def __init__(self):
        super().__init__()
        for i in self.items:
            self.addItem(i[0])

    def process(self,data,fs):
        f = self.items[self.currentIndex()][1]
        if f == 0:
            return data
        if f < 0:
            data = np.abs(data)
            f = np.abs(f)
        b,a = signal.butter(4, f/fs*2, 'low')
        return signal.lfilter(b,a,data)

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 680, 500)

        greeting = "Welcome to attys-plot. Please choose a tsv file."

        filename,filetypes = QFileDialog.getOpenFileName(self, greeting, 
                                                         '.',"TSV files (*.tsv *.TSV)")
        if not filename:
            quit()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        flowLayout = QHBoxLayout(central_widget)
        
        channelsLayout = QVBoxLayout()
        channelsLayout.setContentsMargins(0,0,0,0)
        channelsLayout.setSpacing(0)
        flowLayout.addLayout(channelsLayout)

        self.attysData = AttysData(filename)

        self.doUseCheckboxes = []
        self.bandStopBoxes = []
        self.highpassBoxes = []
        self.lowpassBoxes = []

        for channel in self.attysData.channels:
            
            layh = QHBoxLayout()
            name = QLabel(channel['name'])
            name.setStyleSheet("padding-left: 1em; min-width: 4em; max-width: 4em")
            layh.addWidget(name)

            ch = self.attysData.data[:,channel['idx']]
            view = self.createGraph(self.attysData.t,ch,channel)
            layh.addWidget(view, stretch=1)

            arrow = '\u2794'
            cb = QCheckBox("Use")
            cb.setChecked(True)
            cb.setStyleSheet("padding-left: 1em;")
            self.doUseCheckboxes.append(cb)
            layh.addWidget(cb)
            layh.addWidget(QLabel(arrow))

            bs = BandstopBox()
            self.bandStopBoxes.append(bs)
            layh.addWidget(bs)
            layh.addWidget(QLabel(arrow))
            
            hp = HighpassBox()
            self.highpassBoxes.append(hp)
            layh.addWidget(hp)
            layh.addWidget(QLabel(arrow))
            
            lp = LowpassBox()
            self.lowpassBoxes.append(lp)
            layh.addWidget(lp)
            layh.addWidget(QLabel(arrow))

            channelsLayout.addLayout(layh)

        actionsLayout = QVBoxLayout()
#        actionsLayout.setAlignment(Qt.AlignTop)
        logoLabel = QLabel()
        logoLabel.setAlignment(Qt.AlignRight | Qt.AlignTop);
        logoLabel.setPixmap(QPixmap('attyslogo.png'))
        actionsLayout.addWidget(logoLabel)
        
        createPlot = QPushButton("Create plot")
        createPlot.setStyleSheet("padding: 2em;")
        createPlot.clicked.connect(self.doPlot)
        actionsLayout.addStretch()
        actionsLayout.addWidget(createPlot)
        actionsLayout.addStretch()
        flowLayout.addLayout(actionsLayout)
        

    def createGraph(self,t,data,channel):
        series = QLineSeries()
        for i,j in zip(t,data):
            series.append(i,j)

        chart = QChart()
        chart.layout().setContentsMargins(1, 1, 1, 1);
        chart.legend().hide()
        chart.addSeries(series)
        chartview = QChartView(chart)
        return chartview


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
        for channel,cb,bs,hp,lp in zip(self.attysData.channels,
                                    self.doUseCheckboxes,
                                    self.bandStopBoxes,
                                    self.highpassBoxes,
                                    self.lowpassBoxes
        ):
            if cb.isChecked():
                r = r + 1
                tmpdata = self.attysData.data[:,channel['idx']]
                tmpdata = bs.process(tmpdata,self.attysData.fs)
                tmpdata = hp.process(tmpdata,self.attysData.fs)
                tmpdata = lp.process(tmpdata,self.attysData.fs)
                fig.add_trace(go.Scatter(name=channel['name'],
                                         x=self.attysData.t,
                                         y=tmpdata),
                              row=r, col=1)
                fig.update_yaxes(title_text=(channel['name']+"/"+channel['unit']), row=r, col=1)

        if r == 0:
            return
        
        fig.update_layout(title_text="Attys data")
        fig.show()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec_())
