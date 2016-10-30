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
        # necessary declarations, if something fails
        self.file_hdl = None

        # check for string
        if not isinstance(filename, str):
            raise TypeError('filename is supposed to be a string')

        # try opening the file
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
        
        # prepare empty dict to be populated while reading
        head = {}

        # go back to beginning of file
        self.file_hdl.seek(0,0)

        # read 3 int16
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
            raise RuntimeError('Unknown TIA version: "{:#06x}"'.format(data[2]))
        head['SeriesVersion'] = data[2]
        if verbose:
            print('SeriesVersion:\t"{:#06x}",\t{}'.format(data[2], dictSeriesVersion[data[2]]))

        # read 4 int32
        data = np.fromfile(self.file_hdl, dtype='<i4', count=4)

        # DataTypeID
        dictDataTypeID = {0x4120:'1D spectra', 0x4122:'2D images'}
        if not data[0] == 0x4122:
            raise RuntimeError('Only 2D images implemented so far')
        head['DataTypeID'] = data[0]
        if verbose:
            print('DataTypeID:\t"{:#06x}",\t{}'.format(data[0], dictDataTypeID[data[0]]))

        # TagTypeID
        dictTagTypeID = {0x4152:'time only',0x4142:'time and 2D position'}
        if not data[1] in dictTagTypeID:
            raise RuntimeError('Unknown TagTypeID: "{:#06x}"'.format(data[1]))
        head['TagTypeID'] = data[1]
        if verbose:
            print('TagTypeID:\t"{:#06x}",\t{}'.format(data[1], dictTagTypeID[data[1]]))

        # TotalNumberElements
        if not data[2] >= 0:
            raise RuntimeError('Negative total number of elements: {}'.format(data[2]))
        head['TotalNumberElements'] = data[2]
        if verbose:
            print('TotalNumberElements:\t{}'.format(data[2]))

        # ValidNumberElements
        if not data[3] >= 0:
            raise RuntimeError('Negative valid number of elements: {}'.format(data[3]))
        head['ValidNumberElements'] = data[3]
        if verbose:
            print('ValidNumberElements:\t{}'.format(data[3]))
        
        # OffsetArrayOffset, sensitive to SeriesVersion
        if head['SeriesVersion']==0x0210:
            data = np.fromfile(self.file_hdl, dtype='<i4', count=1)
        elif head['SeriesVersion']==0x220:
            data = np.fromfile(self.file_hdl, dtype='<i8', count=1)
        else:
            raise RuntimeError('TIA version not implemented for OffsetArrayOffset')
        head['OffsetArrayOffset'] = data[0]
        if verbose:
            print('OffsetArrayOffset:\t{}'.format(data[0]))

        # NumberDimensions
        data = np.fromfile(self.file_hdl, dtype='<i4', count=1)
        if not data[0] >= 0:
            raise RuntimeError('Negative number of dimensions')
        head['NumberDimensions']=data[0]
        if verbose:
            print('NumberDimensions:\t{}'.format(data[0]))

        # Dimension array
        dimensions = []
        for i in range(head['NumberDimensions']):
            if verbose:
                print('reading Dimension {}'.format(i))
            this_dim = {}
        
            # DimensionSize
            data = np.fromfile(self.file_hdl, dtype='<i4', count=1)
            this_dim['DimensionSize'] = data[0]
            if verbose:
                print('DimensionSize:\t{}'.format(data[0]))
            
            data = np.fromfile(self.file_hdl, dtype='<f8', count=2)
            
            # CalibrationOffset
            this_dim['CalibrationOffset'] = data[0]
            if verbose:
                print('CalibrationOffset:\t{}'.format(data[0]))
            
            # CalibrationDelta
            this_dim['CalibrationDelta'] = data[1]
            if verbose:
                print('CalibrationDelta:\t{}'.format(data[1]))
            
            data = np.fromfile(self.file_hdl, dtype='<i4', count=2)
            
            # CalibrationElement
            this_dim['CalibrationElement'] = data[0]
            if verbose:
                print('CalibrationElement:\t{}'.format(data[0]))
            
            # DescriptionLength
            n = data[1]
            
            # Description
            data = np.fromfile(self.file_hdl, dtype='<i1', count=n)
            data = ''.join(map(chr, data))
            this_dim['Description'] = data
            if verbose:
                print('Description:\t{}'.format(data))
            
            # UnitsLength
            data = np.fromfile(self.file_hdl, dtype='<i4', count=1)
            n = data[0]
            
            # Units
            data = np.fromfile(self.file_hdl, dtype='<i1', count=n)
            data = ''.join(map(chr, data))
            this_dim['Units'] = data
            if verbose:
                print('Units:\t{}'.format(data))


            dimensions.append(this_dim)
            
        head['Dimensions'] = tuple(dimensions)
        
        #import pdb;pdb.set_trace()

        return head


    def getImage(self, i):
        '''Retrieve image i from data file.

        returns:
        - img		image as array
        '''

        raise RuntimeError('Not implemented yet!')


