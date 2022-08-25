

'''----------------------------------------------------------------------------
            Part 0 : import all the necessary libraries
    -----------------------------------------------------------------------------''' 

import time as T
from utils.unique_ids.user_agent_list import User_Agent_list, get_random_user_agent
import requests
from bs4 import BeautifulSoup as BS

import random

# Step 1 : this object should be initalized, only to store session keys and the api timer (since we dont want to out ourselves as a bot)


class Post_Archive_Urls :
  
    '''----------------------------------------------------------------------------
            Part 1 : initalize the class  variables 
    -----------------------------------------------------------------------------''' 
    def __init__(self, name : str, post_archive_map: dict, completed_post_set: set, api_timer: object, run_log :object, error_log :object) -> None:
    
        self.name  = name
        
        self.post_archive_map = post_archive_map    # dict {} of --  post_num : archive_url  --  key-values
        
        self.completed_post_set = completed_post_set
        
        self.hn_api_timer = api_timer
        
        self.wait_limit = 2 * 60 # max time to wait is 2 minutes
        
        self.hn_id_timer_map = None     # this lets us know the ids and maps them to a time they were last used, and a bool value for if the account is new 
        
        self.error_log = error_log
        self.run_log = run_log
        
        
        self.account_name = None      #  TODO --> upload your own and make github secret 
        self.password     = None      #  TODO --> upload your own and make github secret  
    
    
    

    '''----------------------------------------------------------------------------
            Part 2 :    Run the following to post comments
                                :: MAIN PART :: 
    -----------------------------------------------------------------------------''' 
  
    
    def post_comments(self):
        
        # a - itterate through all the posts
        for post_num, archive_url in self.post_archive_map :
            
            # step 1 : get the hmac value
            
            # check_timer_and_429 
            no_timer_errors = self.check_timer_and_429()
            if no_timer_errors : 
            
                self.hn_api_timer.add_to_queue() # update the api timer to include this run
                found_hmac, hmac_value = self.get_hmac(post_num, archive_url)
                
                
                if found_hmac :
                      
                  # check_timer_and_429 
                  no_timer_errors = self.check_timer_and_429()
                  if  no_timer_errors :
                      
                      # step 3 : try to post 
                      self.hn_api_timer.add_to_queue() # update the api timer to include this run
                      posted, response = self.post_comment(post_num, archive_url, hmac_value, id)  #  return bool value for if we were able to post the comment and the response to be evaluated
                      
                      # step 4 : evaluate the response --> already done in post_comment 
                      # --> possibly circle back, see if you need to back off and try another id, or  something similar)
                      # self.update_id_dictionary() # TODO try to incorporate this with the evaluate response i.e. self.evaluate_response_and_update_id_dict()
                      
                                                                              
                      if posted :
                          self.run_log.info( f"  --- Posted Comment :: For post number {post_num}, we added the comment and archived url {archive_url}")
                      
                      #else :  ->  No need to log error for :: post_comment:: if we failed this is logged at the point of failure --> only the success of post_comment needs to be logged 
                      
                  else :
                      self.error_log.error( f"  ------ Error :: Test Function no_timer_errors() - Failed for post  {post_num}."   )
                      
                        
                    
                # else : --> No need to log error for :: get_hmac() ::  error logging happens in process_response for all cases except status_codes in [500, 503, 504] 
            
            else :
                self.error_log.error( f"  ------ Error :: Test Function no_timer_errors() - Failed for post  {post_num}."   )
    
    
    
    #--------------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------------------
    
    ''' 
            Function 1 : get_hmac()
    '''
    def get_hmac(self, post_num, archive_url):
        user_agent = get_random_user_agent()          # User_Agent_list["linux"][2]
        header = { "User-Agent": user_agent, 'Content-Type': 'application/x-www-form-urlencoded', 'Access-Control-Allow-Origin': '*', 'Connection': 'close'}

        post_url = r"https://news.ycombinator.com/item"

        data = {
            "id": str(post_num),
        }
        post_kwargs = dict(timeout=120, allow_redirects=True, headers=header, data=data)
        
        response = requests.post(post_url, **post_kwargs)
        
        requests_succeded = self.process_response(response, "get_hmac", post_num)
        
        if requests_succeded is None: # case of response = one of [500, 503, 504] 
            
            # a - sleep for a bit and give it one more try
            T.sleep(random.uniform(13,18))
            response = requests.post(post_url, **post_kwargs)
            
            requests_succeded = self.process_response(response, "get_hmac", post_num)
            
            # b - see if second try worked out 
            if requests_succeded is None:
                self.error_log.error( f"  ------ Error :: get_hmac() - Failed for post  {post_num} returned with status code = { response.status_code }"   )
                
            elif requests_succeded  :
                extracted_hmac, hmac_value = self.extract_hmac(response.text)
                

        elif requests_succeded :
            extracted_hmac, hmac_value = self.extract_hmac(response.text)
        
        else :
            # error logging happens in process_response for all cases except status_codes in [500, 503, 504] 
            return False, None
        
        
        # if we reached here the requsts succeded, but we need to
        if extracted_hmac :
                return True, hmac_value
        else :
            # error logging happens in process_response for all cases except status_codes in [500, 503, 504] 
            return False, None
                    
            
                
     #-------------------------------------------------------------------------
    
    '''----------------------------------------------------------------------------
          Helper Fuction 1 - forget_hmac_value()
            
            extract_hmac() : Finds and parses the hmac value if it was returned 
    -----------------------------------------------------------------------------''' 
    
    def extract_hmac(self, html_text ):
        parsed_response = BS(html_text, "html.parser")
        try:
            hmac_value = parsed_response.find('input', {'name': 'hmac'}).get('value')
        except Exception as e:
            self.error_log.error( f"  ------ Error :: Failed to - extract_hmace() - with error {e}"   )
            return False, None
        
        if isinstance(hmac_value, str) and len(hmac_value) > 0 :
            return True, hmac_value
        else :
            return False, None
        
    
    #--------------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------------------
    
    
    ''' 
            Function 2 : post_comment()
    '''
    def post_comment(self, post_id, archive_url, hmac_value, id = None):
        
        
        
        # step 1 : setup the request
        user_agent = get_random_user_agent() 
        header = { "User-Agent": user_agent, 
                    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", 
                    "Accept-Language" : "en-US,en;q=0.5" ,
                    "Accept-Encoding" : "gzip, deflate, br",
                    "Referer" : "https://news.ycombinator.com/",
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Connection': 'close',
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest" : "document",
                    "Sec-Fetch-Mode" : "navigate",
                    "Sec-Fetch-Site" : "same-origin",
                    "Sec-Fetch-User" : "?1" , }

        comment_url = r"https://news.ycombinator.com/comment"

    
        data = {
            "acct":   self.account_name,            
            "pw"  :   self.password, 
            "parent": str(post_id),
            "goto" : f"item?id={post_id}",
            "hmac" : str(hmac_value),
            "text" : str(archive_url)  #TOD encode the string to htmlo
        }
        
        post_kwargs = dict(timeout=120, allow_redirects=True, headers=header, data=data)
        
        comment_to_post = f'''If your access to this article is blocked due to a subscription requirement \n\t -- checkout the article's archive : {archive_url}\n''' 
        
        response = requests.post( str(comment_to_post),  **post_kwargs)
        
        requests_succeded = self.process_response(response, "post_comment", post_id)
        
        if requests_succeded is None: # case of response = one of [500, 503, 504] 
            # a - sleep for a bit and give it one more try
            T.sleep(random.uniform(13,18))
            
            response = requests.post( str(comment_to_post),  **post_kwargs)
            
            requests_succeded = self.process_response(response, "post_comment", post_id)
            
            # b - see if second try worked out 
            if requests_succeded is None:
                self.error_log.error( f"  ------ Error :: post_comment() - Failed for post  {post_id} returned with status code = { response.status_code }"   )
                
            elif requests_succeded  :
                return True, response
                
        elif requests_succeded :
            return True, response
        
        # if we reached we failed to post the comment 
        self.error_log.error( f"  ------ Error :: Failed to - post_comment() - For post {post_id}, it returned with status code = { response.status_code }"   )
        return False, response
      
     
    #--------------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------------------
    
    ''' 
            Function 3 :  --> NOTE : maybe change name to  --> evaluate_response 
                process_response() :  processses the status_code for requests, 
                    this informs us of the proper next step to take, and not errors (but not faulty/timeouts)
    ''' 
    def process_response(self, response, function_name, post_id ):
        # case 1 - everything worked perfectly
        if response.status_code == 200 :
            return True
        
        elif response.status_code in [500, 503, 504] :
            return None
            
        elif response.status_code == 429:
            self.hn_api_timer.update_too_many_requests("add")  ## Clean the 429 logic up --> tie it into limit_reached check
        
        self.error_log.error( f"  ------ Error :: {function_name}() - Failed for post  {post_id} returned with status code = { response.status_code }"   )
        return False    
    
    #--------------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------------------
    ''' 
            Function 4 : log_sucess()
    '''
    def log_sucess(self, post_num, archive_url):
        return "TODO"
    #--------------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------------------
    ''' 
            Function 5 : log_failure()
    '''
    def log_failure(self, case):
        return "TODO"
    #--------------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------------------
    
    ''' 
            Function 6 : check_timer_and_429()
    '''
    def check_timer_and_429(self):
        if self.hn_api_timer.too_many_requests() : 
            wait_time_429_error = self.hn_api_timer.get_429_wait_time()
            if wait_time_429_error > 0 and  wait_time_429_error < 10:
                T.sleep(wait_time_429_error)
            else :
                return False
                
        if self.hn_api_timer.limit_reached() :
            wait_time = self.hn_api_timer.get_wait_time()
            if wait_time < self.wait_limit :
                T.sleep(wait_time)
            else :
                return False
        
        return True
    
    
    #--------------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------------------
    
        
    
    