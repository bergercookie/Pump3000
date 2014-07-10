#!/usr/bin/env python
# Mon May 26 23:48:35 EEST 2014, nickkouk
"""
Python Implementation for the Cavro XP3000 GUI.

The GUI is designed with regards to the MVC (Model View Controller)
Ui architectural pattern. Inside this module the View - Controller behaviors
are implemented while the Model behavior is implemented in the imported module:
    pump_model.py

"""


# proper division for python 2.7
from __future__ import division

# Usual importing stuff for PySide
from PySide.QtGui import *
from PySide.QtCore import *

# Module imports
import sys
import time
from classes_used import HistoryDialog,\
        ReportsDialog,\
        NewDevDialog,\
        SyringePickDialog,\
        ParametersChange,\
        AboutDialog,\
        AboutDialog2
        #QuestionBox


# Qt-Designer compiled python code
import python_gui
import python_settings
import history_settings
import device_configuration

import pump_model

class MainWindow(QMainWindow, python_gui.Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.__appname__ = "XP3000 Interface"
        self.setWindowTitle(self.__appname__)

        # Initialize a pump instance
        # TODO
        # You define how to start the pump
        self.pump = pump_model.Pump(1, 'serial')

        # MainWindow related parameters
        self.quick_action = 'push'
        self.editors_open = 1
        self.lcdNumber.display(10)

        #open fd
        self.open_files = [ ]
        self.save_time = 0
        self.modified_time = -1


        # Setting tabs titles
        self.tabWidget.setTabText(0, 'Controls')
        self.tabWidget.setTabText(1, 'Editor - {}'.format(self.editors_open))

         # Set up a timer for periodical refresh of the pump parameters
        self.refresh_status = True
        self.refreshQtimer = QTimer(self)
        self.refreshQtimer.setInterval(5000)

        self.refreshQtimer.start()

        # Other dialogs instances
        self.reports_window = ReportsDialog(self.pump, self)

        # Initialize the port configuration
        #TODO enable it when it comes to the real pump
        #self.newDev()

        # saving the previous status of commands to revert in case pump busy
        self.prev_plung_pos = 10
        self.prev_valve_btn = self.output_btn


        # Connecting signals to functions
        self.connect(self.output_btn,\
                SIGNAL("clicked()"),\
                self.valve_status)
        self.connect(self.input_btn,\
                SIGNAL("clicked()"),\
                self.valve_status)
        self.connect(self.bypass_btn,\
                SIGNAL("clicked()"),\
                self.valve_status)
        self.connect(self.run_script_btn,\
                SIGNAL("clicked()"),\
                self.run_script)
        self.connect(self.clear_editor_btn,\
                SIGNAL("clicked()"),\
                self.clear_editor)

        self.connect(self.speed_slider,\
                SIGNAL("sliderReleased()"),\
                self.speed_control)
        self.connect(self.speed_slider,\
                SIGNAL("valueChanged(int)"),\
                self.lcd_display)
        self.connect(self.volume_button,\
                SIGNAL("clicked()"),\
                self.volume_control)
        self.connect(self.volume_prompt,\
                SIGNAL("textEdited(QString)"),\
                self.enable_button)

        # ComboBox
        self.connect(self.quick_combobox,\
                SIGNAL("currentIndexChanged(int)"),\
                self.quick_combobox_fun)
        self.connect(self.address_combobox,\
                SIGNAL("currentIndexChanged(int)"),\
                self.set_address)
        self.connect(self.make_it_so,\
                SIGNAL("clicked()"),\
                self.make_it_so_function)

        # Other Dialogs
        self.connect(self.actionReports,\
                SIGNAL("triggered()"),\
                self.reports_window_open)
        self.connect(self.actionHistory,\
                SIGNAL("triggered()"),\
                self.history_window_open)
        self.connect(self.actionNew_Device,\
                SIGNAL("triggered()"),\
                self.newDev)
        self.connect(self.actionSyringe_Size,\
                SIGNAL("triggered()"),\
                self.newSyringe)
        self.connect(self.actionPump_Parameters,\
                SIGNAL("triggered()"),\
                self.parameters_change_open)
        self.connect(self.actionLeft_Valve,\
                SIGNAL("triggered()"),\
                self.init_valve_left)
        self.connect(self.actionRight_Valve,\
                SIGNAL("triggered()"),\
                self.init_valve_right)
        self.connect(self.actionAbout,\
                SIGNAL("triggered()"),\
                self.about_software)
        self.connect(self.actionLicense,\
                SIGNAL("triggered()"),\
                self.about_license)
        self.connect(self.actionCommands,\
                SIGNAL("triggered()"),\
                self.editor_help)

        self.connect(self.refreshQtimer,\
                SIGNAL("timeout()"),\
                self.update_pump_values)

        # Editor related action buttons
        self.connect(self.actionSave,\
                SIGNAL("triggered()"),\
                self.save_btn)
        self.connect(self.actionSaveAs,\
                SIGNAL("triggered()"),\
                self.saveAs_btn)
        self.connect(self.actionOpen,\
                SIGNAL("triggered()"),\
                self.open_btn)
        self.connect(self.textEdit,\
                SIGNAL("textChanged()"),\
                self.update_modify_time)

        # Visualizing the pump 
        self.pixmap = QPixmap("cavro.jpg")
        self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.gray)
        self.scene.addItem(self.pixmap_item)

        self.graphicsView.setScene(self.scene)


    # Button Actions


    def closeEvent(self, event):
        if self.save_time <= self.modified_time:
            quit_msg = "The editor script has been modified,\nDo you still want to continue"
            reply = QMessageBox.question(self, self.__appname__,\
                    quit_msg,\
                    QMessageBox.Yes,\
                    QMessageBox.No)

            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else: 
            try:
                self.refreshQtimer.stop()
                self.pump.stop_thread()
            except:
                pass
            # Close open file descriptors
            for a_file in self.open_files:
                a_file.close()
                print "closing {}".format(a_file)
            self.close()

    def save_btn(self):
        dir = "."
        text = self.textEdit.toPlainText()
        try:
            self.file_fd.write(text);self.file_fd.seek(0)
            self.save_time = time.time()
        except AttributeError:
            self.saveAs_btn()
            
    def saveAs_btn(self):
        dir = "."
        text = self.textEdit.toPlainText()
        fileObj = QFileDialog.getSaveFileName(self, self.__appname__, dir=dir, filter="Text Files (*.txt)")
        fileName = fileObj[0]
        try:
            self.file_fd = open(fileName, mode="w")
            self.open_files.append(self.file_fd)
            self.file_fd.write(text);self.file_fd.seek(0);
            self.save_time = time.time()
        except IOError: # Cancel was pressed
            pass

    def open_btn(self):
        dir = "."
        fileObj = QFileDialog.getOpenFileName(self, self.__appname__ + " Open File Dialog", dir=dir, filter="Text files (*.txt)")
        fileName = fileObj[0]

        try:
            file_fd = open(fileName, "r")
            self.open_files.append(file_fd)
            read = file_fd.read()
            self.textEdit.setText(read)
            file_fd.close()
        except IOError:
            pass

    def update_modify_time(self):
        self.modified_time = time.time()

    def run_script(self):
        text = self.textEdit.toPlainText()
        script_commands = text.split('\n')
        print script_commands
        script_commands = filter(lambda x: x != '', script_commands)
        for i in range(len(script_commands)):
            script_commands[i] = "self." + script_commands[i]
            print script_commands[i]
            eval(script_commands[i])
    def clear_editor(self):
        self.textEdit.clear()

    def init_valve_left(self):
        self.pump.initialize_pump(output = 'left')
        self.speed_slider.setValue(10)
    def init_valve_right(self):
        self.pump.initialize_pump(output = 'right')
        self.speed_slider.setValue(10)

    # Updating pump status values periodically
    # TODO do not wait for the method to finish!
    # Assign a fucking thread to it!!
    def update_pump_values(self):
        self.pump.update_values()

    def cancel_timer(self):
        """
        The purpose of the cancel_timer is to cancel the status refreshing.
        Can be used by the user to manually update the pump status 

        """

        self.refreshQtimer.stop()
        self.refresh_status = False
        print "TIMER closed"



    # Enabling the volume button
    def enable_button(self):
        if self.volume_prompt.text().isdigit():
            self.volume_button.setEnabled(True)
        else:
            self.volume_button.setEnabled(False)

 
    # Functions for either fulling or emptying the whole syringe
    def quick_combobox_fun(self):
        if self.quick_combobox.currentIndex() == 0:
            self.quick_action = 'push'
        elif self.quick_combobox.currentIndex() == 1:
            self.quick_action = 'pull'
        elif self.quick_combobox.currentIndex() == 2:
            self.quick_action = 'terminate'
    def make_it_so_function(self):
        if self.quick_action == 'terminate':
            self.pump.terminate_execution()
        else:
            self.pump.volume_command(special = self.quick_action)
            label = "Quick Action {action} executed".format(action = self.quick_action)
            self.command_label_show(label)

    # Opening Dialogs
    def editor_help(self):
        fd1 = open('pump_commands.txt', 'r')
        text = fd1.read()
        self.open_files.append(fd1)
        self.editor_help_win = AboutDialog(text, "Editor Commands")
        self.editor_help_win.show()
        self.editor_help_win.raise_()

    def about_license(self):

        fd1 = open('lgpl-2.1.txt', 'r')
        text = fd1.read()
        self.open_files.append(fd1)
        self.about_dialog = AboutDialog(text, "Software License")
        self.about_dialog.exec_()

    def about_software(self):

        fd1 = open('about.txt', 'r')
        text = fd1.read()
        self.open_files.append(fd1)
        self.about_soft = AboutDialog2(text, "About the Software")
        self.about_soft.exec_()

    def parameters_change_open(self):
        """ Opens a ParametersChange Instance"""

        self.parameters_window = ParametersChange(self.pump)
        self.parameters_window.show()
        self.parameters_window.raise_()

        self.connect(self.parameters_window,\
                SIGNAL("accepted()"),\
                self.parameters_window.update_pump_param)



    def history_window_open(self):
        """ Opens a HistoryDialog Instance"""

        self.history_window = HistoryDialog(self.pump)
        self.history_window.show()
        self.history_window.raise_()
        self.history_window.refresh_Btn.click()

    def reports_window_open(self):
        """ Opens a ReportsDialog Instance"""


        self.connect(self.reports_window.noRefresh,\
                SIGNAL("clicked()"),\
                self.reports_window.tick_refresh)

        self.reports_window.refresh()
        self.reports_window.show()
        self.reports_window.raise_()
   
    # Device Configuration
    def newDev(self):
        QMessageBox.information(self, "New Pump Configuration", "Select the device name")

        self.dev_window = NewDevDialog(self.pump)
        self.dev_window.show()
        self.dev_window.exec_()

        self.connect(self.dev_window,\
                SIGNAL("accepted()"),\
                self.dev_window.connect_with_port())
        
    def newSyringe(self):

        self.syringe_window = SyringePickDialog(self.pump)
        self.syringe_window.show()
        self.syringe_window.exec_()

        self.connect(self.syringe_window,\
                SIGNAL("accepted()"),\
                self.syringe_window.select_new_syringe())

    def set_address(self):
        self.pump.addr = '/%s' %self.address_combobox.currentText()
        label = "Addressing to pump #{}".format(self.pump.addr[-1])
        self.command_label_show(label)
       
    # Valve Status
    def valve_status(self):
        """ Determine which valve is pressed, 
        send the command, 
        update the label"""

        if self.output_btn.isChecked():
            answer = self.pump.valve_command("out")
        elif self.input_btn.isChecked():
            answer = self.pump.valve_command("in")
        else:
            answer = self.pump.valve_command("bypass")

#        if answer = 'busy':
            #self.prev_valve_btn.click()
        #else:

        label = "Valve position changed to {valve_pos}".format(\
                valve_pos = self.pump.own_status["valve_pos"])
        self.command_label_show(label)

    # Plunger speed
    def speed_control(self):
        # Changing the velocity of the plunger

        speed = self.speed_slider.value()
        self.pump.property_set("speed", speed)
        label = "Plunger Speed Changed: {}".format(speed)
        self.command_label_show(label)
    def lcd_display(self):
        speed = self.speed_slider.value()
        self.lcdNumber.display(speed)

    def volume_control(self):
        """function for calling the pump.volume_command method."""

        volume = self.volume_prompt.text()

        if self.PushBtn.isChecked():
            direction = "D"
        elif self.PullBtn.isChecked():
            direction = "P"

        #print "volume: {0}\n volume_type: {1}\n direction: {2}: ".format(volume, type(volume), direction)

        (done, answer) = self.pump.volume_command(direction, volume)
        #print "done: {0}\n answer: {1}".format(done, answer)

        if not done:
            QMessageBox.warning(self, self.__appname__, answer)
        else:
            if direction == "D":
                label = "Drew {volume}".format(volume = volume)
            else:
                label = "Pushed {volume}".format(volume = volume)

            self.command_label_show(label)
        self.volume_prompt.selectAll()

    # The statusline
    def command_label_show(self, a_string):
        self.command_label.setText(a_string)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window= MainWindow()
    window.show()
    app.exec_() # Event-loop of the application
