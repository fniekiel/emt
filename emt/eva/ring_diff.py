'''
Module to process ring diffraction patterns.
'''

import emt.algo.local_max
import emt.algo.distortion
import emt.io.emd
import matplotlib.pyplot as plt

def run_SingleImage(img, dims, verbose=False):
    '''
    Evaluate a single ring diffraction pattern.
    
    input:
    return:
    '''
    
    points = emt.algo.local_max.local_max(img, 10, 600)
    
    plot = emt.algo.local_max.plot_points(img, points, vminmax=(0,0.2), show=True)
    
    points = emt.algo.distortion.filter_ring(points, (984,1032), (700,900))
    
    plot = emt.algo.local_max.plot_points(img, points, vminmax=(0,0.2), show=True)
    
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
            res = run_SingleImage(data[:,:,i], dims[0:1], verbose=verbose)
    
    return None
