#!/usr/bin/env python

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import qimage2ndarray
import qdarkstyle

import cv2
import sys
import numpy as np
from pypylon import pylon

import platform
import ctypes
import itertools
import string

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from result import Result, combine_results
from config import region_dict, read_config, write_config
from roi_selector import ROISelector

def set_qdarkstyle_plot_theme():
    plt.rcParams['axes.facecolor'] = '#19232D'
    plt.rcParams['savefig.facecolor'] = '#19232D'
    plt.rcParams['figure.facecolor'] = '#19232D'
    plt.rcParams['axes.edgecolor'] = '#FFFFFF'
    plt.rcParams['axes.labelcolor'] = '#FFFFFF'
    plt.rcParams['xtick.color'] = '#FFFFFF'
    plt.rcParams['ytick.color'] = '#FFFFFF'
    plt.rcParams['axes.titlecolor'] = '#FFFFFF'
    plt.rcParams['text.color'] = '#FFFFFF'
    plt.rcParams['axes.grid'] = False
    plt.rcParams['grid.linestyle'] = 'dashed'


class MainApp(QWidget):

    def __init__(self):
        super().__init__()

        # Read initial config
        self.initial_config: dict = read_config()

        self.video_size = QSize(160, 768)
        self.camera_listbox_size = QSize(120, 400)
        self.canvas = FigureCanvas(plt.Figure(figsize=(5,2)))
        self.ax = self.canvas.figure.subplots()
        self.setWindowTitle('ENCIRC')
        self.setWindowIcon(QIcon('i3dr_logo.png'))
        self.setup_ui()

        self.camera = None
        self.inspection_part = Result.NO_BOTTLE
        self.inspection_ROI = Result.NO_BOTTLE


    def setup_ui(self):
        """Initialize widgets.
        """  
        self.image_labelL = QLabel()
        self.image_labelL.setFixedSize(self.video_size)
        
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, 10)
        self.slider.setValue(0)
        self.slider.setGeometry(0, 0, 120, 80)
        self.slider.valueChanged[int].connect(self.changeValue)
        
        self.exposureValue = QLabel(self)
        self.exposureValue.setText("0")
        
        self.save_msg = QLabel(self)
        
        self.exposureText = QLabel(self)
        self.exposureText.setText("Exposure")
        
        self.cameraListBox = QListWidget()
        self.cameraListBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow expansion
        
        self.getCameraList()
        self.reset_graphdata()
        
        self.cameraRefreshBtn = QPushButton("Refresh List")
        self.cameraRefreshBtn.clicked.connect(self.getCameraList)
        self.cameraConnectBtn = QPushButton("Connect")
        self.cameraConnectBtn.setStyleSheet("background-color: green")
        self.cameraConnectBtn.setCheckable(True)
        self.cameraConnectBtn.clicked.connect(self.control_camera)
        self.cameraStatusText = QLabel(self)
        self.cameraStatusText.setText("No camera connected")

        self.clearBtn = QPushButton("Clear Graph")
        self.clearBtn.setStyleSheet("background-color: green")
        self.clearBtn.clicked.connect(self.clear_graph)

        self.bottlePartBtn = QPushButton(" ")
        self.bottlePartBtn.setFixedSize(QSize(100, 100))
        self.bottleAllBtn = QPushButton(" ")
        self.bottleAllBtn.setFixedSize(QSize(100, 100))
        self.bottlePartText = QLabel(self)
        self.bottlePartText.setText("Part of Bottle")
        self.bottleAllText = QLabel(self)
        self.bottleAllText.setText("Whole Bottle")
        self.recommendationText = QLabel(self)
        self.recommendationText.setText("Recommendation: ")
        self.recommendedText = QLabel(self)

        self.main_layout = QHBoxLayout()
        self.image_display = QHBoxLayout()
        self.image_display.addWidget(self.image_labelL)
        self.image_display.addWidget(self.canvas)
        
        self.devicelist_layout = QVBoxLayout()
        self.devicelist_layout.addWidget(self.cameraRefreshBtn)
        self.devicelist_layout.addWidget(self.cameraConnectBtn)
        self.devicelist_layout.addWidget(self.cameraListBox, stretch=1)  # Add stretch to cameraListBox
        
        self.exposure_display = QHBoxLayout()
        self.exposure_display.addWidget(self.exposureText)
        self.exposure_display.addWidget(self.exposureValue)
        
        self.feature_layout = QVBoxLayout()
        self.feature_layout.addLayout(self.exposure_display)
        self.feature_layout.addWidget(self.slider)
        self.feature_layout.addWidget(self.clearBtn)
        
        self.devicelist_layout.addLayout(self.feature_layout)
        
        self.image_display_layout = QVBoxLayout()
        self.image_display_layout.addWidget(self.cameraStatusText)
        self.image_display_layout.addLayout(self.image_display)
        self.image_display_layout.addWidget(self.save_msg)

        self.inspect_layout = QVBoxLayout()
        self.part_layout = QHBoxLayout()
        self.part_layout.addWidget(self.bottlePartText)
        self.part_layout.addWidget(self.bottlePartBtn)
        self.inspect_layout.addLayout(self.part_layout)
        self.ROI_layout = QHBoxLayout()
        self.ROI_layout.addWidget(self.bottleAllText)
        self.ROI_layout.addWidget(self.bottleAllBtn)
        self.inspect_layout.addLayout(self.ROI_layout)
        self.recommendation_layout = QHBoxLayout()
        self.recommendation_layout.addWidget(self.recommendationText)
        self.recommendation_layout.addWidget(self.recommendedText)
        self.inspect_layout.addLayout(self.recommendation_layout)

        self.roi_selector = ROISelector()
        self.inspect_layout.addWidget(self.roi_selector)
        # Set default values using the values in self.config
        self.roi_selector.set_rois(self.initial_config["regions"])
        
        self.main_layout.addLayout(self.devicelist_layout, 1)
        self.main_layout.addLayout(self.image_display_layout, 4)
        self.main_layout.addLayout(self.inspect_layout, 1)

        self.setLayout(self.main_layout)

        
    def control_camera(self):
        if not self.device_list:
            self.cameraStatusText.setText("No devices to connect to.")
            return
        if self.cameraConnectBtn.isChecked():
            self.setup_camera()
            self.set_connect_button(connected=True)
        else:
            self.disconnect_camera()
            self.set_connect_button(connected=False)


    def set_connect_button(self, connected:bool):
        if connected:
            self.cameraConnectBtn.setText("Disconnect")
            self.cameraConnectBtn.setStyleSheet("background-color: red")
        else:
            self.cameraConnectBtn.setText("Connect")
            self.cameraConnectBtn.setStyleSheet("background-color: green")


    def setup_camera(self):
        """Initialize camera.
        """
        if self.camera is not None:
            self.cameraStatusText.setText("Camera already connected.")
            return
        device_info = self.device_connected
        camera_name = device_info.GetUserDefinedName()
        self.cameraStatusText.setText(camera_name+" Connected")
        
        # Create stereo camera device information from parameters
        self.camera = pylon.InstantCamera(self.tlFactory.CreateDevice(device_info))
        self.camera.Open()
        self.camera.StartGrabbing()
    
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_video_stream)
        self.timer.start(0)


    def display_video_stream(self):
        """Read frame from camera and repaint QLabel widget.
        """
        try:
            self.camera.ExposureTime.SetValue(self.slider.value()*5000+5000)      
            read_result = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            
            if read_result.GrabSucceeded():
                self.ax.cla()
                self.ax = self.insert_ax(self.ax)
                frame = read_result.Array

                if not read_result.IsValid:
                    self.cameraStatusText.setText("Failed to read from camera")

                frameROI = frame[400:800,:]

                # get ROI from the selector
                rois = self.roi_selector.get_rois()

                def get_sample(roi):
                    return frameROI[roi["y_low"]:roi["y_high"], roi["x_low"]:roi["x_high"]]

                # self.sample1 = frameROI[120:320,300:500]
                # self.sample2 = frameROI[120:320,500:850]
                # self.sample3 = frameROI[120:320,850:1200]
                # self.sample4 = frameROI[120:320,1200:1600]

                self.sample1 = get_sample(rois[0])
                self.sample2 = get_sample(rois[1])
                self.sample3 = get_sample(rois[2])
                self.sample4 = get_sample(rois[3])

                frameROI_display = cv2.resize(frameROI,(768,160))
                frame_display = np.rot90(frameROI_display,1)

                image = qimage2ndarray.array2qimage(frame_display)  #SOLUTION FOR MEMORY LEAK
                self.image_labelL.setPixmap(QPixmap.fromImage(image))

                self.s1, dataSum1 = self.shiftdata(self.s1, self.sample1)
                self.s2, dataSum2 = self.shiftdata(self.s2, self.sample2)
                self.s3, dataSum3 = self.shiftdata(self.s3, self.sample3)
                self.s4, dataSum4 = self.shiftdata(self.s4, self.sample4)

                line1, = self.ax.plot(self.t, self.s1, color='red', label="Region 1")
                line2, = self.ax.plot(self.t, self.s2, color='green', label="Region 2")
                line3, = self.ax.plot(self.t, self.s3, color='blue', label="Region 3")
                line4, = self.ax.plot(self.t, self.s4, color='yellow', label="Region 4")
                self.ax.legend(handles=[line1, line2, line3, line4], loc='upper right').set_visible(True)

                self.canvas.draw()
                self.part_inspection(np.max([dataSum1,dataSum2,dataSum3,dataSum4]))
                self.ROI_inspection(np.sum(frameROI))
                inspection_result = combine_results([self.inspection_part, self.inspection_ROI])
                self.recommendedText.setText(inspection_result.name.replace("_"," ").title())
            read_result.Release()

        except pylon.RuntimeException as e:
            # Disconnected while running
            self.timer.stop()
            self.camera = None
            self.image_labelL.clear()
            self.cameraStatusText.setText("No camera connected")
            self.getCameraList()
            self.set_connect_button(connected=False)


    def insert_ax(self, ax):
        # self.ax.set_ylim([0,260])
        ax.set_xlim([0,500])
        ax.set(xlabel='time (s)', ylabel='Intensity',
            title='Intensity Variation')
        return ax


    def clear_graph(self):
        self.reset_graphdata()
        self.canvas.draw()


    def disconnect_camera(self):
        if self.camera is None:
            print("No camera connected.")
            return
        if self.camera.IsCameraDeviceRemoved():
            print("Camera already removed.")
            self.camera = None
            return
        # self.phaseCam.stopCapture()
        self.camera.Close()
        self.timer.stop()
        self.image_labelL.clear()
        self.cameraStatusText.setText("No camera connected")
        self.camera = None
            

    def getCameraList(self):
        self.cameraListBox.clear()
        self.tlFactory = pylon.TlFactory.GetInstance()
        self.device_list = self.tlFactory.EnumerateDevices()
        for device_info in self.device_list:
            self.cameraListBox.setCurrentRow(0)
            camera_name = device_info.GetUserDefinedName()
            # self.cameraList.addItem(camera_name)
            # self.cameraList.activated.connect(self.itemClicked_event)
            self.cameraListBox.addItem(camera_name)
            self.cameraListBox.currentRowChanged.connect(self.itemClicked_event)
        # Select the first camera in the list if possible
        if self.cameraListBox.count() > 0:
            self.cameraListBox.setCurrentRow(0)

            
    def get_available_drives(self):
        if 'Windows' not in platform.system():
            return []
        drive_bitmask = ctypes.cdll.kernel32.GetLogicalDrives()
        return list(itertools.compress(string.ascii_uppercase,
                map(lambda x:ord(x) - ord('0'), bin(drive_bitmask)[:1:-1])))


    def printtime(self, now):
        y = str(now.year)
        month = now.month
        m = self.addZeroDigit(month)

        day = now.day
        d = self.addZeroDigit(day)

        hour = now.hour
        h = self.addZeroDigit(hour)

        min = now.minute
        mn = self.addZeroDigit(min)

        sec = now.second
        s = self.addZeroDigit(sec)
        return y,m,d,h,mn,s
    

    def addZeroDigit(self, number):
        if number < 10:
            result = '0'+str(number)
        else:
            result = str(number) 
        return result
    

    def shiftdata(self,data_array,data):
        data_array = np.roll(data_array,1)
        data_sum = np.sum(data)
        data_array[0] = data_sum
        return data_array, data_sum
    

    def reset_graphdata(self):
        self.ax.cla()
        # self.ax.set_ylim([0,260])
        self.ax = self.insert_ax(self.ax)
        self.s1 = np.zeros(500)
        self.s2 = np.zeros(500)
        self.s3 = np.zeros(500)
        self.s4 = np.zeros(500)
        self.t = np.arange(500)


    def part_inspection(self, sumValue):
        if sumValue < 100000:
            self.bottlePartBtn.setStyleSheet("background-color: green")
            self.inspection_part = Result.ACCEPT
        elif 100001<sumValue<200000:
            self.bottlePartBtn.setStyleSheet("background-color: orange")
            self.inspection_part = Result.INSPECT
        elif sumValue > 200001:
            self.bottlePartBtn.setStyleSheet("background-color: red")
            self.inspection_part = Result.REJECT


    def ROI_inspection(self, sumValue):
        if sumValue < 500000:
            self.bottleAllBtn.setStyleSheet("background-color: green")
            self.inspection_ROI = Result.ACCEPT
        elif 500001<sumValue<700000:
            self.bottleAllBtn.setStyleSheet("background-color: orange")
            self.inspection_ROI = Result.INSPECT
        elif sumValue > 700001:
            self.bottleAllBtn.setStyleSheet("background-color: red")
            self.inspection_ROI = Result.REJECT
    

    def changeValue(self, value):
        self.exposureValue.setText(str(value))
        #change3: move label position up(20 to 30)
        self.exposureValue.move(self.slider.x() + value, self.slider.y() - 30)
        

    def itemClicked_event(self,index):
        # print(index)
        self.device_connected = self.device_list[index]

    def get_current_config(self) -> dict:
        config_dict = {}
        current_rois = self.roi_selector.get_rois()
        config_dict["regions"] = current_rois
        return config_dict

    def check_config_dialog(self):
        """
        Checks if the current configuration is different from the initial configuration.
        If it is, pops up a dialog asking if the user wants to save the changes.
        If the user chooses to save the changes, writes the current configuration to the config file.
        """
        current_config = self.get_current_config()
        if current_config == self.initial_config:
            return
        qm = QMessageBox()
        ret = qm.question(self, "Save New Configuration?", "The configuration has been changed. Do you want to save the changes?", qm.Yes | qm.No)
        if ret == qm.Yes:
            print("Saving config")
            write_config(current_config)

    def closeEvent(self, event):
        self.check_config_dialog()
        try:
            self.disconnect_camera()
            print("Camera disconnected.")
        except:
            pass
        print("Closing...")
        event.accept()


if __name__ == "__main__":
    set_qdarkstyle_plot_theme()
    app = QApplication(sys.argv)
    win = MainApp()
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    win.show()
    sys.exit(app.exec_())