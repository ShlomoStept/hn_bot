


import requests
from urllib.parse import urlparse

from sys import path
path.append("../utils") # this is hacky --> dont love it but it works for importing sibling modules
from utils.request_responses import request_response_description_map ## 
from utils.dynamic_site_set import dynamic_site_set

from .wayback_save_api.save_api import Wayback_Machine_Save_API
import time as T



class Process_Archived_Urls:
    
    
    def __init__(self, posts_to_process, wayback_timer, archive_today_timer, global_error_log):
        
        
        # a - global_lists : the list of the posts to process --> new list is passed in everytime
        self.posts_to_process = posts_to_process   # list of (post_num, url) tuples
        
        # b - timer objects : these objects track the time of last/all api calls --> they should be initalized in the run.py/main.py and passed in
        self.wayback_api_timer = wayback_timer
        self.archive_api_timer = archive_today_timer
        
        self.processed_post_set = set()       # set of the post-ids of the posts already processed
        self.processed_post_map = {}    # map of the processed posts in the form of  --> { int(<post_num>) :str(archived_url) }
        
        self.list_of_urls_to_save_wbm = []
        
        self.wb_save_api = None 
        
        # d - error logger object(list to be used/saved in another operation)
        self.error_log = global_error_log
        

    '''------------------------------------------------------------------------------------------------
            0 -                            Helper Functions
    ------------------------------------------------------------------------------------------------'''

    
    
    '''----------------------------------------------------------------------------
                Helper Function 1 : 
                        add_archive_url() : adds the (a) post number and (b) the <archive-url> as a key-value pair to the processed_post_set.
            -----------------------------------------------------------------------------'''
            
    def add_archive_url(self, post_num, archived_url ,remove_wip=False):
        self.processed_post_set.add( post_num ) 
        
        if remove_wip:
            archived_url = archived_url.replace("/wip", "")
                                               
        self.processed_post_map[ post_num ] = archived_url
    #------------------------------------------------------------------------------------------------


    '''----------------------------------------------------------------------------
            helper function 2 :  
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
    #------------------------------------------------------------------------------------------------
         
#--------------------------------------------------------------------------------------------------------------------------------------------------------       
#-------------------------------------------------------------------------------------------------------------------------------------------------------
       

    '''------------------------------------------------------------------------------------------------
            1 -           Core Functions : functions that run key componets of the process
        ------------------------------------------------------------------------------------------------'''
        
            
        
    '''----------------------------------------------------------------------------
                Core Function 1 : 
                    find_wayback(self, url) : try to find the archived url on wayback machine
            -----------------------------------------------------------------------------'''
    def find_wayback(self, url):
        
        # Step 0 : if we called this function - (a) we know that the api call lmit has not been reached
        # Step 1 :  sends a request to wayback machine, for the latest snapshot 
        
        ## MAKE MORE ROBUST
        # 'Connection':'close'
        headers_ = { "User-Agent": "testing_new UA",'Connection':'close'}
        get_response = requests.get(f'http://archive.org/wayback/available?url={url}', headers=headers_, timeout=120, allow_redirects=True)
        
        
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
                            assert closest_snapshot['status'] == '200', f" {str(T.asctime())} --- Error :: Wayback Machine closest_snapshot['status'] returned with status code = {closest_snapshot['status']}"
                            assert closest_snapshot['available'] == True, f" {str(T.asctime())} --- Error :: Wayback Machine closest_snapshot['available'] returned with value - {closest_snapshot['available']}"
                
                        except AssertionError as msg: 
                            self.error_log.append(msg)
                            return False, None
                        
                        # v - if all the checks are sucessfully passed, return 
                        return True , closest_snapshot['url'] 
        
        # Step 3 : if we get a 429 response -> update the too_many requests
        elif get_response.status_code == 429 :
            self.wayback_api_timer.update_too_many_requests("add")
            self.error_log.append( f" {str(T.asctime())} --- Error :: Wayback Machine Get-Url returned with status code = {get_response.status_code}"   )
            
        # Step 4 : if we got a bad response code then -> log the response code 
        else :
            self.error_log.append( f" {str(T.asctime())} --- Error :: Wayback Machine Get-Url returned with status code = {get_response.status_code}"   )       

        # Step 5 : if any step or check resulted in a failure, we need to return -->  False, None
        return False, None
    #------------------------------------------------------------------------------------------------
    
    
    
    '''----------------------------------------------------------------------------
                Core Function 2 : 
                    add_archive_url(self, url) :  try to find the archived url on archive.today 
            -----------------------------------------------------------------------------'''
    def find_archive(self, url):
        # Step 0 : if we called this function - (a) we know that the api call lmit has not been reached
         
        # Step 1 : initalize all the variables to be used in the request to archive_today
        # archiveis - api hn_bot
        headers = { "User-Agent": "testing_new UA", "host": urlparse(str(r'https://archive.ph/')).netloc,'Connection':'close'}
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
        
        # Step 4 : if we get a 429 response -> update the too_many requests
        elif get_response.status_code == 429 :
            self.archive_api_timer.update_too_many_requests("add")
            self.error_log.append( f" {str(T.asctime())} --- Error :: Archive Today Get-Url returned with status code = {get_response.status_code}" )         
         
        # Step 5 : if we got a bad response code then -> log the response code    
        else :
            self.error_log.append( f" {str(T.asctime())} --- Error :: Archive Today Get-Url returned with status code = {get_response.status_code}" )         
        
        # Step 6 : if any step or check resulted in a failure, we need to return -->  False, None    
        return False, None, False
    #------------------------------------------------------------------------------------------------
    
        
        
#------------------------------------------------------------------------------------------       
#-----------------------------------
    '''----------------------------------------------------------------------------
                Helper function for run_wayback_save 3 : TODO
            -----------------------------------------------------------------------------'''
    def save_wayback(self, url):
        
        # Step 0 : if no wayback_machine save-api object exists create one, if one exists, update it with the current url
        if self.wb_save_api == None :
            wb_user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
            self.wb_save_api = Wayback_Machine_Save_API(str(url).strip().replace(" ", "%20"), wb_user_agent)
        else :
            self.wb_save_api.url = str(url).strip().replace(" ", "%20")
            

        # Step 1 : Run the wayback_url save function  --> this will repeatidly try to archive the given url, 
        self.wb_save_api.save()
        
        # SIDE STEP 1 --> incorporate the gloabl api call timer with the wb_save_api timer 
        # SIDE STEP 1 :  before anything else we need to update the global wb_api_timer
        start_time = self.wb_save_api.time_range[0]
        end_time = self.wb_save_api.time_range[1]
        num_calls = self.wb_save_api.number_of_tries
        
        # b - make sure the number of adds is only up to the max size of the queue
        if self.wayback_api_timer.api_call_limit >  len(self.wayback_api_timer.queue) + num_calls :
            num_calls =  len(self.wayback_api_timer.queue) - self.wayback_api_timer.api_call_limit
        
        # c - for now we add all the calls as being run at end-time TODO --> incorporate this into the save_api class
        self.wayback_api_timer.special_add_to_queue(num_calls, end_time)
        
        
        # a - if even this failed, return False, None to indicate that waybackj save failed
        if self.wb_save_api.wayback_save_failed  or self.wb_save_api.exceeded_wayback_api_limit :  # TODO ---> seperate and log the correct error 
            return False , None 
        # b - f it succeded return True, and the archive url
        else :
            return True, self.wb_save_api._archive_url
    #------------------------------------------------------------------------------------------------
    
            
                        
    '''----------------------------------------------------------------------------
             Core Function 3 :
                    run_wayback_save() : runs the wayback-save helper function for each post in the list of urls to save wbm
        -----------------------------------------------------------------------------''' 
    def run_wayback_save(self) :
    
        saved_archived_url_map = {}
        
        # Step 1 : if all the posts have not been processed (i.e there are some urls that need to be saved using wayback_machine do it)
        
        # a - first make sure that wayback_timer limit has not been reached, if yes then wait
        for post_num, url in self.list_of_urls_to_save_wbm : 
            
            #TODO --> incorporate the gloabl api call timer with the wb_save_api timer ** TODO
            
            if self.wayback_api_timer.limit_reached() :
                wait_time = self.wayback_api_timer.get_wait_time()
                T.sleep(wait_time)
                
            # b - then try to save it 
            saved, archived_url = self.save_wayback(url)
            # c - and if this suceeded add it to the map of - <postnum>:<archived_url>
            if saved :
                saved_archived_url_map[post_num] = archived_url
            
        
        if len(saved_archived_url_map.keys()) > 0 :
            return True, saved_archived_url_map
        else :
            return False, None
    #------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------------------------------------       
#-------------------------------------------------------------------------------------------------------------------------------------------------------
                            
        
    
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
                if url not in dynamic_site_set and not self.wayback_api_timer.too_many_requests():
                    
                    # c - determine if wayback_timer limit has not been reached, or if its less than 20 seconds
                    wb_limit_reached = self.wayback_api_timer.limit_reached() 
                    
                    print(f"1-Error log is: {self.error_log}")
                    print(wb_limit_reached)
                    
                    if not  wb_limit_reached or (wb_limit_reached and self.wayback_api_timer.get_wait_time() < 60) :
                        
                        wait_time = self.wayback_api_timer.get_wait_time()
                        # i -get wait time, and make sure we dont have a negative wait time (i.e. see if we have the case of wait time < 20 seconds)
                        if wait_time > 0:
                            T.sleep(wait_time)
                        
                        # ii - if we can check wayback machine -> add the api call to the api-timer and try to find on wayback
                            self.wayback_api_timer.add_to_queue()
                            found, archived_url = self.find_wayback(url)  #TODO --> make the call be in a try-catch

                            print(f"2-Error log is: {self.error_log}")
                            
                        # iii - if we found it add it to the -> self.processed_post_map  {<post_num>:archived_url}
                            if found :
                                self.add_archive_url(post_num, archived_url)
                                continue # -> start new run
                    
                
                #TODO --> incorporate rate limiiting knowledge and backing off or exchanging proxies
                # c - if we failed to find the url archived by waybackmachine -> try archive.ph
                # i - first test if the archive -today limit has not been reached if yes then wait --> because we want to get the url from here and wayback has already failed
                if not not self.archive_api_timer.too_many_requests() :
                    if self.archive_api_timer.limit_reached()  :
                        wait_time = self.archive_api_timer.get_wait_time()
                        T.sleep(wait_time)
                    
                    # ii - then try to find the site archive on archive.today, (and add the run to the timer)
                    self.archive_api_timer.add_to_queue()
                    found, archived_url, contains_wip  = self.find_archive(url)
                    
                    print(f"3-Error log is: {self.error_log}")
                    
                    # iii - if we find then add to 
                    if found :
                        self.add_archive_url(post_num, archived_url, contains_wip)
                        continue
                    
                # d - if all the gets failed and archive.ph couldnt save --> now we add this to the wayback_machine_save list - to be processed later (once we finnished findig the rest of the archived_urls (or inbetween runs (after part 3)))
                self.list_of_urls_to_save_wbm.append( (post_num,url) )
        
        
        
    
                            
                            
                        
                    
            
            