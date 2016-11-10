'''
Module to process ring diffraction patterns.
'''

import emt.algo.local_max
import emt.algo.distortion
import emt.algo.radial_profile
import emt.algo.math
import emt.io.emd
import matplotlib.pyplot as plt
import numpy as np


def get_settings( parent ):
    '''
    Get settings for radial profile evaluation.
    
    '''
    
    


    return settings

def put_settings( parent, settings ):
    '''
    Put settings for radial profile evaluation.
    
    Creates a subgroup in parent holding the settings as attributes.
    '''
    
    



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
        
        # get parameters from meta
        
        settings = { 'lmax_r': 10,
                     'lmax_thresh': 600,
                     'lmax_cinit': (984, 1032),
                     'lmax_range': (6e9, 8e9),
                     'plt_imgminmax': (0.0, 0.2),
                     'ns': (2,3,4),
                     'rad_rmax': None,
                     'rad_dr': None,
                     'rad_sigma': None,
                     'mask': None,
                     'fit_rrange': (1.5e9, 9.5e9),
                     'fit_funcs': ('const', 'powlaw', 'voigt'),
                     'fit_init': ( 10,
                                   1.0e12, -1.0,
                                   5e10, 7.3e9, 1.1e7, 2.5e7 ),
                     'fit_maxfev': None
                   }
         
        # evaluate image
        for i in range(data.shape[2]):
            profile, res, center, dists, myset = emt.algo.radial_profile.run_singleImage( data[:,:,i], dims[0:2], settings,  show=verbose)
            
        #import pdb;pdb.set_trace()
    
    return None
