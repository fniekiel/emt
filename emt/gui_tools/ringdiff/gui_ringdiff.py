'''
GUI tool to evaluate ring diffraction patterns.
'''


import sys
import numpy as np

import emt.io.emd
import emt.algo.local_max
import emt.algo.distortion

from PySide import QtGui, QtCore

import pyqtgraph as pg

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class Main(QtGui.QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.gui_file = {}
        self.femd_in = None
        self.gui_localmax = {}
        
        self.plt_localmax = None
        self.plt_polar = None
        self.plt_radprof = None
        
        self.data = None
        self.dims = None
        self.points = None
        
        self.initUI()
        
    
    def initUI(self):
    
        self.statusBar().showMessage('Welcome')
        
        self.mnwid = QtGui.QWidget()
        
        self.setCentralWidget(self.mnwid)
        
        ## file informations
        frame_files = QtGui.QFrame(self.mnwid)
        frame_files.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        layout_files = QtGui.QVBoxLayout(frame_files)
        
        label_files = QtGui.QLabel('files', frame_files)
        
        hbox_files = QtGui.QHBoxLayout()
        hbox_files.addWidget(label_files)
        hbox_files.addStretch(1)
        
        self.gui_file['out_btn'] = QtGui.QPushButton('Open', frame_files)
        self.gui_file['out_btn'].clicked.connect(self.on_open_outfile)
        
        self.gui_file['out_lbl'] = QtGui.QLabel( 'evaluation file: ', frame_files )

        self.gui_file['out_txt'] = QtGui.QLineEdit( '', frame_files )
        self.gui_file['out_txt'].setReadOnly(True)

        hbox_outfile = QtGui.QHBoxLayout()
        hbox_outfile.addWidget(self.gui_file['out_lbl'])        
        hbox_outfile.addWidget(self.gui_file['out_txt'])
        hbox_outfile.addWidget(self.gui_file['out_btn'])

        self.gui_file['in_btn'] = QtGui.QPushButton('Open', frame_files)
        self.gui_file['in_btn'].clicked.connect(self.on_open_infile)
        
        self.gui_file['in_lbl'] = QtGui.QLabel( 'input emd file: ', frame_files )

        self.gui_file['in_txt'] = QtGui.QLineEdit( '', frame_files )
        self.gui_file['in_txt'].setReadOnly(True)

        hbox_infile = QtGui.QHBoxLayout()
        hbox_infile.addWidget(self.gui_file['in_lbl'])        
        hbox_infile.addWidget(self.gui_file['in_txt'])
        hbox_infile.addWidget(self.gui_file['in_btn'])
        
        layout_files.addLayout(hbox_files)
        layout_files.addLayout(hbox_outfile)
        layout_files.addLayout(hbox_infile)
        

        ## local maxima stuff
        frame_localmax = QtGui.QFrame(self.mnwid)
        frame_localmax.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        layout_localmax = QtGui.QVBoxLayout(frame_localmax)
        
        label_localmax = QtGui.QLabel('local maxima', frame_localmax)
        hbox_localmax_lbl = QtGui.QHBoxLayout()
        hbox_localmax_lbl.addWidget(label_localmax)
        hbox_localmax_lbl.addStretch(1)
        layout_localmax.addLayout(hbox_localmax_lbl)

        self.gui_localmax['lbl_lmax_r'] = QtGui.QLabel('local radius: ', frame_localmax)
        self.gui_localmax['txt_lmax_r'] = QtGui.QLineEdit( '', frame_localmax)
        hbox_lmax_r = QtGui.QHBoxLayout()
        hbox_lmax_r.addWidget(self.gui_localmax['lbl_lmax_r'])
        hbox_lmax_r.addWidget(self.gui_localmax['txt_lmax_r'])
        layout_localmax.addLayout(hbox_lmax_r)
        
        self.gui_localmax['lbl_lmax_thresh'] = QtGui.QLabel('threshold: ', frame_localmax)
        self.gui_localmax['txt_lmax_thresh'] = QtGui.QLineEdit( '', frame_localmax)
        hbox_lmax_thresh = QtGui.QHBoxLayout()
        hbox_lmax_thresh.addWidget(self.gui_localmax['lbl_lmax_thresh'])
        hbox_lmax_thresh.addWidget(self.gui_localmax['txt_lmax_thresh'])
        layout_localmax.addLayout(hbox_lmax_thresh)
        
        self.gui_localmax['lbl_lmax_cinit'] = QtGui.QLabel('init center: ')
        self.gui_localmax['txt_lmax_cinit'] = QtGui.QLineEdit( '', frame_localmax)
        hbox_lmax_cinit = QtGui.QHBoxLayout()
        hbox_lmax_cinit.addWidget(self.gui_localmax['lbl_lmax_cinit'])
        hbox_lmax_cinit.addWidget(self.gui_localmax['txt_lmax_cinit'])
        layout_localmax.addLayout(hbox_lmax_cinit)
        
        self.gui_localmax['lbl_lmax_range'] = QtGui.QLabel('radial range: ', frame_localmax)
        self.gui_localmax['txt_lmax_range'] = QtGui.QLineEdit( '', frame_localmax)
        hbox_lmax_range = QtGui.QHBoxLayout()
        hbox_lmax_range.addWidget(self.gui_localmax['lbl_lmax_range'])
        hbox_lmax_range.addWidget(self.gui_localmax['txt_lmax_range'])
        layout_localmax.addLayout(hbox_lmax_range)
        
        self.gui_localmax['min_lbl'] = QtGui.QLabel('min: ', frame_localmax)
        self.gui_localmax['min_slider'] = QtGui.QSlider(QtCore.Qt.Orientation.Horizontal, frame_localmax)
        self.gui_localmax['min_slider'].valueChanged.connect(self.on_intensitySlider)
        self.gui_localmax['min_value'] = QtGui.QLabel('0', frame_localmax)
        hbox_lmax_min = QtGui.QHBoxLayout()
        hbox_lmax_min.addWidget(self.gui_localmax['min_lbl'])
        hbox_lmax_min.addWidget(self.gui_localmax['min_slider'])
        hbox_lmax_min.addWidget(self.gui_localmax['min_value'])
        layout_localmax.addLayout(hbox_lmax_min)
        
        self.gui_localmax['max_lbl'] = QtGui.QLabel('max: ', frame_localmax)
        self.gui_localmax['max_slider'] = QtGui.QSlider(QtCore.Qt.Orientation.Horizontal, frame_localmax)
        self.gui_localmax['max_slider'].valueChanged.connect(self.on_intensitySlider)
        self.gui_localmax['max_value'] = QtGui.QLabel('0', frame_localmax)
        hbox_lmax_max = QtGui.QHBoxLayout()
        hbox_lmax_max.addWidget(self.gui_localmax['max_lbl'])
        hbox_lmax_max.addWidget(self.gui_localmax['max_slider'])
        hbox_lmax_max.addWidget(self.gui_localmax['max_value'])
        layout_localmax.addLayout(hbox_lmax_max)
        
        self.gui_localmax['upd_btn'] = QtGui.QPushButton('Update', frame_localmax)
        self.gui_localmax['upd_btn'].clicked[bool].connect(self.update_localmax)
        
        
        layout_localmax.addWidget(self.gui_localmax['upd_btn'])

        
        vbox_left = QtGui.QVBoxLayout()
        vbox_left.addWidget(frame_files)
        vbox_left.addWidget(frame_localmax)
        vbox_left.addStretch(1)
        
        
        self.plt_localmax = pg.PlotWidget()
        self.plt_localmax.setAspectLocked()
        #self.imv_localmax = pg.ImageView(view=self.plt_localmax)
        
        
        
        self.plt_polar = pg.PlotWidget()
        
        
        
        self.plt_radprof = pg.PlotWidget()
        
        
        left = QtGui.QWidget(self.mnwid)
        hbox_left = QtGui.QHBoxLayout(left)
        hbox_left.addLayout(vbox_left)
        
        #hbox.addWidget(self.imv_localmax)
        #hbox.addStretch(1)
        
        self.right = QtGui.QTabWidget(self.mnwid)
        self.right.addTab(self.plt_localmax, 'Local Maxima')
        self.right.addTab(self.plt_polar, 'Polar Plot')
        self.right.addTab(self.plt_radprof, 'Radial Profile')
        #hbox_right = QtGui.QHBoxLayout(self.right)
        #hbox_right.addWidget(self.imv_localmax)
        
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(self.right)
        splitter.setStretchFactor(0, 0.2)
        splitter.setStretchFactor(1, 1.0)   
        
        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(splitter)
        
        self.mnwid.setLayout(hbox)
        
        self.setGeometry(300,300,1024,512)
        self.setWindowTitle('Evaluation of Ring Diffraction Patterns')
        
        self.show()
        
        
    def keyPressEvent(self, e):
        
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
            
    def on_open_outfile(self):
        '''
        Open or create an EMD file to hold the evaluation.
        '''
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open/create EMD file', filter='EMD files (*.emd);;All files (*.*)')
        try:
            
            self.gui_file['out_txt'].setText(fname)
        except: 
            self.gui_file['out_txt'].setText('')
            pass
    
            
    def on_open_infile(self):
        '''
        Open an EMD file with input images.
        '''
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open EMD file', filter='EMD files (*.emd);;All files (*.*)')
        try:
            self.femd_in = emt.io.emd.fileEMD(fname, readonly=True)
            
            self.gui_file['in_txt'].setText(fname)
            
            data, dims = self.femd_in.get_emdgroup(self.femd_in.list_emds[0])
            
            #data = np.swapaxes(data, 0,2)
            #data = np.swapaxes(data, 1,2)
            
            self.data = np.copy(data)
            self.dims = dims
            
            
            self.gui_localmax['min_slider'].setMinimum(np.min(self.data))
            self.gui_localmax['min_slider'].setMaximum(np.max(self.data))
            
            self.gui_localmax['max_slider'].setMinimum(np.min(self.data))
            self.gui_localmax['max_slider'].setMaximum(np.max(self.data))
            
            
            self.plt_localmax.clear()
            img = pg.ImageItem(self.data[:,:,0].astype('float64'), levels=(self.gui_localmax['min_slider'].value(), self.gui_localmax['max_slider'].value()))
            img.setZValue(-100)
            self.test_img = img
            self.plt_localmax.addItem(img)
            
        except: 
            self.gui_file['in_txt'].setText('')
            raise
    
    
    def on_intensitySlider(self):
        self.gui_localmax['min_value'].setText('{:d}'.format(self.gui_localmax['min_slider'].value()))
        self.gui_localmax['max_value'].setText('{:d}'.format(self.gui_localmax['max_slider'].value()))      
        self.test_img.setLevels( (self.gui_localmax['min_slider'].value(), self.gui_localmax['max_slider'].value()) )


    def update_localmax(self):
        
        if not self.femd_in is None:
        
            # parse the input
            try:
                max_r = float(self.gui_localmax['txt_lmax_r'].text())
                thresh = float(self.gui_localmax['txt_lmax_thresh'].text())
                cinit = [float(item.strip()) for item in self.gui_localmax['txt_lmax_cinit'].text().split(',')]
                rrange = [float(item.strip()) for item in self.gui_localmax['txt_lmax_range'].text().split(',')]
                
                assert(len(cinit)==2)
                assert(len(rrange)==2)
                
            except:
                raise
        
            data = np.copy(self.data[:,:,0])

            # find local max
            points = emt.algo.local_max.local_max(data, max_r, thresh)
            
            # working in px for now
            
            # filter to single ring
            points = emt.algo.distortion.filter_ring(points, cinit, rrange)
        
            self.points = np.copy(points)
        
            self.plt_localmax.clear()
            self.plt_localmax.plot(points[:,1], points[:,0], pen=None, symbol='o', symbolPen=(255,0,0), symbolBrush=None)
            
            img = pg.ImageItem(self.data[:,:,0].astype('float64'), levels=(self.gui_localmax['min_slider'].value(), self.gui_localmax['max_slider'].value()))
            img.setZValue(-100)
            self.test_img = img
            self.plt_localmax.addItem(img)
            
            #img.setRect(pg.QtCore.QRectF(0,0,2047,2047))
            

            #import pdb;pdb.set_trace()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
