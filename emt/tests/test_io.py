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

        # non existing file
        with self.assertRaises(IOError):
            fser = emt.io.ser.fileSER('')

        # existing file
        fser = emt.io.ser.fileSER('resources/Pt_SAED_D910mm_single/im01_1.ser', verbose=True)

        #fser.getImage(0)


# to test with unittest runner
if __name__ == '__main__':
    unittest.main()
