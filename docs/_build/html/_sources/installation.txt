
Software Configuration
=========================================================


By now the user should have a copy of the project on his machine. If not refer
to section: :doc:`Getting Started <getting-started>`

.. _running-it:

Running the .exe 
************************

*Running the executable* version of the project is as simple as running the Pump3000.exe
located in the <location_to_project>/python_code/dist folder [#f1]_ [#f2]_.

.. figure::  ../Images/finding-exe.png
   :height: 7000px
   :scale:  10 %
   :align:  center

   Finding the .exe file

Running from source
************************

In case the user wants to run the software *from source*, a basic python distribution 
must be installed on the platform, (already preconfigured on most \*NIX systems). 
The user must also have the following packages installed:

- pyserial
- PySide

After this configuration, the user can run the software from the command-line [\*NIX]
command-prompt [Windows]::

    python Pump3000.py

Note that the user must first go to the folder, the Pump3000.py is located. 

.. figure::  ../Images/running-py.png
   :height: 7000px 
   :scale:  10 %
   :align:  center

   Running from source on MacOS

Using the software
************************


The first thing the user should do, if he doesn't know the serial connector 
to the pump, is figure out the correct port:

- On **Windows** machines this can be done by getting the *'Ports (COM & LPT)'* tab::

    Start Menu > right-click "My Computer" > select "Manage" >  Click on the "Device Manager"

    (On the "Device Manager") Click "Ports (COM & LPT)" tab > select the port your connector is on

  See :ref:`finding-manage`, :ref:`finding-com-ports`
  
- On **\*NIX** machines this can be done the following way::
  
    cd /dev

    ls -lart| grep tty

This will give  you a list of the currently available ports. Ejecting and reinserting the connector 
to the computer and in the meantime running the second command again will help you recognise 
the port the pump is running on.

    
.. _finding-manage:

.. figure::  ../Images/finding-manage.png
   :height: 7000px 
   :scale: 10 %
   :align: center

   'Manage' tab

.. _finding-com-ports:

.. figure::  ../Images/finding-com-ports.png
   :height: 7000px 
   :scale:  10 %
   :align:  center

   Configuring COM ports


.. Warning::

    Make sure that you have selected the correct port, otherwise the pump will not respond and will
    not raise any error Message

After that you are ready to :ref:`run the software <running-it>` (whichever way you want). You should be directed to the New_Device window where the
port connected to the pump must be selected

.. figure::  ../Images/dev-conf.png
   :height: 7000px 
   :scale: 10 %
   :align: center

   Configuring correct port for pump

If you have selected the correct port, the connection to the pump is established and 
the software will automatically initialize the pump, by moving the plunger to the upper position.

You are now in the Main Window. From here you can:

- Command a volume delivery,
- Change the speed of the plunger,
- Issue a quick command to the pump (halt, push_all, etc) 

.. figure::  ../Images/main-window.png
   :height: 7000px 
   :scale: 10 %
   :align: center

   Main window

From the main window you can navigate to a series of **other dialogs:** 

- **Editor's Tab**

  The Editor's Tab gives the user the ability to issue a series of commands to the pump.
  These commands are supplied in the "Pump Commands" page. The user can also issue raw 
  pump commands in the same way.
  
  A typical example of issued commands would be the following::

    pump.property_set('speed', '5')
    # Python Comments, write as many as you want
    # Empty lines don't matter

    # Raw commands as well
    /1?2R\r 

    pump.send_Command('A0')


.. figure::  ../Images/editor-tab.png
   :height: 7000px 
   :scale: 10 %
   :align: center
 
   The Editor's Tab


- **History**

  From here the user can see all the commands sent to the pump which can be devided to 2 types:

  * Commands issued by the user

  * Commands issued by the software to decide pump status

.. figure::  ../Images/history-window.png
   :height: 7000px 
   :scale: 10 %
   :align: center

   History window

- **Syringe Size**

  The user can decide the syringe size.

- **Reports**

  Gives the user an overview of the pump currently configured settings

.. figure::  ../Images/reports-window.png
   :height: 7000px 
   :scale: 10 %
   :align: center

   Reports window

- **Pump Parameters**
  
  The user can change certain parameters of the plunger movement such as "Top Velocity", "Slope" etc.

  **Port**

  The user can configure the port that the pump is connected to. This window is 
  also summoned at the start of the Pump30000
  
.. rubric:: Footnotes

.. [#f1] You can make a shortcut to Pump.exe file but do not move it outside 
         the dist folder as it depends on the dlls files located there

.. [#f2] If the executable doesn't run correctly try installing the vcredist86.exe
         (located at the root of the Pump3000 folder) and after the installation, rerun the .exe. If the 
         problem persists, `contact me <http://www.github.com/bergercookie>`_
