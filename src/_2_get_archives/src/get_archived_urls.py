
import requests
from urllib.parse import urlparse

from sys import path
path.append("../../../utils") # this is hacky --> dont love it but it works for importing sibling modules
from utils.general.request_response_map import request_response_description_map ## 
from utils.general.dynamic_site_set import dynamic_site_set
from utils.general.encode_url import encode_url ## 
from utils.general.generate_core_urls import get_core_url_list

from utils.unique_ids.user_agent_list import User_Agent_list, get_random_user_agent

from ..utils.wayback_process.wb_save_api import Wayback_Machine_Save_API
import time as T



class Process_Archived_Urls:
    
    
    def __init__(self, posts_to_process, wayback_timer, archive_today_timers, global_error_log):
        
        
        # a - global_lists : the list of the posts to process --> new list is passed in everytime
        self.posts_to_process = posts_to_process   # list of (post_num, url) tuples
        
        # b - timer objects : these objects track the time of last/all api calls --> they should be initalized in the run.py/main.py and passed in
        self.wayback_api_timer = wayback_timer
        self.archive_api_timer_st = archive_today_timers[0]
        self.archive_api_timer_lt  = archive_today_timers[1]
        
        self.processed_post_set = set()       # set of the post-ids of the posts already processed
        self.processed_post_map = {}    # map of the processed posts in the form of  --> { int(<post_num>) :str(archived_url) }
        
        self.list_of_urls_to_save_wbm = []
        
        self.wb_save_api = None 
        
        # d - error logger object(list to be used/saved in another operation)
        self.error_log = global_error_log
        
        
        self.list_of_posts_for_archive_today = []
        
        
        
    '''------------------------------------------------------------------------------------------------
            2 -                   The Main Function : runs the core process
        ------------------------------------------------------------------------------------------------'''
        
        
    def process_post_urls(self):  # maybe change name it process_urls
        
        # step 1 : for each url/post in the list of urls/posts to process
        for (post_num, url) in self.posts_to_process:
            
            # a - test if the post number is in the set of processed posts ?? - when would this be true
            if post_num in self.processed_post_set :
                continue        # if yes, skip
            else:
                #  b - Test that the url is mnot in the dynamic set (i.e. the set of sites that wayback-machine has too-many-redirect-failures) 
                #           - and we have not returned a too_many requests status for our last call
                if url not in dynamic_site_set :
                    
                    # c - if there is a 429 error on the last call ou need to back off for 30 minutes , to reset and not get a permnant ban 
                    if self.wayback_api_timer.too_many_requests() : 
                        wait_time_429_error = self.wayback_api_timer.get_429_wait_time()
                        T.sleep(wait_time_429_error)
                        
                    
                    # d - determine if wayback_timer limit has not been reached, or if its less than 20 seconds
                    wb_limit_reached = self.wayback_api_timer.limit_reached() 
                    
                    
                    if not wb_limit_reached or (wb_limit_reached and (self.wayback_api_timer.get_wait_time() < 60)) :
                        
                        #  e - if time since last call is < N seconds, then wait ! --> this is done when you test for limit_Reached automatically if there has been 1 or more calls
                        wait_time = self.wayback_api_timer.get_wait_time()
                        
                        # i -get wait time, and make sure we dont have a negative wait time (i.e. see if we have the case of wait time < 20 seconds)
                        if wait_time > 0:
                            T.sleep(wait_time)
                        
                        # ii - if we can check wayback machine -> add the api call to the api-timer and try to find on wayback
                        self.wayback_api_timer.add_to_queue()
                        found, archived_url = self.find_wayback(url)  #TODO --> make the call be in a try-catch

                            
                        # iii - if we found it add it to the -> self.processed_post_map  {<post_num>:archived_url}
                        if found :
                            self.add_archive_url(post_num, archived_url)
                            continue # -> start new run
                
                elif (post_num, url) not in self.list_of_posts_for_archive_today :
                    self.list_of_posts_for_archive_today.append( (post_num,url) )    
                
                ''' 
                --------------------------------------------------------------------------------------------------------------------------------------------------
                
                        FOR now archive.today calls are not allowed, cloudfare seems to automatically place a google captcha after 15 calls 
                            NOTE :: TODO == Find a solution : (i-proxies, ii-captcha_solver (ai/ru) )
                
                --------------------------------------------------------------------------------------------------------------------------------------------------
                --------------------------------------------------------------------------------------------------------------------------------------------------
                 TODO --> incorporate rate limiiting knowledge and backing off or exchanging proxies
                
                # c - if we failed to find the url archived by waybackmachine -> try archive.ph
                # i - first test if the archive -today limit has not been reached if yes then wait --> because we want to get the url from here and wayback has already failed
                if not self.archive_api_timer_st.too_many_requests() :
                    
                    if self.archive_api_timer_st.limit_reached()  :
                        wait_time = self.archive_api_timer_st.get_wait_time()
                        T.sleep(wait_time)
                    
                    # ii - then try to find the site archive on archive.today, (and add the run to the timer)
                    self.archive_api_timer_st.add_to_queue()
                    #found, archived_url, contains_wip  = self.find_archive(url)
                    
                    print(f"3-Error log is: {self.error_log}")
                    
                    found = False
                    contains_wip = False
                    # iii - if we find then add to 
                    if found :
                        self.add_archive_url(post_num, archived_url, contains_wip)
                        continue
                
                --------------------------------------------------------------------------------------------------------------------------------------------------
                --------------------------------------------------------------------------------------------------------------------------------------------------
                '''
               
            
                # d - if all the gets failed and archive.ph couldnt save --> now we add this to the wayback_machine_save list - to be processed later (once we finnished findig the rest of the archived_urls (or inbetween runs (after part 3)))
                if (post_num, url) not in self.list_of_urls_to_save_wbm:
                    self.list_of_urls_to_save_wbm.append( (post_num, url) )
                            
#--------------------------------------------------------------------------------------------------------------------------------------------------------       
#-------------------------------------------------------------------------------------------------------------------------------------------------------

       
        

    '''------------------------------------------------------------------------------------------------

                PART 1           :: --> FIND  <-- WAYBACK MACHINE    ::
                                        CORE Functions: 
                
    ------------------------------------------------------------------------------------------------'''

       
    '''----------------------------------------------------------------------------
                Core Function 1 : 
                    find_wayback(self, url) : try to find the archived url on wayback machine
            -----------------------------------------------------------------------------'''
    def find_wayback(self, url): ### maybe pass in connection object --> connection handels api timer inside it ??
        
        # Step 0 : if we called this function - (a) we know that the api call lmit has not been reached
        # Step 1 :  sends a request to wayback machine, for the latest snapshot 


        headers_ = { "User-Agent": User_Agent_list["linux"][0]}  # TODO --> determine if there are any issues, and if yes then use -> get_random_user_agent()
        get_response = requests.get(f'http://archive.org/wayback/available?url={encode_url(url)}', headers=headers_, timeout=120, allow_redirects=True)
        
        
        # Step 2 : make sure that the response is good -> if not log the error 
        if get_response.status_code == 200 :
            wb_response_obj = get_response.json()
            
            # i - test for the existance of an archived snapshot, if it exists  get the 'archived_snapshots' map 
            if 'archived_snapshots' in wb_response_obj  :  
                archived_snapshop_map = wb_response_obj['archived_snapshots']
                
                # ii - test that the 'archived_snapshots' map is not empty
                if archived_snapshop_map :      # True if the map is not empty 
                    
                    # iii - test for the existance of a closest snapshot, and then get the 'closest' map object if it exists    
                    if 'closest' in archived_snapshop_map:
                        closest_snapshot = archived_snapshop_map['closest']

                        # iv - at this point it seems that a valid archived shapshot exists but just sanity checks, make sure this url status is 'ok', and that its available
                        try :
                            assert closest_snapshot['status'] == '200', f"  --- Error :: Wayback Machine closest_snapshot['status'] returned with status code = {closest_snapshot['status']}"
                            assert closest_snapshot['available'] == True, f"  --- Error :: Wayback Machine closest_snapshot['available'] returned with value - {closest_snapshot['available']}"
                
                        except AssertionError as msg: 
                            self.error_log.error(msg)
                            return False, None
                        
                        # v - if all the checks are sucessfully passed, return 
                        return True , closest_snapshot['url'] 
        
        # Step 3 : if we get a 429 response -> update the too_many requests
        elif get_response.status_code == 429 :
            self.wayback_api_timer.update_too_many_requests("add") ## Clean the 429 logic up --> tie it into limit_reached check
            self.error_log.error( f"  --- Error :: Wayback Machine Get-Url returned with status code = {get_response.status_code}"   )
            
        # Step 4 : if we got a bad response code then -> log the response code 
        else :
            self.error_log.error( f"  --- Error :: Wayback Machine Get-Url returned with status code = {get_response.status_code}"   )       

        # Step 5 : if any step or check resulted in a failure, we need to return -->  False, None
        return False, None

    #--------------------------------------------------------------------------------------------------------------------------------------------------------       
#-------------------------------------------------------------------------------------------------------------------------------------------------------


    
    

    '''------------------------------------------------------------------------------------------------
               
                PART 2           :: --> SAVE  <-- WAYBACK MACHINE    ::
                                        CORE Functions: 
                
    ------------------------------------------------------------------------------------------------'''



    '''----------------------------------------------------------------------------
             Core Function 1 :
                    run_wayback_save() : runs the wayback-save helper function for each post in the list of urls to save wbm
        -----------------------------------------------------------------------------''' 
    def run_wayback_save(self) :
        
        # keep track of start time, once we go over 20 minutes of trying to do this, we have to go to the next round, so we on
        max_save_time_alloted = 15 * 60 # this is 20 minutes 
        save_start_time = T.time()
        
        saved_archived_url_map = {}
        
        # Step 1 : if all the posts have not been processed (i.e there are some urls that need to be saved using wayback_machine do it)
        # a - first make sure that wayback_timer limit has not been reached, if yes then wait
        for post_num, url in self.list_of_urls_to_save_wbm : 
            
            # b - (side-check) if any of the urls are to a dnamic site, skip, beause wayback machine wont properly save them
            possible_urls = get_core_url_list(url)
            if any(url_ in dynamic_site_set for url_ in possible_urls):
                continue
            
            # c - Make sure you havent been spending more than 15/20 minutes, on trying to save the site, move on
            if T.time() - save_start_time >= max_save_time_alloted :
                break
            
            if self.wayback_api_timer.limit_reached() :
                wait_time = self.wayback_api_timer.get_wait_time()
                T.sleep(wait_time)
                
            # d - then try to save it 
            #self.wb_save_api._archive_url = None # key -> make the _archive_url value none -> alternative == make a new wb_save_api object --> TODO == test
            try :
                saved, archived_url = self.save_wayback(url) #### TODO ITS NOT ITTERATING!!!!!
            except Exception as msg: 
                self.error_log.error(f"  --- Error :: self.save_wayback(url) returned with {msg} \n\t for url = {url}")
                saved = False
        
            
            # e - and if this suceeded add it to the map of - <postnum>:<archived_url>
            if saved :
                saved_archived_url_map[post_num] = archived_url
            
        
        if len(saved_archived_url_map.keys()) > 0 :
            return True, saved_archived_url_map
        else :
            return False, None
    #------------------------------------------------------------------------------------------------


    '''----------------------------------------------------------------------------
                Helper function 1 :
                        save_wayback() : attempts to archive the url given, (not easy and very time consuming (TODO --> make this a thread worker)
            -----------------------------------------------------------------------------'''
    def save_wayback(self, url):
        
        # Step 0 : if no wayback_machine save-api object exists create one, if one exists, update it with the current url
        if self.wb_save_api == None :
            wb_user_agent = User_Agent_list["linux"][0]     # TODO --> determine if there are any issues, and if yes then use -> get_random_user_agent()
            self.wb_save_api = Wayback_Machine_Save_API(encode_url(url), wb_user_agent)
        else :
            self.wb_save_api.sleep(self.wb_save_api.number_of_tries)
            del self.wb_save_api  # KEY** == you need r=to reset the values so that we dont 
            self.wb_save_api = Wayback_Machine_Save_API(encode_url(url), wb_user_agent)
            

        # Step 1 : Run the wayback_url save function  --> this will repeatidly try to archive the given url, 
        self.wb_save_api.save()
        
        
        # Step 2 : keep get the start time and end time and number of save calls made to wayback-machine (so we can incorporate into the api call timer (TODO - Determin if this should get its own timer object seperate from the find wayback ones)
        
        # a - grab the values :  start time, end time , number of calls
        # start_time = self.wb_save_api.time_range[0]
        end_time = self.wb_save_api.time_range[1]
        num_calls = self.wb_save_api.number_of_tries
        
        # b - make sure the number of adds is only up to the max size of the queue
        if self.wayback_api_timer.api_call_limit >  len(self.wayback_api_timer.queue) + num_calls :
            num_calls =  len(self.wayback_api_timer.queue) - self.wayback_api_timer.api_call_limit ##TODO @@ QQ
        
        # c - for now we add all the calls as being run at end-time TODO --> incorporate this into the save_api class
        self.wayback_api_timer.batch_add_to_queue(num_calls, end_time)
        
        
        # STEP 3:  if the save failed, return False, None to indicate that waybackj save failed
        if self.wb_save_api.wayback_save_failed  or self.wb_save_api.exceeded_wayback_api_limit :  # TODO ---> seperate and log the correct error 
            return False , None 
        # b - f it succeded return True, and the archive url
        else :
            return True, self.wb_save_api._archive_url                     
   

    #--------------------------------------------------------------------------------------------------------------------------------------------------------       
#-------------------------------------------------------------------------------------------------------------------------------------------------------





    '''------------------------------------------------------------------------------------------------
       
                PART 3          :: --> FIND  <-- ARCHIVE TODAY   ::
                                        CORE Functions: 
                
    ------------------------------------------------------------------------------------------------'''


    '''----------------------------------------------------------------------------
                 Core Function 1 : 
                    add_archive_url(self, url) :  try to find the archived url on archive.today 
            -----------------------------------------------------------------------------'''
    
    #TODO --> create adn maintain identities, so that the ones that worked are used again and we dont use ones that failed, plus maintain sessions 
    #       --> each session for one IP address gets captchd every 15 calls --> TODO figure out the cooling off period (initial guess = 10 minutes) for 10 calls, and if using normal behaviour changes this --> initial assumption == it does not 
    
    def find_archive(self, url):
        # Step 0 : if we called this function - (a) we know that the api call lmit has not been reached
         
        # Step 1 : initalize all the variables to be used in the request to archive_today
        # archiveis - api hn_bot
        headers = { "User-Agent": User_Agent_list["linux"][2],  "host": urlparse(str(r'https://archive.ph/')).netloc, 'Connection':'close'}
        
        data = { "url": url , "anyway": 1, }  
        act_post_kwargs = dict(timeout=120, allow_redirects=True, headers=headers, data=data)
        
        # Step 2 :  sends a request to archive.today, for the latest snapshot 
        get_response = requests.post(str(r'https://archive.ph/submit/') , **act_post_kwargs)
        
        # Step 3 :  if the response returns ok 
        if get_response.status_code == 200 :
            # a - try to find the url in the mess of the text returned
            found, archived_url = self.get_act_archived_url(get_response)

            # b - if the url was found then, then see if it already snapshotted or its currently saving a current snapshot
            if found:
                
                if "/wip/" in archived_url :
                    return found , archived_url, True
                else :
                    return found , archived_url, False
        
        # Step 4 : if we get a 429 response -> update the too_many requests  --> TODO --> FIX THIS LOGIC in all places for what happens when 429 call
        elif get_response.status_code == 429 :
            self.archive_api_timer_st.update_too_many_requests("add")
            self.error_log.error( f"  --- Error :: Archive Today Get-Url returned with status code = {get_response.status_code}" )         
         
        # Step 5 : if we got a bad response code then -> log the response code    
        else :
            self.error_log.error( f"  --- Error :: Archive Today Get-Url returned with status code = {get_response.status_code}" )         
        
        # Step 6 : if any step or check resulted in a failure, we need to return -->  False, None    
        return False, None, False
    #------------------------------------------------------------------------------------------------



    '''----------------------------------------------------------------------------
            helper function 1 :  
                    used in find_archive_today()
                        - Tries to obtain the url from the archive_today site if one exists in the returned requests header
        -----------------------------------------------------------------------------'''
    def get_act_archived_url(self, act_response):
        if "Refresh" in act_response.headers:
            archived_url  = str(act_response.headers["Refresh"]).split(";url=")[1]
            return True, archived_url
        
        
        elif  "Location" in act_response.headers:
            archived_url  = act_response.headers["Location"]
            return True, archived_url
        
        else :
            for i, r in enumerate(act_response.history):
                if "Location" in r.headers:
                    archived_url  = r.headers["Location"]
                    return True, archived_url
        
        self.curr_post_archive_url = None
        return False, None    
         
    #--------------------------------------------------------------------------------------------------------------------------------------------------------       
#------------------------------------------------------------------------------------------------------------------------------------------------------



    '''------------------------------------------------------------------------------------------------
                PART 4           :: --> FIND  <-- WAYBACK MACHINE    ::
                                       HELPER FUNCTION
    ------------------------------------------------------------------------------------------------'''

    
    '''----------------------------------------------------------------------------
                Helper Function 1 : 
                        add_archive_url() : adds the (a) post number and (b) the <archive-url> as a key-value pair to the processed_post_set.
            -----------------------------------------------------------------------------'''
            
    def add_archive_url(self, post_num, archived_url_ ,remove_wip=False):
        self.processed_post_set.add( post_num ) 
        
        if remove_wip:
            archived_url_ = archived_url_.replace("/wip", "")
        
        #print(f"before = {self.processed_post_map}")                                       
        self.processed_post_map[ post_num ] = archived_url_
        #print(f"after = {self.processed_post_map}")

         
    #--------------------------------------------------------------------------------------------------------------------------------------------------------       
#------------------------------------------------------------------------------------------------------------------------------------------------------
            
     
    
    
    
    
    
    
    
        
                            
        
    
    
        
    
                            
                            
                        
                    
            
            