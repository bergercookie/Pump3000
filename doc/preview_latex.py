#!/usr/bin/env python
# Fri Jun 13 17:35:22 EEST 2014, nickkouk

import sys
import time
from subprocess import call

while True:
    try:
        latex_file = sys.argv[1]
        call(["latex", latex_file])
        call(["open", latex_file[:-3] + "pdf"])
        time.sleep(60)

    except IndexError:
        print "No Arguement Given!"
        break
    except:
        pass


