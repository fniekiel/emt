'''
Module to calculate radial profiles.
'''

import numpy as np
import scipy.ndimage.filters
import matplotlib.pyplot as plt

import emt.algo.math
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
    
    
def calc_radialprofile( img, rs, rMax, dr, rsigma, mask=None):
    '''
    Calculate the radial profile using Gaussian density estimator.
    
    It is suggested to use an rMax such that all directions are still in the image, otherwise outer areas will contribute differently and lead to different signal-to-noise. A value of dr corresponding to 1/10 px and rsigma corresponding to 1 px are good parameters.
    
    input:
    - img       image to take radial profile of intensity from
    - rs        array containing the radial distance, same shape as img
    - rMax      maximum radial distance used for the radial profile
    - dr        stepsize for r-axis of radial distance
    - rsigma    sigma for Gaussian used as kernel density estimator
    - mask      binary image, 0 for pixels to exclude
    
    return:
    - r, intens
    '''
    
    # check input
    try:
        assert(isinstance(img, np.ndarray))
        assert(isinstance(rs, np.ndarray))
        assert(np.array_equal(img.shape, rs.shape))
        
        rMax = float(rMax)
        dr = float(dr)
        rsigma = float(rsigma)
        
        if not mask is None:
            assert(isinstance(mask, np.ndarray))
            assert(np.array_equal(img.shape, mask.shape))
        
    except:
        raise TypeError('Something wrong with input.')
    
    # process mask
    if mask is None:
        mask = np.ones(img.shape)
    mask[np.where( mask > 0 )] = 1
    mask[np.where( mask == 0 )] = np.nan
    
    
    # prepare radial axis for hist  
    rBins = np.arange(0, rMax, dr)
    
    radialIndex = np.round(rs/dr)+1
    rBinMax = len(rBins)
    sel = (radialIndex<=rBinMax)
    
    sel = np.logical_and(sel, np.logical_not(np.isnan(mask)) )
    
    signal = np.histogram(rs[sel], rBins, weights=img[sel])
    count = np.histogram(rs[sel], rBins, weights=np.ones(img[sel].shape))

    signal_sm = scipy.ndimage.filters.gaussian_filter1d(signal[0], rsigma/dr)
    count_sm = scipy.ndimage.filters.gaussian_filter1d(count[0], rsigma/dr)
    
    # masked regions lead to 0 in count_sm, divide produces nans, just ignore the warning    
    old_err_state = np.seterr(divide='ignore',invalid='ignore')    
    signal_sm = np.divide(signal_sm,count_sm)
    np.seterr(**old_err_state)    
        
    return rBins[:-1], signal_sm
    
    
def plot_radialprofile( r, intens, dims, show=False ):
    '''
    Plot radial profile.
    
    input:
    - r             r-axis of radial profile
    - intens        intensity-axis of radial profile
    - dims          dimensions of original image to read out units
    
    return:
    - plot          plot rendered to np.ndarray
    '''
    
    try:
        # check data
        assert(isinstance(r, np.ndarray))
        assert(isinstance(intens, np.ndarray))
        assert(np.array_equal(r.shape, intens.shape))
        
        # check if dims availabel
        assert(len(dims)>=1)
        assert(len(dims[0])==3)

    except:
        raise TypeError('Something wrong with the input!')
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.plot(r, intens, 'r-')
    
    # labels
    ax.set_xlabel('r /{}'.format(dims[0][2].decode('utf-8')))
    ax.set_ylabel('I /[a.u.]')
        
    if show:
        plt.show(block=False)
    
    # render to array
    fig.canvas.draw()
    plot = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    plot = plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    return plot


def residuals_fit( param, r, intens, funcs ):
    '''
    Residual function to fit radial profile with flexibility.
    
    The arguments for the single functions are automatically cut from the fit parameters.
    
    input:
    - param         fit parameters
    - r             r-axis
    - intens        intensity-axis
    - funcs         list of functions to include
        
    return:
    - residuals
    '''

    return intens - emt.algo.math.sum_functions(r, funcs, param)
    
    
def fit_radialprofile( r, intens, funcs, init_guess, maxfev=1000 ):
    '''
    Fit the radial profile.
    
    Convenience wrapper for fitting.
    
    input:
    - r             r-axis of radial profile
    - intens        intensity-axis of radial profile
    - funcs         list of functions
    - init_guess    initial guess for parameters of functions in funcs
    '''    
    
    try:
        # check data
        assert(isinstance(r, np.ndarray))
        assert(isinstance(intens, np.ndarray))
        assert(np.array_equal(r.shape, intens.shape))
        
        # funcs and params
        assert(len(funcs)>=1)
        for i in range(len(funcs)):
            assert(funcs[i] in emt.algo.math.lkp_funcs)
        
        init_guess = np.array(init_guess)
        init_guess = np.reshape(init_guess, sum(map(lambda x: emt.algo.math.lkp_funcs[x][1], funcs)))

    except:
        raise TypeError('Something wrong with the input!')
    
 
    popt, flag = scipy.optimize.leastsq( residuals_fit, init_guess, args=(r, intens, funcs), maxfev=maxfev)

    if flag not in [1,2,3,4]:
        print('WARNING: fitting of radial profile failed.')

    return popt


def plot_fit( r, intens, dims, funcs, param, show=False ):
    '''
    Plot the fit results to the radial profile.
    
    input:
    - r             r-axis of radial profile
    - intens        intensity-axis of radial profile
    - dims          dimensions of original image to read out units
    - funcs         list of functions
    - param         parameters for functions in funcs
    
    return:
    - plot          plot rendered to np.ndarray
    '''
    
    try:
        # check data
        assert(isinstance(r, np.ndarray))
        assert(isinstance(intens, np.ndarray))
        assert(np.array_equal(r.shape, intens.shape))
        
        # check if dims availabel
        assert(len(dims)>=1)
        assert(len(dims[0])==3)
        
        # funcs and params
        assert(len(funcs)>=1)
        for i in range(len(funcs)):
            assert(funcs[i] in emt.algo.math.lkp_funcs)
            
        param = np.array(param)
        param = np.reshape(param, sum(map(lambda x: emt.algo.math.lkp_funcs[x][1], funcs)))

    except:
        raise TypeError('Something wrong with the input!')
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    # plot radial profile
    ax.plot(r, intens, 'r-')
    
    # plot single
    n = 0
    for i in range(len(funcs)):
        ax.plot(r, emt.algo.math.lkp_funcs[funcs[i]][0]( r, param[n:n+emt.algo.math.lkp_funcs[funcs[i]][1]]), 'g-' )
        n += emt.algo.math.lkp_funcs[funcs[i]][1]
    # sum of functions
    sum_funcs = emt.algo.math.sum_functions( r, funcs, param )
    ax.plot(r, sum_funcs, 'b-')
    
    # labels
    ax.set_xlabel('r /{}'.format(dims[0][2].decode('utf-8')))
    ax.set_ylabel('I /[a.u.]')
        
    if show:
        plt.show(block=False)
    
    # render to array
    fig.canvas.draw()
    plot = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    plot = plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    return plot
