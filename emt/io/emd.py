'''
This module provides an interface to the EMD file format.

See https://emdatasets.com/ for more details.
'''

import numpy as np
import h5py


class fileEMD:
    '''
    Class to represent EMD files. 
    
    Implemented for spec 0.2.
    Meant to provide convenience functions for commonly occuring tasks. This means that you will still want to acces fileEMD.file_hdl to manipulate the HDF5 file for so commonly occuring tasks.
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
        self.version = None
        
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
                raise
        
        
        # if we got a working file
        if self.file_hdl:        
        
            # check version information
            if 'version_major' in self.file_hdl.attrs and 'version_minor' in self.file_hdl.attrs:
                # read version information
                self.version = (self.file_hdl.attrs['version_major'], self.file_hdl.attrs['version_minor'])
                # compare to implementation
                if not self.version == (0,2):
                    print('WARNING: You are reading a version {}.{} EMD file, this implementation assumes version 0.2!'.format(self.version[0], self.version[1]))
            else:
                # set version information
                self.file_hdl.attrs['version_major'] = 0
                self.file_hdl.attrs['version_minor'] = 2
                
            # check for data group
            if not 'data' in self.file_hdl:
                self.file_hdl.create_group('data')
                
            
            

        
    def __del__(self):
        '''Destructor for EMD file object'''
        # close the file
        if(self.file_hdl):
            self.file_hdl.close()
