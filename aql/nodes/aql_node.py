
# Copyright (c) 2011-2013 The developers of Aqualid project - http://aqualid.googlecode.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__all__ = (
  'Node',
)

import hashlib

from aql.util_types import toSequence
from aql.values import Value, SignatureValue, DependsValue, DependsValueContent

#//===========================================================================//

class   ErrorNodeDependencyInvalid( Exception ):
  def   __init__( self, dep ):
    msg = "Invalid node dependency: %s" % (dep,)
    super(ErrorNodeDependencyInvalid, self).__init__( msg )

class   ErrorNoTargets( Exception ):
  def   __init__( self, node ):
    msg = "Node targets are not built yet: %s" % (node.buildStr())
    super(ErrorNoTargets, self).__init__( msg )

class   ErrorNoDeps( Exception ):
  def   __init__( self, node ):
    msg = "Node dependencies are not built yet: %s" % (node.buildStr())
    super(ErrorNoDeps, self).__init__( msg )

#//===========================================================================//

#noinspection PyAttributeOutsideInit
class Node (object):
  
  __slots__ = \
  (
    'builder',
    'builder_data',
    
    '_sources',
    'source_values',
    'dep_nodes',
    'dep_values',
    
    'sources_value',
    'targets_value',
    'itargets_value',
    'ideps_value',
  )
  
  #//-------------------------------------------------------//
  
  def   __init__( self, builder, sources ):
    
    self.builder = builder
    self.builder_data = None
    self._sources = toSequence( sources )
    self.dep_nodes = set()
    self.dep_values = []
  
  #//=======================================================//
  
  def   depends( self, dependencies ):
    
    for value in toSequence( dependencies ):
      if isinstance( value, Node ):
        self.dep_nodes.add( value )
      
      elif isinstance( value, Value ):
        self.dep_values.append( value )
      
      else:
        raise ErrorNodeDependencyInvalid( value )
  
  #//=======================================================//
  
  def   split( self, builder ):
    nodes = []
    
    dep_nodes = self.dep_nodes
    dep_values = self.dep_values
    for src_value in self.sourceValues():
      node = Node( builder, src_value )
      node.dep_nodes = dep_nodes
      node.dep_values = dep_values
      nodes.append( node )
    
    return nodes
  
  #//=======================================================//
  
  def   __setValues( self ):
    
    names = [ self.builder.name.encode('utf-8') ]
    sign  = [ self.builder.signature ]
    
    sources = sorted( self.sourceValues(), key = lambda v: v.name )
    
    names += ( value.name.encode('utf-8') for value in sources )
    
    sign += ( value.content.signature for value in sources )
    
    deps = self.dependencies()
    
    sign += ( value.name.encode('utf-8') for value in deps )
    sign += ( value.content.signature for value in deps )
    
    #//-------------------------------------------------------//
    #// Signature
    
    sign_hash = hashlib.md5()
    for s in sign:
      sign_hash.update( s )
    
    signature = sign_hash.digest()
    
    #//-------------------------------------------------------//
    #// Name key
    name_hash = hashlib.md5()
    for s in names:
      name_hash.update( s )
    
    name_key = name_hash.digest()
    
    self.sources_value = SignatureValue( name_key, signature )
    
    #//-------------------------------------------------------//
    #// Targets
    
    name_hash.update( b'targets' )
    self.targets_value = DependsValue( name_hash.digest() )
    
    name_hash.update( b'itargets' )
    self.itargets_value = DependsValue( name_hash.digest() )
    
    name_hash.update( b'ideps' )
    self.ideps_value = DependsValue( name_hash.digest() )
  
  #//=======================================================//
  
  def   __getattr__( self, attr ):
    if attr in ('sources_value', 'targets_value', 'itargets_value', 'ideps_value'):
      self.__setValues()
      return getattr(self, attr)
    
    if attr == 'source_values':
      self.source_values = source_values = self.__getSourceValues()
      return source_values
    
    raise AttributeError( "%s instance has no attribute '%s'" % (type(self), attr) )
  
  #//=======================================================//
  
  def   values( self ):
    
    values = [ self.sources_value, self.targets_value, self.itargets_value, self.ideps_value ]
    
    targets = self.targets_value.content.data
    if targets: values += targets
    
    itargets = self.itargets_value.content.data
    if itargets: values += itargets
    
    ideps = self.ideps_value.content.data
    if ideps: values += ideps
    
    return values
  
  #//=======================================================//
  
  def   load( self, vfile ):
    
    values = [ self.targets_value, self.itargets_value, self.ideps_value ]
    values = vfile.findValues( values )
    
    self.targets_value, self.itargets_value, self.ideps_value = values
  
  #//=======================================================//
  
  def   actual( self, vfile  ):
    
    values = [ self.sources_value, self.targets_value, self.itargets_value, self.ideps_value ]
    values = vfile.findValues( values )
    
    if self.sources_value != values.pop(0):
      return False
    
    for value in values:
      if not value.actual():
        return False
    
    self.targets_value, self.itargets_value, self.ideps_value = values
    
    return True
  
  #//=======================================================//
  
  def   __getSourceValues(self):
    values = []

    for value in self._sources:
      if isinstance( value, Node ):
        values += value.targets()
      
      elif isinstance( value, Value ):
        values.append( value )
      
      else:
        values += self.builder.makeValues( value, use_cache = True )

    return tuple(values)
  
  #//=======================================================//
  
  def   sources(self):
    return tuple( src.get() for src in self.source_values )
  
  def   sourceValues(self):
    return self.source_values
  
  def   sourceNodes(self):
    return tuple( filter( lambda node: isinstance(node,Node), self._sources ) )
  
  #//=======================================================//
  
  def   dependencies(self):
    values = []
    
    for node in self.dep_nodes:
      values += toSequence( node.targets_value.content.data )
    
    values += self.dep_values
    
    values.sort( key = lambda v: v.name )
    
    return values
  
  #//=======================================================//
  
  def   targets(self):
    content = self.targets_value.content
    if not content:
      raise ErrorNoTargets( self )

    return content.data
  
  #//=======================================================//
  
  def   sideEffects(self):
    content = self.itargets_value.content
    if not content:
      raise ErrorNoDeps( self )

    return content.data
  
  #//=======================================================//
  
  def   setTargets( self, targets, itargets = None, ideps = None ):

    makeValues = self.builder.makeValues
    
    target_values = makeValues( targets, use_cache = False )
    itarget_values = makeValues( itargets, use_cache = False )
    idep_values = makeValues( ideps, use_cache = True )
    
    self.targets_value.content = DependsValueContent( target_values )
    self.itargets_value.content = DependsValueContent( itarget_values )
    self.ideps_value.content = DependsValueContent( idep_values )
  
  #//-------------------------------------------------------//
  
  def   buildStr( self ):
    return self.builder.buildStr( self )
