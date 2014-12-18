#!/usr/bin/env python
# Mon May 26 23:48:35 EEST 2014, nickkouk
"""
===============================================================================
                                About
===============================================================================

Pump3000 was developed by Nikos Koukis (nickkouk@gmail.com). Its main purpose is 
to offer a simple Graphical User Interface for communication with the Cavro XP3000
pumps. It was created primarily for scientific usage for the "Systems Biology and
Bioengineering" Laboratory of the National Technical University of Athens
(NTUA).

For further assistance see the documentation on http://https://github.com/bergercookie

For bug reports, and suggestions either raise an issue on the Github page of the
project, or contact me in person (nickouk@gmail.com)

===============================================================================
                        Redistribution Policy
===============================================================================

The Pump3000 software is licensed under BSD. The specific license encourages redistribution and 
free usage of the software as long as the use complies to the license terms.
For complete policy of terms, consult a version of the license, either on the documentation page:
https://github.com/bergercookie/Cavro-Pump-XP3000-GUI/blob/master/LICENSE or on
the page: http://opensource.org/licenses/BSD-2-Clause

===============================================================================
            Python Implementation for the Cavro XP3000 GUI.
                             Pump3000
===============================================================================

The GUI is designed with regards to the MVC (Model View Controller)
UI architectural pattern. Inside this module the View - Controller behaviors
are implemented while the Model behavior is implemented in the imported module: pump_model.py


"""


# proper division for python 2.7
from __future__ import division

# Usual importing stuff for PySide
from PySide.QtGui import *
from PySide.QtCore import *

# Module imports
import sys
import time

import pump_model
from classes_used import HistoryDialog,\
        ReportsDialog,\
        NewDevDialog,\
        SyringePickDialog,\
        ParametersChange,\
        AboutDialog,\
        AboutDialog2

# Qt-Designer compiled python code
import python_gui
import python_settings
import history_settings
import device_configuration


class MainWindow(QMainWindow, python_gui.Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.__appname__ = "Pump3000"
        self.setWindowTitle(self.__appname__)

        # Initialize a pump instance
        # Define how to start the pump
        self.pump = pump_model.Pump(3, 'serial')
        #avail_meths = [method for method in dir(self.pump) \
                #if callable(getattr(self.pump, method))]
        #print "Pump3000->__init__->avail_meths = {}".format(avail_meths)

        # MainWindow related parameters
        self.quick_action = 'push_all'
        self.editors_open = 1
        self.lcdNumber.display(10)

        #open fd
        self.open_files = [ ]
        self.save_time = 0
        self.modified_time = -1

        # Setting tabs titles
        self.tabWidget.setTabText(0, 'Controls')
        self.tabWidget.setTabText(1, 'Editor - {}'.format(self.editors_open))

        # Reverting any changes not shown in the Window
        self.revertQtimer = QTimer(self)
        self.revertQtimer.setInterval(60000)
        self.revertQtimer.start()

        # Initialize the port configuration
        self.newDev()

        # Set up a timer for periodical refresh of the pump parameters
        self.refresh_status = True
        self.refreshQtimer = QTimer(self)
        self.refreshQtimer.setInterval(60000)
        self.refreshQtimer.start()

        # Other dialogs instances
        self.reports_window = ReportsDialog(self.pump,\
                self,\
                parent = None)

        # saving the previous status of commands to revert in case pump busy
        self.prev_plung_pos = 10
        self.prev_valve_btn = self.output_btn
        self.valve_correspond = {"out": self.output_btn,\
                "in": self.input_btn,\
                "bypass": self.bypass_btn
                }

        # Valve Signals
        self.connect(self.output_btn,\
                SIGNAL("clicked()"),\
                self.valve_status)
        self.connect(self.input_btn,\
                SIGNAL("clicked()"),\
                self.valve_status)
        self.connect(self.bypass_btn,\
                SIGNAL("clicked()"),\
                self.valve_status)

        # Plunger Movement
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

        # Quick CommandsComboBox
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

        # QTimer events
        self.connect(self.refreshQtimer,\
                SIGNAL("timeout()"),\
                self.update_pump_values)
        self.connect(self.revertQtimer,\
                SIGNAL("timeout()"),\
                self.revert_GUI_values)

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
        self.connect(self.run_script_btn,\
                SIGNAL("clicked()"),\
                self.run_script)
        self.connect(self.clear_editor_btn,\
                SIGNAL("clicked()"),\
                self.clear_editor)

        # Visualizing the pump 
        if sys.platform[:3] == 'win': #Running on windows, most probably executable
            self.pixmap = QPixmap("../../Images/cavro.jpg")
        else:
            self.pixmap = QPixmap("../Images/cavro.jpg")

        self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.gray)
        self.scene.addItem(self.pixmap_item)
        self.graphicsView.setScene(self.scene)

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
            self.pump.stop_thread()
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
        """Evaluate all the commands written in the given script."""

        self.pump.exc_mode = 'editor'
        text = self.textEdit.toPlainText() #Grab the commands
        script_commands = text.split('\n')
        script_commands = filter(lambda x: x != '' and not x.startswith('#'), script_commands) #remove the empty lines & the # lines
        print "*****\nPump3000.py -> run_script: script_commands = {}\n*****".format(script_commands)
        script_commands.append('pump.change_mode(interactive)') #change back to interactive mode
        try:
            self.pump.update_values()
            for i in range(len(script_commands)):
                if script_commands[i][:4] == 'pump':
                    eval("self." + script_commands[i])
                    print "self.%s" %script_commands[i]
                elif script_commands[i][0] == '/':
                    self.pump.send_Command(script_commands[i]) 
                else:
                    # TODO The user currently may not issue common python commands yet
                    print "Command #{0}: {1}".format(i, script_commands[i])
                    eval(script_commands[i])
        except:
            #print sys.exc_info()[0]
            print "Pump3000>run_script>except:\n{}".format(sys.exc_info()[0])


    def clear_editor(self):
        self.textEdit.clear()

    def init_valve_left(self):
        self.pump.initialize_pump(output = 'left')
        self.speed_slider.setValue(10)
    def init_valve_right(self):
        self.pump.initialize_pump(output = 'right')
        self.speed_slider.setValue(10)


    # Qtimer event handling
    def update_pump_values(self):
        """ 
        First call the refresh method of the reports_window instance
        which in turn calls the update_values on the pump
        """
        self.reports_window.refresh()

    def revert_GUI_values(self, doit = False):
        """ 
        Function for applying the GUI properties to the pump. 

        The user can call this function to make sure that the status on screen
        do correspond to the actual pump properties. The function should always
        be called when the pump was previously running on editor mode and the
        user switches back to interactive mode.
        """

        if doit:
            self.pump.exc_mode = 'interactive'

        if self.pump.exc_mode  == 'interactive':
            speed_val = self.speed_slider.value()
            self.pump.property_set('speed', '%s' % speed_val)
            time.sleep(0.5)
            self.pump.update_values()
            self.valve_status()
        
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
 
    def quick_combobox_fun(self):
        # Functions for either fulling or emptying the whole syringe
        if self.quick_combobox.currentIndex() == 0:
            self.quick_action = 'push_all'
        elif self.quick_combobox.currentIndex() == 1:
            self.quick_action = 'pull_all'

        # Other quick_actions
        elif self.quick_combobox.currentIndex() == 2:
            self.quick_action = 'terminate'
        elif self.quick_combobox.currentIndex() == 3:
            self.quick_action = 'revert_values'
    # Implement when the button is pressed
    def make_it_so_function(self):
        if self.quick_action == 'terminate':
            self.pump.terminate_execution()
            self.revert_GUI_values()

        elif self.quick_action == 'revert_values':
            self.revert_GUI_values(doit = True)
        else:
            if self.bypass_btn.isChecked():
                answer = "Bypass Mode is ON"
                QMessageBox.warning(self, self.__appname__, answer)
                return
            else:
                self.pump.volume_command(special = self.quick_action)
                label = "Quick Action {action} executed".format(action = self.quick_action)
                self.command_label_show(label)

    # Opening Dialogs
    def editor_help(self):

        fd1 = open('../text_files/pump_commands_html', 'r')
        text = fd1.read()
        self.open_files.append(fd1)
        self.editor_help_win = AboutDialog(text,\
                "Editor Commands",\
                parent = None)
        self.editor_help_win.show()
        self.editor_help_win.raise_()

    def about_license(self):

        fd1 = open('../text_files/bsd-2clause.txt', 'r')
        text = fd1.read()
        self.open_files.append(fd1)
        self.about_dialog = AboutDialog(text, "Software License")
        self.about_dialog.exec_()

    def about_software(self):

        fd1 = open('../text_files/about.txt', 'r')
        text = fd1.read()
        self.open_files.append(fd1)
        self.about_soft = AboutDialog2(text, "About the Software")
        self.about_soft.exec_()

    def parameters_change_open(self):
        """ Opens a ParametersChange Instance."""

        self.parameters_window = ParametersChange(self.pump, self)
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
        self.dev_window = NewDevDialog(self.pump, self)
        self.dev_window.exec_()
       
    def newSyringe(self):

        self.syringe_window = SyringePickDialog(self.pump, self)
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
        """ Configures the valve of the pump
        Determines which valve is pressed, 
        sends the command, 
        updates the label """

        if self.output_btn.isChecked():
            pos = "out"
        elif self.input_btn.isChecked():
            pos = "in"
        else:
            pos = "bypass"

        answer, done = self.pump.valve_command(pos)
        if done:
            label = "Valve position changed to {valve_pos}".format(\
                    valve_pos = self.pump.own_status["valve_pos"])
            self.command_label_show(label)
            self.prev_valve_btn = self.valve_correspond[pos]
        else:
            self.prev_valve_btn.click()


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

        # Thu Dec 18 17:28:35 EET 2014, nickkouk
        # the volume is a text command
        volume = self.volume_prompt.text()
        if self.bypass_btn.isChecked():
            answer = "Bypass Mode is ON"
            QMessageBox.warning(self, self.__appname__, answer)
            return
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
                label = "Pushed {volume}".format(volume = volume)
            else:
                label = "Drew {volume}".format(volume = volume)
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
