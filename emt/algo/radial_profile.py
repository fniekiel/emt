'''
Module to calculate radial profiles.
'''

import numpy as np

import emt.algo.distortion

def calc_polarcoords ( center, dims, ns=None, dists=None ):
    '''
    Calculate the polar coordinates for an image of given shape.
    
    Center is assumed to be in real coordinates (if not just fake the dims).
    Distortions are corrected if ns and corresponding dists are given.
    
    input:
    - center
    - dims
    - ns
    - dists
    
    return:
    - rs, thes
    '''
    
    # check input
    try:
        # check center 
        center = np.array(center)
        center = np.reshape(center, 2)
        
        # check if enough dims availabel
        assert(len(dims)>=2)
        assert(len(dims[0])==3)
        
        # check orders
        if ns:
            assert(len(ns)>=1)
        
            # check dists
            assert(dists.shape[0] == len(ns)*2+1)
            
    except:
        raise TypeError('Something wrong with the input!')
    
    # create coordinates
    xx, yy = np.meshgrid( dims[0][0], dims[1][0] )
    
    # calculate polar coordinate system
    rs = np.sqrt( np.square(xx-center[0]) + np.square(yy-center[1]) )
    thes = np.arctan2(yy-center[1], xx-center[0])
    
    # correct for distortions
    if ns:
        for i in range(len(ns)):
            rs /= emt.algo.distortion.rad_dis(thes, dists[i*2+1], dists[i*2+2], ns[i])
            
    return rs, thes
