'''
Module to process ring diffraction patterns.
'''

import emt.algo.local_max
import emt.io.emd

def evaSinglePattern():
    '''
    Evaluate a single ring diffraction pattern.
    
    input:
    return:
    '''
    
    emt.algo.local_max.local_max()
    
    
    return None
    
    

def evaEMDFile():
    '''
    Run on a single EMD file.
    
    input:
    return:
    '''
    
    evaSinglePattern()
    
    return None
