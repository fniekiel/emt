'''
This module provides an interface to the EMD file format.

See https://emdatasets.com/ for more details.
'''

import numpy as np
import h5py


class fileEMD:
    '''
    Class to represent EMD files.
    '''
    
    def __init__(self, filename, readonly=False, verbose=False):
        '''Init opening/creating the file.
        
        input:
        - filename (string)     name of the EMD file
        - readonly (bool)       set to open in read only mode
        - verbose (bool)        set to get extensive output while reading the file
        '''
        
        # necessary declarations in case something goes bad
        self.file_hdl = None
        
        # check for string
        if not isinstance(filename, str):
            raise TypeError('Filename is supposed to be a string')

        # try opening the file
        if readonly:
            try:
                self.file_hdl = h5py.File(filename, 'r')
            except:
                print('Error opening file for readonly: "{}"'.format(filename))
                raise
        else:
            try:
                self.file_hdl = h5py.File(filename, 'a')
            except:
                print('Error opening file for read/write: "{}"'.format(filename))


        
    def __del__(self):
        '''Destructor for EMD file object'''
        # close the file
        if(self.file_hdl):
            self.file_hdl.close()
