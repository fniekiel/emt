'''
Module to handle distortions in diffraction patters.
'''

import numpy as np


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
