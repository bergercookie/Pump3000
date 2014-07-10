#!/usr/bin/env python

"""

Python Implementation for the Cavro XP3000 GUI.

The GUI is designed with regards to the MVC (Model View Controller)
Ui architectural pattern. Inside this module the View - Controller behaviors
are implemented while the Model behavior is implemented in the imported module:
    pump_model.py

"""

# Sat May 24 10:57:50 EEST 2014, nickkouk

# proper division for python 2.7
from __future__ import division

# Usual importing stuff
from PySide.QtGui import *
from PySide.QtCore import *

# Module imports
import sys
import python_gui # Designer outcome
import python_settings
import serial
import time

__appname__ = "XP3000 Interface"

# pump_oriented settings
addr = '/1'
term = 'R\r'

class MainWindow(QMainWindow, python_gui.Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle(__appname__)

        # Connection settings
        self.port_name = 'loop://'
        self.baud = 9600
        self.byte_size = 8
        self.par = 'N' 
        self.stopb = 1
        self.timeout_time = 0 

        self.addr = addr
        self.term = term
        self.ser = serial.serial_for_url(self.port_name, timeout = self.timeout_time)
        #self.ser.open()

        # Threading for non-blocking behavior
        self.updateThread = updateThread(self)
        self.updateThread.start()


        # TODO Pump settings
        self.plung_pos = 0
        self.valve_pos = 'O'
        self.plung_speed = 1
        self.syr_size = 50 # The size of the syringe is 50 micro litre
        self.steps_tot = 3000
        self.valve_pos = '0'

        # Connecting signals to functions
        self.connect(self.output_btn, SIGNAL("clicked()"), self.output_fun)
        self.connect(self.input_btn, SIGNAL("clicked()"), self.input_fun)
        self.connect(self.bypass_btn, SIGNAL("clicked()"), self.bypass_fun)
        self.connect(self.speed_slider, SIGNAL("sliderReleased()"), self.setSpeed)
        self.connect(self.speed_spinbox, SIGNAL("editingFinished()"), self.setSpeed)
        self.connect(self.volume_prompt, SIGNAL("returnPressed()"), self.volume_command)
        self.connect(self.actionReports, SIGNAL("triggered()"), self.reportsThread_start)


        # Action Signals - Slots
        self.connect(self.actionNew_Device, SIGNAL("triggered()"), self.newDev)
        #self.connect(self.actionReports, SIGNAL("triggered()"), self.reports_dialog)
        self.status = {}
    
    def reportsThread_start(self):
        self.reportsThread = reportsThread(self.status)
        self.reportsThread.start()

        reports = Reports_class()
        reports.exec_()

    def close_window(self):
        pass

    def open_btn(self):
        pass

    def save_btn(self):
        pass

    def newDev(self):
        #TODO have to fix the device search filter
        QMessageBox.information(self, "New Pump Configuration", "Select the device name")
        
        # Platform specific
        if sys.platform[:3] == 'win':
            dir = '.' # Windows device path?!
        if sys.platform[:3] == 'dar':
            dir = '~/src/python' # Should include this for compatibility issues
        else:
            dir = '.'

        fileObj = QFileDialog.getOpenFileName(self, "New Pump Configuration", dir=dir)
        if fileObj[0]:
            self.ser.port_name = fileObj[0]

    def update_values(self):
        """
        The purpose of this function is to constantly update the settings 
        related to the pump, should be run by a thread periodically
        """
        # keep the gathering info
        status = {"abs_pos": '', "top_vel": '', "cutoff": '',\
                "act_pos": '', "start": '', "backlash": '', "fluid": '',\
                "buffer": '', "version": '', "checksum": ''}

        # reading info mechanism
        self.ser.write(self.addr + '?' + self.term)
        status["abs_pos"] = self.ser.read(8)
        self.ser.write(self.addr + '?1' + self.term)
        status["start"] = self.ser.read(8)
        self.ser.write(self.addr + '?2' + self.term)
        status["top_vel"] = self.ser.read(8)
        self.ser.write(self.addr + '?3' + self.term)
        status["cutoff"] = self.ser.read(8)
        self.ser.write(self.addr + '?4' + self.term)
        status["act_pos"] = self.ser.read(8)
        self.ser.write(self.addr + '?12' + self.term)
        status["backlash"] = self.ser.read(8)
        self.ser.write(self.addr + '?22' + self.term)
        status["fluid"] = self.ser.read(8)
        self.ser.write(self.addr + 'F' + self.term)
        status["buffer"] = self.ser.read(8)
        self.ser.write(self.addr + '&' + self.term)
        status["version"] = self.ser.read(8)
        self.ser.write(self.addr + '#' + self.term)
        status["checksum"] = self.ser.read(8)

        self.status = status

    def volume_command(self):
        """
        This function calculates the steps needed to deliver the volume, 
        checks if it can be delivered and updates the plunger position and 
        down_remaining steps
        """
        vol = self.volume_prompt.text()
        if not vol.isdigit():
            QMessageBox.warning(self, __appname__, "Please enter a numerical value")
            self.volume_prompt.selectAll()
            return
        vol = float(vol)
        steps = self.steps_tot / self.syr_size * vol

        if self.PushBtn.isChecked():
            if self.plung_pos - steps < 1:# Check for validity of the command
                QMessageBox.warning(self,__appname__, "Not a valid value")
                self.volume_prompt.selectAll()
                return
            else:
                self.plung_pos -= steps
                #self.ser.write(self.addr + 'D' + steps + self.term)
        else:
            if self.plung_pos + steps > self.steps_tot:
           #     print "plunge position: {}".format(self.plung_pos)
                #print "steps: {}".format(steps)
           #     print "steps_total: {}".format(self.steps_tot)
                QMessageBox.warning(self, __appname__, "Exceeds the available space")
                self.volume_prompt.selectAll()
                return
            else:
                self.plung_pos += steps
                #self.ser.write(self.addr + 'P' + steps + self.term)

        print "Plunger Position: {}".format(self.plung_pos)
    


class updateThread(QThread):

    def __init__(self, window, parent=None):
        super(updateThread, self).__init__(parent)
        self.window = window

    def run(self):
        #status = self.update_values()
        while True:
            self.window.update_values()
            time.sleep(1)

class reportsThread(QThread):

    def __init__(self, status, parent=None):
        super(reportsThread, self).__init__(parent)

        self.status = status

    def run(self):
        #self.reports.Position_Edit.setText(self.status["abs_pos"])
        #self.reports.Top_Velocity_Edit.setText(self.status["top_vel"])
        #self.reports.Cutoff_Velocity_Edit.setText(self.status["cutoff"])
        #self.reports.Actual_Position_Edit.setText(self.status["act_pos"])
        #self.reports.Start_Velocity_Edit.setText(self.status["start"])
        #self.reports.Backlash_Edit.setText(self.status["backlash"])
        #self.reports.Fluid_Sensor_Edit.setText(self.status["fluid"])
        #self.reports.Buffer_Status_Edit.setText(self.status["buffer"])
        #self.reports.Firmware_Edit.setText(self.status["version"])
        #self.reports.Checksm_Edit.setText(self.status["checksum"])
        pass


class Reports_class(QDialog, python_settings.Ui_Dialog):

    def __init__(self, parent=None):
        super(Reports_class, self).__init__(parent)
        self.setupUi(self)

        __appname__ = "Reports Screen"
        self.setWindowTitle(__appname__)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window= MainWindow()
    window.show()
    app.exec_() # Event-loop of the application
