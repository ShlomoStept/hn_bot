
import requests
from urllib.parse import urlparse
import regex as reg
import time as T


from sys import path
path.append("../../../utils") # this is hacky --> dont love it but it works for importing sibling modules
from utils.general.request_response_map import request_response_description_map ## 
from utils.general.subscription_site_set import subscription_site_set
from utils.general.generate_core_urls import get_core_url_list


'''
    Process_HN_Posts : 
                
            The Following Class can be used to process the Hacker news posts for the bot by
                i    - getting a list of hackernews posts (new, best, and top), via - get_top_posts()         
                ii   - testing some range of those posts to see if they contain a url to a site that requires a subscription
                    --> add if they do add to a list of posts to process --> ( <post_num>, <url>) tuples 
                    --> if they are not add to completed post set
            
            
'''
class Process_HN_Posts:
    
    def __init__(self, error_logger ) -> None:
        
        #self.hn_posts_list = None
        
        self.hn_top_posts_list = None
        self.hn_new_posts_list = None
        self.hn_best_posts_list = None
        
        self.completed_post_set = set()    # set of the posts which have aready been processed

        self.posts_to_process_list = []     # list of ( <post_num>, <url>) tuples for all the posts with urls to websites that require subscription 
        
        self.error_log = error_logger  # list of errors that occurend durint the process
        
        # variables used when testing each post (determine if this is needed)
        self.curr_post_id = None
        self.curr_post_details = None
        self.curr_post_url = None

        self.request_response_description_map: dict[int, str] = request_response_description_map
        
        self.subscription_site_set = subscription_site_set
        
        
    

    '''
        helper function :
          
                1 - add_completed_post() - adds a post to the completed list
                        Note : this will be used to ensure that posts arent tested twice -> once processing has succedded in part-2
                        
    '''
    def add_completed_posts(self, set_of_fully_completed_posts) -> None:
      self.completed_post_set.update(set_of_fully_completed_posts)
    #------------------------------------------------------------------------------------ 


    
    
    '''
        Function 1 :  
                get_top_posts() - sends a request to hackernews to recive the top 500 posts
                        Note : the request is not garentted to succeed - you must check this before proceeding 
                        
                        TODO - test and determine best course of action for different error codes 
    '''
    def get_top_posts(self):
        
        hn_ts_request = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json')

        if hn_ts_request.status_code == 200:
            self.hn_top_posts_list  =  hn_ts_request.json()   # this line is redundant but serves as a comment
        else:
          # TODO -->  and make everything a catch try         
          error = f"  --- Error :: get_top_posts() :: Request returned status_code : {hn_ts_request.status_code}, {self.request_response_description_map[int(hn_ts_request.status_code)]} "
          self.error_log.error(error)
          self.hn_top_posts_list = None
    #------------------------------------------------------------------------------------ 
    
    def get_new_posts(self):
        
        hn_ts_request = requests.get('https://hacker-news.firebaseio.com/v0/newstories.json')

        if hn_ts_request.status_code == 200:
            self.hn_new_posts_list  =  hn_ts_request.json()   # this line is redundant but serves as a comment
        else:
          # TODO -->  and make everything a catch try         
          error = f"  --- Error :: get_new_posts() :: Request returned status_code : {hn_ts_request.status_code}, {self.request_response_description_map[int(hn_ts_request.status_code)]} "
          self.error_log.error(error)
          self.hn_top_posts_list = None

    #------------------------------------------------------------------------------------
    
    def get_best_posts(self):
        
        hn_ts_request = requests.get('https://hacker-news.firebaseio.com/v0/beststories.json')

        if hn_ts_request.status_code == 200:
            self.hn_best_posts_list  =  hn_ts_request.json()   # this line is redundant but serves as a comment
        else:
          # TODO -->  and make everything a catch try         
          error = f"  --- Error :: get_best_posts() :: Request returned status_code : {hn_ts_request.status_code}, {self.request_response_description_map[int(hn_ts_request.status_code)]} "
          self.error_log.error(error)
          self.hn_top_posts_list = None
          
    #------------------------------------------------------------------------------------
    #------------------------------------------------------------------------------------
    #------------------------------------------------------------------------------------



    '''
        Function 2 :  
                get_post_details() - sends a request to hackernews to recive the post details for the post_num supplied
                        Note : the request is not garentted to succeed - you must check this before proceeding 
                        
                        TODO - test and determine best course of action for different error codes 
    '''
    def get_post_details(self):

        get_post_str = str(f'https://hacker-news.firebaseio.com/v0/item/{self.curr_post_id}.json')
        hn_post_request = requests.get(get_post_str)
        
        
        if hn_post_request.status_code == 200:
            self.curr_post_details  =  hn_post_request.json()   
  
        else:
          # TODO -->  and make everything a catch try         
          error = f"  --- Error :: get_post_details() :: Request returned status_code : {hn_post_request.status_code}, {self.request_response_description_map[int(hn_post_request.status_code)]} "
          self.error_log.error(error)
          self.curr_post_details = None
    #------------------------------------------------------------------------------------ 
    



    
    '''
        Function 3 : 
                get_post_url() - obtains the url linked to in the post, if it exists
                
                        Notes : 
                            i   - the url is not garnetted to be in the dict, 
                            ii  - the text (post text) might contain the url in it

    '''

    # https://github.com/lipoja/URLExtract
    def get_post_url(self):

      if "url" in self.curr_post_details:
          post_url = self.curr_post_details['url']
          return [post_url]

      elif "text" in self.curr_post_details:

        # TODO -- what to do if there are multiple urls
        post_text = self.curr_post_details["text"]

        http_list = reg.findall(r'(https?://[^\s]+)', post_text)
        www_list = reg.findall(r'(?:www[^\s]+)', post_text)
        
        post_url_list = http_list + [ 'http://'+www  for www in www_list]
        return post_url_list
      else :
        return []
  #------------------------------------------------------------------------------------ 



    '''
        Function 4 :  
                post_has_sub_block() - returns True if the url* is in the set of urls that requires subscritptions, otherwise False
                    
                    note: * if any of the urls in the diff_url-flavor-list, it shoud return True (i.e. if the core/parent site is in the sub-set)
    '''
    def post_has_sub_block(self):
      
      # Step 1 : get the urls in the url field or in the text of the current posts details
      post_url_list = self.get_post_url()

      # TODO - Curretly we return the first bad-url on list, but might want to search all
      
      # Step 2 : for all the urls foudn if curr post details, (a) generate all the possible url derivations *1*,
      for post_url_ in post_url_list :
        possible_url_list =  get_core_url_list(post_url_) 
        # *1* Some parent sites have different subdomains or may be in a diffenrent string form, but lead to the same core site, so this finds (hopefully) all the variants

        # (b) and test if one of the current sites url varients leads to a parent site that requires a sub, and return findings
        for possible_url in possible_url_list:
          if possible_url in self.subscription_site_set:
            return (True, post_url_)
            
      return (False, post_url_list)
  #------------------------------------------------------------------------------------       
        


    '''
        Function 5 :  
            test_n_posts() - for each posts in the top_post_list, from start->stop , we process it 
                                a - if the url exists and is in the set, we add the (id,url,post_details) 
                                        to the posts_to_process_list, for further processing in part 2
                                
                          DONE  b -  --> if the request fails, we add this to the  error_log, to possiby process later 
                                
                                c - for all other cases (i.e. if the post does not contain a url or the url is not in the set of website_urls that need a subscritption)
                                        we add this to the --> completed_post_set
    '''
    
    #-------------------------------------
    # Helper function
    #-------------------------------------
    def add_sets(self, list_of_lists=None):
      set_ = set()
      for list_ in list_of_lists:
        if list_ is not None :
          set_.update(set(list_))

      return set_
    #-------------------------------------  
    #-------------------------------------  
    
    
    def process_all_posts(self):
      
      # Testing all the posts  
      # TODO determine a filtering metric based on predicted impact score of post  --> also useful for using when deciding which 15 urls to use archive.today to save /search for 
      
      # pre-step 0 : join the sets without duplicates
      set_of_all_hn_posts = self.add_sets([ self.hn_top_posts_list, self.hn_new_posts_list, self.hn_best_posts_list])
      if len(set_of_all_hn_posts) > 0 :
        self.hn_top_posts_list = list(set_of_all_hn_posts)
      
      
      # step 0 -- inital error checking and correcting
      if self.hn_top_posts_list == None :
        error = (f"Error : initial API request to HackerNews failed with response - {self.hn_top_posts_list[0]} ")
        self.error_log.error(error)
      
      else:
        
        # a - for each post-id in the list of the top hn posts from start->stop
        for self.curr_post_id in self.hn_top_posts_list: # TODO TODO TODO --> take off the 0:150 this is just to speed up testing
  
          # b - make sure that the post-id was not already processed previously
          if self.curr_post_id not in self.completed_post_set:
            
            # c - next call the hn api to get the post details
            self.get_post_details()
            
            # c-1 : if the post returns an error : skip error already added to error log
            if self.curr_post_details == None :
              continue
            
            # c-2 : if the the post returns a ok resonsem evaluate the details
            else:
              
              # d : first determine if the current post url is in the set of webstes the require a subscription
              has_sub_block, url = self.post_has_sub_block()
              
              # TODO ---> add a check to see if there is a archive url posted in the comments 
              # NOTE the word archive can be part of the url title so look for archive.ph or the http://web.archive.org/web/ strings in the substrings

              # d-1 : if yes, then add a tuple if  (id,  post_details, url)  to the list of urls -> to process (find internet-archive snapshots)
              if has_sub_block:
                self.posts_to_process_list.append( (self.curr_post_id, url ) )
              
              # d-2 : otherwise add it to the completed post set and move on, (if the url is not present maybe add some other process)
              else :      
                self.completed_post_set.add(self.curr_post_id)
                
        
