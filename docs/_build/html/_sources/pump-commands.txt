
Pump Commands
=========================================================

In this section the basic commands for communication with the pump are introduced.
You can issue a series of these commands from the editor's tab.
For the full list of available commands see the pump_model.py. You can use most 
of the methods of the Pump Class in the Editor tab as well.

.. note::

    'self' is a Python class arguement and shouldn't be issued by the user. 

**pump.connect_new(self, port_name)**

*Arguements*::

    port_name: string

*Description*

    Connect to the given port address.

*Example*::

    pump.connect_new(`/dev/tty.-SerialPort1-1') -> Configuring a serial connection on OSX

**pump.initialize_pump(self, output = 'right')**

*Arguements*::

    output: string [Optional]
        
        values: 'left', 'right'

*Description*
    
    Initialize the pump. The user can optionally issue the output valve. By default if not 
    given otherwise, the output valve is set to the right. 

*Examples*::
    
    pump.initialize_pump() -> Initializing the pump with default output valve (right)
    pump.initialize_pump(output = `left') -> Initializing the pump with output valve set to left

**pump.valve_command(self, position)**

*Arguements*::
    
    position: string

        values: 'I' (Input)
                'O' (Output)
                'B' (Bypass)

*Description*
    
    Set the valve to certain position.

*Examples*::
    
    pump.valve_command(`B') -> Set the valve to Bypass position

**pump.property_set(self, a_proprty, value)**

*Arguements*::
    
    a_property : string
    value      : int

*Description*

    Set a certain property for the plunger. The following properties are available for 
    modification. These are listed with regards to the command that should be issued 
    and the range of the values permitted::

        'speed'                 : 'S', [1  , 40]
        'backlash'              : 'K', [0  , 31]
        'slope                  : 'L', [1  , 20]
        'start_velocity'        : 'v', [50 , 1000]
        'top_velocity'          : 'V', [5  , 5800]
        'cutoff_velocity'       : 'c', [50 , 2700]
        'cuttof_velocity_steps' : 'C', [0  , 25]

    The user is encouraged to consult the manual for an overview on the 
    commands above

*Examples*::
 
    pump.property_set(`speed', `10') -> Set the plunger speed to 10
    pump.property_set(`backlash', `15') -> set the backlash steps to 15

**pump.volume_command(self, direction = `P', vol = `0', special=None)**


*Arguements*::

    direction : string
    
        Values: 'P'
                'D'

    vol       : string [Microliters]

    special   : string [Optional]

        Values: 'push_all'
                'pull_all'

*Description*
    
    Volume pushing / drawing mechanism. The user can issue a volume delivery as well
    as issue a special push / pull all action. In case the special action is given, 
    the  'vol' argument is neglected

*Examples*::

    pump.volume_command(direction = 'D', vol = '5') -> Dispense 5 microlitres
    pump.volume_command(special = `push_all') -> Dispense fluid volume

**pump.send_Command(self, command, bits_on_return = 0)**

*Arguements*::

    command        : string
    bits_on_return : int [Optional]

*Description*

    Sending Commands to the pump.
    Consult the manual for a detailed list of the pump commands for the RS-485 Protocol. 
    Using this method you must have already defined the pump address to send to (Via
    the main window or the Editor tab) and you should issue neither 
    the Run character [R] nor the terminating character

*Examples*::

    pump.send_Command(`A3000', 10) -> Move the plunger to abs. position 3000, read back 10 bits
    pump.send_Command(`T') -> Terminate plunger move in progress


**pump.ser.write(comand)**

*Arguements*::

    command: string

*Description*

    This command should be used only when a direct serial command has to be sent to the pump.
    User must issue the pump to which he is addressing to as well as the terminating character
    It is advisable that the user should prefere higher level commands such as 'send_Command'
    which doesn't require the prefix & suffix characters, and also check the availability of the pump

*Examples*::

    pump.ser.write(`/2ZR\r') -> Initialize the pump with the address 1

.. note::

    As seen in the Examples section of pump.ser.write, the user should refer to the pump
    address + 1. 
