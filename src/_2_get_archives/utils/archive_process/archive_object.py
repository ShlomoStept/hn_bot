
#TODO --> this doesnt seem to work so for now we wont try to do this 


from .....utils.unique_ids.user_agent_list import User_Agent_list
import random
import time as T


class archive_today:
    
    def __init__(self, url_list, identity, archive_timer_api, proxy_finder_api):
        
        self.url_list = url_list
        self.identity = None        #  user_agent, ?? 
        self.timer_api = archive_timer_api
        self.bad_proxy_set = set()
        self.proxy_finder_api = proxy_finder_api
        
        self.last_working_proxy = None
        self.set_of_burned_user_agents = set()
        self.burned_user_a_counts = {}  
        
        self.used_user_agent_set = set()
        

    # NO PAUSING OR WAITING < its rapid fire
    def find_urls_proxy_swapping(self, url) :
        
        start_time = T.time()
        # Step 1 : generate a random user_agent and
        user_agent = None
        while user_agent is None or (user_agent in self.set_of_burned_user_agents and self.burned_user_a_counts[user_agent] > 5):
            os_to_use = random.choice([ 'mac', "windows", "linux"])
            rand_selction = random.randint(0, len(User_Agent_list[os_to_use]))
        
            user_agent = User_Agent_list[os_to_use][rand_selction]
        
        self.used_user_agent_set.add(user_agent)
        
        
        # Step 2 : Setup header
        
        
        # Step 3 : Test of the proxy is good  (a) get a list of them if its null, (b) test if we have a good one, then against a list of burned ones 
        # if its not burned try it, and based on the response, add it to the burned list or 
        
        found_archive = False 
        # while not found 
        # --- call get proxy, which will (a) get a list of them if its null, (b) test it against a list of burned ones  --> save in a file for future
        # if its not burned  it will return it for us to use 
        while not found_archive and (T.now() - start_time)  < 20*60   :
            proxy_t_use = self.proxy_finder_api.get_proxy()
            
            found_archive = self.set_of_burned_user_agentsfind_archive(url, proxy_t_use ,user_agent)
        
        
        if found_archive :

            print("todo")            
        #** if it works ou want to save the session and the user infor and .. for user again, also process the timeout details and more...
        
        # a - call the find_archive --> if its response is successfull 200, sent back and set found == true, if its 429 mark the proxy and user_agent (any user_agent with nore than 5 fails doesnt get chosen again, they get chosen now at random, but they have failure counts to keep track of the ones that should not be used again, and possibly for pattern tracking  later)
        # b -  process response, and hopefully save it to succefully found, and keep a logger of the proxy and useragents that work
        # c -else continue , and get a new proxy url 
         
        return "TODO"
    
    
    
    
    def find_urls(self) :  # this will be the more complicated on of the 5 -step followed by the 2 step and with backing off and the whole shebang and continious keeping track of
        return "todo"
        
        # Step 1 : Start Connection, and note that this will only be good for 12 calls 
        
        # Step 2 : test if the user_agent, is None or was burned , and update it in eother case
        
        
        # Step 3 : Test of the proxy is good  (a) get a list of them if its null, (b) test if we have a good one, then against a list of burned ones 
        # if its not burned try it, and based on the response, add it to the burned list or 
        
        # found = False 
        # while not found 
        # --- call get proxy, which will (a) get a list of them if its null, (b) test it against a list of burned ones  --> save in a file for future
        # if its not burned  it will return it for us to use 
        
        # a - call the find_archive --> if its response is successfull. process response, and set found == true
        # b - else continue , and get a new proxy url 
        
    def get_user_agent():
        print("TODO :: FIND a user-agent that has not been burned ")
        
    
    def generate_header():
        print("TODO :: generate the proper header ")
                
    
    def find_archive(self, url):
        # Step 0 : if we called this function - (a) we know that the api call lmit has not been reached
         
        # Step 1 : initalize all the variables to be used in the request to archive_today
        # archiveis - api hn_bot
        
        user_agent = ""
        headers = { "User-Agent": User_Agent_list["linux"][2],  "host": urlparse(str(r'https://archive.ph/')).netloc}  # 'Connection':'close'
        
        data = { "url": url , "anyway": 1, }  
        act_post_kwargs = dict(timeout=120, allow_redirects=True, headers=headers, data=data)
        
        # Step 2 :  sends a request to archive.today, for the latest snapshot 
        
        # TODO --> not user the requests because they dont do it in iorder
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
            self.error_log.append( f"  --- Error :: Archive Today Get-Url returned with status code = {get_response.status_code}" )         
         
        # Step 5 : if we got a bad response code then -> log the response code    
        else :
            self.error_log.append( f"  --- Error :: Archive Today Get-Url returned with status code = {get_response.status_code}" )         
        
        # Step 6 : if any step or check resulted in a failure, we need to return -->  False, None    
        return False, None, False
        
    
