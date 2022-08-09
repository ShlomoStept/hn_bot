## TODO -- use main to run the program (not just for testing )

from src.process_hn_posts import Process_HN_Posts

# test to see that part 1 works

# a - initialize an object of the process_hn_posts class
process_hn_posts = Process_HN_Posts()

# b - get the top 500 post ids
process_hn_posts.get_top_posts()

# c - test the first 50 posts to see if any of their urls require a subscription
process_hn_posts.test_n_posts(0,100)

# d - print out how many do, and how many dont and a list of the id/details

print("-"*30)
print(f"We have {len(process_hn_posts.completed_post_set)} posts of the {100}, that ::Do NOT:: contain urls to websites that require a subsription")
print(process_hn_posts.completed_post_set)
print()
print(f"We have {len(process_hn_posts.hn_url_sub_post_list)} posts of the {100}, that ::DO Indeed:: contain urls to websites that require a subsription, and here they are ")
[ print(post[1]) for post in process_hn_posts.hn_url_sub_post_list]
print("-"*30)


'''
    test_run ::  print_out ::
    
        We have 90 posts of the 100, that ::Do NOT:: contain urls to websites that require a subsription
    {32401413, 32405510, 32399368, 32403471, 32402977, 32403498, 32403504, 32398391, 32395831, 32401468, 32395840, 32405062, 32401480, 32398923, 32399949, 32396892, 32397920, 32405089, 32401510, 32402542, 32398963, 32398969, 32400002, 32399495, 32401548, 32384653, 32384147, 32394902, 32404635, 32401564, 32403121, 32401075, 32401078, 32398010, 32395971, 32405189, 32402630, 32402631, 32405705, 32404170, 32402661, 32405734, 32403685, 32402664, 32404730, 32399612, 32395518, 32404225, 32403206, 32401159, 32404248, 32396569, 32401691, 32403739, 32403746, 32399663, 32399672, 32401721, 32388410, 32395076, 32395589, 32402758, 32378695, 32403275, 32396638, 32396641, 32398181, 32396651, 32394607, 32404857, 32390526, 32397699, 32399238, 32404358, 32399752, 32396685, 32403353, 32399266, 32393634, 32401849, 32402373, 32398789, 32390600, 32403403, 32400849, 32400852, 32404957, 32404961, 32392161, 32395256}

    We have 10 posts of the 100, that ::DO Indeed:: contain urls to websites that require a subsription, and here they are
    https://medium.com/luminasticity/to-speak-meaningfully-about-art-329093dbce7f
    https://www.bloomberg.com/news/articles/2022-08-09/coinbase-falls-after-second-quarter-revenue-misses-estimates
    https://www.nytimes.com/2022/08/09/business/ford-f-150-lightning-electric-truck-price.html
    https://www.reuters.com/markets/deals/applovin-offers-buy-unity-software-2022-08-09/
    https://www.reuters.com/world/us/wildfires-are-destroying-californias-forest-carbon-credit-reserves-study-2022-08-05/
    https://www.wired.com/story/vastaamo-psychotherapy-patients-hack-data-breach/
    https://www.bloomberg.com/news/articles/2022-08-09/gainesville-florida-moves-to-end-single-family-zoning
    https://www.scientificamerican.com/article/spiders-seem-to-have-rem-like-sleep-and-may-even-dream/
    https://www.bloomberg.com/news/articles/2022-08-09/doj-poised-to-sue-google-over-ad-market-as-soon-as-september
    https://www.theatlantic.com/technology/archive/2022/08/stick-shift-manual-transmission-cars/671078/
'''