# Tue Jun 3 19:49:03 EEST 2014, nickkouk

""" 
This is the pump model.

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
        self.com  = com

        # Control Related properties
        self.history      = [ ]
        self.interval     = 2
        self.timeout_time = 0.2

        self.stop_flag    = False
        signal.signal(signal.SIGINT, self.stop_thread)


        # sending mechanism
        self.questions_out = Queue.Queue(-1)
        self.answers_ret = Queue.Queue(-1)
        self.answers_lock = threading.Lock()

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


        self.ser = serial.Serial()
        self.connect_new(port_name = 'loop://')

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
            # Might be a bug when ran on Windows!
            if sys.platform[:2] == win:
                print "The OS used is Windows %s" % sys.platform()
                time.sleep(1)
            else:
                print "The System is not Windows"
                self.ser = serial.serial_for_url('loop://',\
                        timeout = self.timeout_time)


        finally:
            print "In the Finally Statement"
            self.initialize_pump()


    # Initialization Phase
    def initialize_pump(self, output = 'right'):
        """Initialize (the newly) configured pump"""

        if not self.ser.isOpen():
            self.ser.open()

        # These commands should be sent when the pump first gets set
        if output == 'right':
            commands = ['Z', 'S10']
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
        return answer

    # Plunger Functions
    def property_set(self, a_property, value):
        # Checking the validity of the command
        min_value, max_value = self.correspondance[a_property][1:]
        if value >= min_value and value <= max_value:
            # Sending the Command to the queue
            print "SENDING THE COMMAND"
            command = self.correspondance[a_property][0]
            value = "%s" %value
            return_stat = self.send_Command("{}".format(\
                command + value), 10)
        else:
            return (1, "Value out of bounds")
                        
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
        answer = "Done"

        if special:
            if special == 'push':
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
                    answer = "Not a valid Value"
                else:
                    self.own_status["plung_pos_mine"] -= steps
                    answer = self.send_Command(direction + "%s" %steps, 10)

            else:
                if self.own_status["plung_pos_mine"] +\
                        steps > self.own_status["steps_tot"]:
                    valid = False
                    answer = "Not a valid Value"
                else: 
                    self.own_status["plung_pos_mine"] += steps
                    answer = self.send_Command(direction + "%s" %steps, 10)

        return (valid, answer)
            
    # Pump related Settings update method
    def update_values(self, initialize = False):
        """
        This is the parameters update method.

        The purpose of this function is to constantly update the settings 
        related to the pump, should be run by a thread periodically
        """

        self.update_thread = threading.Thread(\
                target = self.actual_update_method,\
                args = (initialize,))
        self.update_thread.start()
        
    def actual_update_method(self, initialize):

        # reading info mechanism
        self.status["absolute_pos"] = self.send_Command('?', 10)
        self.status["actual_pos"] = self.send_Command('?4', 10)
        self.status["starting_vel"] = self.send_Command('?1', 10)
        self.status["top_vel"] = self.send_Command('?2', 10)
        self.status["cutoff_vel"] = self.send_Command('?3', 10)
        self.status["backlash_steps"] = self.send_Command('?12', 10)
        self.status["fluid_sensor"] = self.send_Command('?22', 10)
        self.status["buffer_status"] = self.send_Command('?F', 10)

        # These must be asked only once, at the initialization phase
        if initialize:
            #print "version set as well!"
            self.status["version"] = self.send_Command('?&', 10)
            self.status["checksum"] = self.send_Command('?#', 10)

        # TODO When you actually connect to the pump uncomment this line!!
        # Update own variables as well
        #self.own_status["plung_pos_mine"] = self.status["absolute_pos"]



    # Supplementary Functions
    def terminate_execution(self):
        self.send_Command('T')

    def stop_thread(self, signum=0, fname=0):
        print "C-c caught!!"
        self.stop_flag = True
        self.update_Thread.stop()
        sys.exit(1)


    def send_Command(self, command, bits_to_read = 0):
        """ Two lines for the incoming commands:

        --- Priority line: No need to wait for the pump to be free
        --- Ordinary line: Terminating Commands

        When a process wants to send a command to the pump, it pushes it to 
        one of the two open queues:
        --- update_questions_out: for auto-sent commands
        --- questions_out: for ordinary commands
        
        After sending, the process either waits if it has bits_to_read ON on the 
        corresponding queue or exits the send_Command function without reading
        the output
        """

        full_command = self.addr + command + self.term

        self.answers_lock.acquire()
        try:
            self.questions_out.put(full_command)
            self.history.append(full_command)
            if bits_to_read:
                #print "Send_Command| in the answers_ret Queue"
                answer = self.answers_ret.get(timeout = 1)
                print "Got back the answer {}".format(answer)
                self.answers_lock.release()
                return answer

            self.answers_lock.release()
        except:
            print "ERROR in SEND_COMMAND:"
            print sys.exc_info()[0]



    #def is_priority(self, command):
        ## Don't need to wait for the line to empty
        #if '?' in command or 'T' in command:
            #return True

        #return False
    #def is_busy(*command):
        #busy_code = 'c'

        ## TODO
        ## May need to implement a command-specific is_busy function
        ## judging from the pump's behavior
        #print "is_busy COMMAND {}".format(command)
        #if busy_code == command[2]:
           #return True
        #return False



class delivery_thread(threading.Thread):

    def __init__(self, pump):
        threading.Thread.__init__(self)
        self.pump = pump
        self.forSending = self.pump.questions_out
        self.forGivingBack = self.pump.answers_ret

    def run(self):
        while not self.pump.stop_flag:
            try:
                #print "Inside the run of the delivery_thread"
                com_to_send = self.forSending.get(timeout = 0.1)
                self.pump.ser.write(com_to_send)
                # The pump needs some time to answer
                time.sleep(0.1)
                answer = self.pump.ser.read(10)
                self.forGivingBack.put(answer)
                
                print "SENT the command: {}".format(com_to_send)

            except Queue.Empty:
                print "ITS EMPTY"
                #print "Unexpected Error!! {}".format(sys.exc_info()[0])
                pass

    #def run(self):
        #while not self.pump.stop_flag:
            #try:
                #if self.w_prior_queue.empty():
                    #command = self.w_queue.get(timeout = 1)
                ## if there are no commands in the prior buffer
                #else:
                    #command = self.w_prior_queue.get()             
            #except Queue.Empty:
                #print "It's EMPTY???"

            #while 'command' in locals():
                #print 'THE COMMAND', command
                #try:
                    #print "Going to Write-Sleep-Reed"
                    #self.pump.ser.write(command)
                    ##TODO uncomment the sleep command
                    #time.sleep(0.2)
                    #return_stat = self.pump.ser.read(self.pump.bits_to_read)
                    #if self.pump.bits_to_read:
                        #if self.pump.is_busy(return_stat):
                            #raise BusyPump()

                        #if self.pump.is_priority(command):
                            #self.r_prior_queue.put(return_stat)
                        #else:
                            #self.r_queue.put(return_stat)
                    #else:
                        ##self.pump.clean_read() # clean up the serial-in buffer
                        #print "Nothing to read"

                    #break

                #except BusyPump:
                    #pass
