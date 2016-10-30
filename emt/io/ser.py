'''
This module provides an interface to the SER file format written by TIA.

Following the information provided by Dr Chris Boothroyd (http://www.er-c.org/cbb/info/TIAformat/) and the implementation by Peter Ercius.
'''
import numpy as np

class NotSERError(Exception):
    pass

class fileSER:
    '''
    Class to represent SER files (read only).
    '''

    def __init__(self, filename, verbose=False):
        '''Init opening the file and reading in the header.
        '''
        # try opening the file
        self.file_hdl = None
        try:
            self.file_hdl = open(filename, 'rb')
        except IOError:
            print('Error reading file: "{}"'.format(filename))
            raise
        except :
            raise

        # read header
        self.head = self.readHeader(verbose)


    def __del__(self):
        '''Closing the file stream on del.'''
        # close the file
        if(self.file_hdl):
            self.file_hdl.close()


    def readHeader(self, verbose=False):
        '''
        Read and return the SER files header.

        returns:
        - head		the header of the SER file
        '''
        
        head = {}

        data = np.fromfile(self.file_hdl, dtype='<i2', count=3)

        # ByteOrder (only little Endian expected)
        dictByteOrder = {0x4949 : 'little endian'}
        if not data[0] in dictByteOrder:
            raise RuntimeError('Only little Endian implemented for SER files')
        head['ByteOrder'] = data[0]
        if verbose:
            print('ByteOrder:\t"{:#06x}",\t{}'.format(data[0], dictByteOrder[data[0]]))

        # SeriesID, check whether TIA Series Data File   
        if not data[1] == 0x0197:
            raise NotSERError('This is not a TIA Series Data File (SER)')
        head['SeriesID'] = data[1]
        if verbose:
            print('SeriesID:\t"{:#06x},\tTIA Series Data File'.format(data[1]))

        # SeriesVersion
        dictSeriesVersion = {0x0210 : '< TIA 4.7.3', 0x0220 : '>= TIA 4.7.3'}
        if not data[2] in dictSeriesVersion:
            raise RuntimeError('Unknown TIA version: "{}"'.format(hex(data[2])))
        head['SeriesVersion'] = data[2]
        if verbose:
            print('SeriesVersion:\t"{:#06x}",\t{}'.format(data[2], dictSeriesVersion[data[2]]))




        return head


    def getImage(self, i):
        '''Retrieve image i from data file.

        returns:
        - img		image as array
        '''

        raise RuntimeError('Not implemented yet!')


