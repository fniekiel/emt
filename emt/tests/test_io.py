'''
Tests for the io module
'''

import unittest
import emt.io

class test(unittest.TestCase):

    def test_ser(self):
        '''
        test the SER module
        '''
        emt.io.ser.test_ser()
        self.assertTrue(False)


# to test with unittest runner
if __name__ == '__main__':
    unittest.main()
