'''
Tests for the evaluation of ring diffraction patterns.
'''

import unittest
import numpy as np
import matplotlib.pyplot as plt
import os

import emt.io.emd
import emt.algo.local_max
import emt.algo.math
import emt.eva.ring_diff


class test_ringdiff(unittest.TestCase):
    '''
    Test the evaluation of ring diffraction patterns.
    '''
    
    def test_local_max(self):
        '''
        Test the local_maxima algorithm to be used for ring diffraction patterns.
        '''
        
        plt.close('all')        
        show=False
        
        # get an image
        femd = emt.io.emd.fileEMD('resources/Pt_SAED_D910mm_single/Pt_SAED_D910mm_single.emd')
        data, dims = femd.get_emdgroup(femd.list_emds[0])
        
        img = data[:,:,0]
        dims = dims[0:2]
        
        
        ## local_max
        # not working
        with self.assertRaises(TypeError):
            points = emt.algo.local_max.local_max(42, 10, 600)
        with self.assertRaises(TypeError):
            points = emt.algo.local_max.local_max(img, 'ten', 600)
        with self.assertRaises(TypeError):
            points = emt.algo.local_max.local_max(img, 10, 'sixhundred')
            
        # no points detected
        self.assertIsNone (emt.algo.local_max.local_max(img, 10, 100000))
        
        # working
        points = emt.algo.local_max.local_max(img, 10, 600)
        self.assertIsNotNone(points)
        
        
        ## plot_points
        # not working
        with self.assertRaises(TypeError):
            plot = emt.algo.local_max.plot_points(42, points)
        with self.assertRaises(TypeError):
            plot = emt.algo.local_max.plot_points(img, np.array([[0,1,2,3,4],[5,6,7,8,9]]))
            
        # px coords, non inverted
        plot = emt.algo.local_max.plot_points(img, points, vminmax=(0.0,0.2), show=show)
        
        
        ## points_todim
        # not working
        with self.assertRaises(TypeError):
            points = emt.algo.local_max.points_todim([0,1,2,3,5], dims)
        with self.assertRaises(TypeError):
            points = emt.algo.local_max.points_todim(points, dims[0])
        
        # convert points to real dim
        point = emt.algo.local_max.points_todim((0,0), dims)
        points = emt.algo.local_max.points_todim(points, dims)
        
        # real coords, inverted
        plot = emt.algo.local_max.plot_points(img, points, vminmax=(0.0,0.2), dims=dims, invert=True, show=show)
        
        
        # wait for plots
        if show:
            plt.show()
    
    
    def test_distortion(self):
        '''
        Test the distortion fitting algorithms to be used on ring diffraction patterns.
        '''
        
        plt.close('all')
        show=False
        
        # get an image
        femd = emt.io.emd.fileEMD('resources/Pt_SAED_D910mm_single/Pt_SAED_D910mm_single.emd')
        data, dims = femd.get_emdgroup(femd.list_emds[0])
        
        img = data[:,:,0]
        dims = dims[0:2]
        
        # and a list of maxima
        points = emt.algo.local_max.local_max(img, 10, 600)
        points = emt.algo.local_max.points_todim(points, dims)
        
        # parameters
        center_init = emt.algo.local_max.points_todim((984,1032), dims)
        
        
        ## filter_ring
        # wrong input
        with self.assertRaises(TypeError):
            nopoints = emt.algo.distortion.filter_ring(np.array([[0,1,2,3,4],[5,6,7,8,9]]), center_init, (6e9, 8e9))
        with self.assertRaises(TypeError):
            nopoints = emt.algo.distortion.filter_ring(42, center_init, (6e9, 8e9))    
        with self.assertRaises(TypeError):
            nopoints = emt.algo.distortion.filter_ring(points, (1,2,3,4), (6e9, 8e9))        
            
        # no points
        nopoints = emt.algo.distortion.filter_ring(points, center_init, (8e9, 6e9))
        self.assertIsNone(nopoints)
        
        # feed through center
        self.assertTrue(np.array_equal(center_init, emt.algo.distortion.filter_ring(center_init, center_init, (0,0))))
        
        # working
        points = emt.algo.distortion.filter_ring(points, (center_init[0,0], center_init[0,1]), (6e9, 8e9))
        self.assertIsNotNone(points)
        points = emt.algo.distortion.filter_ring(points, center_init, (6e9, 8e9))
        self.assertIsNotNone(points)
        
        
        ## points_topolar
        # wrong input
        with self.assertRaises(TypeError):
            nopoints_plr = emt.algo.distortion.points_topolar(42, center_init)
        with self.assertRaises(TypeError):
            nopoints_plr = emt.algo.distortion.points_topolar(points, (1,2,3))
        with self.assertRaises(TypeError):
            nopoints_plr = emt.algo.distortion.points_topolar(np.array([[0,1,2],[3,4,5],[6,7,8]]), center_init)
        
        # working
        points_plr = emt.algo.distortion.points_topolar(points, center_init)
        
        
        ## plot_ringpolar
        # wrong input
        with self.assertRaises(TypeError):
            noplot = emt.algo.distortion.plot_ringpolar(np.array([0,1,2,3,4]), dims)
        with self.assertRaises(TypeError):
            noplot = emt.algo.distortion.plot_ringpolar(42, dims)
        with self.assertRaises(TypeError):
            noplot = emt.algo.distortion.plot_ringpolar(points_plr, dims[0])
        with self.assertRaises(TypeError):
            noplot = emt.algo.distortion.plot_ringpolar(points_plr, 42)
                    
        # working
        plot = emt.algo.distortion.plot_ringpolar(points_plr, dims, show=show)
        
        
        ## optimize_center
        # wrong input
        with self.assertRaises(TypeError):
            nocenter = emt.algo.distortion.optimize_center(np.array([0,1,2,3,4]), center_init)
        with self.assertRaises(TypeError):
            nocenter = emt.algo.distortion.optimize_center(42, center_init)
        with self.assertRaises(TypeError):
            nocenter = emt.algo.distortion.optimize_center(points, (1,2,3,4,5))
        with self.assertRaises(TypeError):
            nocenter = emt.algo.distortion.optimize_center(points, 'string')
        
        # get warning
        #center = emt.algo.distortion.optimize_center(points, center_init, maxfev=1)
        # working
        center = emt.algo.distortion.optimize_center(points, center_init, verbose=True)
        
        points_plr = emt.algo.distortion.points_topolar(points, center)
        plot = emt.algo.distortion.plot_ringpolar(points_plr, dims, show=show)
    
        ## optimize_distortion
        # wrong input
        with self.assertRaises(TypeError):
            nodists = emt.algo.distortion.optimize_distortion(np.array([[0,1,2,3,4],[5,6,7,8]]), (2,3,4))
        with self.assertRaises(TypeError):
            nodists = emt.algo.distortion.optimize_distortion(42, (2,3,4))        
        with self.assertRaises(TypeError):
            nodists = emt.algo.distortion.optimize_distortion(points_plr, 2)
            
        # working
        dists = emt.algo.distortion.optimize_distortion(points_plr, (2,3,4))
        
        ## plot_distpolar
        # wrong input
        with self.assertRaises(TypeError):
            noplot = emt.algo.distortion.plot_distpolar(np.array([[0,1,2,3],[4,5,6,7]]), dims, dists, (2,3,4))
        with self.assertRaises(TypeError):
            noplot = emt.algo.distortion.plot_distpolar(42, dims, dists, (2,3,4))
        with self.assertRaises(TypeError):
            noplot = emt.algo.distortion.plot_distpolar(points_plr, dims[0], dists, (2,3,4))
        with self.assertRaises(TypeError):
            noplot = emt.algo.distortion.plot_distpolar(points_plr, dims, dists[0:3], (2,3,4))
        with self.assertRaises(TypeError):
            noplot = emt.algo.distortion.plot_distpolar(points_plr, dims, dists, 42)


        ## corrected images
        img_corr = emt.algo.radial_profile.correct_distortion( img, dims, center, (2,3,4), dists )

        import pdb;pdb.set_trace()
        
        # try a bunch of fits
        for ns in ( (2,), (2,3), (2,3,4), (2,3,4,5), (4,) ):
     
            dists = emt.algo.distortion.optimize_distortion(points_plr, ns, verbose=True)
            plot = emt.algo.distortion.plot_distpolar(points_plr, dims, dists, ns, show=show)
            

        # wait for plots
        if show:
            plt.show()
    
    
    #def test_radialprofile(self):
        '''
        Test the radial_profile algorithms to be used on ring diffraction patterns.
        '''
        
        plt.close('all')        
        show=True
        
        # get an image
        femd = emt.io.emd.fileEMD('resources/Pt_SAED_D910mm_single/Pt_SAED_D910mm_single.emd')
        data, dims = femd.get_emdgroup(femd.list_emds[0])
        
        img = data[:,:,0]
        dims = dims[0:2]
        
        # points on a ring
        points = emt.algo.local_max.local_max(img, 10, 600)
        points = emt.algo.local_max.points_todim(points, dims)
        center_init = emt.algo.local_max.points_todim((984,1032), dims)
        points = emt.algo.distortion.filter_ring(points, center_init, (6e9, 8e9))
        
        # optimize center
        center = emt.algo.distortion.optimize_center(points, center_init, verbose=True)
        
        # fit distortions
        ns = (2,3,4)
        points_plr = emt.algo.distortion.points_topolar(points, center)
        dists = emt.algo.distortion.optimize_distortion(points_plr, ns)
        
        # check input
        plot = emt.algo.distortion.plot_distpolar(points_plr, dims, dists, ns, show=show)
        
        
        ## calc_polarcoords
        # wrong input
        with self.assertRaises(TypeError):
            nors, nothes = emt.algo.radial_profile.calc_polarcoords( (1,2,3,4,5) )
        with self.assertRaises(TypeError):
            nors, nothes = emt.algo.radial_profile.calc_polarcoords( center, dims[0] )
        with self.assertRaises(TypeError):
            nors, nothes = emt.algo.radial_profile.calc_polarcoords( center, dims, ns )            
        with self.assertRaises(TypeError):
            nors, nothes = emt.algo.radial_profile.calc_polarcoords( center, dims, 42, dists )                    
        with self.assertRaises(TypeError):
            nors, nothes = emt.algo.radial_profile.calc_polarcoords( center, dims, ns, dists[0:5] )

        # working
        rs_nodist, thes_nodist = emt.algo.radial_profile.calc_polarcoords( center, dims )
        rs, thes = emt.algo.radial_profile.calc_polarcoords( center, dims, ns, dists )


        ## calc_radialprofile
        rMax = np.abs(dims[0][0][0]-dims[0][0][1])*np.min(img.shape)/2.0
        dr = np.abs(dims[0][0][0]-dims[0][0][1])/10.
        rsigma = np.abs(dims[0][0][0]-dims[0][0][1])
        # wrong input
        with self.assertRaises(TypeError):
            noR, noI = emt.algo.radial_profile.calc_radialprofile( 42, rs, rMax, dr, rsigma )
        with self.assertRaises(TypeError):
            noR, noI = emt.algo.radial_profile.calc_radialprofile( img, 42, rMax, dr, rsigma )
        with self.assertRaises(TypeError):
            noR, noI = emt.algo.radial_profile.calc_radialprofile( img, rs[0:25,0:25], rMax, dr, rsigma )
        with self.assertRaises(TypeError):
            noR, noI = emt.algo.radial_profile.calc_radialprofile( img, rs, 'one', dr, rsigma )
        with self.assertRaises(TypeError):
            noR, noI = emt.algo.radial_profile.calc_radialprofile( img, rs, rMax, 'two', rsigma )
        with self.assertRaises(TypeError):
            noR, noI = emt.algo.radial_profile.calc_radialprofile( img, rs, rMax, dr, 'three' )
        with self.assertRaises(TypeError):
            noR, noI = emt.algo.radial_profile.calc_radialprofile( img, rs, rMax, dr, rsigma, mask=42 )
        with self.assertRaises(TypeError):
            noR, noI = emt.algo.radial_profile.calc_radialprofile( img, rs, rMax, dr, rsigma, mask=np.ones((25,25)) )
                                                
        # working
        R, I = emt.algo.radial_profile.calc_radialprofile( img, rs, rMax, dr, rsigma )
        
        # everything masked
        emR, emI = emt.algo.radial_profile.calc_radialprofile( img, rs, rMax, dr, rsigma, mask=np.zeros(img.shape) )


        ## plot_radialprofile
        # wrong input
        with self.assertRaises(TypeError):
            noplot = emt.algo.radial_profile.plot_radialprofile( 42, I, dims )
        with self.assertRaises(TypeError):
            noplot = emt.algo.radial_profile.plot_radialprofile( R, 42, dims )
        with self.assertRaises(TypeError):
            noplot = emt.algo.radial_profile.plot_radialprofile( R, I, 'notdims' )
        
        # working
        plot = emt.algo.radial_profile.plot_radialprofile( R, I, dims, show=show) 
        plot = emt.algo.radial_profile.plot_radialprofile( emR, emI, dims, show=show)
        
        
        ## compare without distortion correction
        R_nodist, I_nodist = emt.algo.radial_profile.calc_radialprofile( img, rs_nodist, rMax, dr, rsigma )
        plot = emt.algo.radial_profile.plot_radialprofile( R_nodist, I_nodist, dims, show=show)
        
        
        # cut radial profile
        sel = (R>=1.5e9)*(R<=9.5e9)
        I = I[sel]
        R = R[sel]
        

        ## fit_radialprofile
        funcs = [ 'const', 'powlaw', 'voigt' ]
        init_guess = (  10,
                        1.0e12, -1.0,
                        5e10, 7.3e9, 1.1e7, 2.5e7 )
        
        # wrong input
        with self.assertRaises(TypeError):
            nores = emt.algo.radial_profile.fit_radialprofile( 42, I, funcs, init_guess )
        with self.assertRaises(TypeError):
            nores = emt.algo.radial_profile.fit_radialprofile( R, 42, funcs, init_guess )
        with self.assertRaises(TypeError):
            nores = emt.algo.radial_profile.fit_radialprofile( R, I[0:25], funcs, init_guess )
        with self.assertRaises(TypeError):
            nores = emt.algo.radial_profile.fit_radialprofile( R, I, funcs, init_guess[0:3] )
        with self.assertRaises(TypeError):
            nores = emt.algo.radial_profile.fit_radialprofile( R, I, 42, init_guess )
        
        # working
        res = emt.algo.radial_profile.fit_radialprofile( R, I, funcs, init_guess, maxfev=10000 ) 
                 
        
        ## plot_fit
        # wrong input
        with self.assertRaises(TypeError):
            noplot = emt.algo.radial_profile.plot_fit( 42, I, dims, funcs, res )
        with self.assertRaises(TypeError):
            noplot = emt.algo.radial_profile.plot_fit( R, 42, dims, funcs, res )
        with self.assertRaises(TypeError):
            noplot = emt.algo.radial_profile.plot_fit( R, I, 'notdims', funcs, res )
        with self.assertRaises(TypeError):
            noplot = emt.algo.radial_profile.plot_fit( R, I, dims, funcs, res[0:3] )
        with self.assertRaises(TypeError):
            noplot = emt.algo.radial_profile.plot_fit( R, I, dims, 42, res )

        # before fit
        plot = emt.algo.radial_profile.plot_fit( R, I, dims, funcs, init_guess, show=show )
        # after fit
        plot = emt.algo.radial_profile.plot_fit( R, I, dims, funcs, res, show=show )
        
        
        # try two voigts
        funcs = [ 'voigt', 'voigt' ]
        init_guess = ( 6e10, 7.3e9, 2e7, 2e7, 
                       8e10, 2.4e9, 1e8, 1e8 )
        res = emt.algo.radial_profile.fit_radialprofile( R, I, funcs, init_guess, maxfev=10000 )
        plot = emt.algo.radial_profile.plot_fit( R, I, dims, funcs, res, show=show )


        # subtract a power law background fitted to specific points
        # get some fixpoints
        fit_xs = [1.3e9, 1.5e9, 9.05e9]
        fit_xswidth = 0.05e9
        fit_R = np.array([])
        fit_I = np.array([])
        for xpoint in fit_xs:
            ix = np.where( np.abs(R-xpoint) < fit_xswidth )
            fit_R = np.append(fit_R, R[ix])
            fit_I = np.append(fit_I, I[ix])
            
        funcs = [ 'const', 'powlaw']
        init_guess = (1, 1.0e12, -1.0)
        res = emt.algo.radial_profile.fit_radialprofile( fit_R, fit_I, funcs, init_guess, maxfev=1000 )
        plot = emt.algo.radial_profile.plot_fit( R, I, dims, funcs, res, show=show )
        
        I = I - emt.algo.math.sum_functions(R, funcs, res)
        
        plot = emt.algo.radial_profile.plot_radialprofile( R, I, dims, show=show )

        #import pdb;pdb.set_trace()
        
        # wait for plots
        if show:
            plt.show()            
    
    
    #def test_eva(self):
        
        plt.close('all')        
        show=True
        
        
        ### test settings writing and reading
        if os.path.isfile('resources/output/test_settings.emd'):
            os.remove('resources/output/test_settings.emd')
            
        femd = emt.io.emd.fileEMD('resources/output/test_settings.emd')
        
        ## minimum settings necessary, with many nones
        settings_minimum = { 'lmax_r': 10,
                 'lmax_thresh': 600,
                 'lmax_cinit': (984, 1032),
                 'lmax_range': (6e9, 8e9),
                 'plt_imgminmax': None,
                 'ns': (2,3,4),
                 'rad_rmax': None,
                 'rad_dr': None,
                 'rad_sigma': None,
                 'mask': None,
                 'fit_rrange': (1.5e9, 9.5e9),
                 'back_xs': (1.3e9, 1.5e9, 9.05e9),
                 'back_xswidth': 0.05e9,
                 'back_init': (1, 1.0e12, -1.0),
                 'fit_funcs': ('voigt',),
                 'fit_init': ( 5e10, 7.3e9, 1.1e7, 2.5e7 ),
                 'fit_maxfev': None
               }
            
        # put       
        par = femd.file_hdl.create_group('put_minimum')
        
        # wrong input
        with self.assertRaises(TypeError):
            emt.eva.ring_diff.put_settings( 'not_par', settings_minimum )
        with self.assertRaises(TypeError):
            emt.eva.ring_diff.put_settings( par, 42 )
              
        emt.eva.ring_diff.put_settings( par, settings_minimum )
        
        # get
        
        # wrong input
        with self.assertRaises(TypeError):
            no_settings = emt.eva.ring_diff.get_settings('not a group')        
        
        in_settings_minimum = emt.eva.ring_diff.get_settings( par['settings_ringdiffraction'] )
        
        # compare the two settings
        for key in settings_minimum:
            self.assertTrue(key in in_settings_minimum)
            
            comp = (settings_minimum[key]==in_settings_minimum[key])
            if isinstance(comp, bool):
                self.assertTrue(comp)
            else:
                self.assertTrue(comp.all())
        
        ## full settings with all parameters set
        settings_full = { 'lmax_r': 10,
                 'lmax_thresh': 600,
                 'lmax_cinit': (984, 1032),
                 'lmax_range': (6e9, 8e9),
                 'plt_imgminmax': (0.0, 0.2),
                 'ns': (2,3,4),
                 'rad_rmax': 42.,
                 'rad_dr': 0.1,
                 'rad_sigma': 0.01,
                 'mask': np.ones((25,25)),
                 'fit_rrange': (1.5e9, 9.5e9),
                 'back_xs': (1.3e9, 1.5e9, 9.05e9),
                 'back_xswidth': 0.05e9,
                 'back_init': (1, 1.0e12, -1.0),
                 'fit_funcs': ('voigt',),
                 'fit_init': ( 5e10, 7.3e9, 1.1e7, 2.5e7 ),
                 'fit_maxfev': 1000
               }
               
        # put       
        par = femd.file_hdl.create_group('put_full')
        emt.eva.ring_diff.put_settings( par, settings_full )
        
        # get
        in_settings_full = emt.eva.ring_diff.get_settings( par['settings_ringdiffraction'] )
        
        # compare the two settings
        for key in settings_full:
            self.assertTrue(key in in_settings_full)
            
            comp = (settings_full[key]==in_settings_full[key])
            if isinstance(comp, bool):
                self.assertTrue(comp)
            else:
                self.assertTrue(comp.all())
        
        
        ### single evaluation
        femd = emt.io.emd.fileEMD('resources/Pt_SAED_D910mm_single/Pt_SAED_D910mm_single.emd')
        emdgrp = femd.list_emds[0]
        
        if os.path.isfile('resources/output/evaluation_Pt_SAED_D910mm_single.emd'):
            os.remove('resources/output/evaluation_Pt_SAED_D910mm_single.emd')
        femd_out = emt.io.emd.fileEMD('resources/output/evaluation_Pt_SAED_D910mm_single.emd')
        
        # write evaluation details
        grp_eva = femd_out.file_hdl.create_group('evaluation')
        
        # wrong input
        with self.assertRaises(TypeError):
            nohdl = emt.eva.ring_diff.put_sglgroup('nogroup', 'not_working', emdgrp)
        with self.assertRaises(TypeError):
            nohdl = emt.eva.ring_diff.put_sglgroup(grp_eva, 'not_working', 'nogroup')
        
        hdl = emt.eva.ring_diff.put_sglgroup(grp_eva, 'Pt_SAED_D910mm_single', emdgrp)

        # put the settings
        settings = { 'lmax_r': 10,
                 'lmax_thresh': 600,
                 'lmax_cinit': (984, 1032),
                 'lmax_range': (6e9, 8e9),
                 'plt_imgminmax': (0.,0.2),
                 'ns': (2,3,4),
                 'rad_rmax': None,
                 'rad_dr': None,
                 'rad_sigma': None,
                 'mask': None,
                 'fit_rrange': (1.5e9, 9.5e9),
                 'back_xs': (1.3e9, 1.5e9, 9.05e9),
                 'back_xswidth': 0.05e9,
                 'back_init': (1, 1.0e12, -1.0),
                 'fit_funcs': ('voigt',),
                 'fit_init': ( 5e10, 7.3e9, 1.1e7, 2.5e7 ),
                 'fit_maxfev': None
               }
        emt.eva.ring_diff.put_settings(femd_out.file_hdl, settings)

        # run the evaluation
        # wrong input
        with self.assertRaises(TypeError):
            emt.eva.ring_diff.run_sglgroup(42, femd_out)
        with self.assertRaises(TypeError):
            emt.eva.ring_diff.run_sglgroup(hdl, 'notanemdfile')
                    
        emt.eva.ring_diff.run_sglgroup(hdl, femd_out, verbose=True, showplots=False)
        
        
        ### evaluation of a series
        femd = emt.io.emd.fileEMD('resources/Au_SAED_D910mm_20x_at_800/Au_SAED_D910mm_20x_at_800.emd')
        emdgrp = femd.list_emds[0]
        
        if os.path.isfile('resources/output/evaluation_Au_SAED_D910mm_20x_at_800.emd'):
            os.remove('resources/output/evaluation_Au_SAED_D910mm_20x_at_800.emd')
        femd_out = emt.io.emd.fileEMD('resources/output/evaluation_Au_SAED_D910mm_20x_at_800.emd')
        
        # write evaluation details
        grp_eva = femd_out.file_hdl.create_group('evaluation')
        
        hdl = emt.eva.ring_diff.put_sglgroup(grp_eva, 'Au_SAED_D910mm_20x_at_800', emdgrp)
        
        # put the settings
        settings = { 'lmax_r': 16,
                     'lmax_thresh': 250,
                     'lmax_cinit': (1012, 1020),
                     'lmax_range': (6.5e9, 7.3e9),
                     'plt_imgminmax': (0.,0.4),
                     'ns': (2,3,4),
                     'rad_rmax': None,
                     'rad_dr': None,
                     'rad_sigma': None,
                     'mask': None,
                     'fit_rrange': (1.5e9, 9.5e9),
                     'back_xs': (1.5e9, 5.7e9, 9.05e9),
                     'back_xswidth': 0.05e9,
                     'back_init': (1, 1.5e9, -0.8),
                     'fit_funcs': ('voigt','voigt','voigt','voigt','voigt'),
                     'fit_init': ( 3.4e10, 4.25e9, 1.1e7, 2.5e7,
                                   9.1e9, 4.90e9, 1.1e7, 2.5e7,
                                   1.6e10, 6.95e9, 1.1e7, 2.5e7,
                                   1.1e10, 8.14e9, 1.1e7, 2.5e7,
                                   1.6e9, 8.50e9, 1.1e7, 2.5e7 ),
                     'fit_maxfev': None
                   }
        emt.eva.ring_diff.put_settings(femd_out.file_hdl, settings)

        # run the evaluation
        emt.eva.ring_diff.run_sglgroup(hdl, femd_out, verbose=True, showplots=False)
        
        
        ### run multiple evaluations
        ### single evaluation
        femd = emt.io.emd.fileEMD('resources/Pt_SAED_D910mm_single/Pt_SAED_D910mm_single.emd')
        emdgrp = femd.list_emds[0]
        
        if os.path.isfile('resources/output/evaluation_Pt_SAED_D910mm_multiple.emd'):
            os.remove('resources/output/evaluation_Pt_SAED_D910mm_multiple.emd')
        femd_out = emt.io.emd.fileEMD('resources/output/evaluation_Pt_SAED_D910mm_multiple.emd')
        
        # write evaluation details
        grp_eva = femd_out.file_hdl.create_group('evaluation')
        hdl = emt.eva.ring_diff.put_sglgroup(grp_eva, 'Pt_SAED_D910mm_first', emdgrp)
        hdl = emt.eva.ring_diff.put_sglgroup(grp_eva, 'Pt_SAED_D910mm_second', emdgrp)
        hdl = emt.eva.ring_diff.put_sglgroup(grp_eva, 'Pt_SAED_D910mm_third', emdgrp)

        # put the settings
        settings = { 'lmax_r': 10,
                 'lmax_thresh': 600,
                 'lmax_cinit': (984, 1032),
                 'lmax_range': (6e9, 8e9),
                 'plt_imgminmax': (0.,0.2),
                 'ns': (2,3,4),
                 'rad_rmax': None,
                 'rad_dr': None,
                 'rad_sigma': None,
                 'mask': None,
                 'fit_rrange': (1.5e9, 9.5e9),
                 'back_xs': (1.3e9, 1.5e9, 9.05e9),
                 'back_xswidth': 0.05e9,
                 'back_init': (1, 1.0e12, -1.0),
                 'fit_funcs': ('voigt',),
                 'fit_init': ( 5e10, 7.3e9, 1.1e7, 2.5e7 ),
                 'fit_maxfev': None
               }
        emt.eva.ring_diff.put_settings(grp_eva, settings)
        
        emt.eva.ring_diff.run_all(grp_eva, femd_out, verbose=True, showplots=False)
        

        # wait for plots
        if show:
            plt.show()     
        

# to test with unittest runner
if __name__ == '__main__':
    unittest.main()
