## TODO -- use main to run the program (not just for testing )

import time ## use this to make sure we only run a process every 5 minutes 

from src.process_hn_posts import Process_HN_Posts
from src.get_archived_url import Get_Archived_URL


#---------------------------------------------------------------------------------------------------------
# test to see that part 1 works
#---------------------------------------------------------------------------------------------------------

# a - initialize an object of the process_hn_posts class
process_hn_posts = Process_HN_Posts()


# b - get the top 500 post ids

# TODO --> WHILE loop that waits:
'''
run_number = 0
while 1 :
    curr_time = timer.now()
    if curr_time < last_timestamp + 5*60 :
        wait_time = curr_time - (last_timestamp + 5*60)
    
'''
process_hn_posts.get_top_posts()

# TODO --> need to check here if the response was to hn-API failed  --> currently its built into the test_n_posts() function

# c - test the first 50 posts to see if any of their urls require a subscription # process_hn_posts.test_n_posts(490,600)
process_hn_posts.test_n_posts(0,100)

# d - print out how many do, and how many dont and a list of the id/details

# TODO --> log the current run number --> before any possible errors and the time of the day the run started

print("-"*30)
print(f"We have {len(process_hn_posts.completed_post_set)} posts of the {500}, that ::Do NOT:: contain urls to websites that require a subsription")
print(process_hn_posts.completed_post_set)
print()
print(f"We have {len(process_hn_posts.hn_url_sub_post_list)} posts of the {500}, that ::DO Indeed:: contain urls to websites that require a subsription, and here they are ")
[ print(post[2]) for post in process_hn_posts.hn_url_sub_post_list]
# print("-"*30)



#---------------------------------------------------------------------------------------------------------
# test to see that part 2 works
#---------------------------------------------------------------------------------------------------------
if len(process_hn_posts.hn_url_sub_post_list) > 0:
    
    get_archived_urls= Get_Archived_URL(process_hn_posts.hn_url_sub_post_list)
    
    get_archived_urls.process_list_of_posts()
    
    number_of_processed_urls = len(get_archived_urls.successfully_processed_post_set)
    if number_of_processed_urls > 0:
        [print(f"For post_num : {arc_url_obj[0]} : we have the archived url ->{arc_url_obj[3]}") for arc_url_obj in get_archived_urls.successfully_processed_post_list ]
    
    if get_archived_urls.run_wbm_save  == True :
        get_archived_urls.save_wayback_snapshots()
        
        if len(get_archived_urls.successfully_processed_post_set) > number_of_processed_urls :
            
            #TODO --> figure out how to only obtain those --> maybe have the part3 run and save all the post-ids of the ones it commented on
            #         then run it again and there wont be any dupliate work as long as we check each post-id on the set of the sucessfully-commented 
            [print(f"For post_num : {arc_url_obj[0]} : we have the archived url ->{arc_url_obj[3]}") for arc_url_obj in get_archived_urls.successfully_processed_post_list ]





    #TODO ---> add the sucessfully completed list to the --> process_hn_posts.add_completed_post
    
    #TODO --> add a timer to the class --> to tracke the number of calls to the 
        
'''
        We have 470 posts of the 500, that ::Do NOT:: contain urls to websites that require a subsription
    {32382977, 32385026, 32401413, 32405510, 32399368, 32403471, 32405526, 32417815, 32430108, 32397341, 32409632, 32421925, 32403498, 32428077, 32430128, 32403504, 32383028, 32401468, 32426048, 32432195, 32401480, 32385102, 32430165, 32413789, 32401510, 32376937, 32432244, 32411769, 32383099, 32399495, 32401548, 32403604, 32401564, 32379066, 32420029, 32422082, 32405713, 32409811, 32407766, 32377063, 32397547, 32430317, 32430319, 32420081, 32420082, 32411900, 32399612, 32395518, 32416003, 32379139, 32387345, 32381206, 32401691, 32403746, 32430373, 32426278, 32399663, 32430386, 32375095, 32399672, 32401721, 32393536, 32407873, 32432451, 32420165, 32430406, 32393545, 32385362, 32422227, 32430423, 32405848, 32375128, 32416099, 32420205, 32409966, 32379245, 32422260, 32409980, 32397699, 32412036, 32420228, 32399752, 32393634, 32432555, 32385470, 32424385, 32383426, 32432588, 32416209, 32420312, 32422361, 32383448, 32410075, 32422374, 32430570, 32416236, 32426498, 32428547, 32414215, 32381448, 32412170, 32424461, 32428562, 32379430, 32416295, 32430638, 32395831, 32395840, 32430659, 32420423, 32399949, 32397920, 32422505, 32381550, 32410223, 32424559, 32416402, 32424595, 32430745, 32387746, 32426663, 32416424, 32430761, 32410283, 32410286, 32410293, 32398010, 32395971, 32410307, 32383686, 32426700, 32410333, 32426720, 32426738, 32410355, 32414461, 32428832, 32420641, 32424743, 32416556, 32377646, 32408393, 32383820, 32430939, 32383835, 32381790, 32398181, 32430950, 32428915, 32418675, 32375667, 32418679, 32424827, 32410492, 32406422, 32420761, 32426922, 32428977, 32406452, 32424892, 32428990, 32394176, 32390083, 32402373, 32383943, 32420807, 32410576, 32394195, 32431063, 32414684, 32392161, 32408546, 32414698, 32431082, 32410602, 32416766, 32408577, 32410630, 32384016, 32429073, 32398353, 32416786, 32379927, 32392217, 32424990, 32429089, 32406563, 32386085, 32398391, 32429111, 32431167, 32425028, 32412740, 32412745, 32384074, 32414811, 32402542, 32414835, 32420986, 32425086, 32431231, 32412803, 32429194, 32408716, 32429197, 32386189, 32384147, 32414870, 32380079, 32423107, 32402630, 32402631, 32427235, 32421092, 32386276, 32402661, 32402664, 32412905, 32414954, 32386290, 32417031, 32421137, 32386328, 32396569, 32394533, 32427308, 32427309, 32429367, 32419129, 32388410, 32384320, 32410948, 32376136, 32429385, 32396618, 32415055, 32427345, 32376154, 32396638, 32374113, 32396641, 32406883, 32390499, 32425319, 32423274, 32419182, 32394607, 32421243, 32390526, 32396685, 32413075, 32417174, 32392599, 32382365, 32392611, 32425382, 32419253, 32374207, 32376256, 32390600, 32390605, 32429520, 32400849, 32431568, 32415184, 32374227, 32396759, 32404957, 32431584, 32431596, 32429548, 32425452, 32415224, 32417272, 32376322, 32425475, 32411141, 32431622, 32374278, 32409102, 32411153, 32415256, 32409112, 32427546, 32423451, 32402977, 32413220, 32384550, 32411178, 32417323, 32382514, 32411206, 32407114, 32398923, 32390730, 32396892, 32417373, 32376414, 32415331, 32384613, 32398963, 32398969, 32417410, 32384646, 32384653, 32415378, 32394902, 32384662, 32429721, 32421538, 32413349, 32384687, 32403121, 32401075, 32423604, 32417460, 32419522, 32425674, 32431819, 32386762, 32421578, 32423632, 32415445, 32376542, 32392937, 32415470, 32409329, 32394994, 32425722, 32423680, 32403206, 32401159, 32425737, 32419601, 32421659, 32423712, 32392997, 32409386, 32425780, 32380731, 32384827, 32407361, 32395076, 32378695, 32423752, 32405321, 32415580, 32380769, 32384868, 32411493, 32384870, 32427896, 32421755, 32419708, 32378752, 32407430, 32399238, 32409479, 32417675, 32382860, 32382868, 32425876, 32403353, 32417690, 32407451, 32399266, 32429992, 32411586, 32423913, 32395256}
    
    
    We have 30 posts of the 500, that ::DO Indeed:: contain urls to websites that require a subsription, and here they are
    https://medium.com/luminasticity/to-speak-meaningfully-about-art-329093dbce7f
    https://www.businessinsider.com/google-hiring-freeze-cuts-performance-improvement-plans-2022-8
    https://hbr.org/2022/08/stop-ghosting-and-start-saying-no
    https://www.lrb.co.uk/the-paper/v44/n16/geoff-mann/reversing-the-freight-train
    https://www.wsj.com/articles/electric-cars-batteries-lithium-triangle-latin-america-11660141017
    https://www.theatlantic.com/technology/archive/2022/08/what-to-do-with-old-clothing-donation-waste/671043/
    https://www.scientificamerican.com/article/spiders-seem-to-have-rem-like-sleep-and-may-even-dream/
    https://www.wsj.com/articles/perfect-linkedin-profile-headshot-photo-is-worth-1-000-and-a-job-11660160047
    https://www.nytimes.com/interactive/2022/08/11/arts/anime-hugs.html
    https://www.newyorker.com/news/q-and-a/googles-caste-bias-problem
    https://www.bloomberg.com/news/features/2022-08-10/europe-s-low-water-levels-threaten-rhine-river-hit-80b-trade-lifeline
    https://www.wsj.com/articles/cdc-drops-quarantine-recommendation-following-covid-19-exposure-11660244410
    https://www.reuters.com/business/media-telecom/exclusive-google-fiber-plans-5-state-growth-spurt-biggest-since-2015-2022-08-10/
    https://www.wired.com/story/this-anti-tracking-tool-checks-if-youre-being-followed/
    https://www.bloomberg.com/news/articles/2022-08-11/cdc-says-people-don-t-need-to-quarantine-after-covid-exposure
    https://www.wsj.com/articles/the-unclear-future-for-gifted-and-talented-education-11660144014
    https://www.reuters.com/markets/deals/applovin-offers-buy-unity-software-2022-08-09/
    https://www.washingtonpost.com/national-security/2022/08/11/garland-trump-mar-a-lago/
    https://www.thestar.com/news/gta/2022/08/10/safe-for-swimming-torontos-new-tool-for-measuring-water-quality-at-its-beaches-is-misleading-say-advocates.html
    https://www.wired.com/story/starlink-internet-dish-hack/
    https://www.newyorker.com/magazine/2022/08/15/the-reluctant-prophet-of-effective-altruism
    https://www.washingtonpost.com/opinions/interactive/2022/irs-pipeline-tax-return-delays/
    https://medium.com/super-jump/replayability-in-game-design-798fbb91a726
    https://www.wsj.com/articles/more-than-a-third-of-u-s-teens-are-on-social-media-almost-constantly-survey-says-11660140000
    https://www.reuters.com/world/us/wildfires-are-destroying-californias-forest-carbon-credit-reserves-study-2022-08-05/
    https://www.wired.com/story/facebook-eu-us-data-transfers/
    https://www.bloomberg.com/news/articles/2022-06-27/world-s-most-aggressive-central-bank-raises-key-rate-to-200
    https://www.theatlantic.com/technology/archive/2022/08/stick-shift-manual-transmission-cars/671078/
    https://www.wired.com/story/starlink-internet-dish-hack/
    https://www.bloomberg.com/news/articles/2022-08-09/coinbase-falls-after-second-quarter-revenue-misses-estimates



    test run printout for part 2 
    
For post_num : 32392070 : we have the archived url ->http://web.archive.org/web/20220810064141/https://medium.com/luminasticity/to-speak-meaningfully-about-art-329093dbce7f
For post_num : 32427146 : we have the archived url ->http://web.archive.org/web/20220811093753/https://www.businessinsider.com/google-hiring-freeze-cuts-performance-improvement-plans-2022-8
For post_num : 32430867 : we have the archived url ->http://web.archive.org/web/20220811195836/https://hbr.org/2022/08/stop-ghosting-and-start-saying-no
For post_num : 32416815 : we have the archived url ->http://web.archive.org/web/20220811080525/https://www.lrb.co.uk/the-paper/v44/n16/geoff-mann/reversing-the-freight-train
For post_num : 32432826 : we have the archived url ->http://web.archive.org/web/20220811230238/https://www.wsj.com/articles/electric-cars-batteries-lithium-triangle-latin-america-11660141017
For post_num : 32410096 : we have the archived url ->http://web.archive.org/web/20220811083730/https://www.theatlantic.com/technology/archive/2022/08/what-to-do-with-old-clothing-donation-waste/671043/
For post_num : 32396061 : we have the archived url ->http://web.archive.org/web/20220809141426/https://www.scientificamerican.com/article/spiders-seem-to-have-rem-like-sleep-and-may-even-dream/
For post_num : 32431472 : we have the archived url ->http://web.archive.org/web/20220811142435/https://www.wsj.com/articles/perfect-linkedin-profile-headshot-photo-is-worth-1-000-and-a-job-11660160047
For post_num : 32426031 : we have the archived url ->http://web.archive.org/web/20220811134258/https://www.nytimes.com/interactive/2022/08/11/arts/anime-hugs.html
For post_num : 32425308 : we have the archived url ->http://web.archive.org/web/20220812005109/https://www.newyorker.com/news/q-and-a/googles-caste-bias-problem
For post_num : 32428824 : we have the archived url ->http://web.archive.org/web/20220810094238/https://www.bloomberg.com/news/features/2022-08-10/europe-s-low-water-levels-threaten-rhine-river-hit-80b-trade-lifeline
For post_num : 32432768 : we have the archived url ->http://web.archive.org/web/20220811225150/https://www.wsj.com/articles/cdc-drops-quarantine-recommendation-following-covid-19-exposure-11660244410
For post_num : 32410610 : we have the archived url ->http://web.archive.org/web/20220812005758/https://www.reuters.com/business/media-telecom/exclusive-google-fiber-plans-5-state-growth-spurt-biggest-since-2015-2022-08-10/
For post_num : 32427077 : we have the archived url ->http://web.archive.org/web/20220811164447/https://www.wired.com/story/this-anti-tracking-tool-checks-if-youre-being-followed/
For post_num : 32431662 : we have the archived url ->https://archive.ph/AGbm2
For post_num : 32420935 : we have the archived url ->https://archive.ph/4SGdL
For post_num : 32397510 : we have the archived url ->https://archive.ph/aPihu
For post_num : 32433568 : we have the archived url ->https://archive.ph/imeBT
For post_num : 32427554 : we have the archived url ->https://archive.ph/ba46U
For post_num : 32427402 : we have the archived url ->https://archive.ph/o1vnP
For post_num : 32386984 : we have the archived url ->https://archive.ph/exCE5
For post_num : 32410374 : we have the archived url ->https://archive.ph/CtkIF
For post_num : 32375868 : we have the archived url ->https://archive.ph/rIqe2
For post_num : 32417726 : we have the archived url ->https://archive.ph/O11t0
For post_num : 32399148 : we have the archived url ->https://archive.ph/3LorN
For post_num : 32410162 : we have the archived url ->https://archive.ph/tyLEZ
For post_num : 32424598 : we have the archived url ->https://archive.ph/7bRYC
For post_num : 32397432 : we have the archived url ->https://archive.ph/NY0Vs
For post_num : 32421292 : we have the archived url ->https://archive.ph/o1vnP
For post_num : 32404366 : we have the archived url ->https://archive.ph/B5noE

QQ --> why are they perfectly synced ?? am i getting a blocked for too many requests by wayback_machine ?? 14 
--> the answer was yes

--> waybackmachine = We are limiting the number of URLs you can submit to be Archived to the Wayback Machine, using the Save Page Now features, to no more than 15 per minute. If you submit more than that we will block Save Page Now requests from your IP number for 5 minutes.

--> archive.today = IDK could not find anything 
'''