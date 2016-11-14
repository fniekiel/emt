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
import h5py


# used to indicate settings format
cur_set_vers = 'ring_diffraction_setting_vers0.1'
cur_eva_vers = 'ring_diffraction_evaluation_vers0.1'


def get_settings( parent ):
    '''
    Get settings for radial profile evaluation.
    
    input:
    - parent     input group
    
    return:
    - settings   settings read from parent
    '''
    
    try:
        assert( isinstance(parent, h5py._hl.group.Group) )
    except:
        raise TypeError('Something wrong with the input.')
    
    
    if not parent.attrs['type'] == np.string_(cur_set_vers):
        print('Don\'t  know the format of these settings.')
        return None
    
    settings = {}
    
    settings['lmax_r'] = parent.attrs['lmax_r']
    settings['lmax_thresh'] = parent.attrs['lmax_thresh']
    settings['lmax_cinit'] = parent.attrs['lmax_cinit']
    settings['lmax_range'] = parent.attrs['lmax_range']
    settings['ns'] = parent.attrs['ns']
    settings['fit_rrange'] = parent.attrs['fit_rrange']
    settings['back_xs'] = parent.attrs['back_xs']
    settings['back_xswidth'] = parent.attrs['back_xswidth']
    settings['back_init'] = parent.attrs['back_init']
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
    
    input:
    - parent        group to hold settings subgroup
    - setting       dict of settings to write
    
    return:
    - grp_set       handle to settings group
    '''
 
    try:
        assert( isinstance(parent, h5py._hl.group.Group) )
        assert( type(settings) is dict )
    except:
        raise TypeError('Something wrong with the input.')
    
  
    try:
        grp_set = parent.create_group('settings_ringdiffraction')
    except:
        raise RuntimeError('Could not write to {}'.format(parent))
        
        
    # set version information    
    grp_set.attrs['type'] = np.string_(cur_set_vers)
    
    # hardcoding the written settings to keep control
    grp_set.attrs['lmax_r'] = settings['lmax_r']
    grp_set.attrs['lmax_thresh'] = settings['lmax_thresh']
    grp_set.attrs['lmax_cinit'] = settings['lmax_cinit']
    grp_set.attrs['lmax_range'] = settings['lmax_range']
    grp_set.attrs['ns'] = settings['ns']
    grp_set.attrs['fit_rrange'] = settings['fit_rrange']
    grp_set.attrs['back_xs'] = settings['back_xs']
    grp_set.attrs['back_xswidth'] = settings['back_xswidth']
    grp_set.attrs['back_init'] = settings['back_init']
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
        
    return grp_set


def put_sglgroup(parent, label, data_grp):
    '''
    Puts the todo evaluation into parent.
    
    Remember that the ressource of the external link must not be already opened elsewhere to access data.
    
    input:
    - parent        hdf5 group to add this evaluation group to
    - label         label for the evaluation group    
    - data_grp      emdtype group where to find the data
    
    return:
    - grp           handle to group
    '''
    
    try:
        assert( isinstance(parent, h5py._hl.group.Group) )
        label = str(label)
        assert( isinstance(data_grp, h5py._hl.group.Group) )
    except:
        raise TypeError('Something wrong with the input')
        
    
    # create the evaluation group
    grp = parent.create_group(label)
    grp.attrs['type'] = np.string_(cur_eva_vers)
    
    # put a link to the data
    grp.attrs['filename'] = np.string_(data_grp.file.filename)
    grp.attrs['internal_path'] = np.string_(data_grp.name)
    #grp['emdgroup'] = h5py.ExternalLink(data_grp.file.filename, data_grp.name)    
    
    return grp
    

def run_sglgroup(group, outfile, verbose=False, showplots=False):
    '''
    Run evaluation on a single group.
    
    input:
    - group         handle to evaluation group to execute
    - outfile       emdfile for output
    '''

    try:
        assert(isinstance(group, h5py._hl.group.Group))
        assert( group.attrs['type'] == np.string_(cur_eva_vers) )
        
        assert(isinstance(outfile, emt.io.emd.fileEMD))
    except:
        raise TypeError('Something wrong with the input.')
        
    
    if verbose:
        print('Running evaluation of "{}".'.format(group.name))
        
        
    # get the emdgroup
    if verbose:
        print('.. getting data from {}:{}'.format(group.attrs['filename'].decode('utf-8'), group.attrs['internal_path'].decode('utf-8')))
    readfile = emt.io.emd.fileEMD( group.attrs['filename'].decode('utf-8'), readonly=True )
    data, dims = readfile.get_emdgroup(readfile.file_hdl[group.attrs['internal_path'].decode('utf-8')])
    
    # find the settings moving upwards in hierarchy
    if verbose:
        print('.. searching for settings.')
    def proc_group(grp):
        #print('scanning group {}'.format(grp))
        if 'settings_ringdiffraction' in grp:
            stt = grp['settings_ringdiffraction']
            if stt.attrs['type'] == np.string_(cur_set_vers):
                return stt
        else:
            if not grp == grp.file:
                return proc_group(grp.parent)

    grp_set = proc_group(group)
    
    if grp_set is None:
        raise RuntimeError('Could not find settings in evaluation group or its parents.')
    else:
        if verbose:
            print('.. loading settings from {}.'.format(grp_set.name))
        settings = get_settings(grp_set)
    
    # what data to collect
    profiles = None
    centers = None
    distss = None
    fits = None
    rawprofiles = None
    fits_back = None
    
    # run evaluation with settings
    for i in range(data.shape[2]):
        profile, res, center, dists, rawprofile, res_back, myset = emt.algo.radial_profile.run_singleImage( data[:,:,i], dims[0:2], settings,  show=showplots)
    
        # after first run I know the size
        if profiles is None:
            profiles = np.zeros( (profile.shape[0], data.shape[2]) )
            fits = np.zeros( (res.shape[0], data.shape[2]) )
            centers = np.zeros( (2, data.shape[2]) )
            distss = np.zeros( (dists.shape[0], data.shape[2]) )
            rawprofiles = np.zeros( (rawprofile.shape[0], data.shape[2]) )
            fits_back = np.zeros( (res_back.shape[0], data.shape[2]) )
            
        # assign data    
        profiles[:,i] = profile[:,1]
        fits[:,i] = res[:]
        centers[:,i] = center[:]
        distss[:,i] = dists[:]
        rawprofiles[:,i] = rawprofile[:,1]
        fits_back[:,i] = res_back[:]

    # save results in this group
    outfile.put_emdgroup('radial_profile', profiles, ( (profile[:,0], 'radial distance', dims[0][2]) , dims[2]), group)
    outfile.put_emdgroup('fit_results', fits, ( ( np.array(range(fits.shape[0])), 'parameters', '[]') , dims[2]), group)
    outfile.put_emdgroup('centers', centers, ( ( np.array(range(2)), 'dimension', dims[0][2]) , dims[2]), group)    
    outfile.put_emdgroup('distortions', distss, ( ( np.array(range(distss.shape[0])), 'parameters', '[]') , dims[2]), group)
    outfile.put_emdgroup('radial_profile_noback', rawprofiles, ( (rawprofile[:,0], 'radial distance', dims[0][2]) , dims[2]), group)
    outfile.put_emdgroup('back_results', fits_back, ( ( np.array(range(fits_back.shape[0])), 'background parameters', '[]') , dims[2]), group)
    
    # save a log comment
    outfile.put_comment('Evaluated "{}" using ring diffraction analysis.'.format(group.name))
    

def run_all(parent, outfile, verbose=False, showplots=False):
    '''
    Run on a set-up emd file to do evaluations and save results.
    
    All evaluations within parent are run.
    
    input:
    - parent        handle to parent group
    - outfile       emdfile to save evaluations
    '''
    
    # get all groups with evaluations to do
    todo = []
    
    # recursive function
    def proc_group(grp, todo):
        for item in grp:
            if grp.get(item, getclass=True) == h5py._hl.group.Group:
                item = grp.get(item)
                if 'type' in item.attrs:
                    if item.attrs['type'] == np.string_(cur_eva_vers):
                        todo.append(item)
                        if verbose:
                            print('Found evaluation group at "{}".'.format(item.name) )
                proc_group(item, todo)    
    
    proc_group(parent, todo)
    
    # run through all evaluations
    for i in range(len(todo)):
        run_sglgroup(todo[i], outfile, verbose=verbose, showplots=showplots)
    

