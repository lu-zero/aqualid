import threading

try:
  import queue
except ImportError:
  import Queue as queue # python 2

#//===========================================================================//

class _ExitException( Exception ):
  pass

def   _exitEventFunction():
  raise _ExitException()

_exit_task = ( None, _exitEventFunction, [], {} )

#//===========================================================================//

class _TaskProcessor( threading.Thread ):
  
  def __init__(self, tasks, completed_tasks, stop_on_error, exit_event ):
    
    super(_TaskProcessor,self).__init__()
    
    self.tasks            = tasks
    self.completed_tasks  = completed_tasks
    self.stop_on_error    = stop_on_error
    self.exit_event       = exit_event
    self.daemon           = True  # let that main thread to exit even if task threads are still active
    
    self.start()
  
  #//-------------------------------------------------------//
  
  def run(self):
    
    tasks             = self.tasks
    completed_tasks   = self.completed_tasks
    exit_event        = self.exit_event
    
    while not exit_event.is_set():
      id, func, args, kw = tasks.get()
      try:
        func(*args, **kw)
        success = (id, None)
        completed_tasks.put( success )
      
      except _ExitException:
        exit_event.set()
      
      except (Exception, BaseException) as err:
        fail = ( id, err )
        completed_tasks.put( fail )
        
        if self.stop_on_error:
          exit_event.set()
      
      except:
        fail = ( id, Exception("Unknown exception") )
        completed_tasks.put( fail )
        
        if self.stop_on_error:
          exit_event.set()
      
      finally:
        tasks.task_done()
    
    tasks.put( _exit_task ) # exit other threads too

#//===========================================================================//

class TaskManager (object):
  __slots__ = (
    
    'tasks',
    'threads',
    'completed_tasks',
    'exit_event',
  )
  
  #//-------------------------------------------------------//
  
  def   __init__(self, num_threads = 1, stop_on_error = True ):
    self.completed_tasks  = queue.Queue()
    self.exit_event       = threading.Event()
    self.threads          = []
    
    self.start( num_threads, stop_on_error )
  
  #//-------------------------------------------------------//
  
  def   start( self, num_threads = 1, stop_on_error = True ):
    self.tasks = queue.Queue()
    self.exit_event.clear()
    
    threads = []
    
    while num_threads > 0:
      num_threads -= 1
      t = _TaskProcessor( self.tasks, self.completed_tasks, stop_on_error, self.exit_event )
      threads.append( t )
    
    self.threads = threads
  
  #//-------------------------------------------------------//
  
  def   stop(self):
    
    self.exit_event.set()
    self.tasks.put( _exit_task )
    
    for t in self.threads:
      t.join()
    
    self.threads = []
  
  #//-------------------------------------------------------//
  
  def   addTask( self, id, function, *args, **kw ):
    task = ( id, function, args, kw )
    self.tasks.put( task )
  
  #//-------------------------------------------------------//
  
  def   completedTasks( self ):
    completed_tasks = []
    isExit = self.exit_event.is_set
    
    while True:
      try:
        block = (not completed_tasks) and (not isExit())
        task_result = self.completed_tasks.get( block = block )
        
        completed_tasks.append( task_result )
        self.completed_tasks.task_done()
      except queue.Empty:
        break
    
    return completed_tasks