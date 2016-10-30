'''
Tests for the io module.
'''

import unittest
import emt.io.ser

class test(unittest.TestCase):

    def test_ser(self):
        '''
        test the SER module
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

        # try single image file
        fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01_1.ser', verbose=True)
        
        # wrong index
        with self.assertRaises(IndexError):
            fser.getDataset(-1)
            
        # wrong index type
        with self.assertRaises(TypeError):
            fser.getDataset('foo')
        
        dataset, meta = fser.getDataset(0, verbose=True)
        tag = fser.getTag(0, verbose=True)
        
        fser.writeEMD('resources/output/Pt_SAED_D910mm_single.emd')
        
        # try series file
        fser = emt.io.ser.fileSER('resources/Au_SAED_D910mm_20x_at_800/pos01_1.ser', verbose=True)
        fser.writeEMD('resources/output/Au_SAED_D910mm_20x_at_800.emd')

        fser = emt.io.ser.fileSER('resources/Au_SAED_D910mm_100x_at_RT/step_off_1.ser', verbose=True)
        fser.head['ValidNumberElements'] = 20
        fser.writeEMD('resources/output/Au_SAED_D910mm_100x_at_RT.emd')

# to test with unittest runner
if __name__ == '__main__':
    unittest.main()
