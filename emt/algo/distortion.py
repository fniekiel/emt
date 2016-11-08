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
    
    # calculate radii
    rs = np.sqrt( np.square(points[:,0]-center[0]) + np.square(points[:,1]-center[1]) )
    
    # filter by given limits
    points_f = points[(rs>rminmax[0])*(rs<rminmax[1])]
    
    return points_f
