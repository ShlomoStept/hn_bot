
import requests
from urllib.parse import urlparse
import regex as reg


from sys import path
path.append("../utils") # this is hacky --> dont love it but it works for importing sibling modules
from utils.request_responses import request_response_description_map ## 
from utils.subscription_site_set import subscription_site_set
  
'''
    Process_HN_Posts : 
                
            The Following Class can be used to process the Hacker news posts for the bot by
                i    - getting a list of the top 500 posts, via - get_top_posts()          TODO -- add other options as well (maybe new/ask/show ...)
                ii   - testing some range of those posts to see if they contain a url to a site that requires a subscription, via - test_n_posts(self, start, stop):
                    
                        ~ and then all the urls to sites that require a subscription are saved in a list as a tuple of (<id_num>, <url>, <detail_map>)
                
                iv   -  and then the object 
            note - this class is mostly used to more easily pass around objects/data-structures
'''
class Process_HN_Posts:
    
    def __init__(self):
        
        self.hn_top_posts_list = None
        
        self.completed_post_set = set()    # set of the posts which have aready been processed

        self.hn_url_sub_post_list = []     # a list of tuples (<id_num>, <detail_map>, <url>) for all the posts with urls to websites that require subscription 
        
        self.hn_failed_request_list = []   # list of lists of form -> [<id>, <requests-response>, <request-attemp-num>, <api-called>] 

        # these are tobe used when testing each post (determine if this is needed)
        self.curr_post_id = None
        self.curr_post_details = None
        self.curr_post_url = None
        #self.curr_post_stat = None

        self.request_response_description_map = request_response_description_map
        
        self.subscription_site_set = subscription_site_set
        
        
    

    '''
        helper function :
          
                1 - add_completed_post() - adds a post to the completed list
                        Note : this will be used to ensure that posts arent tested twice -> once processing has succedded in part-2
                        
    '''
    def add_completed_post(self, url_):
      self.completed_post_set.add(url_)
    


    
    
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
            print(f"Error: request status code is : {hn_ts_request.status_code},  {self.request_response_description_map[int(hn_ts_request.status_code)]}") 
            self.hn_top_posts_list = [hn_ts_request.status_code]

    

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
            print(f"Error: request status code is : {hn_post_request.status_code},  {self.request_response_description_map[int(hn_post_request.status_code)]}") 
            self.curr_post_details = hn_post_request.status_code
    
    



    
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




    '''
        Function 4 :  
            get_core_url_list() - returns a list of all the possible url, equivelants/derivatives for the given url

                        notes :
                            i - since urls can be modified, be a subdomain, or have slightly different flavors, but still lead to the same core site
                                its important to extract out all the possible url_flavors to test against the set of urls that require subscriptions
                                    
    '''
    def get_core_url_list(self, url_):
      core_url_list = []
      
      # a - parse the url
      parsed_url = urlparse(url_)
      
      # b - get the base url, without any modifications
      base_url = parsed_url.netloc
      core_url_list.append(base_url)

      # c - base without leading subdomain
      base_no_subd = base_url
      while base_no_subd.count(".") > 1 :
        base_no_subd = base_no_subd[ base_no_subd.find('.')+1 : ] # take off subdomains untill theres only <base>.<com/net/...>
      core_url_list.append(base_no_subd)

      # d - base and base_no_subd with just www.
      core_url_list.append("www." + base_no_subd)
      core_url_list.append("www." + base_url)


      # e - base and base_no_subd with just https://
      core_url_list.append("https://" + base_no_subd)
      core_url_list.append("https://" + base_url)


      # f - base and base_no_subd with just http://  --> no websites with a http for now --> so skip this  
      #core_url_list.append("http://" + base_no_subd)
      #core_url_list.append("http://" + base_url)

      # g - base and base_no_subd with  https://www.
      core_url_list.append("https://www." + base_no_subd)
      core_url_list.append("https://www." + base_url)

      return core_url_list




    '''
        Function 5 :  
                post_has_sub_block() - returns True if the url* is in the set of urls that requires subscritptions, otherwise False
                    
                    note: * if any of the urls in the diff_url-flavor-list, is in the set (i.e. if the core/parent site is in the sub-set)
    '''
    # TODO -- change returns to field state, and add function comment
    def post_has_sub_block(self):
      post_url_list = self.get_post_url()

        # TODO - Curretly we return the first bad-url on list, but might want to search all
      for post_url_ in post_url_list :
        possible_url_list =  self.get_core_url_list(post_url_)

        for possible_url in possible_url_list:
          if possible_url in self.subscription_site_set:
            return (True, post_url_)
            
      return (False, post_url_list)
        
        


    '''
        Function 6 :  
            test_n_posts() - for each posts in the top_post_list, from start->stop , we process it 
                                a - if the url exists and is in the set, we add the (id,url,post_details) 
                                        to the hn_url_sub_post_list, for further processing in part 2
                                
                                b - TODO --> if the request fails, we add this to the  hn_failed_request_list, to possiby process later <-- TODO
                                
                                c - for all other cases (i.e. if the post does not contain a url or the url is not in the set of website_urls that need a subscritption)
                                        we add this to the --> completed_post_set
    '''
    # TODO -- change returns to field state, and add function comment
    def test_n_posts(self, start, stop):
      
      # step 0 -- inital error checking and correcting
      if len(self.hn_top_posts_list) == 1 :
        print(f"Error : initial API request to HackerNews failed with response - {self.hn_top_posts_list[0]} ")
      
      else:
        if len(self.hn_top_posts_list) < start :
          print(f"Error : The start index - {start} - is out of bounds. There are only {len(self.hn_top_posts_list)} posts ")
          return
        elif len(self.hn_top_posts_list) < stop :
          print(f":: warning :: The stop index - {stop} - is out of bounds. There are only {len(self.hn_top_posts_list)} posts ")
          stop = len(self.hn_top_posts_list)
      
      
        # a - for each post-id in the list of the top hn posts from start->stop
        for post_num in self.hn_top_posts_list[start:stop]:
          self.curr_post_id = post_num

          # b - make sure that the post-id was not already processed previously
          if self.curr_post_id not in self.completed_post_set:
            
            # c - next call the hn api to get the post details
            self.get_post_details()
            
            # c-1 : if the post returns an error : add to list of errors with the error number --> to be processed later after a try
            #       save as a list [<id>, <requests-response>, <request-attemp-num>, <api-called>] 
            if type(self.curr_post_details) != type({}) :
              self.hn_failed_request_list.apppend([self.curr_post_id, self.curr_post_details, 1, "details" ])

            # c-2 : if the the post returns a ok resonsem evaluate the details
            else:
              
              # d : first determine if the current post url is in the set of webstes the require a subscription
              has_sub_block, url = self.post_has_sub_block()

              # d-1 : if yes, then add a tuple if  (id,  post_details, url)  to the list of urls -> to process (find internet-archive snapshots)
              if has_sub_block:
                self.hn_url_sub_post_list.append( (self.curr_post_id, self.curr_post_details, url ) )
              
              # d-2 : otherwise add it to the completed post set and move on, (if the url is not present maybe add some other process)
              else :      
                self.completed_post_set.add(self.curr_post_id)
                
        
'''
    TODO --> 
        1. processing logic for different request failure responses
            
        2. possible text processing : note the &#x2 repeated pattern ->> 0x0002 or --> possibly XML (need to keep in mind to test for binary charchter codes that can occur and clean them before testing for presence of a url)
'''