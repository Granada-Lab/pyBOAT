#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QCheckBox, QTableView, QComboBox, QFileDialog, QAction, QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QMessageBox, QSizePolicy, QWidget, QVBoxLayout, QHBoxLayout, QDialog, QGroupBox, QFormLayout, QGridLayout, QTextEdit, QTabWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from numpy.fft import rfft
import matplotlib.pyplot as plt

from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt

import wavelets_lib as wl
from helper.pandasTable import PandasModel
import random
import numpy as np
import pandas as pd

DEBUG = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initzialize data handling unit
        self.dh = DataHandler()
        self.i =0
        self.view = {}
        self.synth = {}
        self.initUI()
    def initUI(self):
        self.setGeometry(100,100,400,100)
        self.setWindowTitle('TFAnalyzer')
        
        #Build Menu and Actions 
        self.quitAction = QAction("&Quit", self)
        self.quitAction.setShortcut("Ctrl+Q")
        self.quitAction.setStatusTip('Leave The App')
        self.quitAction.triggered.connect(self.close_application)

        openFile = QAction("&Load data", self)
        openFile.setShortcut("Ctrl+L")
        openFile.setStatusTip('Load data')
        openFile.triggered.connect(self.load)

        creatsynth = QAction('&Synthetic signal', self)
        creatsynth.setShortcut('Ctrl+S')
        creatsynth.setStatusTip('Create synthetic signals')
        creatsynth.triggered.connect(self.creatsynth)
        
        batch = QAction('&Batch',self)
        batch.setShortcut('Ctrl+B')
        batch.setStatusTip('Analyze in batch process')
        batch.triggered.connect(self.batch)

        #plotSynSig = QAction('&Plot synthetic signal',self)
        #plotSynSig.setShortcut('Ctrl+P')
        #plotSynSig.setStatusTip('Plot synthetic signal')
        #plotSynSig.triggered.connect(self.plotSynSig)
        
        viewer = QAction('&View Data',self)
        viewer.setShortcut('Ctrl+D')
        viewer.setStatusTip('View data')
        viewer.triggered.connect(self.viewing)

        self.statusBar()

        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)
        
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(self.quitAction)
        fileMenu.addAction(openFile)
        
        analyzerMenu = mainMenu.addMenu('&Analyzer')
        #analyzerMenu.addAction(plotSynSig)
        analyzerMenu.addAction(batch)
        analyzerMenu.addAction(creatsynth)
        analyzerMenu.addAction(viewer)
        
        #Adding action buttons
        
        quitButton = QPushButton("Quit", self)
        quitButton.clicked.connect(self.close_application)
        quitButton.resize(quitButton.minimumSizeHint())
        quitButton.move(50,50)

        openFileButton = QPushButton("Load data",self)
        openFileButton.clicked.connect(self.load)
        quitButton.resize(quitButton.minimumSizeHint())
        openFileButton.move(120,50)

        #Showing the main window
        self.show()
        
    def close_application(self):
        choice = QMessageBox.question(self, 'Quitting',
                                            'Do you want to exit this application?',
                                            QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            print("Quitting ...")
            #sys.exit()
            appc = QApplication.instance()
            appc.closeAllWindows()
        else:
            pass
        
    def load (self):
        # Create window to load data
        self.new_data = DataLoader()
        # Connect data loader with data handling unit to pass on loaded data
        self.dh.make_connection(self.new_data)
        ui = self.new_data.initUI()
        if ui:
            self.viewing() # initialize data viewer and passes loaded data on
###################################
    def viewing (self): # Initializes data viewing window(s)
    
        print ('function viewing called')
        self.i +=1
        self.view[self.i] = DataViewer()
        # Connect data viewer with data handling unit to receive data
        self.view[self.i].make_connection(self.dh) 
        
        
        self.dh.emit_current_data() #Emits data
        self.view[self.i].initUI()
        print ('DataViewer and DH connected')
        
    def creatsynth (self):
        # Create window to generate synthetic signals
        print ('function creatsynth called')
        self.i +=1
        self.synth[self.i] = SynthViewer()
        self.synth[self.i].data_input()

        self.synth[self.i].initUI()
        print ('synth and plotSynSig connected')
        
    def batch (self):
        #Create window for batch process
        print ('function batch called')
        self.batchprocess = Batch()
        self.batchprocess.initUI()

    '''def plotSynSig (self):
        pdic = {'T' : 900, 'amp' : 6, 'per' : 70, 'sigma' : 2, 'slope' : -10.}
        gen_func = synth_signal1 #TODO dropdown which synthetic signal
        default_para_dic = pdic
        self.synSig=SyntheticSignalGenerator(gen_func, default_para_dic)
        self.dh.make_connection(self.synSig)
        self.synSig.initUI()
        '''
class DataLoader(QWidget):
    timeSignal = pyqtSignal('PyQt_PyObject') # This signal contains and emits the data points (not any time points) to the data handling unit (DataHandler)
    def __init__(self):
        super().__init__()
        self.raw_data = pd.DataFrame()
        self.signal_dic = {}
        
    def initUI(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open File') #Opens File Dialog and returns file name that will be opend in the following
        
        #If correct file path/type is supplied data are read in and emitted
        #try: 
        if DEBUG:
            print (file_name[0])

        try:
            self.raw_data = pd.read_excel(file_name[0], header=0)
        #except:
        #    try:
        #        self.raw_data = pd.read_csv(file_name[0])
        except:
            self.raw_data = pd.DataFrame()
            self.noFile = Error('No valid path or file supplied!', 'No File')
            print ('returned no values emiited')
            return False
        
        
        ## TODO drop NaNs
        ## later TODO deal with 'holes'
        self.emit_values()
        return True

        

        ### TODO change emitted signal ???
    def emit_values(self):
        # Emits a dictionary containing id and data value pairs to the DataHandler
        for name, values in self.raw_data.iteritems():
            self.signal_dic[name] = values
            
        self.timeSignal.emit(self.signal_dic)
        #self.timeSignal.emit(self.raw_data)
    


class DataHandler(QWidget):
    #Add signal
    signalIds = pyqtSignal('PyQt_PyObject')
    
    def __init__(self):
        super().__init__()
        self.signal_ids = []
        self.signal_dic = {}

    def emit_current_data(self):
        print ('emit_current_data called')
        # Emits ids list and dictionary containing id value pairs to DataViewer
        self.signalIds.emit([self.signal_ids, self.signal_dic])
        #self.signalIds.emit([self.raw_data])
    

    def make_connection(self, signal_object):        #This function connects DataHandler with DataLoader so that data emitted from DataLoder can be received by the DataHandler, signal_object is parsed and should be of class DataLoader
        signal_object.timeSignal.connect(self.get_signal) # Triggers function self.get_signal if timeSignal signal is received

        

    @pyqtSlot('PyQt_PyObject')
    def get_signal(self, raw_data): # raw_data is dictionary containing id and data pairs
        self.signal_ids = raw_data.keys()
        self.signal_dic = raw_data
        #self.raw_data = raw_data


    

class DataViewer(QWidget):

    @pyqtSlot('PyQt_PyObject')
    def get_signal_ids(self, signal_ids):
        print ('get_signal_ids called')
        self.series_ids = signal_ids[0]
        self.signal_dic= signal_ids[1]
        #self.tvec_dic = signal_ids[2]
        
        for id in self.series_ids:
            #self.raw_data[id+'time'] = self.tvec_dic[id]
            self.raw_data[id] = self.signal_dic[id]

        self.data_input()

    def __init__(self):
        super().__init__()
        print ('__init__ of DataViewer called')
        self.raw_data= pd.DataFrame()
        #self.signal_dic = {}
        self.anaWindows = {}
        self.i = 0
        self.signal_id='None'
        self.raw_signal = None
        self.titel = 'DataViewer'
        
    def initUI(self):
        self.plotWindow = TimeSeriesViewCanvas()
        main_frame = QWidget()
        self.plotWindow.setParent(main_frame)
        ntb = NavigationToolbar(self.plotWindow, main_frame) # full toolbar

        
        self.setWindowTitle(self.titel)
        self.setGeometry(20,30,900,650)
        
        
        #Data selection box (very top)
        main_layout_v =QVBoxLayout()
        #Data selction drop-down
        dataLable = QLabel('Select signal', self)
        
        self.signalBox = QComboBox(self)
        self.signalBox.addItem('None')
        self.fillSignalBox()
        
        dt_label= QLabel('Sampling intervall:')
        self.dt_edit = QLineEdit()
        self.dt_edit.textChanged.connect(self.set_dt)
        self.dt_edit.insert(str(1))
        unit_label= QLabel('in:')
        unitBox = QComboBox(self)
        unitBox.addItem('min')
        unitBox.addItem('s')
        self.time_unit ='min'
        
        
        data_selection_layout_h =QHBoxLayout()
        data_selection_layout_h.addWidget(dataLable)
        data_selection_layout_h.addWidget(self.signalBox)
        data_selection_layout_h.addStretch(0)
        data_selection_layout_h.addWidget(dt_label)
        data_selection_layout_h.addWidget(self.dt_edit)
        data_selection_layout_h.addStretch(0)
        data_selection_layout_h.addWidget(unit_label)
        data_selection_layout_h.addWidget(unitBox)
        data_selection_layout_h.addStretch(0)
        main_layout_v.addLayout(data_selection_layout_h)
        

        self.signalBox.activated[str].connect(self.set_signal_id)
        unitBox.activated[str].connect(self.set_time_unit)
        
        # plot options box
        plot_options_box = QGroupBox('Signal plot options')
        cb_layout= QFormLayout()
        cb_raw = QCheckBox('Raw signal', self)
        cb_trend = QCheckBox('Trend', self)
        cb_detrend = QCheckBox('Detrended Signal', self)
        plotButton = QPushButton('Plot signal', self)
        button_layout_h = QHBoxLayout()
        plotButton.clicked.connect(self.doPlot)
        button_layout_h.addStretch(0)
        button_layout_h.addWidget(plotButton)
        
        ##detrending parameters
        
        self.T_c = QLineEdit()
        self.T_c.insert(str(100)) 
        self.v_max = QLineEdit()
        self.v_max.insert(str(20))
        
        ## checkbox layout
        cb_layout.addRow(cb_raw)
        cb_layout.addRow(QLabel('Cut-off period for detrending:'),self.T_c)
        cb_layout.addRow(cb_trend)
        cb_layout.addRow(cb_detrend)
        cb_layout.addRow(button_layout_h)
        
        plot_options_box.setLayout(cb_layout)
        #Fix X size of plot_options_box containing parameter boxes
        size_pol= QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        plot_options_box.setSizePolicy(size_pol)
        
        ## checkbox signal set and change
        cb_raw.toggle()
        
        cb_raw.stateChanged.connect(self.toggle_raw)
        cb_trend.stateChanged.connect(self.toggle_trend)
        cb_detrend.stateChanged.connect(self.toggle_detrended)
        
        self.plot_raw = bool(cb_raw.checkState() )
        self.plot_trend = bool(cb_trend.checkState() )
        self.plot_detrended = bool(cb_detrend.checkState() )
        
        #Plot box
        plot_box = QGroupBox('Signal and trend')
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.plotWindow)
        plot_layout.addWidget(ntb)
        plot_box.setLayout(plot_layout)
        
        
        #Analyzer box with tabs
        table_widget = QWidget()
        ana_box = QVBoxLayout()
 
        ## Initialize tab screen
        tabs = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()

        ## Add tabs
        tabs.addTab(tab1,"Wavelet analysis")
        tabs.addTab(tab2,"Fourier transform")
 
        ## Create first tab
        tab1.ana_box = QFormLayout()
        
        ## for wavlet params, button, etc.
        self.T_min = QLineEdit()
        self.step_num = QLineEdit()
        self.step_num.insert('100')
        self.T_max = QLineEdit()
        self.v_max = QLineEdit()
        self.v_max.insert(str(20))
        
        T_min_lab = QLabel('Smallest period')
        step_lab = QLabel('Number of periods')
        T_max_lab = QLabel('Highest  period')
        v_max_lab = QLabel('Expected maximal power')
        
        T_min_lab.setWordWrap(True)
        step_lab.setWordWrap(True)
        T_max_lab.setWordWrap(True)
        v_max_lab.setWordWrap(True)
        
        
        wletButton = QPushButton('Analyze signal', self)
        #wletButton.clicked.connect(self.doPlot)
        ## add  button to layout
        wlet_button_layout_h = QHBoxLayout()
        wletButton.clicked.connect(self.wlet_ana)
        wlet_button_layout_h.addStretch(0)
        wlet_button_layout_h.addWidget(wletButton)

        self.cb_use_detrended = QCheckBox('Use detrended signal', self)
        self.cb_use_detrended.stateChanged.connect(self.toggle_use)
        self.use_detrended = bool(self.cb_use_detrended.checkState() )

        
        ## Add Wavelet analyzer options to tab1.ana_box layout
        
        tab1.ana_box.addRow(T_min_lab,self.T_min)
        tab1.ana_box.addRow(step_lab, self.step_num)
        tab1.ana_box.addRow(T_max_lab,self.T_max)
        tab1.ana_box.addRow(v_max_lab, self.v_max)
        tab1.ana_box.addRow(self.cb_use_detrended)
        tab1.ana_box.addRow(wlet_button_layout_h)
        
        tab1.setLayout(tab1.ana_box)

        # fourier button
        fButton = QPushButton('Analyze signal', self)
        ## add  button to layout
        f_button_layout_h = QHBoxLayout()
        fButton.clicked.connect(self.fourier_ana)
        f_button_layout_h.addStretch(0)
        f_button_layout_h.addWidget(fButton)

        # fourier detrended switch
        self.cb_use_detrended2 = QCheckBox('Use detrended signal', self)
        self.cb_use_detrended2.stateChanged.connect(self.toggle_use)
        self.use_detrended2 = bool(self.cb_use_detrended2.checkState() )

        ## Create second tab
        tab2.ana_box = QFormLayout()
        #tab2.ana_box.addRow(T_min_lab,self.T_min)
        #tab2.ana_box.addRow(T_max_lab,self.T_max)
        tab2.ana_box.addRow(self.cb_use_detrended2)
        tab2.ana_box.addRow(f_button_layout_h)
        tab2.setLayout(tab2.ana_box)
        
        
        #Add tabs to widget
        ana_box.addWidget(tabs)
        #set layout of table_widget (will be added to options layout) as ana_box (containing actual layout)
        table_widget.setLayout(ana_box)
        
        #Fix X size of table_widget containing parameter boxes
        size_pol= QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        table_widget.setSizePolicy(size_pol)
        

        #Options box (big box)
        #options_box = QGroupBox('Options')
        #options_layout=QFormLayout()
        #options_layout.addRow(plot_options_box)
        #options_layout.addRow(table_widget)
        
        #options_box.setLayout(options_layout)

        
        
        #Merge all layout in main layout
        horizontalGroupBox = QGroupBox('Input data')
        layout = QGridLayout()
        layout.addWidget(self.table,0,0,3,6)
        layout.addWidget(plot_box, 4,0,4,5)
        layout.addWidget(plot_options_box, 4,5,2,1)
        layout.addWidget(table_widget, 6,5,2,1)
        # layout.addWidget(options_box, 3,4,4,2)
        horizontalGroupBox.setLayout(layout)

        main_layout_v.addWidget(horizontalGroupBox)

        
        self.setLayout(main_layout_v)
        self.show()
        
    def fillSignalBox(self):
        j = self.signalBox.count()
        while j > 0:
            self.signalBox.removeItem(j)
            j -=1
        for i in self.series_ids:
            print (i)
            self.signalBox.addItem(i)
        
    def toggle_use (self,state):
        if state == Qt.Checked:
            self.use_detrended = True
            self.use_detrended2 = True
            self.cb_use_detrended.setCheckState(Qt.Checked)
            self.cb_use_detrended2.setCheckState(Qt.Checked)
        else:
            self.use_detrended = False
            self.use_detrended2 = False
            self.cb_use_detrended.setCheckState(Qt.Unchecked)
            self.cb_use_detrended2.setCheckState(Qt.Unchecked)
            
    def toggle_raw (self, state):
        if state == Qt.Checked:
            self.plot_raw = True
        else:
            self.plot_raw = False
        print (self.plot_raw)
        
    def toggle_trend (self, state):
        print (self.plot_trend)
        if state == Qt.Checked:
            self.plot_trend = True
        else:
            self.plot_trend = False
        print (self.plot_trend)
        
    def toggle_detrended (self, state):
        if state == Qt.Checked:
            self.plot_detrended = True
            #self.cb_use_detrended.setCheckState(Qt.Checked)
        else:
            self.plot_detrended = False
            #self.cb_use_detrended.setCheckState(Qt.Unchecked)
        print (self.plot_detrended)
        
    def data_input(self):
        print ('data_input called')
        self.table = QTableView()
        model= PandasModel(self.raw_data)
        self.table.setModel(model)
        
    def set_time_unit(self,text):
        '''Sets current working time unit to selected'''
        self.time_unit = text
        
    def set_signal_id(self, text):
        '''Sets current working id to selected'''
        self.signal_id = text
        self.set_periods()
        self.doPlot()

    def set_dt(self):
        '''Sets current working time interval to selected'''
        t = self.dt_edit.text()
        if t:
            self.dt = int(t)
            self.set_periods()
        
    def set_periods(self):
        
        if np.size(self.raw_signal) <= 1: # no data yet
            self.data_prep()
        
        if np.size(self.raw_signal) > 1: # data prep didn't succeed
            self.T_min.clear()
            self.T_max.clear()
            self.T_min.insert(str(2*self.dt))
            self.T_max.insert(str(self.dt*len(self.raw_signal)))
        
    def data_prep(self):
        self.dt = int(self.dt_edit.text())
        print('prep', self.signal_id)
        
        if self.signal_id != 'None':
            self.raw_signal = np.array(self.raw_data[self.signal_id].values)
            self.tvec =np.arange(0,len(self.raw_signal)*self.dt,self.dt)
            self.tvec =self.tvec[~np.isnan(self.raw_signal)]
            self.raw_signal =self.raw_signal[~np.isnan(self.raw_signal)]
            

    def periods_changed (self):
        
        self.T_min_value = int(self.T_min.text())
        self.step_num_value = int(self.step_num.text())
        self.T_max_value =int(self.T_max.text())
        self.v_max_value = int(self.v_max.text())
       
        
    def doPlot(self):
        self.data_prep()
        T_c = float(self.T_c.text())
        
        try:
            self.trend = wl.sinc_smooth(raw_signal = self.raw_signal,T_c = T_c, dt = self.dt)
            self.plotWindow.mpl_update(self.tvec, self.raw_signal, self.trend, plot_raw= self.plot_raw, plot_trend=self.plot_trend, plot_detrended=self.plot_detrended, time_unit = self.time_unit)

        except:
            self.noDataSelected = Error('Please select one dataseries from the drop down menu or load data first!','Missing data')
            
    def wlet_ana(self):
        self.periods_changed()
        if self.T_min_value < 2*self.dt:
            self.outofBoundary = Error('Out of boundary: Please select value bigger than '+str(2*self.dt)+' (Nyqvist limit is 2*sampling interval) for \'Smallest period\'!','Out of boundary')
            return
        elif self.T_max_value > self.dt*len(self.raw_signal):
            self.outofBoundary = Error('Out of boundary: Please select value smaller than '+str(self.dt*len(self.raw_signal))+' (Length of data series) for \'Highest period\' (Length of data series)!','Out of boundary')
            return
        if self.step_num_value > 1000:
            
            choice = QMessageBox.question(self, 'High number: ',
                                            'High number: Do you want to continue?',
                                            QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                pass
            else:
                return
            
        if self.use_detrended:
            signal= self.raw_signal-self.trend
        else:
            signal= self.raw_signal
        self.i = self.i+20
        
        self.anaWindows[self.i] = WaveletAnalyzer(signal=signal, dt=self.dt, T_min= self.T_min_value, T_max= self.T_max_value, position= self.i, signal_id =self.signal_id, step_num= self.step_num_value, v_max = self.v_max_value, time_unit= self.time_unit)

    def fourier_ana(self):
        self.i = self.i+20

        if self.use_detrended2:
            signal= self.raw_signal-self.trend
        else:
            signal= self.raw_signal
        
        self.anaWindows[self.i] = FourierAnalyzer(signal = signal, dt = self.dt, signal_id = self.signal_id, position = self.i, time_unit = self.time_unit)

    def make_connection(self, datahandler_object):
        datahandler_object.signalIds.connect(self.get_signal_ids)
        #datahandler_object.dataSignal.connect(self.get_data)

class FourierAnalyzer(QWidget):
    def __init__(self, signal, dt, signal_id, position,time_unit, parent = None):
        super().__init__()

        self.fCanvas = FourierCanvas()
        self.fCanvas.plot_spectrum(signal,dt, time_unit)

        self.initUI(position, signal_id)

    def initUI(self, position, signal_id):

        self.setWindowTitle('Fourier spectrum ' + signal_id)
        self.setGeometry(510+position,30+position,550,600)

        main_frame = QWidget()
        self.fCanvas.setParent(main_frame)
        ntb = NavigationToolbar(self.fCanvas, main_frame)

        main_layout = QGridLayout()
        main_layout.addWidget(self.fCanvas,0,0,9,1)
        main_layout.addWidget(ntb,10,0,1,1)

        # test canvas resize
        # dummy_h = QHBoxLayout()
        # dummy_h.addStretch(0)
        # button = QPushButton('push me', self)
        # dummy_h.addWidget(button)
        # main_layout.addLayout(dummy_h,11,0)
        
        self.setLayout(main_layout)
        self.show()
        
class FourierCanvas(FigureCanvas):
    def __init__(self):
        self.fig, self.axs = plt.subplots(1,1)

        FigureCanvas.__init__(self, self.fig)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    def plot_spectrum(self,signal,dt, time_unit):

        #time_label = '[min]'

        N = len(signal)
        
        df = 1./(N*dt) # frequency bins
        fft_freqs = np.arange(0,1./(2*dt)+df+df/2., step = df) # prevent rounding errors
        rf = rfft(signal) # positive frequencies
        
        print(N,dt,df)
        print(len(fft_freqs),len(rf))
        
        print('Fourier power: ', max(np.abs(rf)))
        fpower = np.abs(rf)/np.var(signal)
        print('Fourier power/var: ', max(fpower))


        # period view
        self.axs.plot(1/fft_freqs[1:-1],fpower[1:],lw = 1.8, alpha = 0.8)
        self.axs.set_xlabel('Periods ' + time_unit)
        self.axs.set_ylabel('Fourier power')

class WaveletAnalyzer(QWidget):

    def __init__(self, signal, dt, T_min, T_max, position, signal_id, step_num, v_max, time_unit):
        super().__init__()
        self.signal_id = signal_id
        self.signal = signal
        self.v_max = v_max
        self.time_unit = time_unit
        self.cb= {}

        self.periods=np.linspace(T_min, T_max, step_num)
        #self.periods = periods
        
        print (self.periods[-1])
        
        # Plot input signal
        self.tvec = np.arange(0,len(signal)*dt,dt)
        #self.tvec = tvec

        # no ridge yet
        self.rdata = None
        #self._has_ridge = False # no plotted ridge

        #=============Compute Spectrum============================
        self.modulus, self.wlet = wl.compute_spectrum(self.signal, dt, self.periods)
        #========================================================
        
        
        self.initUI(position)
        
    def initUI(self, position):
        self.setWindowTitle('WaveletAnalyzer - '+str(self.signal_id))
        self.setGeometry(510+position,30+position,600,700)
        
        # Wavelet and signal plot
        self.waveletPlot = SpectrumCanvas()
        main_frame = QWidget()
        self.waveletPlot.setParent(main_frame)
        ntb = NavigationToolbar(self.waveletPlot, main_frame) # full toolbar

        #-------------plot the wavelet power spectrum---------------------------
        self.waveletPlot.plot_signal_modulus(self.tvec, self.signal,self.modulus,self.periods, self.v_max, self.time_unit)
        #-----------------------------------------------------------------------
        
        
        #Analyzer box with tabs
        table_widget = QWidget()
        ridge_opt_box = QVBoxLayout()
 
        ## Initialize tab screen
        tabs = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()

        ## Add tabs
        tabs.addTab(tab2,'Trace maxima')
        tabs.addTab(tab1,'Simulated annealing')
 
        ## Create first tab
        tab1.ridge_opt_box = QFormLayout()

        #Start ridge detection
        ridgeButton2 = QPushButton('Detect maxRidge!', self)
        # ridgeButton2.setFixedHeight(20) # has almost no effect
        ridgeButton2.clicked.connect(self.do_maxRidge_detection)

        ridgeButton1 = QPushButton('Detect annealRidge!', self)
        ridgeButton1.clicked.connect(self.do_annealRidge_detection)
        
        #saveButton_hbox = QHBoxLayout()

        self.power_thresh = None
        self.power_thresh_tb = QLineEdit()
        self.power_thresh_tb.textChanged.connect(self.read_power_thresh)
        self.power_thresh_tb.insert('0')

        # anneal parameters
        self.per_ini = QLineEdit(str(int(np.mean(self.periods)))) # start at middle of period interval
        self.T_ini = QLineEdit('1')
        self.Nsteps = QLineEdit('5000')
        self.max_jump = QLineEdit('3')
        self.curve_pen = QLineEdit('0')
        
        power_thresh_lab = QLabel('Power threshold')
        per_ini_lab = QLabel('Initial period guess')
        T_ini_lab = QLabel('Initial temperature')
        Nsteps_lab = QLabel('Number of iterations')
        max_jump_lab = QLabel('Maximal jumping distance')
        curve_pen_lab = QLabel('Curvature cost')

        power_thresh_lab.setWordWrap(True)
        per_ini_lab.setWordWrap(True)
        T_ini_lab.setWordWrap(True) 
        Nsteps_lab.setWordWrap(True) 
        max_jump_lab.setWordWrap(True)
        curve_pen_lab.setWordWrap(True)
        
        #Copy of powerth
        power_thresh2_tb = QLineEdit()
        power_thresh2_tb.textChanged.connect(self.read_power_thresh)
        power_thresh2_tb.insert('0')
        power_thresh_lab2 = QLabel('Power threshold')

        # anneal parameters end
        
        ridgebutton2_h = QHBoxLayout()
        ridgebutton2_h.addWidget(ridgeButton2)
        #buttons_hbox.addWidget(ridgeButton2)
        #buttons_hbox.addWidget(saveButton)
        ridgebutton2_h.addStretch(0)

        ridgebutton1_h = QHBoxLayout()
        ridgebutton1_h.addWidget(ridgeButton1)
        #buttons_hbox.addWidget(saveButton)
        ridgebutton1_h.addStretch(0)
        
        
        grid_lay = QGridLayout()
        #grid_lay.addWidget(self.waveletPlot, 0,0,5,5)
        grid_lay.addWidget(power_thresh_lab, 0,0,1,1)
        grid_lay.addWidget(self.power_thresh_tb, 0,1,1,1)
        grid_lay.addWidget( per_ini_lab, 1,0,1,1)
        grid_lay.addWidget(self.per_ini, 1,1,1,1)
        grid_lay.addWidget(T_ini_lab, 2,0,1,1)
        grid_lay.addWidget(self.T_ini, 2,1,1,1)
        grid_lay.addWidget(Nsteps_lab, 0,2,1,1)
        grid_lay.addWidget(self.Nsteps, 0,3,1,1)
        grid_lay.addWidget(max_jump_lab, 1,2,1,1)
        grid_lay.addWidget(self.max_jump, 1,3,1,1)
        grid_lay.addWidget(curve_pen_lab, 2,2,1,1)
        grid_lay.addWidget(self.curve_pen, 2,3,1,1)
        
        grid = QWidget()
        grid.setLayout(grid_lay)

        tab1.ridge_opt_box.addRow(grid)
        tab1.ridge_opt_box.addRow(ridgebutton1_h)
        
        tab1.setLayout(tab1.ridge_opt_box)
        
        ## Create second tab
        tab2.ridge_opt_box = QFormLayout()
        tab2.ridge_opt_box.addRow(power_thresh_lab2,power_thresh2_tb)
        tab2.ridge_opt_box.addRow(ridgebutton2_h)
        tab2.setLayout(tab2.ridge_opt_box)
        
        #Add tabs to widget
        ridge_opt_box.addWidget(tabs)
        #set layout of table_widget (will be added to options layout) as ridge_opt_box (containing actual layout)
        table_widget.setLayout(ridge_opt_box)
        size_pol= QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        table_widget.setSizePolicy(size_pol)
        #table_widget.updateGeometry(self)
        
        #box_layout.addLayout(tab1.ridge_opt_box)
        
        #box_layout.addLayout(buttons_hbox)
        #big_box.setLayout(box_layout)
        
        #Add save options
        #Save output
        saveButton = QPushButton('Save', self)
        saveButton.clicked.connect(self.save_out)
        
        cb_layout= QFormLayout()
        
        _h = QHBoxLayout()
        
        self.opts =['time', 'amplitudes', 'periods', 'phase', 'inds', 'z']
        for key in self.opts:
            self.cb[key] = QCheckBox(str(key), self)
            _h.addWidget(self.cb[key])
        cb_layout.addRow(_h)
        
        
        savebutton_h = QHBoxLayout()
        savebutton_h.addStretch(0)
        savebutton_h.addWidget(saveButton)
        
        cb_layout.addRow(savebutton_h)
        
        
        save_options_box = QGroupBox('Save options')
        
        save_options_box.setLayout(cb_layout)
        
        
        #Button go to batch processing
        batchButton = QPushButton('Go to batch', self)
        batchButton.clicked.connect(self.go_to_batch)
        
        batchbutton_h = QHBoxLayout()
        batchbutton_h.addWidget(batchButton)
        batchbutton_h.addStretch(0)
        
        #Build main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.waveletPlot)
        main_layout.addWidget(ntb)
        main_layout.addWidget(table_widget)
        main_layout.addWidget(save_options_box)
        main_layout.addLayout(batchbutton_h)
        self.setLayout(main_layout)
        
        self.show()

    def read_power_thresh(self, text):
        
        try:
            power_thresh = float(text)
        except ValueError:
            print('except')
            self.e = Error('Enter positive number (or 0) for Wavelet power threshold!','Value Error')
            return
        
        if power_thresh < 0:
            print('<0')
            self.e = Error('Enter positive number (or 0) for Wavelet power threshold!','Value Error')
            return
        print('read power thresh', power_thresh)
        self.power_thresh = power_thresh

    def do_maxRidge_detection(self):
        #print(self.RidgeMSelection.currentText())
        #print(self.power_thresh_tb.text())
        

        ridge_y = wl.get_maxRidge(self.modulus)

        rdata = wl.mk_rdata(ridge_y,self.modulus,self.wlet,self.periods,self.tvec,Thresh = self.power_thresh, smoothing = True, win_len = 17)

        if not rdata:
            self.e = Error('No ridge found..check spectrum!','Ridge detection error')
            return
        
        self.rdata = rdata
       

        # plot the ridge
        ax_spec = self.waveletPlot.axs[1] # the spectrum

        # already has a plotted ridge
        if ax_spec.lines:
            ax_spec.lines.pop() # remove old one
            
        ax_spec.plot(rdata['time'],rdata['periods'],'o',color = 'crimson',alpha = 0.6,ms = 3)
        # refresh the canvas
        self.waveletPlot.draw()

    def do_annealRidge_detection(self):

        # todo add out-of-bounds parameter check
        per_ini = float(self.per_ini.text())
        T_ini = float(self.T_ini.text())
        Nsteps = int(self.Nsteps.text())
        max_jump = int(self.max_jump.text())
        curve_pen = float(self.curve_pen.text())

        # get modulus index of initial straight line ridge
        y0 = np.where(self.periods < per_ini)[0][-1]

        ridge_y, cost = wl.find_ridge_anneal(self.modulus,y0,T_ini,Nsteps,mx_jump = max_jump,curve_pen = curve_pen)

        rdata = wl.mk_rdata(ridge_y,self.modulus,self.wlet,self.periods,self.tvec,Thresh = self.power_thresh, smoothing = True, win_len = 17)

        if not rdata:
            self.e = Error('No ridge found..check spectrum!','Ridge detection error')
            return
        
        self.rdata = rdata
       
        
        # plot the ridge
        ax_spec = self.waveletPlot.axs[1] # the spectrum

        # already has a plotted ridge
        if ax_spec.lines:
            ax_spec.lines.pop() # remove old one

        ax_spec.plot(rdata['time'],rdata['periods'],'o',color = 'crimson',alpha = 0.6,ms = 3)
        # refresh the canvas
        self.waveletPlot.draw()
    
    
        
    def save_out (self):
        dialog = QFileDialog()
        options = QFileDialog.Options()
        #options = QFileDialog.DontUseNativeDialog
        #file_name, _ = dialog.getSaveFileName(self,"Save as","","All Files (*);;Text Files (*.txt);; Image Files (*.png)", options=options)
        file_name, _ = dialog.getSaveFileName(self,"Save as","","All Files (*);;Text Files (*.txt)", options=options)

        if not self.rdata:
            print('no ridge data!')
            self._ridgeError = Error('No Ridge detection performed! Can\'t save data.','Missing data')
            # no ridge detection performed -> show warning/error window
            return
        
        print('ridge data keys:', self.rdata.keys())
        df_out = pd.DataFrame()

        # add everything to data frame
        for key in self.rdata:
            df_out[key] = self.rdata[key]
            

        
        if file_name:
            print (_)
            print(file_name)

            # choose what to write out, reading out checkboxes
            obs_value =[]
            obs_mask = []
            for key in self.opts:
                obs_value.append(key)
                obs_mask.append(self.cb[key].isChecked())

            obs_list = np.array(obs_value)[np.array(obs_mask)]
            df_out[ obs_list ].to_csv(file_name, sep = '\t', index = False)
            
        else: 
            self._error = Error('No valid file name! Couldn\'t save data.','File name error')
            
    def go_to_batch (self):
        self.batch = Batch()
    
        

            
class SpectrumCanvas(FigureCanvas):
    def __init__(self, parent=None): #, width=6, height=3, dpi=100):
        self.fig, self.axs = plt.subplots(2,1,gridspec_kw = {'height_ratios':[1, 2.5]}, sharex = True)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        
    def plot_signal_modulus(self,tvec, signal,modulus,periods, v_max, time_unit):
        
        # self.fig.clf() # not needed as only once initialised?!
        sig_ax = self.axs[0]
        mod_ax = self.axs[1]

        # Plot Signal

        sig_ax.plot(tvec, signal, color = 'black', lw = 1.5, alpha = 0.7)
        sig_ax.set_ylabel('signal [a.u.]')
        sig_ax.ticklabel_format(style='sci',axis='y',scilimits=(0,0))
        # Plot Wavelet Power Spectrum
        
        # aspect = len(tvec)/len(periods)
        im = mod_ax.imshow(modulus[::-1], cmap = 'viridis', vmax = v_max,extent = (tvec[0],tvec[-1],periods[0],periods[-1]),aspect = 'auto')
        mod_ax.set_ylim( (periods[0],periods[-1]) )
        mod_ax.set_xlim( (tvec[0],tvec[-1]) )
        mod_ax.set_xlabel('time ' + time_unit)

        min_power = modulus.min()
        cb_ticks = [np.ceil(min_power),v_max]
        cb = self.fig.colorbar(im,ax = mod_ax,orientation='horizontal',fraction = 0.08,shrink = .6, pad = 0.25, ticks = cb_ticks)
        #cb.set_label('$|\mathcal{W}_{\Psi}(t,T)|^2$',rotation = '0',labelpad = 5,fontsize = 15)
        cb.set_label('Wavelet power',rotation = '0',labelpad = -5,fontsize = 10)

        mod_ax.set_xlabel('Time [' + time_unit + ']')
        mod_ax.set_ylabel('Period [' + time_unit + ']')
        plt.subplots_adjust(bottom = 0.11, right=0.95,left = 0.13,top = 0.95)
        self.fig.tight_layout()
        
    def save (self, signal_id):
        self.fig.savefig(signal_id)
        
        




class SynthViewer (DataViewer):
    def __init__(self):
        super().__init__()
        self.default_para_dic = {'T' : 900, 'amp' : 6, 'per' : 70, 'sigma' : 2, 'slope' : -10.}
        self.gen_func = synth_signal1
        self.raw_data= pd.DataFrame()
        self.series_ids = []
        self.titel = 'SynthViewer'
        self.count = 1
        
        
        
    def data_input(self):
        print ('SynthViewer data_input called')
        self.parameter = NumericParameterDialog(self.default_para_dic) #table needs to be QWidget
        pdic = self.parameter.read()
        
        addButton=QPushButton('Add signal', self)
        addButton.clicked.connect(self.add_button)
        
        self.table = QGroupBox('Test')
        data_layout = QVBoxLayout()
        data_layout.addWidget(self.parameter)
        data_layout.addWidget(addButton)
        self.table.setLayout(data_layout)
        
        # Button to save synthetic signal
    def add_button (self):
        pdic = self.parameter.read()
        tvec, signal = self.gen_func( **pdic)
        self.raw_data[str(self.count)+'_SynSig_{}'.format(pdic)] = signal
        self.series_ids.append(str(self.count) +'_SynSig_{}'.format(pdic))
        self.count +=1
        self.fillSignalBox()
        print ('SynView called fillSignalBox')
        
        #self.series_ids.append('synthetic siganl1_{}'.format(pdic))
        
        
class Batch (QWidget):
    def __init__(self):
        super().__init__()
        self.raw_data = pd.DataFrame()
        self.cb = {}
        
    def initUI (self):
        self.setWindowTitle('Batch processing')
        self.setGeometry(310,310,600,600)
        
        main_layout_v = QVBoxLayout()
        #Loading data
        self.data_path = QTextEdit()
        self.data_path.append(os.getcwd())
        loadButton = QPushButton('Browse', self)
        self.dt_edit= QLineEdit()
        unitBox = QComboBox(self)
        unitBox.addItem('min')
        unitBox.addItem('s')
        unitBox.activated[str].connect(self.set_time_unit)
        
        
        loadButton.clicked.connect(self.load)
        
        button_layout_h = QHBoxLayout()
        button_layout_h.addWidget(self.data_path)
        #button_layout_h.addStretch(0)
        button_layout_h.addWidget(loadButton)
        #button_layout_h.addStretch(0)
        
        load_para_layout= QFormLayout() 
        load_para_layout.addRow('Sampling intervall', self.dt_edit)
        load_para_layout.addRow('in:', unitBox)
        
        load_layout= QVBoxLayout()
        load_layout.addLayout(button_layout_h)
        load_layout.addLayout(load_para_layout)
        

        
        
        
        #Analysis options
        
        
        pre_label = QLabel('Pre-processing:', self)
        self.cb_detrend = QCheckBox('Use detrended signal', self)
        #cb_detrend.stateChanged.connect(self.detrended)
        self.cut_off = QLineEdit()
        #Add inactivation of cut_off if cb not toggled
        pre_pro_layout = QFormLayout()
        pre_pro_layout.addRow(pre_label)
        pre_pro_layout.addRow(self.cb_detrend)
        pre_pro_layout.addRow(QLabel('Cut-off period'),self.cut_off)
        
        
        
        
        
         ## for wavlet params, button, etc.
         
        wav_label = QLabel('Parameters for wavelet analysis:', self)
        self.T_min = QLineEdit()
        self.step_num = QLineEdit()
        self.step_num.insert('100')
        self.T_max = QLineEdit()
        self.v_max = QLineEdit()
        self.v_max.insert(str(20))
        
        T_min_lab = QLabel('Smallest period')
        step_lab = QLabel('Number of periods')
        T_max_lab = QLabel('Highest  period')
        v_max_lab = QLabel('Expected maximal power')
        
        T_min_lab.setWordWrap(True)
        step_lab.setWordWrap(True)
        T_max_lab.setWordWrap(True)
        v_max_lab.setWordWrap(True)
        
        
        ## Add Wavelet analyzer options to layout
        wav_layout = QFormLayout()
        wav_layout.addRow(wav_label)
        wav_layout.addRow(T_min_lab,self.T_min)
        wav_layout.addRow(step_lab, self.step_num)
        wav_layout.addRow(T_max_lab,self.T_max)
        wav_layout.addRow(v_max_lab, self.v_max)
        #wav_layout.addRow(wlet_button_layout_h)
        
        
        
        
        ana_layout = QHBoxLayout()
        ana_layout.addLayout(pre_pro_layout)
        ana_layout.addLayout(wav_layout)
        
        
        ana_box = QGroupBox('Analysis parameters')
        ana_box.setLayout(ana_layout)
        
        #Saving
        saveButton = QPushButton('Analyze and Save', self)
        saveButton.clicked.connect(self.ana)
        
        cb_layout= QFormLayout()
        
        _v = QVBoxLayout()
        
        
        self.opts =['Wavlet analysis', 'Fourier analysis', 'Save wavlet spectrum plot', 'Save Fourier plot']
        for key in self.opts:
            self.cb[key] = QCheckBox(str(key), self)
            _v.addWidget(self.cb[key])
        
        cb_layout.addRow(_v)
        
        
        savebutton_h = QHBoxLayout()
        savebutton_h.addStretch(0)
        savebutton_h.addWidget(saveButton)
        
        cb_layout.addRow(savebutton_h)
        
        
        save_options_box = QGroupBox('Save and Analysis options')
        
        save_options_box.setLayout(cb_layout)
        
        
        
        
        main_layout_v.addLayout(load_layout)
        main_layout_v.addWidget(ana_box)
        main_layout_v.addWidget(save_options_box)
        
        
        self.setLayout(main_layout_v)
        self.show()
        
        
    def load(self):
        
        file_name = QFileDialog.getOpenFileNames(self, 'Open File')
        #file_name = ['synth_signals2c.xlsx']
        ###If correct file path/type is supplied data are read in and emitted
        #try: 
        if DEBUG:

            print (len(file_name))
            for i in range(len(file_name)):
                print (i)
                print (file_name[0][i])

        try:
            self.data_path.clear()
            for i in range(len(file_name)):
                self.raw_data = pd.read_excel(file_name[0][i], header=0)
                self.data_path.append(file_name[0][i])
       
        except:

            self.noFile = Error('No valid path or file supplied!', 'No File')

            return False
        
        
        return True
        
        
        
        
        
        
        
        #def __init__(self, signal, dt, T_min, T_max, position, signal_id, step_num, v_max, time_unit):
        #super().__init__()
        #self.signal_id = signal_id
        #self.signal = signal
        #self.v_max = v_max
        #self.time_unit = time_unit
        #self.cb= {}


        # no ridge yet
        #self.rdata = None
        #self._has_ridge = False # no plotted ridge
    def set_time_unit(self,text):
        self.time_unit = text

    def read_params (self):
        
        self.T_min_value = int(self.T_min.text())
        self.step_num_value = int(self.step_num.text())
        self.T_max_value =int(self.T_max.text())
        self.v_max_value = int(self.v_max.text())
        self.dt= int(self.dt_edit.text())
        
        
        
        
    def ana(self):
        files = self.data_path.toPlainText()
        file_list = [s.strip() for s in files.splitlines()]

        for i in file_list:
            print (i)
            raw_data = pd.read_excel(i, header=0)
            for xy in raw_data.keys():
                print (xy)
                raw_signal= raw_data[xy].values
                
                self.read_params()
                T_min = self.T_min_value
                step_num = self.step_num_value
                T_max = self.T_max_value
                v_max = self.v_max_value
                dt = self.dt
                T_c = int(self.cut_off.text())
                
                self.detrended = bool(self.cb_detrend.checkState() )
                if self.detrended:
                    trend = wl.sinc_smooth(raw_signal = raw_signal,T_c = T_c, dt = self.dt)
                    signal = raw_signal-trend
                else:
                    signal = raw_signal
                
                self.periods=np.linspace(T_min, T_max, step_num)
                self.tvec = np.arange(0,len(signal)*dt,dt)
                
                #=============Compute Spectrum============================
                self.modulus, self.wlet = wl.compute_spectrum(signal, dt, self.periods)
                #========================================================
                
                
                # ToDo be modified save plot without spectrum canvas
                #-------------plot the wavelet power spectrum---------------------------
                #self.waveletPlot.plot_signal_modulus(self.tvec, self.signal,self.modulus,self.periods, v_max, self.time_unit)
                #-----------------------------------------------------------------------
                
                
            
       
                self.df_out = pd.DataFrame()

                # add everything to data frame
                for key in self.rdata:
                    self.df_out[xy+key] = self.rdata[key]
            

                
                
                
                
            self.save_out()

    def save_out (self):
        #dialog = QFileDialog()
        #options = QFileDialog.Options()
        
        #file_name, _ = dialog.getSaveFileName(self,"Save as","","All Files (*);;Text Files (*.txt)", options=options)

        
        
        #if file_name:
        #    print (_)
        #    print(file_name)

            # choose what to write out, reading out checkboxes
            obs_value =[]
            obs_mask = []
            for key in self.opts:
                obs_value.append(key)
                obs_mask.append(self.cb[key].isChecked())

            obs_list = np.array(obs_value)[np.array(obs_mask)]
            df_out[ obs_list ].to_csv(test.csv, sep = '\t', index = False)
            
            
        
            






class Detrender2(QWidget):
    dataRequest =pyqtSignal('PyQt_PyObject')
    def __init__(self):
        super().__init__()
        self.raw_data= pd.DataFrame()
        self._connected=False
        
        #self.initUI()
    def initUI(self):
        self.plotWindow = TimeSeriesWindow()
        print(self.plotWindow.sizeHint())
        self.plotWindow_signal = TimeSeriesWindow()
        print (type(self.plotWindow))
        
        self.setWindowTitle('Detrender')
        self.setGeometry(310,310,450,900)
        
        main_layout_v =QVBoxLayout()
        button_layout_h = QHBoxLayout()
        self.dialog = NumericParameterDialog({'T_c': 100})
        
        
        dataLable = QLabel('Select signal', self)
        self.dataChoice = QLabel('',self)

        self.comboBox = QComboBox(self)
        self.comboBox.addItem('None')
        if self._connected:
            for i in self.series_ids:
                print (i)
                self.comboBox.addItem(i)
        
        dataChoic_layout_h =QHBoxLayout()
        dataChoic_layout_h.addWidget(dataLable)
        dataChoic_layout_h.addWidget(self.comboBox)

        main_layout_v.addWidget(self.plotWindow)
        print (type(self.plotWindow))
        main_layout_v.addWidget(self.plotWindow_signal)
        main_layout_v.addWidget(self.dialog)
        main_layout_v.addLayout(dataChoic_layout_h)

        plotButton = QPushButton('Detrend signal', self)
        plotButton.clicked.connect(self.doPlot)
        button_layout_h.addStretch(0)
        button_layout_h.addWidget(plotButton)
        main_layout_v.addLayout(button_layout_h)
        self.setLayout(main_layout_v)
        self.show()
        
        
        self.comboBox.activated[str].connect(self.data_request)
        
    def data_request(self, text):
        self.id = text
        self.dataRequest.emit(text)
        print ('data requested')

    def make_connection(self, datahandler_object):
        datahandler_object.signalIds.connect(self.get_signal_ids)
        #datahandler_object.dataSignal.connect(self.get_data)
        self._connected= True
        
    @pyqtSlot('PyQt_PyObject')
    def get_signal_ids(self, signal_ids):

        self.series_ids = signal_ids[0]
        self.signal_dic= signal_ids[1]
        self.tvec_dic = signal_ids[2]
        
        for id in self.series_ids:
            self.raw_data[id+'time'] = self.tvec_dic[id]
            self.raw_data[id] = self.signal_dic[id]
        
        
    

    
    def doPlot(self):

        pdic = self.dialog.read()
        if 1:
            #print('Plotting {}'.format(self.dataChoice.text()))
            #dt =self.tvec_dic[self.dataChoice.text()][1]-self.tvec_dic[self.dataChoice.text()][0]
            trend = wl.sinc_smooth(raw_signal = self.raw_data[self.id].values,T_c = pdic['T_c'], dt = 1)
            print(len(self.raw_data[self.id].values), len(trend))
            print(self.raw_data[self.id].values[:-20])
            print(trend[:-20])

            detrended_signal= self.raw_data[self.id].values - trend
            #plot trend and signal
            self.plotWindow.update(self.raw_data[self.id+'time'].values, self.raw_data[self.id].values)
            self.plotWindow.update(self.raw_data[self.id+'time'].values, trend, clear = False)
            print (type(self.plotWindow))

            #plot dtrended signal
            self.plotWindow_signal.update(self.raw_data[self.id+'time'].values, detrended_signal)
        #except:
        #    self.noDataSelected = Error('Please selcte one dataseries from the drop down menu!','Missing data')

class SyntheticSignalGenerator(QWidget):
    ''' 
    tvec: array containing the time vector
    signal: array containing the signal or 'synthetic' if synthetic signal shall be used
    default_para_dic: dictonary containing default parameters for synthetic signal creation


    '''
    # Added a signal, that emits signal name, tvec and signal values
    timeSignal = pyqtSignal('PyQt_PyObject')  #########################

    def __init__(self,gen_func, default_para_dic): 
        super().__init__()
        self.default_para_dic = default_para_dic
        self.gen_func = gen_func

        if DEBUG:
            print ('default para{}'.format(self.default_para_dic))

        #self.initUI()
           
        
        

    def initUI(self):

        self.plotWindow = TimeSeriesCanvas('Synthetic Signal')

        self.setWindowTitle('Synthetic Signal Generator')
        self.setGeometry(300,300,450,550) #???

        main_layout_v = QVBoxLayout()
        button_layout_h = QHBoxLayout()

        # add/create dialog
        self.dialog = NumericParameterDialog(self.default_para_dic)

        main_layout_v.addWidget(self.plotWindow)
        main_layout_v.addWidget(self.dialog)

        # Create a plot button in the window                                                                     
        plotButton = QPushButton('Save / Plot signal', self)
        # connect button to function save_on_click                                                          
        plotButton.clicked.connect(self.doPlot)
        
        button_layout_h.addStretch(1)
        button_layout_h.addWidget(plotButton)
        
        main_layout_v.addLayout(button_layout_h)
        
        # TODO button to reset to default parameters        

        
        self.setLayout(main_layout_v)
        if DEBUG:
            print ('Showing Syn Plot')
        self.show()
        if DEBUG:
            print ('Closing Syn Plot')

    def doPlot(self):
        if DEBUG:
            if not self.gen_func:
                raise ValueError('No gen_func supplied')
        pdic = self.dialog.read()
        print('Plotting with {}'.format(pdic))
        tvec, signal = self.gen_func( **pdic)
        
        self.timeSignal.emit(['synthetic siganl1_{}'.format(pdic),signal])
        self.plotWindow.mpl_update(tvec, signal)

class NumericParameterDialog(QDialog):

    def __init__(self,default_para_dic):
        super().__init__()
        self.default_para_dic = default_para_dic
        self.input_fields ={} #holds para_names:textbox
        self.para_dic = self.default_para_dic.copy()

        self.createFormGroupBox()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        
        self.setLayout(mainLayout)
        #self.show()
        

    def createFormGroupBox(self):

        self.formGroupBox = QGroupBox('Parameters')
        layout = QFormLayout()
        for par_name, value in self.default_para_dic.items():
            textbox = QLineEdit()
            textbox.insert(str(value))
            layout.addRow(QLabel(par_name),textbox)
            self.input_fields[par_name] = textbox
        
        self.formGroupBox.setLayout(layout)
    
    def read(self):

        for pname in self.para_dic.keys():

            textbox = self.input_fields[pname]
            textboxString = textbox.text()

            self.para_dic[pname] = float(textboxString)

        return self.para_dic
        
        

class TimeSeriesCanvas(FigureCanvas):
    def __init__(self, parent=None, width=4, height=3, dpi=100):
        fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        #self.axes.set_xlabel('time')

        #if not signal:
        #    raise ValueError('No time or signal supplied') ###gen_func

        FigureCanvas.__init__(self, fig)
        #self.setParent(parent)
        
        print ('Time Series Size', FigureCanvas.sizeHint(self))
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    def mpl_update(self, tvec, signal, clear = True):

        if DEBUG:
            print('mpl update called with {}, {}'.format(tvec[:10], signal[:10]))

        if clear:
            self.axes.cla()
        self.axes.plot(tvec, signal)
        self.draw()
        self.show()

class TimeSeriesViewCanvas(FigureCanvas):
    def __init__(self, parent=None, width=4, height=3, dpi=100):
        self.fig1 = Figure(figsize=(width,height), dpi=dpi)
        self.fig1.clf()
        #self.axes.set_xlabel('time')

        #if not signal:
        #    raise ValueError('No time or signal supplied') ###gen_func

        FigureCanvas.__init__(self, self.fig1)
        self.setParent(parent)
        
        print ('Time Series Size', FigureCanvas.sizeHint(self))
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    def mpl_update(self, tvec, signal,trend, plot_raw, plot_trend, plot_detrended,time_unit, clear = True):
        self.fig1.clf()
        ax1 = self.fig1.add_subplot(111)
        print (plot_raw, plot_trend, plot_detrended)
        if DEBUG:
            print('mpl update called with {}, {}'.format(tvec[:10], signal[:10]))

        if clear:
            ax1.cla()
        if plot_raw:
            ax1.plot(tvec,signal,lw = 1.5, color = 'royalblue',alpha = 0.8)
        if plot_trend:
            ax1.plot(tvec,trend,color = 'orange',lw = 1.5) 
        if plot_detrended:
            ax2 = ax1.twinx()
            ax2.plot(tvec, signal - trend,'-', color = 'k',lw = 1.5, alpha = 0.6) 
            ax2.set_ylabel('trend')
            ax2.ticklabel_format(style='sci',axis='y',scilimits=(0,0))
    
        ax1.set_xlabel('Time [' + time_unit + ']')
        ax1.set_ylabel(r'signal') 
        ax1.ticklabel_format(style='sci',axis='y',scilimits=(0,0))

        self.fig1.subplots_adjust(bottom = 0.15,left = 0.15, right = 0.85)
        self.draw()
        self.show()
    

        

# test case for data generating function, standard synthetic signal
def synth_signal1(T, amp, per, sigma, slope):  
    
    tvec = np.arange(T)
    trend = slope*tvec**2/tvec[-1]**2*amp
    noise = np.random.normal(0,sigma, len(tvec))
    sin = amp*np.sin(2*np.pi/per*tvec)+noise+trend

    return tvec, sin
        
    

class Error(QWidget):
    def __init__(self, message,title):
        super().__init__()
        self.message = message
        self.title = title
        self.initUI()
       
    def initUI(self):
        error = QLabel(self.message)
        self.setGeometry(300,300,220,100)
        self.setWindowTitle(self.title)
        okButton = QPushButton('OK', self)
        okButton.clicked.connect(self.close)
        main_layout_v = QVBoxLayout()
        main_layout_v.addWidget(error)
        main_layout_v.addWidget(okButton)
        self.setLayout(main_layout_v)
        self.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    pdic = {'T' : 900, 'amp' : 6, 'per' : 70, 'sigma' : 2, 'slope' : -10.}



    #dt = 1
    #T_c = 100
    tvec, raw_signal = synth_signal1(**pdic)

    #pDialog = SyntheticSignalGenerator(synth_signal1, pdic)
    #pDialog2 = Detrender()
    #pDialog2.make_connection(pDialog)
    #detrDialog = InterActiveTimeSeriesPlotter(tvec, detrend, pdic)
    
    #open_file = DataLoader()
    #dh = DataHandler()
    #dh.make_connection(open_file)
    
    #testWavelet = WaveletAnalyzer()
    #test = Detrender()
    window = MainWindow()
    # window.load()
    sys.exit(app.exec_())
        