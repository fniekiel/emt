'''
Find local maxima in an image.
'''

import numpy as np
import scipy.ndimage.filters

import matplotlib.pyplot as plt


def local_max(img, r, thresh):
    '''
    Find local maxima from comparing dilated and eroded images.
    
    Calculates images with maximum and minimum within given radius. If the difference is larger than the threshold, the original pixel position with max value is detected as local maximum.
    
    input:
    - img       input image (np.ndarray)
    - r         radius (int)
    - thresh    intensity difference threshold (int)
    
    return:
    - points    array of points
    '''
    
    try:
        assert(isinstance(r, int))
        assert(isinstance(thresh, int))
        assert(isinstance(img, np.ndarray))
    except:
        raise TypeError('Bad input!')
    
    
    # prepare circular kernel
    y,x = np.ogrid[-r:r+1, -r:r+1]
    kernel = x**2 + y**2 <= r**2
    
    # calculate max and min images
    img_dil = scipy.ndimage.filters.maximum_filter(img, footprint=kernel)
    img_ero = scipy.ndimage.filters.minimum_filter(img, footprint=kernel)
    
    # get selection of local maxima
    sel = (img==img_dil)*(img-img_ero > thresh)
    
    # retrieve points
    points = np.argwhere(sel)
    points = np.roll(points, 1, axis=1)
    
    return points
    
    
def plot_points(img, points, vminmax=(0,1), show=False):
    '''
    Plot the detected points on the input image for checking.
    
    input:
    - img       image
    - points    array containing the points
    - vminmax   tuple of two values for relative lower and upper cut off to display image
    
    return:
    plot        plot image as np.ndarray
    '''
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.imshow(img.transpose(), cmap="Greys", vmin=np.min(img)+vminmax[0]*(np.max(img)-np.min(img)), vmax=np.min(img)+vminmax[1]*(np.max(img)-np.min(img)))
    ax.scatter(points[:,1], points[:,0], color='r', marker='o', facecolors='none')
    
    if show:
        plt.show()
    
    fig.canvas.draw()
    
    plot = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    plot = plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    return plot
    
