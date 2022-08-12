import time as T

class Api_Timer:
  
  #              (<api-name>, <max-#-api calls allowed>, <time-window-for-max-number-of-calls (in minutes)> )
  def __init__(self, name_, api_call_limit_, api_time_window_):   
    self.name = name_

    self.queue = []
    self.window_start_time = None

    self.api_call_limit = api_call_limit_
    self.time_window = api_time_window_ * 60  # minutes to seconds

    self.error_log = []

  def update_queue(self):

    if len(self.queue) > 0:
      # a - itterate through the queue and remove all the times that are passed the time_window 
      #print(101, int(T.time() - self.queue[0]) )
      while int(T.time() - self.queue[0]) > self.time_window :
        self.queue.pop(0)
      
      # b - update the window_start_time, so that its accurate
      self.window_start_time = self.queue[0]

        
  
  
  def add_to_queue(self) -> None :
    # Step 1 -  you MUST updated the queue, and check that the limit hasnt been reached, before calling this  !!! --> this is done via one call to limit_reached()
    #           now just make sure the limit has not been reached, as a sanity check 
    try :
      assert self.limit_reached() == False, f"Error : limit has been reached, you need to wait : {self.get_wait_time()} " 
    except AssertionError as msg:
          print(msg)
          self.error_log.append((T.time(), msg))
          return 
    
    # Step 2 - add the currrent time to the queue
    self.queue.append(T.time())



  def limit_reached(self) -> bool :
    # Step 1 : update the queue
    self.update_queue()

    # Step 2: see if the limit has been reached
    #print(f"The call limit is : {self.api_call_limit}, and currently we have {len(self.queue)} calls -> {(self.queue)} ")
    return (len(self.queue) + 1) >= self.api_call_limit


  def get_wait_time(self) -> float :
    # step 1 : Update the queue
    self.update_queue()

    # step 2 : make sure (a) we actualy have a block (i.e. number api calls are == limit - 1  )
    if self.limit_reached() :
      window_start = self.queue[0]  # first value in the queue

      # a - weird case of limit == 1
      if len(self.queue) == 1:
        #       time until first value is outside the window   = time_window in seconds - ( time_elaped since first api_call = currtime-api_call_time)
        return self.time_window - ( T.time() - window_start )
      else :
        return self.time_window - ( T.time() - window_start )

    
    else : # if there is no block 
      return 0 