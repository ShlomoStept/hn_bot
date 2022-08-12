
import requests
from urllib.parse import urlparse

from sys import path
path.append("../utils") # this is hacky --> dont love it but it works for importing sibling modules
from utils.request_responses import request_response_description_map ## 
from utils.dynamic_site_set import dynamic_site_set

from .wayback_save_api.save_api import Wayback_Machine_Save_API



'''
    ##--> FUTURE TODO  --> rewite this its a mess, and failed several tests
    
    #   DONE                    -- 1. clean up code --> and add ___successfully_processed_post_list and failed_to_process_list  for functions --> 
    #   DONE but more is needed -- 2. test test test ::  normal testing , and error testing, testing in conjunction with part 1 
    #   DONE                       3. eliminate redundacies
    
    #   1. create unit tests --> for all --> to automate it if any updates are made
    #   2. since this is going to be running every __5-10 minutes, and there may be 40-50 urls to find the archive of, need to make sure the API 
    #       doesn't call over 15 times per minute ( for the archive.today --> wayback-machine-get == unlimited calls, wayback-machine-save == limit code already exists  )
    #   3. --->  fix the threading and timer for the Wayback_Machine_Save_API ( make it more efficent)
    
    #   4. try to figure out what to do about dynamic sites where sometimer, archive.today fails to capture them
    #       and wayback_machine has lots of errors with this 
    #           possible solution -> dont process the urls from these site, or at least alter the way you do (for example bloomberg)
    
    #   5. maybe look at both wayback-machine and archive.it and always post both links --> FUTURE TODO
    
    #   6. Refactor code --> its a mess rn --> FUTURE TODO
    
    ##--> FUTURE TODO
'''



'''       
     
    Class :: get_archived_url : 
             The Following Class can be used to find the archive url for all the hn posts woth urls to sites that require a subscription 
'''
class Get_Archived_URL:
    
    def __init__(self, hn_url_sub_post_list):
        
        self.list_of_url_objs_to_process = hn_url_sub_post_list  ## key part == get the list of tuples (<id_num>, <detail_map>, <url>) of the posts we want to process 
        
        self.successfully_processed_post_set = set()  # set of the post-id numbers to the posts that archives were sucessfully found
        
        # TODO might want to put this into a map {} of <id_num> : (<id_num>, <detail_map>, <url>, <archive-url>) to process easier in the part 3
        self.successfully_processed_post_list = [] # list of tuples -(<id_num>, <detail_map>, <url>, <archive-url>)- for the sucessufly processed urls/posts
        
        self.failed_to_process_set = set()   # set of the post-id numbers to the posts that archives were not found, or had a bad_request
        self.failed_to_process_map = {}  # map of  ( id_num, (<id_num>, <detail_map>, <url>))
        
        self.failed_request_list = []   # list of lists of form -> [<id>, <requests-response>, <request-attemp-num>, <api-called>] 
        
        self.curr_post_url = None
        
        self.request_response_description_map = request_response_description_map
        self.dynamic_site_set = dynamic_site_set
        
        #--> TODO save this and dont process the urls from these site, or at least alter the way you do (for example bloomberg)
        #self.dynamic_site_set = dynamic_site_set 
        

        # these are to be used when testing each url object, and if the archive failed for each of the diff types
        #   (determine if this is needed)
        self.curr_url_obj_processing = None   # will have the form of (<id_num>, <detail_map>, <url>)
        
        self.curr_wbm_get_failed = None
        self.curr_act_get_failed = None
        
        self.ac_today_save_api_returned_wip = None
        self.curr_act_save_failed = None
        
        self.curr_wbm_response_obj = None
        self.curr_act_response_obj = None
        
        self.curr_post_archive_url = None
        
        
        self.run_wbm_save = False
        self.list_of_wbm_to_process = []
        self.wb_save_api = None   
        
        
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
    QQ TODO -- why did i put this function here?? --> determine what this functions intended purpose was
        helper function 1 :
                add_completed_posts_to_process_post_object_list() --  adds a post to the completed list
                        Note : this will be used to ensure that posts arent tested twice -> once processing has succedded in part-2
                        
    '''
    def add_completed_posts_to_process_post_object_list(self, process_post_object_list):
        process_post_object_list += [ sucessfuly_processed_[0] for sucessfuly_processed_ in self.successfully_processed_post_list ]
    
    

    '''
        helper function 2 :
                add_archive_url() : adds the (a) post number and (b) the tuple -(<id_num>, <detail_map>, <url>, <archive-url>) - with all the posts key details 
                                    to the uccessfully_processed_post_list

    '''
    def add_archive_url(self, remove_wip=False):
        self.successfully_processed_post_set.add( self.curr_url_obj_processing[0] ) # curr_url_obj_processing ->  (<id_num>, <detail_map>, <url>)
        
        if remove_wip:
            self.curr_post_archive_url = self.curr_post_archive_url.replace("/wip", "")
                                               
                                                                # (<id_num>, <detail_map>, <url>, <archive-url>)    
        self.successfully_processed_post_list.append( ( self.curr_url_obj_processing + ( self.curr_post_archive_url , )  ) )
        # Note - to concatonate - we need to have to make self.curr_post_archive_url into a tuple hence the weird ( <var> , )
       
       
    
    '''
        helper function 3 :
                remove_from_failed() : This function takes removes the post-id, from the set and map of the posts that failed to be processed
                        Notes--
                            1. this is intended to be usefull if (a) the url failed the first time, so it wasnt added to the sucessfully processsed posts set
                                (b) or if we try to save on wayback machine a second time 
                            2. this should only run if the curent post being processed, sucessfully returned an archived url

    '''
    def remove_from_failed(self):
        if self.curr_url_obj_processing[0] in self.failed_to_process_set :
            self.failed_to_process_set.remove( self.curr_url_obj_processing[0] )
        if self.curr_url_obj_processing[0] in self.failed_to_process_map :
            self.failed_to_process_map.remove( self.curr_url_obj_processing[0] )
    
    
    
    
    
    
    '''
        Function 1 :  
                get_top_posts() - sends a request to hackernews to recive the top 500 posts
                        Note : the request is not garentted to succeed - you must check this before proceeding 
                        
                        TODO - test and determine best course of action for different error codes 
    '''
    def process_list_of_posts(self, start=-1, end=-1):
        
        if start==-1 and end==-1:
            start = 0 
            end = len(self.list_of_url_objs_to_process)
        
        # step 1 : for each url object passed in betwen start->end  (end not inclusive)
        for self.curr_url_obj_processing in self.list_of_url_objs_to_process[start:end] :  
            
            # a - test if the url has already been processed in a prior run
            # curr_url_obj_processing ->  (<id_num>, <detail_map>, <url>)
            if self.curr_url_obj_processing[0] in self.successfully_processed_post_set :
                continue
            
            else :
                print("impliment object reset")
            # TODO --> 
            #    self.reset_curr_objects() # TODO -- reset all teh curr objects to their default values 
            # TODO _ Step 1 : write down all the variables potentially used in each run, and their defult values.
            # TODO __Step 2 : by default the use of true/false values for determining if an action was sucessful should make this reset irrelevant but its good practice not to risk some slips throguh the cracks
            # TODO --> 
            
            
            # 0 -TODO- should i test it to see if the the post id num is int he set of succeded archive-url finds ? 
            # KEY  --> for now assume if we are procesing it then it has yet to be processed
                 
            #  a - try to find an archived snapshot on wayback machine
            self.find_wayback() 
            
            #  a.2 - if we succeded, add the archive-url to the list together with the original object, and save the post number to the set
            if not self.curr_wbm_get_failed : 
                self.add_archive_url()
                self.remove_from_failed()
            
            # b - if wayback machine doesnt have a snapshot saved -> try to find an archived snapshot on archive.today
            else :
                self.find_archive_today()  ##-->TODO FIX!!!!
            
                # b.2 - if we succeded, add the archive-url to the list together with the original object, and save the post number to the set
                if not self.curr_act_get_failed :
                    #   i   - first we try to see if archive.today, is saving it , or if it in progress making the snapshot (when we called it, it might automatically cache it if its not archived already)
                    if self.ac_today_save_api_returned_wip :
                        self.add_archive_url(remove_wip=True)
                    else :
                        self.add_archive_url()
                    self.remove_from_failed()
            
                    
                #       ii  - if archive.today, is Not already i making the snapshot then we try to save a snapshot on archive.today 
                else:
                    self.run_wbm_save = True 
                    self.list_of_wbm_to_process.append(self.curr_url_obj_processing)
                
                 #TODO --> seperate this out and run in another function --> because this can take 5-10 minutes  
                #self.save_snapshot_wayback() 
      

# ------------------------ 
#   TODO =  determine which archiver one is (a) faster (b) more reliable (c) easier to impliment 
#   DONE --> archive.today on all 3 counts
# ------------------------ 

        
        
        
        
        
    
    '''
        Function 2 :  
                find_wayback() - sends a request to wayback machine, for the latest snapshot (if one exists) of the current URL 
                        Note : the request is not garenteed to succeed - you must check this before proceeding 
                
                        TODO - test and determine best course of action for different error codes 
    '''
    def find_wayback(self):   
        
        # Step 1 : grab the url from the current post being processed
        self.curr_post_url = self.curr_url_obj_processing[2]    # curr_url_obj_processing ->  (<id_num>, <detail_map>, <url>)
        
        
        # Step 2 :  sends a request to wayback machine, for the latest snapshot 
        wayback_arc_snap_response = requests.get(f'http://archive.org/wayback/available?url={self.curr_post_url}')
        
        
        # Step 3 : process the response ::  (a) if it returns an ok see if there is a snapshot , (b) if it fails, set self.curr_wbm_get_failed = True
        if wayback_arc_snap_response.status_code == 200 :
            self.curr_wbm_response_obj = wayback_arc_snap_response.json()
            
            # a - if the request returns a 'ok' resonse, try to get and validate the closest snapshot
            
            # i - test for the existance of an archived snapshot, and then get the 'archived_snapshots' map if it exists  
            if 'archived_snapshots' in self.curr_wbm_response_obj :  
                archived_snapshop_map = self.curr_wbm_response_obj['archived_snapshots']
                
            # ii - test that the 'archived_snapshots' map is not empty
                if archived_snapshop_map :      # True if the map is not empty 
            
            # iii - test for the existance of a closest snapshot, and then get the 'closest' map object if it exists    
                    if 'closest' in archived_snapshop_map:
                        closest_snapshot = archived_snapshop_map['closest']

                        # iv - at this point it seems that a valid archived shapshot exists but just sanity checks, make sure this url status is 'ok', and that its available
                        try :
                            assert closest_snapshot['status'] == '200', f" Error :: archived snapshot url has status - {closest_snapshot['status']}"
                            assert closest_snapshot['available'] == True, f" Error :: archived snapshot url has Availability - {closest_snapshot['available']}"
                        
                        except AssertionError as msg: 
                            print(msg) # TODO add this to the list of error responses --> rather than printing it out
                            self.curr_wbm_get_failed = True
                            return

                        # if all the checks are sucessfully passed, save and return 
                        self.curr_wbm_get_failed == False
                        self.curr_post_archive_url =  closest_snapshot['url'] 
                        
                        # key -> make sure to return here, to ensure the "self.curr_wbm_get_failed  = True "at the end is not run
                        return  ## key -- we want to return here and not set failed=True
        
        else :
            # TODO add this to the list of error responses --> rather than printing it out
            print(f"Error: request status code is : {wayback_arc_snap_response.status_code}") # ",  {request_response_description_map[int(wayback_arc_snap_response.status_code)]}") 
            
        
        
        # if any of the tests failed, set wayback_machine failed  = True, and make sure that the self. curr_post_archive_url has no leftovers from last run
        self.curr_wbm_get_failed = True
        #self.curr_post_archive_url = None  # q not sure if this is relevant --> if this does anything 
    


#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
    
    '''
            helper function 3 :  used in find_archive_today()
                - Tries to obtain the url from the archive_today site if one exists in the returned requests header
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
        Function 3 : find_archive_today()
            Future TODO --> modify to run simmilarly to wayback_..API class -> i.e to run multiple times, with a timer tracker
        
    '''
    def find_archive_today(self):
        
        # Step 1 : initalize all the variables to be used in the request
        headers = { "User-Agent": "archiveis - api hn_bot", "host": urlparse(str(r'https://archive.ph/')).netloc,}
        data = data = { "url": self.curr_post_url , "anyway": 1, }  # make sure the self.curr_post_url is valid 
        act_post_kwargs = dict(timeout=120, allow_redirects=True, headers=headers, data=data)
        
        # Step 2 :  sends a request to archive.today, for the latest snapshot 
        act_response = requests.post(str(r'https://archive.ph/submit/') , **act_post_kwargs)
        
        # Step 3 :  if the response returns ok 
        if act_response.status_code == 200 :
            
            # a - try to find the url in the mess of the text returned
            found_archived_url = self.get_act_archived_url(act_response)
            
            # b - if the url was found then, set self.curr_act_get_failed = False, and then see if it has a current snapshot, or if the request triggered archive.today to take a snapshot 
            if found_archived_url:
                self.curr_act_get_failed = False
                
                if "/wip/" in self.curr_post_archive_url:
                    self.ac_today_save_api_returned_wip = True
                else :
                    self.ac_today_save_api_returned_wip = False
                
                # key -> make sure to return here, to ensure the "self.curr_act_get_failed = True "at the end is not run
                return 
        
         # Step 4 :  if the response does not return ok --> log the error and 
        else :
            # TODO add this to the list of error responses --> rather than printing it out
            print(f"Error: request status code is : {act_response.status_code}") # ",  {request_response_description_map[int(act_response.status_code)]}") 
        
        self.curr_act_get_failed = True 
    

#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------


    '''
        Function 4 :
                save_snapshot_wayback() :: 
                        if there are urls that have no snapshots in wayback, and failed to get & save via archive.today, we then can run then one by one
                        
    '''    
    def save_wayback_snapshots(self):
        
            # Step 0 : see if there are urls that have no snapshots in wayback,
            if self.run_wbm_save == True :
                
                # Step 1 : for each url that has failed to 
                for self.curr_url_obj_processing in self.list_of_wbm_to_process:
                    
                    print(f"Error testing in save_wayback_snapshots --> self.list_of_wbm_to_process = {self.list_of_wbm_to_process}")
                    
                    ''' TODO --> getting an error : TypeError: unhashable type: 'dict' but 
                                                                    type of self.curr_url_obj_processing = <class 'tuple'>
                                                                    type of elf.successfully_processed_post_set = <class 'set'>
                                                    so i have no idea whats the unhashable dict 
                                                    
                                                    
                    print(f"type of self.curr_url_obj_processing = {type(self.curr_url_obj_processing)}")
                    print(f"type of elf.successfully_processed_post_set = {type(self.successfully_processed_post_set)}")
                    
                    # sanity check --> that the post didnt succeed in a previous post
                    try :
                        assert self.curr_url_obj_processing not in self.successfully_processed_post_set, f" Error :: a succesfully processed post was added to the failed to find url list"
                    
                    except AssertionError as msg: 
                        print(msg) # TODO add this to the list of error responses --> rather than printing it out
                        self.list_of_wbm_to_process.remove(self.curr_url_obj_processing)
                        self.remove_from_failed()
                    '''
                    
                    self.curr_post_url = self.curr_url_obj_processing[2]    # curr_url_obj_processing ->  (<id_num>, <detail_map>, <url>)
    
                    # Step 2 : see if an instance of the Wayback_Machine_Save_API Class was already created, and if not create it
                    if self.wb_save_api == None :
                        wb_user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
                        self.wb_save_api = Wayback_Machine_Save_API(str(self.curr_post_url).strip().replace(" ", "%20"), wb_user_agent)
                    else :
                        self.wb_save_api.url = str(self.curr_post_url).strip().replace(" ", "%20")
                    
                    # Step 2 : Run the wayback_url save function  --> this will repeatidly try to archive the given url, 
                    self.wb_save_api.save()
                    
                    # a - if even this failed, then add the post number to the set and list posts that failed to process
                    if self.wb_save_api.wayback_save_failed  or self.wb_save_api.exceeded_wayback_api_limit :  # TODO ---> seperate and log the correct error 
                        self.failed_to_process_set.add( self.curr_url_obj_processing[0] )
                        self.failed_to_process_map[ self.curr_url_obj_processing[0] ] =  self.curr_url_obj_processing   # save as  <id_num>:(<id_num>, <detail_map>, <url>)
                        # Note - to concatonate - we need to have to make self.curr_post_archive_url into a tuple hence the weird ( <var> , )
                        
                    
                        
                    else :
                        self.curr_post_archive_url =  self.wb_save_api._archive_url
                        self.add_archive_url()  # add to post number to the set of sucessfull posts
                        self.remove_from_failed()
        
                        # key TODO determine if this is needed --> and then remove it from the list of list_of_wbm_to_process
                        self.list_of_wbm_to_process.remove(self.curr_url_obj_processing)
                        
        