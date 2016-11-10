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


# used to indicate settings format
cur_vers = 'ring_diffraction_vers0.1'


def get_settings( parent ):
    '''
    Get settings for radial profile evaluation.
    
    '''
    
    if not parent.attrs['type'] == np.string_(cur_vers):
        print('Don\'t  know the format of these settings.')
        return None
    
    settings = {}
    
    settings['lmax_r'] = parent.attrs['lmax_r']
    settings['lmax_thresh'] = parent.attrs['lmax_thresh']
    settings['lmax_cinit'] = parent.attrs['lmax_cinit']
    settings['lmax_range'] = parent.attrs['lmax_range']
    settings['ns'] = parent.attrs['ns']
    settings['fit_rrange'] = parent.attrs['fit_rrange']
    settings['fit_init'] = parent.attrs['fit_init']
    
    in_funcs = parent.attrs['fit_funcs']
    out_funcs = []
    for i in range(len(in_funcs)):
        out_funcs.append(in_funcs[i].decode('utf-8'))
    settings['fit_funcs'] = tuple(out_funcs)
    
    if 'plt_imgminmax' in parent.attrs:
        settings['plt_imgminmax'] = parent.attrs['plt_imgminmax']
    else:
        settings['plt_imgminmax'] = None

    if 'rad_rmax' in parent.attrs:
        settings['rad_rmax'] = parent.attrs['rad_rmax']
    else:
        settings['rad_rmax'] = None

    if 'rad_dr' in parent.attrs:
        settings['rad_dr'] = parent.attrs['rad_dr']
    else:
        settings['rad_dr'] = None

    if 'rad_sigma' in parent.attrs:
        settings['rad_sigma'] = parent.attrs['rad_sigma']
    else:
        settings['rad_sigma'] = None

    if 'mask' in parent:
        settings['mask'] = np.copy(parent['mask'])
    else:
        settings['mask'] = None

    if 'fit_maxfev' in parent.attrs:
        settings['fit_maxfev'] = parent.attrs['fit_maxfev']
    else:
        settings['fit_maxfev'] = None


    return settings


def put_settings( parent, settings ):
    '''
    Put settings for radial profile evaluation.
    
    Creates a subgroup in parent holding the settings as attributes.
    '''
    
    try:
        grp_set = parent.create_group('settings_ringdiffraction')
    except:
        raise RuntimeError('Could not write to {}'.format(parent))
        
    # set version information    
    grp_set.attrs['type'] = np.string_(cur_vers)
    
    # hardcoding the written settings to keep control
    grp_set.attrs['lmax_r'] = settings['lmax_r']
    grp_set.attrs['lmax_thresh'] = settings['lmax_thresh']
    grp_set.attrs['lmax_cinit'] = settings['lmax_cinit']
    grp_set.attrs['lmax_range'] = settings['lmax_range']
    grp_set.attrs['ns'] = settings['ns']
    grp_set.attrs['fit_rrange'] = settings['fit_rrange']
    grp_set.attrs['fit_init'] = settings['fit_init']
    
    fit_funcs = []
    for i in range(len(settings['fit_funcs'])):
        fit_funcs.append(np.string_(settings['fit_funcs'][i]))
    grp_set.attrs['fit_funcs'] = fit_funcs
    
    if not settings['plt_imgminmax'] is None:
        grp_set.attrs['plt_imgminmax'] = settings['plt_imgminmax']
    if not settings['rad_rmax'] is None:
        grp_set.attrs['rad_rmax'] = settings['rad_rmax']
    if not settings['rad_dr'] is None:
        grp_set.attrs['rad_dr'] = settings['rad_dr']
    if not settings['rad_sigma'] is None:
        grp_set.attrs['rad_sigma'] = settings['rad_sigma']
    if not settings['mask'] is None:
        grp_set.create_dataset('mask', data=settings['mask'])
    if not settings['fit_maxfev'] is None:
        grp_set.attrs['fit_maxfev'] = settings['fit_maxfev']


def evaEMDFile(emdfile, outfile, verbose=False):
    '''
    Run on a single EMD file evaluating all images inside.
    
    input:
    return:
    '''
    
    try:
        assert(isinstance(emdfile, emt.io.emd.fileEMD))
    except:
        raise RuntimeError('emdfile needs to be an emt.io.emd.fileEMD object!')
    
    try:
        assert(isinstance(outfile, emt.io.emd.fileEMD))
    except:
        raise RuntimeError('outfile needs to be an emt.io.emd.fileEMD object!')
    

    # settings for evaluation
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
                   
    # set up output emdfile
    grp_eva = outfile.file_hdl.create_group('evaluation')
    put_settings( grp_eva, settings)
    
    
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
        
        
         
        # evaluate image
        for i in range(data.shape[2]):
            profile, res, center, dists, myset = emt.algo.radial_profile.run_singleImage( data[:,:,i], dims[0:2], settings,  show=verbose)
            
        #import pdb;pdb.set_trace()
    
    return None
