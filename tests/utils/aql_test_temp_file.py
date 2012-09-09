import sys
import os.path

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import skip, AqlTestCase, runLocalTests

from aql_temp_file import Tempfile, Tempdir
from aql_utils import openFile

#//===========================================================================//

class TestTempFile( AqlTestCase ):
  def test_temp_file(self):
    temp_file_name = None
    
    with Tempfile() as temp_file:
      
      temp_file.write( '1234567890\n1234567890'.encode() )
      temp_file.flush()
      
      temp_file_name = temp_file.name
    
    self.assertFalse( os.path.isfile(temp_file_name) )
    
  #//=======================================================//
  
  def test_temp_file_rw(self):
    temp_file_name = None
    
    with Tempfile() as temp_file:
      
      test_string = '1234567890'
      
      temp_file.write( test_string.encode() )
      temp_file.flush()
      
      temp_file_name = temp_file.name
      
      with open(temp_file_name, "r") as temp_file_rh:
        test_string_read = temp_file_rh.read()
        self.assertEqual( test_string,test_string_read )
  
  #//=======================================================//
  
  def test_temp_dir(self):
    with Tempdir() as tmp_dir:
      tmp_dir = Tempdir( dir = tmp_dir.path )
      
      for i in range(10):
        Tempfile( dir = tmp_dir.path, suffix = '.tmp' ).close()
      
    self.assertFalse( os.path.exists(tmp_dir.path) )
  
  #//=======================================================//
  
  def test_temp_file_in_use(self):
    with Tempfile() as temp_file:
      
      temp_file.remove()
      
      with openFile( temp_file.name, write = True, binary = True ) as f:
        f.write( b'1234567890' )
    
    self.assertFalse( os.path.isfile(temp_file.name) )

#//===========================================================================//

if __name__ == "__main__":
  runLocalTests()
