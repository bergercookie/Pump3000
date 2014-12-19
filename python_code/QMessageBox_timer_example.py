from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

seconds = 10	#Start counting down from 10

class myMessageBox(QMessageBox):
    
    @pyqtSlot()    
    def timeoutSlot(self):    
    
	#This is to avoid UnboundLocalError
	global seconds
	
	#Decrease seconds here
	seconds -= 1
	
	#Update QMessageBox text here
	QMessageBox.setText(self,"QMessageBox will close after "+QString.number(seconds)+" seconds")
	
	 #If reached 0,close the messagebox	
	if seconds==0:
	  QMessageBox.close(self)
   
def main():    

    app 	 = QApplication(sys.argv)
    messageBox	 = myMessageBox(0,"Auto-Close QMessagebox","QMessageBox will close after 10 seconds")
    timer	 = QTimer()
    
    messageBox.connect(timer,SIGNAL("timeout()"),
		       messageBox,SLOT("timeoutSlot()"))

    timer.start(1000)
    messageBox.show() 
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
