import requests
def find_archive(self, url):
        # Step 0 : if we called this function - (a) we know that the api call lmit has not been reached
         
        # Step 1 : initalize all the variables to be used in the request to archive_today
        # archiveis - api hn_bot
        headers = { "User-Agent": User_Agent_list["linux"][2],  "host": urlparse(str(r'https://archive.ph/')).netloc,'Connection':'close'}
        
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
            self.error_log.append( f"  --- Error :: Archive Today Get-Url returned with status code = {get_response.status_code}" )         
         
        # Step 5 : if we got a bad response code then -> log the response code    
        else :
            self.error_log.append( f"  --- Error :: Archive Today Get-Url returned with status code = {get_response.status_code}" )         
        
        # Step 6 : if any step or check resulted in a failure, we need to return -->  False, None    
        return False, None, False