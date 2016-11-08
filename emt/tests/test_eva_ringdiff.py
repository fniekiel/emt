'''
Tests for the evaluation of ring diffraction patterns.
'''

import unittest

import emt.io.emd
import emt.eva.ring_diff


class test_ringdiff(unittest.TestCase):
    '''
    Test the evaluation of ring diffraction patterns.
    '''
    
    def test_eva(self):
        
        # wrong file
        with self.assertRaises(RuntimeError):
            with open('resources/output/test.txt', 'w') as f:
                emt.eva.ring_diff.evaEMDFile(f)
                
                
        # right file
        femd = emt.io.emd.fileEMD('resources/Pt_SAED_D910mm_single/Pt_SAED_D910mm_single.emd')
        
        emt.eva.ring_diff.evaEMDFile(femd, verbose=True)
        
        
        
        

# to test with unittest runner
if __name__ == '__main__':
    unittest.main()
