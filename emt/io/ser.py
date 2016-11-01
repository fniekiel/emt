'''
This module provides an interface to the SER file format written by TIA.

Following the information provided by Dr Chris Boothroyd (http://www.er-c.org/cbb/info/TIAformat/) and the implementation by Peter Ercius.
'''
import numpy as np
import h5py
import os
import re
import xml.etree.ElementTree as ET
import datetime

class NotSERError(Exception):
    '''Exception if a file is not in SER file format'''
    pass


class fileSER:
    '''
    Class to represent SER files (read only).
    '''

    dictByteOrder = {0x4949 : 'little endian'}
    dictSeriesVersion = {0x0210 : '< TIA 4.7.3', 0x0220 : '>= TIA 4.7.3'}
    dictDataTypeID = {0x4120:'1D spectra', 0x4122:'2D images'}
    dictTagTypeID = {0x4152:'time only',0x4142:'time and 2D position'}
    dictDataType = {1:'<u1', 2:'<u2', 3:'<u4', 4:'<i1', 5:'<i2', 6:'<i4', 7:'<f4', 8:'<f8', 9:'<c8', 10:'<c16'}

    def __init__(self, filename, emifile=None, verbose=False):
        '''Init opening the file and reading in the header.
        
        input:
        - filename (string)     name of the SER file
        - verbose (bool)        True to get extensive output while reading the file
        '''
        # necessary declarations, if something fails
        self.file_hdl = None
        self.emi = None

        # check for string
        if not isinstance(filename, str):
            raise TypeError('Filename is supposed to be a string')

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
        
        # read emi, if provided
        if emifile:
            self.emi = self.readEMI(emifile)


    def __del__(self):
        '''Closing the file stream on del.'''
        # close the file
        if(self.file_hdl):
            self.file_hdl.close()


    def readHeader(self, verbose=False):
        '''
        Read and return the SER files header.
        
        input:
        - verbose (bool)        True to get extensive output while reading the file

        returns:
        - head		the header of the SER file as dict
        '''
        
        # prepare empty dict to be populated while reading
        head = {}

        # go back to beginning of file
        self.file_hdl.seek(0,0)

        # read 3 int16
        data = np.fromfile(self.file_hdl, dtype='<i2', count=3)

        # ByteOrder (only little Endian expected)
        if not data[0] in self.dictByteOrder:
            raise RuntimeError('Only little Endian implemented for SER files')
        head['ByteOrder'] = data[0]
        if verbose:
            print('ByteOrder:\t"{:#06x}",\t{}'.format(data[0], self.dictByteOrder[data[0]]))

        # SeriesID, check whether TIA Series Data File   
        if not data[1] == 0x0197:
            raise NotSERError('This is not a TIA Series Data File (SER)')
        head['SeriesID'] = data[1]
        if verbose:
            print('SeriesID:\t"{:#06x},\tTIA Series Data File'.format(data[1]))

        # SeriesVersion
        if not data[2] in self.dictSeriesVersion:
            raise RuntimeError('Unknown TIA version: "{:#06x}"'.format(data[2]))
        head['SeriesVersion'] = data[2]
        if verbose:
            print('SeriesVersion:\t"{:#06x}",\t{}'.format(data[2], self.dictSeriesVersion[data[2]]))
        # version dependend fileformat for below
        if head['SeriesVersion']==0x0210:
            offset_dtype = '<i4'
        else: #head['SeriesVersion']==0x220:
            offset_dtype = '<i8'
        
        # read 4 int32
        data = np.fromfile(self.file_hdl, dtype='<i4', count=4)

        # DataTypeID
        if not data[0] == 0x4122:
            raise RuntimeError('Only 2D images implemented so far')
        head['DataTypeID'] = data[0]
        if verbose:
            print('DataTypeID:\t"{:#06x}",\t{}'.format(data[0], self.dictDataTypeID[data[0]]))

        # TagTypeID
        if not data[1] in self.dictTagTypeID:
            raise RuntimeError('Unknown TagTypeID: "{:#06x}"'.format(data[1]))
        head['TagTypeID'] = data[1]
        if verbose:
            print('TagTypeID:\t"{:#06x}",\t{}'.format(data[1], self.dictTagTypeID[data[1]]))

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
        data = np.fromfile(self.file_hdl, dtype=offset_dtype, count=1)
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


        # Dimensions array
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
        
        # save dimensions array as tuple of dicts in head dict
        head['Dimensions'] = tuple(dimensions)
        
        
        # Offset array
        self.file_hdl.seek(head['OffsetArrayOffset'],0)
        
        # DataOffsetArray
        data = np.fromfile(self.file_hdl, dtype=offset_dtype, count=head['ValidNumberElements'])
        head['DataOffsetArray'] = data.tolist()
        if verbose:
            print('reading in DataOffsetArray')
        
        # TagOffsetArray
        data = np.fromfile(self.file_hdl, dtype=offset_dtype, count=head['ValidNumberElements'])
        head['TagOffsetArray'] = data.tolist()
        if verbose:
            print('reading in TagOffsetArray')     

        return head


    def checkIndex(self, i):
        '''
        Check index i for sanity, otherwise raise Exception.
        
        input:
        - i(int)        index
        '''
        
        # check type
        if not isinstance(i, int):
            raise TypeError('index supposed to be integer')

        # check whether in range
        if i < 0 or i>= self.head['ValidNumberElements']:
            raise IndexError('Index out of range, trying to access element {} of {} valid elements'.format(i+1, self.head['ValidNumberElements']))
            
        return
        

    def getDataset(self, index, verbose=False):
        '''Retrieve dataset from data file.

        input:
        - index (int)   index of dataset
        - verbose (bool)        True to get extensive output while reading the file
        
        returns:
        - dataset	dataset as array
        - meta          metadata as dict
        '''

        # check index, will raise Exceptions if not
        try:
            self.checkIndex(index)
        except:
            raise

        if verbose:
            print('Getting dataset {} of {}.'.format(index, self.head['ValidNumberElements']))
            
        # go to dataset in file
        self.file_hdl.seek(self.head['DataOffsetArray'][index],0)
        
        # read meta
        meta = {}
        
        # number of calibrations depends on DataTypeID
        if self.head['DataTypeID'] == 0x4120:
            n = 1
        elif self.head['DataTypeID'] == 0x4122:
            n = 2
        else:
            raise RuntimeError('Unknown DataTypeID')
       
        # read in the calibrations    
        cals = []
        for i in range(n):
            if verbose:
                print('Reading calibration {}'.format(i))
                
            this_cal = {}
        
            data = np.fromfile(self.file_hdl, dtype='<f8', count=2)
            
            # CalibrationOffset
            this_cal['CalibrationOffset'] = data[0]
            if verbose:
                print('CalibrationOffset:\t{}'.format(data[0]))
            
            # CalibrationDelta
            this_cal['CalibrationDelta'] = data[1]
            if verbose:
                print('CalibrationDelta:\t{}'.format(data[1]))
            
            data = np.fromfile(self.file_hdl, dtype='<i4', count=1)
            
            # CalibrationElement
            this_cal['CalibrationElement'] = data[0]
            if verbose:
                print('CalibrationElement:\t{}'.format(data[0]))
            
            cals.append(this_cal)
            
        meta['Calibration'] = tuple(cals)
        
        data = np.fromfile(self.file_hdl, dtype='<i2', count=1)
        
        # DataType
        meta['DataType'] = data[0]
        
        if not data[0] in self.dictDataType:
            raise RuntimeError('Unknown DataType: "{}"'.format(data[0]))
        if verbose:
            print('DataType:\t{},\t{}'.format(data[0],self.dictDataType[data[0]]))
        
        data = np.fromfile(self.file_hdl, dtype='<i4', count=2)
        
        # ArrayShape
        data = data.tolist()
        meta['ArrayShape'] = data
        if verbose:
            print('ArrayShape:\t{}'.format(data))
        
        ## ArraySizeX
        #meta['ArraySizeX'] = data[0]
        #if verbose:
        #    print('ArraySizeX:\t{}'.format(data[0]))
        
        ## ArraySizeY
        #meta['ArraySizeY'] = data[1]
        #if verbose:
        #    print('ArraySizeY:\t{}'.format(data[1]))
            
        # dataset
        dataset = np.fromfile(self.file_hdl, dtype=self.dictDataType[meta['DataType']], count=meta['ArrayShape'][0]*meta['ArrayShape'][1])
        dataset = dataset.reshape(meta['ArrayShape'])
        
        if self.head['DataTypeID'] == 0x4122:
            dataset = np.flipud(dataset)

        return dataset, meta


    def getTag(self, index, verbose=False):
        '''Retrieve tag from data file.

        input:
        - index (int)           index of tag
        - verbose (bool)        True to get extensive output while reading the file

        returns:
        - tag		        tag as dict
        '''

        # check index, will raise Exceptions if not
        try:
            self.checkIndex(index)
        except:
            raise

        if verbose:
            print('Getting tag {} of {}.'.format(index, self.head['ValidNumberElements']))
            
        # go to dataset in file
        self.file_hdl.seek(self.head['TagOffsetArray'][index],0)

        # read tag
        tag = {}
        
        data = np.fromfile(self.file_hdl, dtype='<i4', count=2)
        
        # TagTypeID
        tag['TagTypeID'] = data[0]
        if verbose:
            print('TagTypeID:\t"{:#06x}",\t{}'.format(data[0], self.dictTagTypeID[data[0]]))
            
        # Time    
        tag['Time'] = data[1]
        if verbose:
            print('Time:\t{}'.format(data[1]))
        
        # check for position
        if tag['TagTypeID'] == 0x4142:
            data = np.fromfile(self.file_hdl, dtype='<f8', count=2)
            
            # PositionX
            tag['PositionX'] = data[0]
            if verbose:
                print('PositionX:\t{}'.format(data[0]))
            
            # PositionY
            tag['PositionY'] = data[1]
            if verbose:
                print('PositionY:\t{}'.format(data[1]))   
     
        return tag
        
    
    def createDim(self, size, offset, delta, element):
        '''Create dimension labels from SER information
        
        input:
        - size          number of elements
        - offset        value at indicated element
        - delta         difference between elements
        - element       indicates the element of value offset
        
        return:
        - dim           dimension labels as np.array
        
        '''
        
        #dim = np.zeros(size)
        #dim[:] = np.nan
        
        dim = np.array(range(size)).astype('f8')
        dim = dim*delta
        dim += (offset - dim[element])
        
        return dim
    
    def parseEntryEMI(self, value):
        '''Auxiliary function to parse string entry to int, float or np.string_.
        
        input:
        - value (string)        string containing an int, float or string
        
        return:
        - p                     int, float or string of value
        '''
        
        # try to parse as int
        try:
            p = int(value)
        except:
            # if not int, then try float
            try:
                p = float(value)
            except:
                # if neither int nor float, stay with string
                p = np.string_(str(value))
        
        return p
        
    
    def readEMI(self, filename):
        '''Read the meta data from an EMI file.
        
        input:
        - filename (string)     name of the EMI file
        
        return:
        - emi           dict of metadata
        '''
        
        # check for string
        if not isinstance(filename, str):
            raise TypeError('Filename is supposed to be a string')

        # try opening the file
        try:
            # open file for reading bytes, as binary and text are intermixed
            f_emi = open(filename, 'rb')
        except IOError:
            print('Error reading file: "{}"'.format(filename))
            raise
        except :
            raise
        
        # dict to store emi stuff
        emi = {}
        
        # need anything readable from <ObjectInfo> to </ObjectInfo>
        collect = False
        data = b''
        for line in f_emi:
            if b'<ObjectInfo>' in line:
                collect = True
            if collect:
                data += line.strip()
            if b'</ObjectInfo>' in line:
                collect = False

        # close the file
        f_emi.close()
            
        # strip of binary stuff still around
        data = data.decode('ascii', errors='ignore')
        matchObj = re.search('<ObjectInfo>(.+)</ObjectInfo', data)
        try:
            data = matchObj.group(1)
        except:
            raise RuntimeError('Could not find EMI metadata in specified file.')

        # parse metadata as xml
        root = ET.fromstring('<emi>'+data+'</emi>')
        
        # single items
        emi['Uuid'] = root.findtext('Uuid')
        emi['AcquireDate'] = root.findtext('AcquireDate')
        emi['Manufacturer'] = root.findtext('Manufacturer')
        emi['DetectorPixelHeigth'] = root.findtext('DetectorPixelHeight')
        emi['DetectorPixelWidth'] = root.findtext('DetectorPixelWidth')

        # Microscope Conditions
        grp = root.find('ExperimentalConditions/MicroscopeConditions')
        
        for elem in grp:
            emi[elem.tag] = self.parseEntryEMI(elem.text)
            #print('{}:\t{}'.format(elem.tag, elem.text)) 

        # Experimental Description
        grp = root.find('ExperimentalDescription/Root')
        
        for elem in grp:
            emi['{} [{}]'.format(elem.findtext('Label'), elem.findtext('Unit'))] = self.parseEntryEMI(elem.findtext('Value'))
            #print('{} [{}]: \t{}'.format(elem.findtext('Label'), elem.findtext('Unit'), elem.findtext('Value')))

        # AcquireInfo
        grp = root.find('AcquireInfo')
        
        for elem in grp:
            emi[elem.tag] = self.parseEntryEMI(elem.text)
            
        # DetectorRange
        grp = root.find('DetectorRange')
        
        for elem in grp:
            emi['DetectorRange_'+elem.tag] = self.parseEntryEMI(elem.text)

        return emi
        
        
    def writeEMD(self, filename):
        '''
        Write SER data to an EMD file.
        
        input:
        - filename (string)             name of the EMD file
        '''
        
        # create the EMD file and set version attributes
        f = h5py.File(filename, 'w', driver=None)
        f.attrs['version_major'] = 0
        f.attrs['version_minor'] = 2
        
        # create a subgroup to not save data in root
        grp_data = f.create_group('data')
        
        # subgroup for the file
        grp = grp_data.create_group(os.path.basename(self.file_hdl.name))
        
        # mark as EMD group
        grp.attrs['emd_group_type'] = 1
        
        # use first dataset to layout memory
        data, first_meta = self.getDataset(0)
        
        if self.head['DataTypeID'] == 0x4122:
            dset = grp.create_dataset('data', (first_meta['ArrayShape'][0], first_meta['ArrayShape'][1], self.head['ValidNumberElements']), dtype=self.dictDataType[first_meta['DataType']])
        else:
            raise RuntimeError('Only 2D datasets implemented yet!')
        
        # arrays to collect interesting meta data while looping images
        time = np.zeros(self.head['ValidNumberElements'], dtype='i4')
        if self.head['TagTypeID'] == 0x4142:
            positionx = np.zeros(self.head['ValidNumberElements'], dtype='f8')
            positionx[:] = np.nan
            positiony = np.zeros(self.head['ValidNumberElements'], dtype='f8')
            positiony[:] = np.nan
            
        
        # loop over datasets in ser file to retrieve them
        
        ### h5py performance issues, switching to a memory based approach
        #for i in range(self.head['ValidNumberElements']):
        #    print('converting dataset {} of {}'.format(i+1, self.head['ValidNumberElements']))
        #    data, meta = self.getDataset(i)
        #    dset[:,:,i] = data[:,:]
        #    f.flush()
        
        ### if series size is to large, this will lead to heavy swapping   
        dset_buf = np.zeros( dset.shape, dtype=dset.dtype )
        for i in range(self.head['ValidNumberElements']):
            print('converting dataset {} of {}'.format(i+1, self.head['ValidNumberElements']))
            
            # retrieve dataset and put into buffer
            data, meta = self.getDataset(i)
            dset_buf[:,:,i] = data[:,:].transpose()
            
            # get tag data per image
            tag = self.getTag(i)
            time[i] = tag['Time']
            if tag['TagTypeID'] == 0x4142:
                positionx[i] = tag['PositionX']
                positiony[i] = tag['PositionY']
        
        # write buffer to h5
        dset[:,:,:] = dset_buf[:,:,:]
        f.flush()
        del dset_buf
        
        
        # add dimension datasets
        n = 1
        
        if self.head['DataTypeID'] == 0x4122:
            # 2d datasets
            dim = self.createDim(first_meta['ArrayShape'][0], first_meta['Calibration'][0]['CalibrationOffset'], first_meta['Calibration'][0]['CalibrationDelta'], first_meta['Calibration'][0]['CalibrationElement'])
            dim_hdl = grp.create_dataset('dim{:d}'.format(n), data=dim)
            dim_hdl.attrs['name']=np.string_('x')
            dim_hdl.attrs['units']=np.string_('[m]')
            n +=1
            
            dim = self.createDim(first_meta['ArrayShape'][1], first_meta['Calibration'][1]['CalibrationOffset'], first_meta['Calibration'][1]['CalibrationDelta'], first_meta['Calibration'][1]['CalibrationElement'])
            dim_hdl = grp.create_dataset('dim{:d}'.format(n), data=dim)
            dim_hdl.attrs['name']=np.string_('y')
            dim_hdl.attrs['units']=np.string_('[m]')
            n +=1
            
        ### old loop to add dimensions, had to hardcode labels
        #for i in range(len(first_meta['ArrayShape'])):
        #    dim = self.createDim(first_meta['ArrayShape'][i], first_meta['Calibration'][i]['CalibrationOffset'], first_meta['Calibration'][i]['CalibrationDelta'], first_meta['Calibration'][i]['CalibrationElement'])
        #    grp.create_dataset('dim{:d}'.format(n), data=dim)
        #    grp['dim{:d}'.format(n)].attrs['name']='spacial'
        #    grp['dim{:d}'.format(n)].attrs['units']='test'
        #    n +=1
            
        for i in range(self.head['NumberDimensions']):
            dim = self.createDim(self.head['Dimensions'][i]['DimensionSize'], self.head['Dimensions'][i]['CalibrationOffset'], self.head['Dimensions'][i]['CalibrationDelta'], self.head['Dimensions'][i]['CalibrationElement'])
            grp.create_dataset('dim{:d}'.format(n), data=dim)
            grp['dim{:d}'.format(n)].attrs['name']=np.string_(self.head['Dimensions'][i]['Description'])
            grp['dim{:d}'.format(n)].attrs['units']=np.string_('[{}]'.format(self.head['Dimensions'][i]['Units']))
            n +=1
        
        
        # hardcoded dim3_ in here, need to adapt later
        # add additional dimension datasets
        dim_hdl = grp.create_dataset('dim3_time', data=time)
        dim_hdl.attrs['name']=np.string_('timestamp')
        dim_hdl.attrs['units']=np.string_('[s]')
        
        if self.head['TagTypeID'] == 0x4142:
            dim_hdl = grp.create_dataset('dim3_positionx', data=positionx)
            dim_hdl.attrs['name']=np.string_('Position X')
            dim_hdl.attrs['units']=np.string_('[m]')
        
            dim_hdl = grp.create_dataset('dim3_positiony', data=positiony)
            dim_hdl.attrs['name']=np.string_('Position Y')
            dim_hdl.attrs['units']=np.string_('[m]')
            
        
        # put meta information from EMI to Microscope group, if available
        if self.emi:
            grp_microscope = grp.create_group('microscope')
            for key in self.emi:
                grp_microscope.attrs[key] = self.emi[key]
                
        # write comment into Comment group
        grp_comment = f.create_group('comments')
        grp_comment.attrs[str(datetime.datetime.utcnow())+' (UTC)'] = np.string_('Converted SER file "{}" to EMD using the emt library.'.format(self.file_hdl.name))
        
        f.close()
            
