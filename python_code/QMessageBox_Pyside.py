from PySide.QtGui import *
from PySide.QtCore import *
import sys

seconds = 10	#Start counting down from 10

class myMessageBox(QMessageBox):
    
    @Slot()    
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

# class Form(QDialog):

    #def __init__(self, parent=None):
        #super(Form, self).__init__(parent)

        #self.lineedit.setFocus()
        #self.myline = QLineEdit("")
        #self.myline.setText(b'/1c\x40i\x001')
        #layout.addWidget(self.myline)

        #self.connect(self.lineedit, SIGNAL("returnPressed()"), self.updateUi)
        #self.setWindowTitle("Calculate")

        #self.connect(self.lineedit, SIGNAL("returnPressed()"), self.fun)
        #self.connect(self.button, SIGNAL("clicked()"), self.fun2)

        #QMessageBox
def main():    

    app 	 = QApplication(sys.argv)
    messageBox	 = myMessageBox(app,"Auto-Close QMessagebox","QMessageBox will close after 10 seconds")
    timer	 = QTimer()
    
    messageBox.connect(timer,SIGNAL("timeout()"),
		       messageBox,SLOT("timeoutSlot()"))

    timer.start(1000)
    messageBox.show() 
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
