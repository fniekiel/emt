'''
Module to handle distortions in diffraction patters.
'''

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize


def filter_ring(points, center, rminmax):
    '''
    Filter points to be in a certain radial distance range from center.
    
    input:
    - points        candidate points
    - center        center position
    - rminmax       tuple of min and max radial distance
    
    return:
    - points_f      list of filtered points
    '''
    
    try:
        # points have to be 2D array with 2 columns
        assert(isinstance(points, np.ndarray))
        assert(points.shape[1] == 2)
        assert(len(points.shape) == 2)    
        
        # center can either be tuple or np.array    
        center = np.array(center)
        center = np.reshape(center, 2)
   
    except:
        raise RuntimeError('Something wrong with the input!')
    
    # calculate radii
    rs = np.sqrt( np.square(points[:,0]-center[0]) + np.square(points[:,1]-center[1]) )
    
    # filter by given limits
    points_f = points[(rs>rminmax[0])*(rs<rminmax[1])]
    
    return points_f
    
    
def points_todim(points, dims):
    '''
    Convert points from px coordinates to read dim.
    
    Points are expected to be array indices for the first two dimensions in dims.
    '''
    
    try:
        # try to convert input to np.ndarray with 2 columns (necessary if only one entry provided)
        points = np.reshape(np.array(points), (-1,2))
        # check if enough dims availabel
        assert(len(dims)>=2)
    except:
        raise RuntimeError('Something wrong with the input!')
    
    # do the conversion by looking up thing in dimension vectors
    points_d = np.array( [ dims[0][0][points[:,0]], dims[1][0][points[:,1]] ] ).transpose()
    
    return points_d
    
    
def points_topolar(points, center):
    '''
    Convert points to polar coordinate system.
    
    Can be either in pixel or real dim, but should be the same for points and center.
    '''
    
    try:
        # points have to be 2D array with 2 columns
        assert(isinstance(points, np.ndarray))
        assert(points.shape[1] == 2)
        assert(len(points.shape) == 2)    
        
        # center can either be tuple or np.array    
        center = np.array(center)
        center = np.reshape(center, 2)
   
    except:
        raise RuntimeError('Something wrong with the input!')
    
    # calculate radii
    rs = np.sqrt( np.square(points[:,0]-center[0]) + np.square(points[:,1]-center[1]) )
    # calculate angle
    thes = np.arctan2(points[:,1]-center[1], points[:,0]-center[0])
    
    points_p = np.array( [rs, thes] ).transpose()
    
    return points_p
    
    
def plot_ringpolar(points, dims, show=False): 

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axhline(np.mean(points[:,0]), ls='--', c='k')
    ax.plot(points[:,1], points[:,0], 'rx')
    ax.set_xlabel('theta /[rad]')
    ax.set_xlim( (-np.pi, np.pi) )
    ax.set_ylabel('r /{}'.format(dims[0][2].decode('utf-8')))
    
    if show:
        plt.show(block=False)
    
    fig.canvas.draw()
    plot = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    plot = plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    return plot


def residuals_center( param, data):
    '''
    Residual function for minimizing the deviations from the mean radial distance.
    
    input:
    - param     the center to optimize
    - data      the points in x,y coordinates of the original image
    '''
    
    # manually calculating the radii, as we do not need the thetas
    rs = np.sqrt( np.square(data[:,0]-param[0]) + np.square(data[:,1]-param[1]) )
    
    return (rs-np.mean(rs))
    
    
def optimize_center(points, center, maxfev=1000):
    '''
    Optimize the center by minimizing the sum of square deviations from the mean radial distance.
    
    input:
    - points        the points to which the optimization is done (x,y coords in org image)
    - center        initial center guess
    - maxfev        max number of iterations forwarded to scipy.optimize.leastsq()
    
    return:
    - opt_center    the optimized center
    '''

    try:
        # points have to be 2D array with 2 columns
        assert(isinstance(points, np.ndarray))
        assert(points.shape[1] == 2)
        assert(len(points.shape) == 2)    
        
        # center can either be tuple or np.array    
        center = np.array(center)
        center = np.reshape(center, 2)
   
    except:
        raise RuntimeError('Something wrong with the input!')

    # run the optimization
    popt, flag = scipy.optimize.leastsq( residuals_center, center, args=(points), maxfev=maxfev)
    
    if flag not in [1,2,3,4]:
        print('WARNING: center optimization failed.')

    return popt
    

def rad_dis( theta, alpha, beta, order=2 ):
    '''
    Radial distortion due to ellipticity or higher order distortion.
    
    Relative distortion, to be multiplied with radial distance.
    '''
    
    return (1.-np.square(beta))/np.sqrt(1.+np.square(beta)-2.*beta*np.cos(order*(theta+alpha)))

    
def residuals_dis(param, points, ns):
    '''
    Residual function for distortions
    '''

    est = param[0]*np.ones(points[:,1].shape)
    for i in range(len(ns)):
        est *=rad_dis( points[:,1], param[i*2+1], param[i*2+2], ns[i])
            
    return points[:,0] - est 
    
    
def optimize_distortion(points, ns, maxfev=1000):
    '''
    Optimize distortions.
    
    input:
    - points        points to optimize to (in polar coords)
    - ns            list of distortion orders to correct for
    - maxfev        max number of iterations forwarded to scipy.optimize.leastsq()
    '''
    
    init_guess = np.ones(len(ns)*2+1)*0.1
    init_guess[0] = np.mean(points[:,0])
    
    popt, flag = scipy.optimize.leastsq( residuals_dis, init_guess, args=(points, ns), maxfev=maxfev)
    
    if flag not in [1,2,3,4]:
        print('WARNING: optimization of distortions failed.')
    
    return popt
    
