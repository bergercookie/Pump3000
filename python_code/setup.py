# python setup.py py2exe
# We will be using py2exe to build the binaries.
# You may use other tools, but I know this one.

from distutils.core import setup
import py2exe

# Now you need to pass arguments to setup
# windows is a list of scripts that have their own UI and
# thus don't need to run in a console.

setup(console=['Pump3000.py'],
      options={

# And now, configure py2exe by passing more options;

          'py2exe': {

# This is magic: if you don't add these, your .exe may
# or may not work on older/newer versions of windows.

              "dll_excludes": [
                  "MSVCP90.dll",
                  "MSWSOCK.dll",
                  "mswsock.dll",
                  "powrprof.dll",
                  "OLEAUT32.dll",
                  "USER32.dll",
                  "IMM32.dll",
                  "SHELL32.dll",
                  "KERNEL32.dll",
                  "WINMM.dll",
                  "COMDLG32.dll",
                  "ADVAPI32.dll",
                  "WS2_32.dll",
                  "GDI32.dll",
                  "VERSION32.dll",
                  "ole32.dll",
                  "VERSION.dll",
                  "WINSPOOL.drv",
                  ],

# Py2exe will not figure out that you need these on its own.
# You may need one, the other, or both.

              'includes': [
                  'sip',
                  'PyQt4.QtNetwork',
                  ],

              'packages': 'encodings, serial.urlhandler.protocol_loop'

            }
      },

)
