'''
GUI tool to evaluate ring diffraction patterns.
'''


import sys

from PySide import QtGui, QtCore


class Main(QtGui.QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    
    def initUI(self):
    
        self.statusBar().showMessage('Welcome')
        
        self.setGeometry(300,300,1024,768)
        self.setWindowTitle('Evaluation of Ring Diffraction Patterns')
        
        self.show()
        
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
