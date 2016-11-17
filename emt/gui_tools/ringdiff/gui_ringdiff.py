'''
GUI tool to evaluate ring diffraction patterns.
'''


import sys
import numpy as np

import emt.io.emd
import emt.algo.local_max
import emt.algo.distortion
import emt.algo.radial_profile

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
        self.gui_polar = {}
        self.gui_radprof = {}
        
        self.plt_localmax = None
        self.plt_localmax_img = None
        self.plt_polar = None
        self.plt_radprof = None
        
        self.data = None
        self.dims = None
        self.settings = {}
        self.points = None
        self.center = None
        self.dists = None
        self.radprof = None
        
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
        
        self.gui_localmax['lmax_btn'] = QtGui.QPushButton('Find Local Maxima', frame_localmax)
        self.gui_localmax['lmax_btn'].clicked.connect(self.on_localmax)
        layout_localmax.addWidget(self.gui_localmax['lmax_btn'])
        
        self.gui_localmax['min_lbl'] = QtGui.QLabel('min: ', frame_localmax)
        self.gui_localmax['min_slider'] = QtGui.QSlider(QtCore.Qt.Orientation.Horizontal, frame_localmax)
        self.gui_localmax['min_slider'].setMinimum(0)
        self.gui_localmax['min_slider'].setMaximum(0)
        self.gui_localmax['min_slider'].valueChanged.connect(self.on_intensitySlider)
        self.gui_localmax['min_value'] = QtGui.QLabel('0', frame_localmax)
        hbox_lmax_min = QtGui.QHBoxLayout()
        hbox_lmax_min.addWidget(self.gui_localmax['min_lbl'])
        hbox_lmax_min.addWidget(self.gui_localmax['min_slider'])
        hbox_lmax_min.addWidget(self.gui_localmax['min_value'])
        layout_localmax.addLayout(hbox_lmax_min)
        
        self.gui_localmax['max_lbl'] = QtGui.QLabel('max: ', frame_localmax)
        self.gui_localmax['max_slider'] = QtGui.QSlider(QtCore.Qt.Orientation.Horizontal, frame_localmax)
        self.gui_localmax['max_slider'].setMinimum(0)
        self.gui_localmax['max_slider'].setMaximum(0)
        self.gui_localmax['max_slider'].valueChanged.connect(self.on_intensitySlider)
        self.gui_localmax['max_value'] = QtGui.QLabel('0', frame_localmax)
        hbox_lmax_max = QtGui.QHBoxLayout()
        hbox_lmax_max.addWidget(self.gui_localmax['max_lbl'])
        hbox_lmax_max.addWidget(self.gui_localmax['max_slider'])
        hbox_lmax_max.addWidget(self.gui_localmax['max_value'])
        layout_localmax.addLayout(hbox_lmax_max)
        
        #self.gui_localmax['upd_btn'] = QtGui.QPushButton('Update', frame_localmax)
        #self.gui_localmax['upd_btn'].clicked.connect(self.update_localmax)
        #layout_localmax.addWidget(self.gui_localmax['upd_btn'])


        ## polar plot stuff
        frame_polar = QtGui.QFrame(self.mnwid)
        frame_polar.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        layout_polar = QtGui.QVBoxLayout(frame_polar)
        
        label_polar = QtGui.QLabel('polar plot', frame_polar)
        hbox_polar_lbl = QtGui.QHBoxLayout()
        hbox_polar_lbl.addWidget(label_polar)
        hbox_polar_lbl.addStretch(1)
        layout_polar.addLayout(hbox_polar_lbl) 
        
        self.gui_polar['center_lbl'] = QtGui.QLabel('center: ', frame_polar)
        self.gui_polar['cencpy_btn'] = QtGui.QPushButton('Copy Init', frame_polar)
        self.gui_polar['cencpy_btn'].clicked.connect(self.on_copyCenter)
        hbox_polar_center = QtGui.QHBoxLayout()
        hbox_polar_center.addWidget(self.gui_polar['center_lbl'])
        hbox_polar_center.addWidget(self.gui_polar['cencpy_btn'])
        layout_polar.addLayout(hbox_polar_center)
        
        self.gui_polar['cenopt_btn'] = QtGui.QPushButton('Optimize Center', frame_polar)
        self.gui_polar['cenopt_btn'].clicked.connect(self.on_optimizeCenter)
        layout_polar.addWidget(self.gui_polar['cenopt_btn'])
        
        self.gui_polar['dist_lbl'] = QtGui.QLabel('distortion orders: ', frame_polar)
        self.gui_polar['dist_txt'] = QtGui.QLineEdit('', frame_polar)
        hbox_polar_dists = QtGui.QHBoxLayout()
        hbox_polar_dists.addWidget(self.gui_polar['dist_lbl'])
        hbox_polar_dists.addWidget(self.gui_polar['dist_txt'])
        layout_polar.addLayout(hbox_polar_dists)
        
        self.gui_polar['dists_btn'] = QtGui.QPushButton('Fit Distortions', frame_polar)
        self.gui_polar['dists_btn'].clicked.connect(self.on_fitDist)
        layout_polar.addWidget(self.gui_polar['dists_btn'])
        
        #self.gui_polar['upd_btn'] = QtGui.QPushButton('Update', frame_polar)
        #self.gui_polar['upd_btn'].clicked.connect(self.update_polar)
        #layout_polar.addWidget(self.gui_polar['upd_btn'])
        
        
        ## radial profile stuff
        frame_radprof = QtGui.QFrame(self.mnwid)
        frame_radprof.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        layout_radprof = QtGui.QVBoxLayout(frame_radprof)
        
        label_radprof = QtGui.QLabel('radial profile', frame_radprof)
        hbox_radprof_lbl = QtGui.QHBoxLayout()
        hbox_radprof_lbl.addWidget(label_radprof)
        hbox_radprof_lbl.addStretch(1)
        layout_radprof.addLayout(hbox_radprof_lbl)
        
        self.gui_radprof['rad_lbl'] = QtGui.QLabel('r_max, dr, sigma: (opt.)', frame_radprof)
        self.gui_radprof['rad_txt'] = QtGui.QLineEdit('', frame_radprof)
        hbox_radprof_rad = QtGui.QHBoxLayout()
        hbox_radprof_rad.addWidget(self.gui_radprof['rad_lbl'])
        hbox_radprof_rad.addWidget(self.gui_radprof['rad_txt'])
        layout_radprof.addLayout(hbox_radprof_rad)
        
        self.gui_radprof['crct_check'] = QtGui.QCheckBox('correct distortions', frame_radprof)
        self.gui_radprof['mask_btn'] = QtGui.QPushButton('Mask', frame_radprof)
        self.gui_radprof['mask_btn'].clicked.connect(self.on_mask)
        hbox_radprof_dist = QtGui.QHBoxLayout()
        hbox_radprof_dist.addWidget(self.gui_radprof['crct_check'])
        hbox_radprof_dist.addWidget(self.gui_radprof['mask_btn'])
        layout_radprof.addLayout(hbox_radprof_dist)
        
        self.gui_radprof['ext_btn'] = QtGui.QPushButton('Extract', frame_radprof)
        self.gui_radprof['ext_btn'].clicked.connect(self.on_extractRadProf)
        layout_radprof.addWidget(self.gui_radprof['ext_btn'])
        
        vbox_left = QtGui.QVBoxLayout()
        vbox_left.addWidget(frame_files)
        vbox_left.addWidget(frame_localmax)
        vbox_left.addWidget(frame_polar)
        vbox_left.addWidget(frame_radprof)
        vbox_left.addStretch(1)
        
        
        self.plt_localmax = pg.PlotWidget()
        self.plt_localmax.setAspectLocked(True)
        self.plt_localmax.invertY(True)
        
        
        self.plt_polar = pg.PlotWidget()
        self.plt_polar.setMouseEnabled(x=False, y=True)
        self.plt_polar.setXRange(-np.pi, np.pi)
        axis1 = self.plt_polar.getAxis('bottom')
        axis1.setLabel('theta','rad')
        axis2 = self.plt_polar.getAxis('left')
        axis2.setLabel('r')
        
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
        
        self.setGeometry(300,300,1024+512,1024)
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
            
            self.data = np.copy(data[:,:,0])
            self.dims = dims[0:2]
            
            min_data = np.min(self.data)
            max_data = np.max(self.data)
            
            self.gui_localmax['min_slider'].setMinimum(min_data)
            self.gui_localmax['min_slider'].setMaximum(max_data)
            self.gui_localmax['min_slider'].setValue(min_data)
            
            self.gui_localmax['max_slider'].setMinimum(min_data)
            self.gui_localmax['max_slider'].setMaximum(max_data)
            self.gui_localmax['max_slider'].setValue(max_data)
            
            
            self.update_localmax()
            
        except: 
            self.gui_file['in_txt'].setText('')
            raise
    
    
    
    def on_intensitySlider(self):
        '''
        Intensity sliders to change the img plot in local maxima.
        '''
        
        # get values
        min_val = self.gui_localmax['min_slider'].value()
        max_val = self.gui_localmax['max_slider'].value()
        
        # update labels
        self.gui_localmax['min_value'].setText('{:d}'.format(min_val))
        self.gui_localmax['max_value'].setText('{:d}'.format(max_val))     
         
        # update plot
        self.plt_localmax_img.setLevels( (min_val, max_val) )
        
        # update settings
        self.settings['plt_imgminmax'] = (min_val, max_val)



    def update_localmax(self):
        '''
        Update the localmax plot view.
        '''
        
        # update plot in local maxima
        self.plt_localmax.clear()
        
        if not self.data is None:
        
            # set axis
            axis1 = self.plt_localmax.getAxis('bottom')
            axis1.setLabel(self.dims[0][1], self.dims[0][2])
            axis2 = self.plt_localmax.getAxis('left')
            axis2.setLabel(self.dims[1][1], self.dims[1][2])
           
            # plot image
            self.plt_localmax_img = pg.ImageItem(self.data.astype('float64'), levels=(self.gui_localmax['min_slider'].value(), self.gui_localmax['max_slider'].value()))
            self.plt_localmax_img.setZValue(-100)
            self.plt_localmax_img.setRect(pg.QtCore.QRectF( self.dims[0][0][0],self.dims[1][0][0],self.dims[0][0][-1]-self.dims[0][0][0],self.dims[1][0][-1]-self.dims[1][0][0]))
            self.plt_localmax.addItem(self.plt_localmax_img)
            
            if not self.points is None:
            
                # draw points
                self.plt_localmax.plot(self.points[:,0], self.points[:,1], pen=None, symbol='o', symbolPen=(255,0,0), symbolBrush=None)



    def on_localmax(self):
        '''
        Calculate local maxima.
        '''
    
        # parse the input
        try:
            max_r = float(self.gui_localmax['txt_lmax_r'].text())
            thresh = float(self.gui_localmax['txt_lmax_thresh'].text())
                
            cinit = self.gui_localmax['txt_lmax_cinit'].text().strip()
            rrange = self.gui_localmax['txt_lmax_range'].text().strip()
                
            if cinit == '' and rrange == '':
                cinit = []
                rrange = []
            else:
                cinit = [float(item.strip()) for item in cinit.split(',')]
                rrange = [float(item.strip()) for item in rrange.split(',')]
                assert(len(cinit)==2 and len(rrange)==2)
                
        except:
            raise TypeError('Bad input to local maxima')

        # update settings
        self.settings['lmax_r'] = max_r
        self.settings['lmax_thresh'] = thresh
        self.settings['lmax_cinit'] = cinit
        self.settings['lmax_range'] = rrange
            
        # find local max
        points = emt.algo.local_max.local_max(self.data, self.settings['lmax_r'], self.settings['lmax_thresh'])
        points = emt.algo.local_max.points_todim(points, self.dims)
                
        # filter to single ring if input provided
        if (len(self.settings['lmax_cinit'])==2 and len(self.settings['lmax_range'])==2):
            points = emt.algo.distortion.filter_ring(points, self.settings['lmax_cinit'], self.settings['lmax_range'])
        
        # save points in main
        self.points = points
        
        # update localmax view
        self.update_localmax() 
            
            
    
    def update_polar(self):
        '''
        Update the polar plot depending on which data is present.
        '''
        
        self.plt_polar.clear()
        
        if not self.center is None:
            # update center in left column
            self.gui_polar['center_lbl'].setText('center: ({:.3f}, {:.3f})'.format(self.center[0], self.center[1]))
        
            if not self.points is None:
                points_plr = emt.algo.distortion.points_topolar(self.points, self.center)
        
                # horizontal mean line
                self.plt_polar.plot( [-np.pi, np.pi], [np.mean(points_plr[:,0]), np.mean(points_plr[:,0])], pen=pg.mkPen('k', style=QtCore.Qt.DashLine))
                
                # uncorrected radial positions
                self.plt_polar.plot(points_plr[:,1], points_plr[:,0], pen=None, symbol='x', symbolPen=(255,0,0), symbolBrush=None)
        
                if not self.dists is None:
                    
                    xpl_ell = np.linspace(-np.pi, np.pi, 200)
                    # single distortions
                    for i in range(len(self.settings['ns'])):
                        self.plt_polar.plot( xpl_ell, self.dists[0]*emt.algo.distortion.rad_dis(xpl_ell, self.dists[i*2+1], self.dists[i*2+2], self.settings['ns'][i]), pen=pg.mkPen('m', style=QtCore.Qt.DashLine) )
                    
                    # sum of distortions
                    sum_dists = self.dists[0]*np.ones(xpl_ell.shape)
                    for i in range(len(self.settings['ns'])):
                        sum_dists *= emt.algo.distortion.rad_dis( xpl_ell, self.dists[i*2+1], self.dists[i*2+2], self.settings['ns'][i])
                    self.plt_polar.plot( xpl_ell, sum_dists, pen=(0,0,255))

                    # corrected radial positions
                    points_plr_corr = np.copy(points_plr)
                    for i in range(len(self.settings['ns'])):
                        points_plr_corr[:,0] /= emt.algo.distortion.rad_dis(points_plr_corr[:,1], self.dists[i*2+1], self.dists[i*2+2], self.settings['ns'][i])
                    
                    self.plt_polar.plot( points_plr_corr[:,1], points_plr_corr[:,0], pen=None, symbol='x', symbolPen=(0,180,0), symbolBrush=None) 





    def on_copyCenter(self):
        
        try:
            cinit = self.gui_localmax['txt_lmax_cinit'].text().strip()   
            if cinit == '':
                cinit = []
            else:
                cinit = [float(item.strip()) for item in cinit.split(',')]
                assert(len(cinit)==2)
        except:
            raise TypeError('Bad input to local maxima')
            
        if len(cinit) == 0:
            print('No initial guess given.')
        else:
            self.settings['lmax_cinit'] = cinit
            self.center=np.array(cinit)

        self.update_polar()
        


    def on_optimizeCenter(self):
    
        center = emt.algo.distortion.optimize_center(self.points, self.center)
        self.center= center
        
        self.update_polar()
        
        
        
    def on_fitDist(self):
        
        try:
            ns = self.gui_polar['dist_txt'].text().strip()
            if ns == '':
                ns = []
            else:
                ns = [int(item.strip()) for item in ns.split(',')]
        except:
            raise TypeError('Bad input in ')
            
        # update setting
        self.settings['ns'] = ns 
       
        # run optimization
        if len(ns) >= 1:
            points_plr = emt.algo.distortion.points_topolar(self.points, self.center)
            dists = emt.algo.distortion.optimize_distortion(points_plr, self.settings['ns'])
            
            self.dists = dists
            
        self.update_polar()
        
        
    
    def update_RadProf(self):
        
        self.plt_radprof.clear()
        
        if not self.radprof is None:
            
            self.plt_radprof.plot(self.radprof[:,0], self.radprof[:,1], pen=(255,0,0))
        
        
    
    def on_extractRadProf(self):
        '''
        Extract the radial profile from the diffraction pattern.
        '''
        
        try:
            pars = self.gui_radprof['rad_txt'].text().strip()
            if pars == '':
                pars = []
            else:
                pars = [float(item.strip()) for item in pars.split(',')]
                assert(len(pars)==3)
        except:
            raise TypeError('Bad input in ')
        
        
        if len(pars) == 0:
            self.settings['rad_rmax'] = np.abs(self.dims[0][0][0]-self.dims[0][0][1])*np.min(self.data.shape)/2.0
            self.settings['rad_dr'] = np.abs(self.dims[0][0][0]-self.dims[0][0][1])/10.
            self.settings['rad_sigma'] = np.abs(self.dims[0][0][0]-self.dims[0][0][1])
        else:
            self.settings['rad_rmax'] = pars[0]
            self.settings['rad_dr'] = pars[1]
            self.settings['rad_sigma'] = pars[2]
        
        
        # get the polar coordinate system
        if self.gui_radprof['crct_check'].isChecked():
            rs, thes = emt.algo.radial_profile.calc_polarcoords( self.center, self.dims, self.settings['ns'], self.dists )
        else:
            rs, thes = emt.algo.radial_profile.calc_polarcoords( self.center, self.dims )
        
        # get the radial profile
        R, I = emt.algo.radial_profile.calc_radialprofile( self.data, rs, self.settings['rad_rmax'], self.settings['rad_dr'], self.settings['rad_sigma'] )
        
        # save in main
        self.radprof = np.array([R,I]).transpose()
    
        # update the plot
        self.update_RadProf()
    
        import pdb;pdb.set_trace()
    
    
    def on_mask(self):
        pass

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
