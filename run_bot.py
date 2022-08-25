'''----------------------------------------------------------------------------

    Program : run_bot.py
    Author  : s.s
    Date    : 8/21/22
    Description : This program runs a bot to (1) grab the newest/top 500 posts on hackernews
                    (2) determine which post, contain lonks to articles whose sites have subscription blocks
                    (3) go to wayback-machine or archove.today, and get the url link to the articles archived snapshot
                    (4) post the link to the archived version as a comment
    
-----------------------------------------------------------------------------''' 




'''----------------------------------------------------------------------------
            Part 0 : import all the necessary libraries
    -----------------------------------------------------------------------------''' 

from random import random
import time as T ## use this to make sure we only run a process every 5 minutes 

from src._1_get_posts.src.get_hn_posts import Process_HN_Posts
from src._2_get_archives.src.get_archived_urls import Process_Archived_Urls

from src._3_post_comments.src.post_archive_urls import Post_Archive_Urls

from utils.api_timer.api_call_timer import Api_Timer

import datetime
from logs.logger_class.custom_logger import *
import logs.logger_class.custom_logger as C_Log



def main() :
    

    '''----------------------------------------------------------------------------
                Part 1 : initalize the key global variables 
        -----------------------------------------------------------------------------''' 

    # a - global loggers
    error_logger = C_Log.Logger("error_logger_2", logging.ERROR)
    run_logger = C_Log.Logger("run_logger_2",  logging.INFO)

    # b - process_hn_posts class
    process_hn_posts = Process_HN_Posts( error_logger.logger  )

    # c - wayback_machine api timer
    wayback_timer = Api_Timer("Wayback Machine", 12, 1, error_logger.logger) # Note each timer_object has its own error log (whearas the other objects share a global error log)

    # d - archive machine api timer
     
    archive_today_timer_short_term = Api_Timer("Archive Today", 3, 1.25, error_logger.logger, random_wait_range=(7.0,11.0)) # short term to avoid, initl overloading requests trigger
    archive_today_timer_long_term = Api_Timer("Archive Today", 35, 60, error_logger.logger , random_wait_range=(15*60,30*60)) # long term to avoid, abnormal usage trigger
    
    archive_today_timers = (archive_today_timer_short_term, archive_today_timer_long_term)
    
    # e - initalize the get url archives Class object
    get_archived_urls= Process_Archived_Urls([] ,wayback_timer, archive_today_timers, error_logger.logger ) #TODO
    
    
    # f - initalize the get url archives Class object
    # TODO ---> only 1 a minute --> how do we eliminate the need to find the hmac
    hacker_news_timer = Api_Timer("HackerNews", 2, 1, error_logger.logger , 15, (10,15)) # short term to avoid, initl overloading requests trigger
    
    hn_poster = Post_Archive_Urls("HackerNews", {},  process_hn_posts.completed_post_set, hacker_news_timer, run_logger.logger, error_logger.logger)

    # g - loop run timer : keep track of the time since the last bot run (do every 10 minutes to start with --> see if i get banned for too many api calls)
    bot_run_timer = Api_Timer("Bot Runner", 1, 20, error_logger.logger)


    #TODO seperate out the completed_post_set from the values that have already been posted

    '''----------------------------------------------------------------------------
            Part 2 :     
                                 :: MAIN PART :: 
                     Run the bot in a loop (once every 20 minutes)
        -----------------------------------------------------------------------------''' 
    
    run_number = 1
    
    while 1 :
        
        run_logger.logger.info( "\n\n" + str("--"*40) + "\n" + f"  --- :: Step 0 :: Starting a new round  (round number {run_number}) " + "\n"+  "--"*40 )
        
        
        # Step 1 : if the bot ran once in the last ten minutes, sleep untill 10 minutes is up, then add the new run to the queue
        if bot_run_timer.limit_reached():
            run_logger.logger.info(f"  --- :: Step 1 :: Sleeping for {bot_run_timer.get_wait_time()} seconds before the run can begin " )    
            T.sleep(bot_run_timer.get_wait_time())
            bot_run_timer.update_queue()
        else :
            run_logger.logger.info(f"  --- :: Step 1 :: No Sleeping required before for the run can begin " )
        
        # add the new run to the queue
        bot_run_timer.add_to_queue()
        
        
        # Step 2 : (a) get the top 500 new posts, the top 500 best posts, and the top 500 new posts, then create a list of all the unique ones to process (TODO  clean up part 1 code, and rename methods)
        run_logger.logger.info(f"  --- :: Step 2 :: Grabbing the top/first 500 posts on hacker_news " )
        
        process_hn_posts.get_top_posts()
        process_hn_posts.get_best_posts()
        process_hn_posts.get_new_posts()
        
        process_hn_posts.process_all_posts()


        #--------------------------------------------------------------------------------------------------------------
        #                   Run Logger 
        #--------------------------------------------------------------------------------------------------------------
    
        posts_not_being_processed = set()
        [ posts_not_being_processed.add(post_num) for post_num in process_hn_posts.hn_top_posts_list  if post_num not in process_hn_posts.posts_to_process_list ]
        run_logger.logger.info("\t"+"--"*30)
        mesage_not_c = f"  ---->  There are {len(posts_not_being_processed)}  posts out of {len(process_hn_posts.hn_top_posts_list)}, that -- Do Not -- contain urls to websites that require a subsription"
        run_logger.logger.info(mesage_not_c)
        run_logger.logger.info(f" ------> Posts --> sucessfully processed : {posts_not_being_processed}")
        
        mesage_that_c = f"  ---->  There are {len(process_hn_posts.posts_to_process_list)} posts posts out of {len(process_hn_posts.hn_top_posts_list)}, that -- Do Indeed -- contain urls to websites that require a subsription"
        run_logger.logger.info(mesage_that_c )
        run_logger.logger.info(f" ------> Posts That are to be processed --> {process_hn_posts.posts_to_process_list}")
        run_logger.logger.info("\t"+"--"*30)
        
        #--------------------------------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------
        
        
        
        # Step 3 : and then get the archive urls for the posts with urls to sites that require subscriptions
        if len( process_hn_posts.posts_to_process_list ) > 0:
            
            run_logger.logger.info(f"  --- :: Step 3 :: Attempting to find the archived urls for all the previous posts " )
            # step a - update the posts_to Process list In part 2's (get-archive_url) object, to be the list of posts to process
            get_archived_urls.posts_to_process = process_hn_posts.posts_to_process_list
                    
            # step b - then try to find the already (*2*) archived urls, for the posts 
            get_archived_urls.process_post_urls()
            
            
            archive_url_list =  get_archived_urls.list_of_posts_for_archive_today
            run_logger.logger.info("\t"+"--"*30)
            run_logger.logger.info(f" \t ------ For run number {run_number} we have  :: {len(archive_url_list)} :: urls that we could use archive.today to post --> {archive_url_list}")
            run_logger.logger.info("\t"+"--"*30 + "\n")

        # Step 4 : Add the archive urls as a comment to the post 
        
        number_of_processed_urls = len(get_archived_urls.processed_post_map.keys()) 
        run_logger.logger.info(f"  --- :: Step 4 :: Start of Attempt to post the {number_of_processed_urls} archived-url's we found to hacker-news " )
        if number_of_processed_urls > 0:
            
            # a - update the map of archoves to past as a comment 
            hn_poster.post_archive_map = get_archived_urls.processed_post_map
            
            # b - now post them 
            hn_poster.post_comments()
            
            
        
        # Step 5 : if there were any missed post that we could not get now we try to save on wayback machine ---> TODO make this a seperate thread that runs in the background QQ how do we save/utalize the results and prevent deadlockiing
         

        #f"   --- Error :: Archive Today Get-Url returned with status code = {get_response.status_code}" )         
        message_1 = f"  --- :: Step 5 - 1 :: As of now we have {len(get_archived_urls.list_of_urls_to_save_wbm)}, urls that we want to save via --> run_wayback_save() "
        run_logger.logger.info(message_1)
        for post_num, temp_url in get_archived_urls.list_of_urls_to_save_wbm :
            run_logger.logger.info(f" ----> Url = {temp_url}")
        
        
        #TODO --> take out the waybackmachine save and feed it here 
        if len(get_archived_urls.list_of_urls_to_save_wbm) > 0  :
            found, post_archived_map = get_archived_urls.run_wayback_save()
                
            # b - Test to see if any of the urls were succesfuly saved
            if found :
                message_2 = f"  --- :: Step 5 - 2:: We were able to save some urls using wayback_save() "
                run_logger.logger.info(message_2)
                
                for key, val in post_archived_map.items():
                    run_logger.logger.info( f" ----> For post num {key}, we found the archived_url is : {val}")

                    # for now we simply print  --> TODO make the upload_archive_comments
            
                # c - now we post the archived urls as comments
                hn_poster.post_comments()
       
        
        
        # Step 6 : reset/update all the values before the next run
        # a - clear the top post list --> automatically done in get_top_posts()
        # b - clear the posts_to_process_list
        process_hn_posts.posts_to_process_list = []
        
        # c - remove the completed posts from get_archived_urls.list_of_urls_to_save_wbm
        for post_num, url in get_archived_urls.list_of_urls_to_save_wbm :
            if post_num in process_hn_posts.completed_post_set:
                get_archived_urls.list_of_urls_to_save_wbm.remove( tuple( post_num, url ) )
        
    
        # Step 7  :  after the run, update the run and 
        message_3 = f"  --- :: Step 6 :: We reset all the lists, for the next run, currently the list of prosts to prcess is empty, and all urls that were saved are now removed from the urls_to_save_wmb list"
        run_logger.logger.info(message_3)
        
        
        # Step 8 : update the logger if the day has changed
        if run_logger.day_change_check() and error_logger.day_change_check() :
            message_4 = f"  --- :: Step 7 :: We changed the run_logger & error logger text files, since the day has changed"
            run_logger.logger.info(message_4)
                            
        run_logger.logger.info("--"*40)    
            
    


if __name__ == "__main__" :
    
    main()