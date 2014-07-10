# Tue Jun 3 19:49:03 EEST 2014, nickkouk

""" 

This is the pump model for the Cavro XP3000 Pump series.

It is designed to implement all the basic controls of the pump independent of
the way the user interacts with it (GUI, CLI, etc).

"""

from __future__ import division
import serial
import threading
import sys
from exceptions_module import BusyPump
import time
import signal
import Queue

class Pump():
    def __init__(self, addr, com = 'serial'):


        self.addr = '/%s' %addr
        self.term = 'R\r'
        self.com = com

        # Control Related properties
        self.history = [ ]
        self.interval = 2
        self.timeout_time = 0.2 

        self.stop_flag = False
        signal.signal(signal.SIGINT, self.stop_thread)


        # sending mechanism
        # TODO Change it when a script is given
        self.exc_mode = 'interactive'
        self.questions_out = Queue.Queue(-1)
        self.answers_ret = Queue.Queue(-1)
        self.answers_lock = threading.Lock()
        self.update_sema = threading.Semaphore(value=1)

        # Dictionary for holding the pump properties
        self.status = {"absolute_pos": '',\
                "top_vel": '',\
                "cutoff_vel": '',\
                "actual_pos": '', \
                "starting_vel": '',\
                "backlash_steps": '',\
                "fluid_sensor": '',\
                "buffer_status": '',\
                "version": '',\
                "checksum": ''}


        # Hold local properties
        self.own_status = {"plung_pos_mine": 0,\
                "valve_pos": '0',\
                "syringe_size": 50,\
                "steps_tot": 3000}

        self.correspondance = {"speed": ['S', 1, 40],\
                "backlash": ['K', 0, 31],\
                "slope": ['L', 1, 20],\
                "start_velocity": ['v', 50, 1000],\
                "top_velocity": ['V', 5, 5800],\
                "cutoff_velocity": ['c', 50, 2700],\
                "cutoff_velocity_steps": ['C', 0, 25],\
                }


        # Start the delivery thread
        self.deliveryThread = delivery_thread(self)
        self.deliveryThread.start()
        print "THREAD STARTED"


        #self.connect_new(port_name = 'loop://')
        self.connect_new(port_name = '/dev/tty.usbserial-FTDWBH0Y')

    # New serial connection
    def connect_new(self, port_name):
        """Function for configuring a new serial connection."""

        try:
            self.ser = serial.Serial(port = port_name,\
                    baudrate = 9600,\
                    parity = 'N',\
                    stopbits = 1,\
                    bytesize = 8,\
                    timeout = self.timeout_time)
        except serial.SerialException:
            self.ser = serial.serial_for_url('loop://',\
                    timeout = self.timeout_time)
            return "WARNING: You are running on a testing algorithm\
                    No communication with pump is configured so far"

        finally:
            self.initialize_pump()


    # Initialization Phase
    def initialize_pump(self, output = 'right'):
        """Initialize (the newly) configured pump"""

        if not self.ser.isOpen():
            self.ser.open()

        # These commands should be sent when the pump first gets set
        if output == 'right':
            commands = ['S10', 'Z']
        else:
            commands = ['Y', 'S10']
        for command in commands:
            self.send_Command(command, 10)
        print "FIRST 2 SENT_COMMAND SEEEENT!"

        # Actions after every initialization
        self.history = [ ]
        self.update_values(initialize = True)

    # Valve Position
    def valve_command(self, position):
        if position == "out":
            answer = self.send_Command('O', 10)
            self.own_status["valve_pos"] = 'O'
        elif position == "in":
            answer = self.send_Command('I', 10)
            self.own_status["valve_pos"] = 'I'
        elif position == "bypass":
            answer = self.send_Command('B', 10)
            self.own_status["valve_pos"] = 'B'
        else:
            print "NO SUCH VALUE for position available"
        return answer

    # Plunger Functions
    def property_set(self, a_property, value):
        # Checking the validity of the command
        min_value, max_value = self.correspondance[a_property][1:]
        if int(value) >= min_value and int(value) <= max_value:
            # Sending the Command to the queue
            command = self.correspondance[a_property][0]
            value = "%s" %value
            print "SENDING THE COMMNAND"
            return_stat = self.send_Command("{}".format(\
                command + value), 10)
            return return_stat
        else:
            return "OUT OF BOUNDS"
                        
    def volume_command(self, direction = 'P', vol = 0, special = None):
        """
        This is the volume command.

        The volume_command function first decides if it can 
        deliver the needed volume, 
        then if the volume given is a valid one,
        calls the move_plunger method with the needed arguments
        to deliver the volume.

        """

        valid = "True"
        status = "Done"

        if special:
            if special == 'push_all':
                self.send_Command('A0')
                self.own_status["plung_pos_mine"] = 0
            else:
                self.send_Command('A3000')
                self.own_status["plung_pos_mine"] = 3000

        else:
            if not vol.isdigit():
                return (False, "Please enter a numerical value")

            vol = float(vol)
            steps = int(self.own_status["steps_tot"] / \
                    self.own_status["syringe_size"] * vol)

            if direction == 'D':
                if self.own_status["plung_pos_mine"] - steps < 0:
                    valid = False
                    status = "Not a valid Value"
                else:
                    self.own_status["plung_pos_mine"] -= steps
                    status = self.send_Command(direction + "%s" %steps, 10)

            else:
                if self.own_status["plung_pos_mine"] +\
                        steps > self.own_status["steps_tot"]:
                    valid = False
                    status = "Not a valid Value"
                else: 
                    self.own_status["plung_pos_mine"] += steps
                    status = self.send_Command(direction + "%s" %steps, 10)

        return (valid, status)
            
    # Pump related Settings update method
    def update_values(self, initialize = False):
        """
        This is the parameters update method.

        The purpose of this function is to constantly update the settings 
        related to the pump, should be run by a thread periodically
        """

        self.update_sema.acquire()
        print "ENTERED THE SEMAPHORE"
        self.update_thread = threading.Thread(\
                target = self.actual_update_method,\
                args = (initialize,))
        self.update_thread.start()
    def actual_update_method(self, initialize):
        try:
            # reading info mechanism
            self.status["absolute_pos"] = self.send_Command('?', 10)[0][3:]
            self.status["actual_pos"] = self.send_Command('?4', 10)[0][3:]
            self.status["starting_vel"] = self.send_Command('?1', 10)[0][3:]
            self.status["top_vel"] = self.send_Command('?2', 10)[0][3:]
            self.status["cutoff_vel"] = self.send_Command('?3', 10)[0][3:]
            self.status["backlash_steps"] = self.send_Command('?12', 10)[0][3:]
            self.status["fluid_sensor"] = self.send_Command('?22', 10)[0][3:]
            self.status["buffer_status"] = self.send_Command('?F', 10)[0][3:]
            self.status["version"] = self.send_Command('?&', 10)[0][3:]
            self.status["checksum"] = self.send_Command('?#', 10)[0][3:]
        except TypeError:
            print "In actual_update_method,\n{}".format(sys.exc_info()[0])

        abs_pos = self.status["absolute_pos"][:-3]
        try:
            if 0 <= int(abs_pos) <= 3000:
                self.own_status["plung_pos_mine"] = int(abs_pos)
                print "Plunger Position is set: {}".format(self.own_status["plung_pos_mine"])
            else:
                print "Out of range value reported by pump!"
                pass
        except ValueError:
            print sys.exc_info()[0]

        self.update_sema.release()
        print "EXITED THE SEMAPHORE"
    # Supplementary Functions
    def terminate_execution(self):
        self.send_Command('T')
        time.sleep(0.1)
        self.update_values() # So that the plunger position may refresh itself

    def stop_thread(self, signum=0, fname=0):
        print "C-c caught!!"
        self.stop_flag = True
        sys.exit(1)

    def change_mode(mode):
        """ Function for changing the mode the commands are executed.

        Must be invoked at the end of the editor commands"""
        self.exc_mode = mode
        print "the mode has changed to {}".format(self.exc_mode)

    def send_Command(self, command, bits_to_read = 0):
        """Major mechanism for sending the commands to the pump.

        Stores the coming commands on a queue from which they are sent to the pump.
        Decides upon waiting for the answer if on interactive mode, or not.
        Finally returns the answer to the calling function
        """

        # TODO Change the fucking description

        full_command = self.addr + command + self.term
        try:
            self.answers_lock.acquire()
            self.questions_out.put(full_command)
            self.history.append(full_command)
            if self.exc_mode == 'interactive':
                if bits_to_read:
                    answer = self.answers_ret.get(timeout = 1)
                else:
                    self.answers_ret.get(timeout = 0.5)
                    print "NO NEED TO READ"

        except Queue.Empty:
            print "Answer Queue is empty!!"
        except:
            print "ERROR in SEND_COMMAND:"
            print sys.exc_info()[0]
            self.stop_thread()
        finally:
            self.answers_lock.release()
            if self.exc_mode == 'interactive':
                if 'answer' in locals():
                    return answer
            else:
                return 0

class delivery_thread(threading.Thread):
    """
    Class for sending the queued commands to the pump.

    When initialized, the instance of the class inherits the pump instance as
    well as the send & return queues.
    On the run method,
    """

    def __init__(self, pump):
        threading.Thread.__init__(self)
        self.pump = pump
        self.forSending = self.pump.questions_out
        self.forGivingBack = self.pump.answers_ret

    def run(self):
        while not self.pump.stop_flag:
            try:
                com_to_send = self.forSending.get(timeout = 3)
                self.pump.ser.write(com_to_send)
                time.sleep(0.1)
                answer = self.pump.ser.read(11)
                done, answer = self.push_command(com_to_send, answer)
                if self.pump.exc_mode == 'interactive':
                    self.forGivingBack.put((answer, done))
            except Queue.Empty:
                time.sleep(1)
                print "Questions Queue is empty"

    def push_command(self, *QA):
        com_to_send = QA[0]
        answer = QA[1]
        if self.pump.exc_mode == 'editor':
            # editor Mode
            while self.pump_busy(com_to_send, answer):

                self.pump.ser.write(com_to_send)
                time.sleep(0.1) 
                answer = self.pump.ser.read(11)
            done = True
        else:
            # interactive Mode
            if self.pump_busy(com_to_send, answer):
                done = False
            else:
                done = True
        print "\n\ndone = {0}\nmode = {1}\nquestion = {2}\nanswer = {3}".format(done, self.pump.exc_mode, com_to_send, answer)
        return (done, answer)

    def pump_busy(self, *QA):
        """ 
        Determines if the pump is busy for the specific command to send.

        Accepts as input the command to the pump the answer returned and returns
        to the caller if the command has been accepted by the pump
        """
        question = QA[0]
        answer = QA[1]

        print 'The answer is {}'.format(answer)
        if 'o' in answer:
            return True
