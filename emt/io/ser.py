'''
This module provides an interface to the SER file format written by TIA.

Following the information provided by Dr Chris Boothroyd (http://www.er-c.org/cbb/info/TIAformat/)
'''

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
            print('Error opening file: "{}"'.format(filename))
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
        Read and return its header.

        returns:
        - head		the header of the SER file
        '''
        
        head = None

        return head


def test_ser():
    print('test_ser')
