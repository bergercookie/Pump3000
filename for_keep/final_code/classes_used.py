#  Thu May 29 02:59:41 EEST 2014, nickkouk

# proper division for python 2.7
from __future__ import division

# Usual importing stuff for PySide
from PySide.QtGui import *
from PySide.QtCore import *

# Module imports
import sys
import os
from serial.tools.list_ports import comports

# Qt-Designer compiled python code
import python_gui
import python_settings
import history_settings
import device_configuration
import parameters_change
import about_dialog


class ParametersChange(QDialog, parameters_change.Ui_Dialog):
    def __init__(self, pump, parent = None):
        super(ParametersChange, self).__init__(parent)
        self.setupUi(self)
        self.pump = pump

    def update_pump_param(self):
        pairs = [('top_velocity', self.Top_Velocity_Edit_2.text()),
                ('cutoff_velocity', self.Cutoff_Velocity_Edit_2.text()),
                ('backlash', self.Backlash_Steps_Edit_2.text()),
                ('start_velocity', self.Start_Velocity_Edit_2.text()),
                ('slope', self.SlopeEdit.text())
                ]
        
        for pair in pairs:
            if pair[1].isdigit():
                print "Pair[1] {}".format(pair[1])
                self.pump.property_set(*pair)

class HistoryDialog(QDialog, history_settings.Ui_Dialog):
    def __init__(self, pump, parent = None):
        super(HistoryDialog, self).__init__(parent)
        self.setupUi(self) 

        self.pump = pump
        self.__appname__ = "Command History"
        self.setWindowTitle(self.__appname__)

        self.connect(self.refresh_Btn,\
                SIGNAL("clicked()"),\
                self.refresh)
        self.connect(self.commands_only,\
                SIGNAL("clicked()"),\
                self.refresh)
        self.connect(self.clear_history_btn,\
                SIGNAL("clicked()"),\
                self.clear_history)



    def clear_history(self):
        self.pump.history = [ ]
        self.refresh()

    def refresh(self):
        wanted = self.pump.history
        wanted_string = ''
        if self.commands_only.isChecked():
            for i in wanted:
                wanted_string += "{}\\r\n".format(i[:-1])
        else:
            for i in range(len(wanted)):
                wanted_string += "{0}:\t {1}\\r\n".format(i+1, wanted[i][:-1])

        self.history_edit.setPlainText(wanted_string)

class ReportsDialog(QDialog, python_settings.Ui_Dialog):

    def __init__(self, pump, window, parent=None):
        super(ReportsDialog,  self).__init__(parent)
        self.setupUi(self)

        self.__appname__ = "Reports Screen"
        self.setWindowTitle(self.__appname__)
        self.pump = pump
        self.window = window

        self.connect(self.refresh_interval_edit,\
                SIGNAL("textEdited(QString)"),\
                self.enable_button)

        self.connect(self.refresh_now_button,\
                SIGNAL("clicked()"),\
                self.refresh)
        
        self.refresh_interval_edit.setText("%s"\
                % int((self.window.refreshQtimer.interval() / 1000)))

        # Setting the refresh interval manually
        self.connect(self.refresh_interval_button,\
                SIGNAL("clicked()"),\
                self.setRefreshTime)

    # Enabling the volume button
    def enable_button(self):
        if self.refresh_interval_edit.text().isdigit():
            self.refresh_interval_button.setEnabled(True)
        else:
            self.refresh_interval_button.setEnabled(False)

    def refresh(self):
        """ The refresh function shows the pump major statistics.

        The refresh function is periodically run using the QTimer refreshQtimer
        When the timer timeouts the stats are fetched from the pump
        """

        self.window.update_pump_values()
        stats = self.pump.status

        self.Actual_Position_Edit.setText(stats["actual_pos"])
        self.Backlash_Steps_Edit.setText(stats["backlash_steps"])
        self.Cutoff_Velocity_Edit.setText(stats["cutoff_vel"])
        self.Position_Edit.setText(stats["absolute_pos"])
        self.Start_Velocity_Edit.setText(stats["starting_vel"])
        self.Top_Velocity_Edit.setText(stats["top_vel"])
        self.Checksum_Edit.setText(stats["checksum"])
        self.Fluid_Sensor_Edit.setText(stats["fluid_sensor"])
        self.Buffer_Status_Edit.setText(stats["buffer_status"])
        self.Version_Edit.setText(stats["version"])

    def setRefreshTime(self):
        text = self.refresh_interval_edit.text()
        if text.isdigit():
            self.window.refreshQtimer.setInterval(\
                    eval(text) * 1000)

            self.refresh_interval_edit.setText("%s"\
                    % int((self.window.refreshQtimer.interval() / 1000)))
            print "Timer interval Set: {} microseconds".format(eval(text) * 1000)
        else: 
            QMessageBox.warning(self, self.__appname__, "Not a valid input")

        self.refresh_interval_edit.selectAll()

    def tick_refresh(self):
        if self.noRefresh.isChecked():
            self.window.cancel_timer()
            self.window.refresh_status = False
            self.window.scene.setForegroundBrush(\
                    QBrush(Qt.lightGray, Qt.CrossPattern))
           
        else:
            self.window.refresh_status = True
            self.window.refreshQtimer.start()
            self.window.scene.setForegroundBrush(\
                    Qt.NoBrush)


class NewDevDialog(QDialog, device_configuration.Ui_Dialog):

    def __init__(self, pump, parent=None):
        super(NewDevDialog,  self).__init__(parent)
        self.setupUi(self)

        self.__appname__ = "Device Configuration"
        self.setWindowTitle(self.__appname__)
        self.comports = comports
        self.pump = pump

        ports_available = list(self.comports())
        self.listWidget.addItem('loop://')
        for i in range(len(ports_available)):
            self.listWidget.addItem(ports_available[i][0])

    def connect_with_port(self):
        """Passes the selected item into the connect_new method of the pump."""
        port = self.listWidget.currentItem().text()
        self.pump.connect_new(port)

class SyringePickDialog(QDialog, device_configuration.Ui_Dialog):

    def __init__(self, pump, parent=None):
        super(SyringePickDialog, self).__init__(parent)
        self.setupUi(self)

        self.__appname__ = "Syringe Configuration"
        self.setWindowTitle(self.__appname__)
        self.pump = pump

        syringe_sizes = ['50 micro', '100 micro', '250 micro', '500 micro', \
                '1000 micro', '5000 micro']

        for i in range(len(syringe_sizes)):
            self.listWidget.addItem(syringe_sizes[i])

    def select_new_syringe(self):
        """Passes the selected item into the connect_new method of the pump."""
        syringe = self.listWidget.currentItem().text().split()[0]
        self.pump.syringe_size = syringe
        print "syringe is set to {size}".format(size = self.pump.syringe_size)

class AboutDialog(QDialog, about_dialog.Ui_Form):

    def __init__(self, text, appname, parent = None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)

        self.__appname__ = appname
        self.setWindowTitle(self.__appname__)
        self.text = text
        self.load_text()

    def load_text(self):
        self.textBrowser.setText(self.text)

class AboutDialog2(QDialog, about_dialog.Ui_Form):

    def __init__(self, text, appname, parent = None):
        super(AboutDialog2, self).__init__(parent)
        self.setupUi(self)

        self.__appname__ = appname
        self.setWindowTitle(self.__appname__)
        self.text = text
        self.load_text()
        self.QtButton = QPushButton("About Qt")
        self.horizontalLayout.addWidget(self.QtButton)
        
        self.connect(self.QtButton,\
                SIGNAL("clicked()"),\
                self.about_qt)

    def load_text(self):
        self.textBrowser.setText(self.text)
    def about_qt(self):
        QMessageBox.aboutQt(self, title = "About Qt")

