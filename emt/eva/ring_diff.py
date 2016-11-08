'''
Module to process ring diffraction patterns.
'''

import emt.algo.local_max
import emt.algo.distortion
import emt.io.emd
import matplotlib.pyplot as plt
import numpy as np

def run_SingleImage(img, dims, verbose=False):
    '''
    Evaluate a single ring diffraction pattern.
    
    input:
    return:
    '''
    pex = {'r':10, 'thresh':600}
    pfil = {'cinit': (984, 1032), 'rang': (6.0e9, 8.0e9)}
    pl = {'vminmax': (0,0.2)}
    
    
    points = emt.algo.local_max.local_max(img, pex['r'], pex['thresh'])
    
    #plot = emt.algo.local_max.plot_points(img, points, pl['vminmax'], invert=True, show=True)
    
    points = emt.algo.distortion.points_todim(points, dims)
    
    cinit = emt.algo.distortion.points_todim(pfil['cinit'], dims)
    
    points = emt.algo.distortion.filter_ring(points, cinit, pfil['rang'])
    
    #plot = emt.algo.local_max.plot_points(img, points, pl['vminmax'], dims=dims, invert=True, show=True)
    
    points_plr = emt.algo.distortion.points_topolar(points, cinit)
    
    #plot = emt.algo.distortion.plot_ringpolar(points_plr, dims, show=True)
    
    center = emt.algo.distortion.optimize_center(points, cinit)
    if verbose:
        print('optimized center: ({}, {})'.format(center[0]*1e-9, center[1]*1e-9))
    
    points_plr = emt.algo.distortion.points_topolar(points, center)
    
    plot = emt.algo.distortion.plot_ringpolar(points_plr, dims, show=True)


    dists = emt.algo.distortion.optimize_distortion(points_plr, (2,))
    if verbose:
        print('optimized distortion: R={} alpha={}, beta={}'.format(dists[0], dists[1], dists[2]))
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axhline(np.mean(points_plr[:,0]), ls='--', c='k')
    ax.plot(points_plr[:,1], points_plr[:,0], 'rx')
    xpl_ell = np.linspace(-np.pi, np.pi, 100)
    plt.plot( xpl_ell, dists[0]*emt.algo.distortion.rad_dis(xpl_ell, dists[1], dists[2], 2), 'b-') 
    plt.plot( points_plr[:,1], points_plr[:,0]/emt.algo.distortion.rad_dis(points_plr[:,1], dists[1], dists[2], 2), 'gx')
    ax.set_xlabel('theta /[rad]')
    ax.set_xlim( (-np.pi, np.pi) )
    ax.set_ylabel('r /{}'.format(dims[0][2].decode('utf-8')))
    
    #if show:
    plt.show(block=False)
    
    #fig.canvas.draw()
    #plot = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    #plot = plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    

    #import pdb; pdb.set_trace()

    # wait for the plot windows
    plt.show()
    
    return None
    
    

def evaEMDFile(emdfile, verbose=False):
    '''
    Run on a single EMD file evaluating all images inside.
    
    input:
    return:
    '''
    
    try:
        assert(isinstance(emdfile, emt.io.emd.fileEMD))
    except:
        raise RuntimeError('emdfile needs to be an emt.io.emd.fileEMD object!')
    
    print(emdfile.list_emds)
    for emdgrp in emdfile.list_emds:
        if verbose:
            print('working on {}'.format(emdgrp.name))
            
        # get the data
        data, dims = emdfile.get_emdgroup(emdgrp)
        
        # assuming stacks of images
        try:
            assert(len(data.shape) == 3)
        except:
            raise RuntimeError('Dont know how to handle that data.')
                
        # evaluate image
        for i in range(data.shape[2]):
            res = run_SingleImage(data[:,:,i], dims[0:2], verbose=verbose)
    
    return None
