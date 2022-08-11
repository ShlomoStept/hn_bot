
import requests
from urllib.parse import urlparse
import regex as reg

from sys import path
path.append("../utils") # this is hacky --> dont love it but it works for importing sibling modules
from ..utils.request_responses import request_response_description_map
from ..utils.dynamic_site_set import dynamic_site_set

from wayback_save_api.save_api import Wayback_Machine_Save_API

'''
     ##-->TODO
     
    #   1. clean up code --> and add ___successfully_processed_post_list and ailed_to_process_list  for functions
    #   2. test test test ::  normal testing , and error testing, testing in conjunction with part 1 
    #   3. eliminate redundacies
    #   4. create unit tests --> for all --> to automate it if any updates are made
    #   5. move on to the next 
    ##-->TODO
     
     
    get_archived_url : 
             The Following Class can be used to find the archive url for all the hn posts woth urls to sites that require a subscription 
'''
class Get_Archived_URL:
    
    def __init__(self, hn_url_sub_post_list):
        
        self.list_of_url_objs_to_process = hn_url_sub_post_list  ## key part == get the list of tuples (<id_num>, <detail_map>, <url>) of the posts we want to process 
        
        self.successfully_processed_post_set = set()  # set of the post-id numbers to the posts that archives were sucessfully found
        self.successfully_processed_post_list = [] # list of tuples -(<id_num>, <detail_map>, <url>, <archive-url>)- for the sucessufly processed urls/posts
        
        self.failed_to_process_set = set()   # set of the post-id numbers to the posts that archives were not found, or had a bad_request
        self.failed_to_process_list = [] 
        
        self.failed_request_list = []   # list of lists of form -> [<id>, <requests-response>, <request-attemp-num>, <api-called>] 
        
        self.curr_post_url = None
        
        
        self.request_response_description_map = request_response_description_map
        self.dynamic_site_set = dynamic_site_set
        

        # these are to be used when testing each url object, and if the archive failed for each of the diff types
        #   (determine if this is needed)
        self.curr_url_obj_processing = None   # will have the form of (<id_num>, <detail_map>, <url>)
        
        self.curr_wbm_get_failed = None
        self.curr_act_get_failed = None
        
        self.curr_wbm_save_failed = None
        self.curr_act_save_failed = None
        
        self.curr_wbm_response_obj = None
        self.curr_act_response_obj = None
        
        self.curr_post_archive_url = None
        
        self.wb_save_api = None
        self.ac_today_save_api = None    
        
        
        #self.curr_post_id = None
        #self.curr_post_details = None
        #self.curr_post_stat = None 
        
        
        ''' --> TODO  Later --> after part 3 is working :: make this program multithreaded, so that at most 15 workers can get sent out to archive_today ot wayback_machine in one single minute
                
                initial thoughts
                    i - parent process stays in a while loop untill final url_object is posted
                            it keeps track of the timer, and increments/decrements the processed_in_curr_min  counter
                                always keeping track of the next longest time (ie once a mnute has passed since a call was made, we can decrement and then update the time that will next expire)
                    
                    ii - the children are the api calls and are only allowed to get called, if the counter of processed_in_curr_min is less than 15
                    
            --> TODO this gets complicated quickly so first get MVP done, before touching this 
            For now just use a timer, and send out 15 per minute to wayback_machine and act, and then start the timer for a minute before the next 15 are sent out 
        
        self.timer = None
        self.num_wbm_api_calls = None
        self.num_act_api_calls = None
        '''
        
    '''
        helper function :
          
                1 - add_completed_post() - adds a post to the completed list
                        Note : this will be used to ensure that posts arent tested twice -> once processing has succedded in part-2
                        
    '''
    def add_completed_posts_to_process_post_object_list(self, process_post_object_list):
        process_post_object_list += [ sucessfuly_processed_[0] for sucessfuly_processed_ in self.successfully_processed_post_list ]
    

    
    '''
        TODO changes to make --> 
                        1. First itterate through all the  list_of_url_objs_to_process and for each
                            a - see if its on wb_machine
                            b - if its not then look at archive.today
                            
                            c - if both fail, then we need to add it to a seperate list for processing later 
                                    ** this point is important, because since wayback save api, has massive issues
                                        it can (ussualy does) take 10 tries and (4-10) minutes to complete  
                                        
                                    ---> also fix the threading and timer for the Wayback_Machine_Save_API
    '''
    
    '''
        Function 1 :  
                get_top_posts() - sends a request to hackernews to recive the top 500 posts
                        Note : the request is not garentted to succeed - you must check this before proceeding 
                        
                        TODO - test and determine best course of action for different error codes 
    '''
    def process_list_of_posts(self, start=-1, end=-1):
        
        if start==-1 and end==-1:
            start = 0 
            end = len(self.list_of_urls_to_process)
        
        # step 1 : for each url object passed in betwen start->end  (end not inclusive)
        for url_obj_to_process in self.list_of_url_objs_to_process[start,end] :   
            
            # 0 -TODO- should i test it to see if the the post id num is int he set of succeded archive-url finds ? 
            # KEY  --> for now assume if we are procesing it then it has yet to be processed

            self.curr_url_obj_processing =  url_obj_to_process
            
            #  a - try to find an archived snapshot on wayback machine
            self.find_wayback() ## -->TODO
            
            #  a.2 - if we succeded, add the archive-url to the list together with the original object, and save the post number to the set
            if not self.curr_wbm_get_arc_failed : # 
                #TODO -> take out repetative code and save as a function
                self.successfully_processed_post_set.add( self.curr_url_obj_processing[0] )                                                          
                                                                # (<id_num>, <detail_map>, <url>, <archive-url>)    
                self.successfully_processed_post_list.append[ ( self.curr_url_obj_processing + (self.curr_post_archive_url,)  ) ]  # Note - to concatonate - we need to have to make self.curr_post_archive_url into a tuple hence the ( <var> , )
            
            # b - if wayback machine doesnt have a snapshot saved -> try to find an archived snapshot on archive.today
            else :
                self.find_archive_today() ##-->TODO
            
            # b.2 - if we succeded, add the archive-url to the list together with the original object, and save the post number to the set
            if not self.curr_act_get_arc_failed :
                #TODO -> take out repetative code and save as a function
                self.successfully_processed_post_set.add( self.curr_url_obj_processing[0] )                                                          
                                                                # (<id_num>, <detail_map>, <url>, <archive-url>)    
                self.successfully_processed_post_list.append[ ( self.curr_url_obj_processing + (self.curr_post_archive_url,)  ) ] 
           
           
            #  c - if we failed to find a snapshot on both wayback-machine and archive.today, now we try to save a snapshot
            #       i   - first we try to save a snapshot on wayback-machine
            #       ii  - if that fails then we try to save a snapshot on archive.today 
            # ------------------------ 
            #   TODO -> determine which one is (a) faster (b) more reliable (c) easier to impliment
            # ------------------------ 
            #   TODO --> 1. HOW do we know, when the saved-snapshot succeded and is available to be used 
            #            2. also does it return the archive-url, and 
            #            3. what does it return if it succeded, or if it failed
            
            else:
                 
                self.save_snapshot_wayback()
                
                if not self.curr_wbm_save_failed :
                    #TODO -> take out repetative code and save as a function
                    self.successfully_processed_post_set.add( self.curr_url_obj_processing[0] )                                       
                                                                # (<id_num>, <detail_map>, <url>, <archive-url>)    
                    self.successfully_processed_post_list.append[ ( self.curr_url_obj_processing + (self.curr_post_archive_url,)  ) ]
                    
                else :
                    self.save_snapshot_ac_today()
                    
                    if not self.curr_act_save_failed :    
                        #TODO -> take out repetative code and save as a function
                        self.successfully_processed_post_set.add( self.curr_url_obj_processing[0]  )                    
                                                                    # (<id_num>, <detail_map>, <url>, <archive-url>)    
                        self.successfully_processed_post_list.append[ ( self.curr_url_obj_processing + (self.curr_post_archive_url,)  ) ] 
                    
                    # -> IF all these methods failed then for now just add then to the failed set and failed list
                    else :
                        self.failed_to_process_set.add( self.curr_url_obj_processing[0] )                      
                                                                    # (<id_num>, <detail_map>, <url>, <archive-url>)    
                        self.failed_to_process_list.append[ ( self.curr_url_obj_processing + (self.curr_post_archive_url,)  ) ] 
                    
        
        
        
    ## TODO TODO --> impliment the folowing 2 functions -> note not to get sidetracked or forget to check for failed requests
    
       
    def find_wayback(self):     ## -->TODO
        self.curr_post_url = self.curr_url_obj_processing[2]    # curr_url_obj_processing ->  (<id_num>, <detail_map>, <url>)
        
        wayback_arc_snap_response = requests.get(f'http://archive.org/wayback/available?url={self.curr_post_url}')
        
        if wayback_arc_snap_response.status_code == 200 :
            self.curr_wbm_response_obj = wayback_arc_snap_response.json()
            
            # a - if the request returns a 'ok' resonse, try to get and validate the closest snapshot
            
            # i - test for the existane of and then get the 'archived_snapshots' map
            if 'archived_snapshots' in self.curr_wbm_response_obj :  
                archived_snapshop_map = self.curr_wbm_response_obj['archived_snapshots']
                
            # ii - test that the 'archived_snapshots' map is not empty
                if archived_snapshop_map :      # True if the map is not empty 
            
            # iii - test for the existane of and then get the ''closest' map object       
                    if 'closest' in archived_snapshop_map:
                        closest_snapshot = archived_snapshop_map['closest']

                        # iv - at this point it seems that a valid archived shapshot exists but just sanity checks, make sure this url status is 'ok', and that its available
                        try :
                            assert closest_snapshot['status'] == '200', f" Error :: archived snapshot url has status - {closest_snapshot['status']}"
                            assert closest_snapshot['available'] == True, f" Error :: archived snapshot url has Availability - {closest_snapshot['available']}"
                        except AssertionError as msg:
                            print(msg)
                            self.curr_wbm_get_failed = True

                        # if all the checks are sucessfully passed, save and return 
                        self.curr_wbm_get_failed == False
                        self.curr_post_archive_url =  closest_snapshot['url'] 
                        return  ## key 
        
        else :
            print(f"Error: request status code is : {wayback_arc_snap_response.status_code}") # ",  {request_response_description_map[int(hn_ts_request.status_code)]}") 
            # TODO add this to the list of error responses
            self.curr_wbm_get_failed = True # QQ
        
        # if any of the tests failed, set wayback_machine failed  = True, and make sure that the self. curr_post_archive_url has no leftovers from last run
        self.curr_wbm_get_failed = True
        self.curr_post_archive_url = None
    
    
    
    
        
    ##-->TODO
    #   1. add comments
    #   2. test test test, normal testing , and error testing 
    #   3. create unit tests --> for all --> to automate it if any updates are made
    ##-->TODO
    
    
    
    '''
            helper function :: to obtain the url from the archive_today site if some returns 
    '''
    def get_act_archived_url(self, act_response):
        if "Refresh" in act_response.headers:
            self.curr_post_archive_url  = str(act_response.headers["Refresh"]).split(";url=")[1]
            return True
        
        
        elif  "Location" in act_response.headers:
            self.curr_post_archive_url  = act_response.headers["Location"]
            return True
        
        else :
            for i, r in enumerate(act_response.history):
                if "Location" in r.headers:
                    self.curr_post_archive_url = r.headers["Location"]
                    return True
        
        self.curr_post_archive_url = None
        return False            
                    
                        
    
    '''
    
             modify  to run simmilarly to wayback_..API class -> i.e to run multiple times, with a timer tracker
    '''
    def find_archive_today(self):
        
        # initalize all the variables to be used
        headers = { "User-Agent": "archiveis - api hn_bot", "host": urlparse(str(r'https://archive.ph/')).netloc,}
        data = data = { "url": self.curr_post_url , "anyway": 1, }  # make sure the self.curr_post_url is valid 
        act_post_kwargs = dict(timeout=120, allow_redirects=True, headers=headers, data=data)
        
        act_response = requests.post(str(r'https://archive.ph/submit/') , **act_post_kwargs)
        
        if act_response.status_code == 200 :
            found_archived_url = self.get_act_archived_url(act_response)
            
            if not found_archived_url:
                self.curr_act_get_failed = True
                self.curr_post_archive_url = None
                
            else:
                self.curr_act_get_failed = False
                
        else :
            print(f"Error: request status code is : {act_response.status_code}") # ",  {request_response_description_map[int(hn_ts_request.status_code)]}") 
            # TODO add this to the list of error responses
            self.curr_act_get_failed = True # QQ
    

    '''
    
            save_snapshot_wayback(self)
    '''    
    def save_snapshot_wayback(self):
        
        if self.wb_save_api == None :
            wb_user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
            self.wb_save_api = Wayback_Machine_Save_API(self.curr_post_url, wb_user_agent)
        else :
            self.wb_save_api.url = str(self.curr_post_url).strip().replace(" ", "%20")
            
        self.wb_save_api.save()
        
        if self.wb_save_api.wayback_save_failed  or self.wb_save_api.exceeded_wayback_api_limit :
            self.curr_wbm_save_failed = True
        else :
           self. curr_post_archive_url =  self.wb_save_api._archive_url
    
    
    

    '''
    
            save_snapshot_wayback(self)
            
            TODO  -> fix the dulicate nature of checking if it exists and saving, for archive.today, to make eliminate redunancy
    '''    
    def save_snapshot_ac_today(self) : 
    
        # initalize all the variables to be used
        headers = { "User-Agent": "archiveis - api hn_bot", "host": urlparse(str(r'https://archive.ph/')).netloc,}
        data = data = { "url": self.curr_post_url , "anyway": 1, }  # make sure the self.curr_post_url is valid 
        act_post_kwargs = dict(timeout=120, allow_redirects=True, headers=headers, data=data)
        
        act_response = requests.post(str(r'https://archive.ph/submit/') , **act_post_kwargs)
        
        if act_response.status_code == 200 :
            found_archived_url = self.get_act_archived_url(act_response)
            
            if not found_archived_url:
                self.curr_act_save_failed = True
                self.curr_post_archive_url = None
        else :
            print(f"Error: request status code is : {act_response.status_code}") # ",  {request_response_description_map[int(hn_ts_request.status_code)]}") 
            # TODO add this to the list of error responses
            self.curr_act_save_failed = True # QQ




        
'''                
        hn_ts_request = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json')

        if hn_ts_request.status_code == 200:
            self.hn_top_posts_list  =  hn_ts_request.json()   # this line is redundant but serves as a comment
        else:
            print(f"Error: request status code is : {hn_ts_request.status_code},  {self.request_response_description_map[int(hn_ts_request.status_code)]}") 
            self.hn_top_posts_list = [-1]
'''

    

