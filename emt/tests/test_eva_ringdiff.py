'''
Tests for the evaluation of ring diffraction patterns.
'''

import unittest
import numpy as np
import matplotlib.pyplot as plt

import emt.io.emd
import emt.algo.local_max
import emt.eva.ring_diff


class test_ringdiff(unittest.TestCase):
    '''
    Test the evaluation of ring diffraction patterns.
    '''
    
    def test_local_max(self):
        '''
        Test the local_maxima algorithm to be used for ring diffraction patterns.
        '''
        
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
            points = emt.algo.local_max.local_max(img, 10.0, 600)
        with self.assertRaises(TypeError):
            points = emt.algo.local_max.local_max(img, 10, 600.42)
            
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
        
        
        # try a bunch of fits
        for ns in ( (2,), (2,3), (2,3,4), (2,3,4,5), (4,) ):
     
            dists = emt.algo.distortion.optimize_distortion(points_plr, ns, verbose=True)
            plot = emt.algo.distortion.plot_distpolar(points_plr, dims, dists, ns, show=show)
            
        
        # wait for plots
        if show:
            plt.show()
    
    
    def test_eva(self):
        
        # wrong file
        with self.assertRaises(RuntimeError):
            with open('resources/output/test.txt', 'w') as f:
                emt.eva.ring_diff.evaEMDFile(f)
                        
        # right file
        femd = emt.io.emd.fileEMD('resources/Pt_SAED_D910mm_single/Pt_SAED_D910mm_single.emd')
        
        emt.eva.ring_diff.evaEMDFile(femd, verbose=True)
        
        
        
        

# to test with unittest runner
if __name__ == '__main__':
    unittest.main()
