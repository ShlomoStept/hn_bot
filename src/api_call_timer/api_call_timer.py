import time as T



#   1 -    TODO : make the requests more robust (headers, cookies, user-agents...)
#   1 -    TODO : ADD COMMENTS AND HEADERS, AND BONUS == UNIT TESTS
class Api_Timer:
  
  #              (<api-name>, <max-#-api calls allowed>, <time-window-for-max-number-of-calls (in minutes)> )
    def __init__(self, name_, api_call_limit_, api_time_window_):   
        self.name = name_

        self.queue = []
        self.window_start_time = None

        self.api_call_limit = api_call_limit_
        self.time_window = api_time_window_ * 60  # minutes to seconds

        self.error_log = []
        self.too_many_requests_ = None
        self.too_many_requests_timestamp = None


    def update_queue(self):
        if len(self.queue) > 0:
        # a - itterate through the queue and remove all the times that are passed the time_window 
        #print(101, int(T.time() - self.queue[0]) )
            while int(T.time() - self.queue[0]) > self.time_window :
                self.queue.pop(0)
        
        # b - update the window_start_time, so that its accurate
        self.window_start_time = self.queue[0]
        
        
        # c - if there was too many requests and 15 minutes have passed since the api-timed out then we can try to reset it 
        if self.too_many_requests() :
            time_since_call = T.time() - self.too_many_requests_timestamp
            
            if time_since_call >= (15 * 60)  :# 15 minutes * 60 seconds per minute
                self.update_too_many_requests("remove")

   
        
    def special_add_to_queue(self, num_adds, specific_time):
        # Step 1 -  assumption is that the num_adds was already checked to be within the limit
        #           now just make sure the limit has not been reached, as a sanity check 
        try :
            assert self.limit_reached() == False, f"Error : limit has been reached, you need to wait : {self.get_wait_time()} " 
        except AssertionError as msg:
            # TODO MAKE the error logger a global variable and set this to wait --> if its less than 60 seconds off 
            self.error_log.append((T.time(), msg))
            return 
        
        # Step 2 - append specified time to queue, num_adds times
        self.queue = self.queue + ( [specific_time] * num_adds )
    
   
  
    def add_to_queue(self) -> None :
        # Step 1 -  you MUST updated the queue, and check that the limit hasnt been reached, before calling this  !!! --> this is done via one call to limit_reached()
        #           now just make sure the limit has not been reached, as a sanity check 
        try :
            assert self.limit_reached() == False, f"Error : limit has been reached, you need to wait : {self.get_wait_time()} " 
        except AssertionError as msg:
            
            # TODO MAKE the error logger a global variable and set this to wait --> if its less than 60 seconds off 
            self.error_log.append((T.time(), msg))
            return 
        
        # Step 2 - add the currrent time to the queue
        self.queue.append(T.time())
    
    
    
    def too_many_requests(self) :
        if self.too_many_requests_ == True:
            return True
        else :
            return False  
        
    
    def update_too_many_requests(self, set_value) :
        
        if set_value == "add":
            self.too_many_requests_ = True
            self.too_many_requests_timestamp = T.time()
            
        elif set_value == "remove" :
            self.too_many_requests_ = False
            self.too_many_requests_timestamp = None
            
            


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
                wait = 7 if (time_since_last_call % 2 == 0)else 11
                T.sleep(wait)
                self.update_queue()  # and now that time has passed update the queue
        
        # Step 2: see if the limit has been reached
        #print(f"The call limit is : {self.api_call_limit}, and currently we have {len(self.queue)} calls -> {(self.queue)} ")
        return (len(self.queue) ) >= self.api_call_limit    # changed the (len(self.queue) + 1) to -> (len(self.queue) ) so the limit = max number of calls that can be made 


    def get_wait_time(self) -> float :
        # step 1 : Update the queue
        self.update_queue()

        # step 2 : make sure (a) we actualy have a block (i.e. number api calls are == limit  )
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