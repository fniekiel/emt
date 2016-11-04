'''
This module provides an interface to the EMD file format.

See https://emdatasets.com/ for more details.
'''

import numpy as np
import h5py


class fileEMD:
    '''
    Class to represent EMD files. 
    
    Implemented for spec 0.2 using the recommended layout for metadata.
    Meant to provide convenience functions for commonly occuring tasks. 
    This means that you will still want to acces fileEMD.file_hdl to manipulate the HDF5 file for not so commonly occuring tasks.
    '''
    
    def __init__(self, filename, readonly=False, verbose=False):
        '''Init opening/creating the file.
        
        input:
        - filename (string)     name of the EMD file
        - readonly (bool)       set to open in read only mode
        - verbose (bool)        set to get extensive output while reading the file
        '''
        
        ## necessary declarations in case something goes bad
        self.file_hdl = None
        
        # convenience handles to access the data in the emd file, everything can as well be accessed using the file_hdl
        self.version = None
        self.data = None
        self.microscope = None
        self.sample = None
        self.user = None
        self.comments = None
        self.list_emds = []             # list of HDF5 groups with emd_data_type type
        
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
                self.data = self.file_hdl.create_group('data')
            else:
                self.data = self.file_hdl['data']
                
            # check for data group
            if not 'microscope' in self.file_hdl:
                self.data = self.file_hdl.create_group('microscope')
            else:
                self.data = self.file_hdl['microscope']
                
            # check for data group
            if not 'sample' in self.file_hdl:
                self.data = self.file_hdl.create_group('sample')
            else:
                self.data = self.file_hdl['sample']
                
            # check for data group
            if not 'user' in self.file_hdl:
                self.data = self.file_hdl.create_group('user')
            else:
                self.data = self.file_hdl['user']
                
            # check for data group
            if not 'comments' in self.file_hdl:
                self.data = self.file_hdl.create_group('comments')
            else:
                self.data = self.file_hdl['comments']
                
            # find emd_data_type groups in the file
            self.list_emds = self.find_emdgroups(self.file_hdl)
            

    def __del__(self):
        '''Destructor for EMD file object'''
        # close the file
        if(self.file_hdl):
            self.file_hdl.close()


    def find_emdgroups(self, parent):
        '''Find all emd_data_type groups within the group parent and return a list of references to their HDF5 groups.'''
        
        emds = []
        
        # recursive function to run and retrieve groups with emd_group_type set to 1
        def proc_group(group, emds):
            # take a look at each item in the group
            for item in group:
                # check if group
                if group.get(item, getclass=True) == h5py._hl.group.Group:
                    item = group.get(item)
                    # check if emd_group_type
                    if 'emd_group_type' in item.attrs:
                        if item.attrs['emd_group_type'] == 1:
                            emds.append(item)
                    # process subgroups
                    proc_group(item, emds)
        
        # run
        proc_group(parent, emds)
        
        return emds
























