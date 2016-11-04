'''
Tests for the ser io module.
'''

import unittest
import emt.io.ser
import numpy as np
import os
import os.path

class test_ser(unittest.TestCase):
    '''
    Test the SER io module.
    '''

    def test_read_ser(self):
        '''
        Test the ser reading functionality.
        '''
        
        # wrong argument type
        with self.assertRaises(TypeError):
            fser = emt.io.ser.fileSER(42)

        # non existing file
        with self.assertRaises(IOError):
            fser = emt.io.ser.fileSER('')
            
        # wrong file
        with self.assertRaises(Exception):
            fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01.emi', verbose=True)

        # single 2D image file
        fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01_1.ser')
        fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01_1.ser', verbose=True)
        fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01_1.ser', 'resources/Pt_SAED_D910mm_single/im01.emi', verbose=True)
        
        # time series of 2D images
        fser = emt.io.ser.fileSER('resources/Au_SAED_D910mm_20x_at_800/pos01_1.ser')
        fser = emt.io.ser.fileSER('resources/Au_SAED_D910mm_20x_at_800/pos01_1.ser', verbose=True)
        fser = emt.io.ser.fileSER('resources/Au_SAED_D910mm_20x_at_800/pos01_1.ser','resources/Au_SAED_D910mm_20x_at_800/pos01.emi', verbose=True)
        
        # single 1D dataset
        # time series of 1D datasets
        # 2D mapping of 2D datasets
        # 2D mapping of 1D dataset
        ## not implemented yet
        
        
    def test_read_emi(self):
        '''
        Test the emi reading functionality.
        '''
        
        # ser file for this testing
        fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01_1.ser')
        
        # wrong argument
        with self.assertRaises(TypeError):
            fser.readEMI(42)
        
        # non existing file
        with self.assertRaises(IOError):
            fser.readEMI('')
        
        # auxiliary function
        self.assertIsInstance(fser.parseEntryEMI('42'), int)
        self.assertIsInstance(fser.parseEntryEMI('42.42'), float)
        self.assertIsInstance(fser.parseEntryEMI('forty two'), np.string_)
        
        # read 
        fser.readEMI('resources/Pt_SAED_D910mm_single/im01.emi')
        
        
    def test_read_dataset(self):
        '''
        Test functions for retrieving datasets.
        '''
    
        # ser file for this testing
        fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01_1.ser')
        
        # wrong index
        with self.assertRaises(IndexError):
            fser.getDataset(-1)
            
        # wrong index type
        with self.assertRaises(TypeError):
            fser.getDataset('foo')
        
        # try dataset + meta
        dataset, meta = fser.getDataset(0, verbose=True)
        
        # try tag
        tag = fser.getTag(0, verbose=True)
        
        
    def test_write_emd(self):
        '''
        Test the emd writing functionality.
        '''
        
        # single 2D image file
        fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01_1.ser')
        if os.path.isfile('resources/output/Pt_SAED_D910mm_single_woemi.emd'):
            os.remove('resources/output/Pt_SAED_D910mm_single_woemi.emd')
        fser.writeEMD('resources/output/Pt_SAED_D910mm_single_woemi.emd')
        fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01_1.ser', 'resources/Pt_SAED_D910mm_single/im01.emi')
        if os.path.isfile('resources/output/Pt_SAED_D910mm_single.emd'):
            os.remove('resources/output/Pt_SAED_D910mm_single.emd')
        fser.writeEMD('resources/output/Pt_SAED_D910mm_single.emd')
        with self.assertRaises(IOError):
            fser.writeEMD('')
        
        # time series of 2D images
        fser = emt.io.ser.fileSER('resources/Au_SAED_D910mm_20x_at_800/pos01_1.ser', 'resources/Au_SAED_D910mm_20x_at_800/pos01.emi')
        if os.path.isfile('resources/output/Au_SAED_D910mm_20x_at_800.emd'):
            os.remove('resources/output/Au_SAED_D910mm_20x_at_800.emd')
        fser.writeEMD('resources/output/Au_SAED_D910mm_20x_at_800.emd')
        
        # large time series of 2D images
        fser = emt.io.ser.fileSER('resources/Au_SAED_D910mm_100x_at_RT/step_off_1.ser','resources/Au_SAED_D910mm_100x_at_RT/step_off.emi', verbose=True)
        ##fser.head['ValidNumberElements'] = 20
        if os.path.isfile('resources/output/Au_SAED_D910mm_100x_at_RT.emd'):
            os.remove('resources/output/Au_SAED_D910mm_100x_at_RT.emd')
        fser.writeEMD('resources/output/Au_SAED_D910mm_100x_at_RT.emd')
        
        # single 1D dataset
        # time series of 1D datasets
        # 2D mapping of 2D datasets
        # 2D mapping of 1D dataset
        ## not implemented yet


# to test with unittest runner
if __name__ == '__main__':
    unittest.main()
