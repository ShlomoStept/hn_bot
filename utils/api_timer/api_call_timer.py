
import time as T

import random

#   1 -    TODO : make the requests more robust (headers, cookies, user-agents...)
#   1 -    TODO : ADD COMMENTS AND HEADERS, AND BONUS == UNIT TESTS

class Api_Timer:
  
  
    '''----------------------------------------------------------------------------
                __init__():
                    initalize all the class variables
        -----------------------------------------------------------------------------''' 
#              (<api-name>, <max-#-api calls allowed>, <time-window-for-max-number-of-calls (in minutes)> )
    def __init__(self, name_, api_call_limit_, api_time_window_, error_log, _429_wait_time = 30 , random_wait_range=(5,7)):   
        self.name = name_

        self.queue = []
        self.window_start_time = None

        self.api_call_limit = api_call_limit_
        self.time_window = api_time_window_ * 60  # minutes to seconds

        self.error_log = error_log
        
        self.too_many_requests_ = False
        self.too_many_requests_timestamp = None
        
        self.random_wait_range =  random_wait_range
        
        self._429_wait_time = _429_wait_time * 60 # time is in minutes we want to convert to second


    '''----------------------------------------------------------------------------
                update_queue()
                
                
        -----------------------------------------------------------------------------''' 
    def update_queue(self):
        
        # a - itterate through the queue and remove all the times that are passed the time_window 
        #print(101, int(T.time() - self.queue[0]) )
        while len(self.queue) > 0 and int(T.time() - self.queue[0]) > self.time_window :
            self.queue.pop(0)
        
        # b - update the window_start_time, so that its accurate
        if len(self.queue) > 0: 
            self.window_start_time = self.queue[0] 
        else :
            # start it now - becase we have no other options (and most likely the update is triggered by a add_to_queue )
            self.window_start_time = T.time()         
        
        
        # c - if there was too many requests and 15 minutes have passed since the api-timed out then we can try to reset it 
        if self.too_many_requests() :
            time_since_call = T.time() - self.too_many_requests_timestamp
            
            if time_since_call >= (15 * 60)  :# 15 minutes * 60 seconds per minute
                self.update_too_many_requests("remove")
                


    '''----------------------------------------------------------------------------
                batch_add_to_queue()
                TODO QQ WHAT IS THIS GUYS PURPOSE
    -----------------------------------------------------------------------------'''   
        
    def batch_add_to_queue(self, num_adds, specific_time):
        # Step 1 -  assumption is that the num_adds was already checked to be within the limit
        #           now just make sure the limit has not been reached, as a sanity check 
        try :
            assert self.limit_reached() == False, f"  --- Error :: batch_add_to_queue() :: limit has been reached, you need to wait : {self.get_wait_time()} " 
        except AssertionError as warning:
            #  NOTE : it should have been checked already, or the lat call caused limit to be reached
            self.error_log.warning( warning )
        
        # Step 2 - append specified time to queue, num_adds times
        self.queue = self.queue + ( [specific_time] * num_adds )
    
    
   
    '''----------------------------------------------------------------------------
            add_to_queue() :
            
    -----------------------------------------------------------------------------''' 
    def add_to_queue(self) -> None :
        # Step 1 -  you MUST updated the queue, and check that the limit hasnt been reached, before calling this  !!! --> this is done via one call to limit_reached()
        #           now just make sure the limit has not been reached, as a sanity check 
        try :
            assert self.limit_reached() == False, f"  --- Error :: add_to_queue() :: limit has been reached, you need to wait : {self.get_wait_time()} " 
        except AssertionError as warning:
            #  NOTE : it should have been checked already, or the lat call caused limit to be reached
            self.error_log.warning( warning )
        
        # Step 2 - add the currrent time to the queue
        self.queue.append(T.time())
    
    
            
            
    '''----------------------------------------------------------------------------
                limit_reached() :

        -----------------------------------------------------------------------------''' 

    def limit_reached(self) -> bool :
        # Step 1 : update the queue
        self.update_queue()

        # Step 2 : if theres been a call to the api in the last 3-5 seconds, wait (3 or 5 seconds) here before making a call
        # TODO
        queue_length = len(self.queue)
        
        if queue_length >= 1 :
            last_time = self.queue[-1]
            time_since_last_call = T.time()-last_time
            
            if time_since_last_call < 5:
                wait = random.uniform(self.random_wait_range[0],self.random_wait_range[1])
                T.sleep(wait)
                self.update_queue()  # and now that time has passed update the queue
        
        # Step 2: see if the limit has been reached
        #print(f"The call limit is : {self.api_call_limit}, and currently we have {len(self.queue)} calls -> {(self.queue)} ")
        return (len(self.queue) ) >= self.api_call_limit    # changed the (len(self.queue) + 1) to -> (len(self.queue) ) so the limit = max number of calls that can be made 


    '''----------------------------------------------------------------------------
               get_wait_time() :

        -----------------------------------------------------------------------------''' 
    def get_wait_time(self) -> float :
        # step 1 : Update the queue
        self.update_queue()

        # step 2 : make sure (a) we actualy have a block (i.e. number api calls are == limit  )
        if self.limit_reached() :
            window_start = self.queue[0]  # first value in the queue
       
            time_to_wait = self.time_window - ( T.time() - window_start )
            #       time until first value is outside the window   = time_window in seconds - ( time_elaped since first api_call = currtime-api_call_time)
            if time_to_wait > 0:
                return time_to_wait
            else :
                return 0 
        else : # if there is no block 
            return 0 
        
        
        

    
    
    '''----------------------------------------------------------------------------
                too_many_requests() --> TODO make this saved to a unique id, the id/ip address has to have this information before a call us made
                ---> in chich case this in then also intertwined with the communication manager class
                
    -----------------------------------------------------------------------------'''    
    
    def too_many_requests(self) :
        if self.too_many_requests_ == True:
            _30_min_break = 30 * 60
            if T.time() - self.too_many_requests_timestamp > _30_min_break :
                self.update_too_many_requests("remove")
                return False 
            else:
                return True
        else :
            return False  
        
        
    def get_429_wait_time(self):
        _30_min_break = 30 * 60
        time_to_wait =  _30_min_break  - ( T.time() - self.too_many_requests_timestamp )
        
        if time_to_wait < 0 :
            self.update_too_many_requests("remove")
            time_to_wait = 0
            
        return time_to_wait
    
      
      
    def update_too_many_requests(self, set_value) :
        if set_value == "add":
            self.too_many_requests_ = True
            self.too_many_requests_timestamp = T.time()
            
        elif set_value == "remove" :
            self.too_many_requests_ = False
            self.too_many_requests_timestamp = None
            
            
            
# TODO --> seperate out the waiting to a different function 
# TODO --> seperate out the 429 value testing and logic