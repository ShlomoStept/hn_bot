
# TODO --> determine how to post to HN 

# Step 0
# b - what am i able to do 
#       how can i post a comment --
#         1 - does the api allow me to
#         2 - if it doesnt how can i script it so i can without abusing the limits, or getting blocke

# step 1 : write pseudo code
# a - what am i going to be given

'''----------------------------------------------------------------------------
            Part 0 : import all the necessary libraries
    -----------------------------------------------------------------------------''' 
from email import header
import requests
import time as T
from utils.unique_ids.user_agent_list import User_Agent_list, get_random_user_agent


# Step 1 : this object should be initalized, only to store session keys and the api timer (since we dont want to out ourselves as a bot)


class Post_Archive_Urls :
  
  '''----------------------------------------------------------------------------
            Part 1 : initalize the class  variables 
    -----------------------------------------------------------------------------''' 
  def __init__(self, name : str, post_archive_map: dict, completed_post_set: set, api_timer: object,run_log :object, error_log :object) -> None:
    self.name  = name
    
    self.post_archive_map = post_archive_map    # dict {} of --  post_num : archive_url  --  key-values
    
    self.completed_post_set = completed_post_set
    
    self.hn_api_timer = api_timer
    
    self.hn_session = None
    
    self.error_log = error_log
    self.run_log = run_log
    
    self.timeout_start_time  = None
    self.max_age = None
    
    self.account_name = None      #  TODO TODO  !!!  DELETE  !!!  and then make github secret just in case you make this public
    self.password =  None #  TODO TODO  !!!  DELETE  !!!  and then make github secret, just in case you make this public
    
    self.ran_a_session = False
    
  
  
  

  '''----------------------------------------------------------------------------
        Part 2 :     
                              :: MAIN PART :: 
                  the main functions
                      1 - post_comments : itterates throught all the comments and takes care of the connection
                      2 - post_comment_ : gets a post_number and a archive_url, and (a) finds the hmac_number, and (b) constructs and posts the comment
    -----------------------------------------------------------------------------''' 
  
  def post_comments(self) ->  None :
    
    # Step 0  :: initalize a connection session, with a persistant connection
     # TODO  --> what happens if theres a timeout and all archive urls have not been posted ??
      
      print(f" -::--> posting run for the following posts {self.post_archive_map} ")
      
      # Step 1 ::  Start point :: for each of the --  post : archive_url's -- in the dict {}
      for post_num, archive_url in self.post_archive_map.items():
        
        print(f" 1 ----> For post_num : {post_num} we have archive url of {archive_url} ")
        
        #if self.ran_a_session :
        self.session_health_check()
        # # a - setu or renew the session
        # if self.hn_session is None :
        #   self.hn_session  = requests.Session()
          
        # elif self.connection_timedout() :
        #   self.hn_session.close()
        #   self.hn_session  = requests.Session()
        #   self.timeout_start_time = None
        #   self.max_age = None
        
           
        if post_num not in self.completed_post_set: # KEY == make sure to post comments once

          if (self.timeout_start_time is None and self.max_age is None) or  not self.connection_timedout() : # the first conditional is for the first run case
            
            if self.process_timers() == False : # only returns false when there is a 429 
              self.error_log.error( f"  --- Error :: Failed to post comment for For post number {post_num} We recived a 429 response and must backoff for a period of {self.hn_api_timer.__429_wait_time}"   )
            else :
              print(f" 2 ----> attempting to post comment for post = {post_num}, wich archive_url as {archive_url}")
              posted, comment = self.post_comment_( post_num, archive_url)
              
              
              # d - if it successfully posted update the completed_post_set
              if posted:
                self.run_log.info( f"  --- Posted Comment :: For post number {post_num}, we added the comment and archived url {archive_url}")
                self.completed_post_set.add(post_num)

              #else:
                #self.error_log.error( f"  --- Error :: Failed to post comment for For post number {post_num} returned with status code = { self.hn_session.status_code }"   )
  
        #-------------------------------------
        
    
  def post_comment_(self, post_num, archive_url) :
    # Step 1 - process the (a) api timer time schedulin, and the 429 error timeing, make sure there isnt massive issues
    sucessfull = self.process_timers()
    
    if sucessfull :
      # Step 2 :: get the hmac_value and then construct and post the commment     
      # a - get the hmac value 
      self.hn_api_timer.add_to_queue()
      
      found, hmac_value = self.get_hmac_value(post_num)
      res = self.update_timeout() # update the new connection timeout 
      # TODO --> fix update timeout
      
      
      if found :
        print(" --> found hmac value ")
        # Step 3 - generate the comment you want to post
        comment = self.construct_comment(archive_url)
        
        # Step 4 - post the comment 
        good_to_post = self.process_timers()
        
        if good_to_post :
          print(" --> good to post ")
          self.session_health_check()
          
          self.hn_api_timer.add_to_queue()
          posted = self.write_comment(hmac_value, post_num, comment)
          
          return posted, comment
        
    return False, ""
    
  #--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------


  '''----------------------------------------------------------------------------
       
              Part 3 :     -->   Core Functions  <--
    
    -----------------------------------------------------------------------------''' 

        
  '''----------------------------------------------------------------------------
                Core Function 1 : 
                        get_hmac_value() : 
            -----------------------------------------------------------------------------'''
  
  def get_hmac_value( self, post_num :int ) -> str: 
    
    user_agent=User_Agent_list["linux"][2]
    header = { "User-Agent": user_agent, 'Content-Type': 'application/x-www-form-urlencoded', 'Access-Control-Allow-Origin': '*', }

    post_url = r"https://news.ycombinator.com/item"

    data = {
          "acct":  self.account_name ,            
          "pw"  :  self.password, 
          "id": str(post_num),
          }
    post_kwargs = dict(timeout=120, allow_redirects=True, headers=header, data=data)
    
    response = None
    while response is None :  # or  response.status_code in [500, 503, 504] :
      
      not_too_many_requests = self.process_timers()
      if not_too_many_requests :
        
        self.session_health_check()
        response = self.hn_session.post(post_url, **post_kwargs)
        self.ran_a_session = True

        if response.status_code == 200:
          found, hmac_value = self.find_and_parse_hmac(response)
          if found :
            return True, hmac_value
          else :
            self.error_log.error( f"  --- Error :: Failed to - find_and_parse_hmac() -- unable to find HMAC value in the response  = { response.text }"   )
            return False, ""

        elif response.status_code in [500, 503, 504] :
              response = None
        
        elif response.status_code == 429:
            self.hn_api_timer.update_too_many_requests("add")  ## Clean the 429 logic up --> tie it into limit_reached check
            self.error_log.error( f"  ------ Error :: Failed to - get_hmac_value() - for For post number {post_num} returned with status code = { response.status_code }"   )
            
        else :
          self.error_log.error( f"  ------ Error :: Failed to - get_hmac_value() - for For post number {post_num} returned with status code = { response.status_code }"   )
      
      else :
        break
      
    return False, "" 

#-----------------------------------

  '''----------------------------------------------------------------------------
          Helper Fuction 1 - for for  get_hmac_value()
            
            find_and_parse_hmac() : Finds and parses the hmac value if it was returned 
  -----------------------------------------------------------------------------''' 
  
  def find_and_parse_hmac( self, response ) :
    hmac_start_str = "<input type=\"hidden\" name=\"hmac\" value=\""
    hmac_end_str = "\">"

    start_index = response.text.find( hmac_start_str ) + len(hmac_start_str)
    end_index =  response.text.find( hmac_end_str , start_index ) 

    try :
      assert end_index != -1,   f"  --- Error :: Post Comments  get_hmac_value, cound not find hmac_end_str in the Response"
      assert end_index != -1,   f"  --- Error :: Post Comments  get_hmac_value, cound not find hmac_end_str in the Response"
    except AssertionError as msg: 
      self.error_log.error(msg)
      return False, None
    
    return True, response.text[start_index:end_index]

  #--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------

  
  
  '''----------------------------------------------------------------------------
                Core Function 2 : 
                        write_comment() : 
            -----------------------------------------------------------------------------'''
  
  def write_comment(self, hmac_value :int, post_id :int, text_to_comment :str ) -> bool:
    
    user_agent=User_Agent_list["linux"][2]
    header = { "User-Agent": user_agent, 'Content-Type': 'application/x-www-form-urlencoded', 'Access-Control-Allow-Origin': '*', }

    comment_url = r"https://news.ycombinator.com/comment"

  
    data = {
          "acct":  self.account_name ,            
          "pw"  :  self.password, 
          "parent": str(post_id),
          "goto" : f"item?id={post_id}",
          "hmac" : str(hmac_value),
          "text" : str(text_to_comment)
      }
    
    post_kwargs = dict(timeout=120, allow_redirects=True, headers=header, data=data)
    
    
    response = None
    while response is None :  # or  response.status_code in [500, 503, 504] :
      
      not_too_many_requests = self.process_timers()
      
      if not_too_many_requests :
        
        self.session_health_check()
        response = self.hn_session.post(comment_url, **post_kwargs)
        self.ran_a_session = True
      
        print(f"When posting the comment the response.text is \n {'-'*30} {response.text} \n {'-'*30} \n")
        

        if response.status_code == 200:
          return True
        
        elif response.status_code in [500, 503, 504] :
          response = None
          
        elif response.status_code == 429:
            self.hn_api_timer.update_too_many_requests("add")  ## Clean the 429 logic up --> tie it into limit_reached check
            self.error_log.error( f"  --- Error :: write_comment() - returned with status code = { response.status_code }"   ) #TODO tie thos woth the error type
        
        else :
          self.error_log.error( f"  --- Error :: write_comment() - returned with status code = { response.status_code }"   )
      
      else :
        break
    
    return False

  #-----------------------------------

  '''----------------------------------------------------------------------------
          Helper Fuction 1 - for  write_comment()
            
            construct_comment() : constructs the comment to post
  -----------------------------------------------------------------------------''' 
  def construct_comment(self, archive_url:str ) -> str:
    
    initial_comment = f'''If your access to this article is blocked due to a subscription requirement \n\t -- checkout the article's archive : {archive_url}\n''' 
    
    #sponsorship_str = f'''If you enjoy this b̶o̶t̶ ahem 'service', and would like to support this project, buy me a coffee at :  https://www.buymeacoffee.com/HN.ArchiveBot   '''
    # https://www.buymeacoffee.com/HN.ArchiveBot
    
    return initial_comment #+ "\n" + sponsorship_str
  
  #--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------



  
  '''----------------------------------------------------------------------------
       
              Part 4 :     -->   Timer and Connection helper functions   <--
    
    -----------------------------------------------------------------------------''' 
  
  
  
  '''----------------------------------------------------------------------------
          Helper Fuction 1 :
              connection_timedout : return True/False dependig on if the session timed out
  -----------------------------------------------------------------------------''' 
  def connection_timedout(self):
    if self.timeout_start_time is None and self.max_age is None : # if both are none that means we never ran a single session
      
      if self.hn_session is not None :
        return False
      
      else : # i have no idea when this would be true but just in case
        return True
      
    elif self.timeout_start_time  +  self.max_age + 30 >= T.time() :
      return True
    
    else :
      return False
  #--------------------------------------------------------------------------------------------------------------
  
  
  
  '''----------------------------------------------------------------------------
          Helper Fuction 2 :
              update_timeout : uses the return text from the response, to update the time untill the connection has timed out
  -----------------------------------------------------------------------------'''
  # TODO --> fix update timeout
  # TODO --> fix update timeout
  # TODO --> fix update timeout
  def update_timeout(self):
    if self.hn_session is None:
      self.hn_session = requests.Session()
      return True
    else :
      if self.hn_session.headers is not None :
        try : 
          if "Strict-Transport-Security" in self.hn_session.headers :
            test_str = self.hn_session.headers["Strict-Transport-Security"]
            self.max_age = test_str[test_str.rfind("max-age=") + len("max-age="):]
        except Exception as msg:
          self.error_log.error(msg)
          
      if self.max_age is None:
        self.max_age = 0
      
      self.timeout_start_time = T.time()
      
      return False
#--------------------------------------------------------------------------------------------------------------

  def session_health_check(self):
    
    # a - make sure teh essuin has not timed out 
  
    if self.hn_session is None :
          self.hn_session  = requests.Session()
      
    elif self.connection_timedout() :
      if self.hn_session is not None :
        self.hn_session.close()
      
      self.hn_session  = requests.Session()
      self.timeout_start_time = None
      self.max_age = None
      
      
  '''----------------------------------------------------------------------------
          Helper Fuction 3 :
                process_timers : checks for timeout states for both api call limit and for returning 429 response, 
                  and waits if the time to sleep is not too long (relative to a full day)
  -----------------------------------------------------------------------------'''
      
  def process_timers(self) :
    if self.hn_api_timer.too_many_requests() : 
      wait_time_429_error = self.hn_api_timer.get_429_wait_time()
      if wait_time_429_error > 0 and  wait_time_429_error < 10:
        T.sleep(wait_time_429_error)
      else :
        return False
            
    if self.hn_api_timer.limit_reached() :
      wait_time = self.hn_api_timer.get_wait_time()
      if wait_time > 0:
        T.sleep(wait_time)
    
    return True
  #--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
