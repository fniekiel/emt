'''
Tests for the emd io module.
'''

import unittest
import emt.io.emd

class test_emd(unittest.TestCase):
    '''
    Test the EMD io module
    '''
    
    def test_init_emd(self):
        
        # wrong argument type
        with self.assertRaises(TypeError):
            femd = emt.io.emd.fileEMD(42)
        
        # non existing file in readonly
        with self.assertRaises(IOError):
            femd = emt.io.emd.fileEMD('resources/output/doesnotexist.emd', readonly=True)
            
        # impossible file for read/write
        with self.assertRaises(IOError):
            femd = emt.io.emd.fileEMD('resources/output/output/')
            
        
            
        # open existing file
        femd = emt.io.emd.fileEMD('resources/Au_SAED_D910mm_20x_at_800/Au_SAED_D910mm_20x_at_800.emd')
        # open existing file readonly
        femd = emt.io.emd.fileEMD('resources/Au_SAED_D910mm_20x_at_800/Au_SAED_D910mm_20x_at_800.emd', readonly=True)
        # open nonexisting file for writing
        femd = emt.io.emd.fileEMD('resources/output/test.emd')


# to test with unittest runner
if __name__ == '__main__':
    unittest.main()
