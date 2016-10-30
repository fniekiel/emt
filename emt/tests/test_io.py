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

        # try single image file
        fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01_1.ser', verbose=True)
        # try series file
        fser = emt.io.ser.fileSER('resources/Au_SAED_D910mm_100x_at_RT/step_off_1.ser', verbose=True)

        #fser.getImage(0)


# to test with unittest runner
if __name__ == '__main__':
    unittest.main()
