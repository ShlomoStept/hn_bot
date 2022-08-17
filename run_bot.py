'''----------------------------------------------------------------------------
            Part 0 : import all the necessary libraries
    -----------------------------------------------------------------------------''' 
import time as T ## use this to make sure we only run a process every 5 minutes 

from src.process_hn_posts import Process_HN_Posts
from src.get_archived_urls import Process_Archived_Urls
from src.api_call_timer.api_call_timer import Api_Timer



'''----------------------------------------------------------------------------
            Part 1 : initalize the key global variables 
    -----------------------------------------------------------------------------''' 

# a - global logger 
global_error_log = []

# b - process_hn_posts class
process_hn_posts = Process_HN_Posts( global_error_log )

# c - wayback_machine api timer
wayback_timer = Api_Timer("Wayback Machine", 14, 1) # Note each timer_object has its own error log (whearas the other objects share a global error log)

# d - archive machine api timer
archive_today_timer = Api_Timer("Archive Today", 14, 1)

# e - initalize the get url archives Class object
get_archived_urls= Process_Archived_Urls([] ,wayback_timer, archive_today_timer, global_error_log )

# f - loop run timer : keep track of the time since the last bot run (do every 10 minutes to start with --> see if i get banned for too many api calls)
bot_run_timer = Api_Timer("Bot Runner", 1, 10)

#           :: MAIN PART :: 
'''----------------------------------------------------------------------------
            Part 2 : Run the bot in a loop (once every 10 minutes)
    -----------------------------------------------------------------------------''' 
while 1 :
    
    # Step 1 : if the bot ran once in the last ten minutes, sleep untill 10 minutes is up, then add the new run to the queue
    if bot_run_timer.limit_reached:
        T.sleep(bot_run_timer.get_wait_time())
        bot_run_timer.update_queue()
    # add the new run to the queue
    bot_run_timer.add_to_queue()
    
    
    # Step 2 : (a) get the top 500 posts and then (b)process the first 100 posts (TODO  clean up part 1 code, and rename methods)
    process_hn_posts.get_top_posts()
    process_hn_posts.process_all_posts()


    #--------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------
    # --for-now : print out the number of posts that do & dont have url that link to sites that require a subscription
    print("-"*30)
    print(f"We have {len(process_hn_posts.completed_post_set)} posts of the {500}, that ::Do NOT:: contain urls to websites that require a subsription")
    print(process_hn_posts.completed_post_set, "\n")
    print(f"We have {len(process_hn_posts.posts_to_process_list)} posts of the {500}, that ::DO Indeed:: contain urls to websites that require a subsription, and here they are ")
    [ print(post[1]) for post in process_hn_posts.posts_to_process_list]
    print("-"*30)
    #--------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------
    
    # Step 3 : and then get the archive urls for the posts with urls to sites that require subscriptions
    if len( process_hn_posts.posts_to_process_list ) > 0:
        
        # step a - update the posts_to Process list In part 2's (get-archive_url) object, to be the list of posts to process
        get_archived_urls.posts_to_process = process_hn_posts.posts_to_process_list
        
        # step b - then try to find the already (*2*) archived urls, for the posts 
        get_archived_urls.process_post_urls()
        
        print("-"*30)
        print("error logs after -> process_post_urls() ")
        for val in global_error_log:
            print(val)
        

    # Step 4 : Add the archive urls as a comment to the post 
    number_of_processed_urls = len(get_archived_urls.processed_post_map.keys())
    if number_of_processed_urls > 0:
        
        # for now we simply print  --> TODO make the upload_archive_comments
        [print(f"For post_num : {key} : we have the archived url ->{val}") for key,val in get_archived_urls.processed_post_map.items() ]
    else:
        print("-"*30)
        print("error logs after -> \"if number_of_processed_urls > 0: else print this\" ")
        for val in global_error_log:
            print(val)
    
    
    # Step 5 : if there were any missed post that we could not get now we try to save on wayback machine ---> TODO make this a seperate thread that runs in the background QQ how do we save/utalize the results and prevent deadlockiing

    #TODO --> take out the waybackmachine save and feed it here
    if len(get_archived_urls.list_of_urls_to_save_wbm) > 0  :
        found, post_archived_map = get_archived_urls.run_wayback_save()
        
        print("-"*30)
        print("error logs after -> get_archived_urls.run_wayback_save() ")
        for val in global_error_log:
            print(val)
            
        # b - Test to see if any of the urls were succesfuly saved
        if found :
            print("Add the archive urls as a comment to the post ") # TODO --> Add the archive urls as a comment to the post 
        
        
#TODO maybe save and send yourself to archive.ph or waybackmachine  