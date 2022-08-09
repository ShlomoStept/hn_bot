# hn_bot 
_________________
## This Project Aims to Create a Bot that adds the internet Archive Link to any hackernews post with a newsite that requires a subscription to read (its a mouthfull)

## Overview of the Process (initial thoughts)

    1. Part 1 : Utalizes the Hackernews API it get a list of the top 500 posts, 
                  and for each post the url is tested against the set of known websites that require a subsription
                - if a site requires a subscription this url is added to a list for further procesing'
                - all other posts are added to a list of already processed posts
                
    2. Part 2 : Utalizing the Internet Archive API  **WARNING : Only 15 requests allowed per minute**
                  
                i   - use the url to see of a snapshot was taken -- if so grab the latest snapshot
                ii  - otherwise --> generate/trigger the creation of a snapshot (TODO-figure out how to do this)
                
                iii - then send back the url to the snapshot, to be used in the next part
                
    3. Part 3 : Use the NH api to post a comment with the webarchive link and a 
              ** Note: figure out how to make this pay for server costs (A/B-test diff call-for-actions)** 
