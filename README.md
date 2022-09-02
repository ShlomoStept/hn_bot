
# hn_bot - Automated Archive Finder for HackerNews Posts
A Bot that searches for and posts links to archived versions of articles after scanning all of HackerNews' top articles for those that contain a link to a site that requires a subscription.

<p align="center">
  <img src="https://user-images.githubusercontent.com/74121686/186787727-f1dd40ed-a5ec-4e82-b7e3-2cc292700bb6.png" width="200">
</p>
<p align="center">
Enjoy a cute robot I made with dalle-2
</p>

## Process 
The Program follows **4 steps** :
        
        1. It collects all of HackerNews' top, new, and best posts.

        2. Identifies which posts include links to articles on websites with subscription blocks.
            (i.e. After a certain number of articles, you must pay to read them.)

        3. Locates the articles' archived snapshots.
            - WaybackMachine is mostly used because archive.today (archive.ph) uses Cloudflare, which has a very robust bot detector.

        4. Leaves a comment with a link to the Archived snapshot.
    
    
    
## State Of Project 
Unfortunately, the application was blocked by the moderator of HackerNews, **@dang**, since bot = evil. 🙄
The software, however, performs flawlessly (p.s. - i'm joking, I'm sure their are 100+ bugs). 

## Future Plans

I enjoyed learning about building a bot and using APIs while also discovering a whole new field of computer science.
- I hope someone finds this project entertaining or useful 
- Feel free to expand on this and build something better (or maybe even 🤫 something that is undetectable 😉)

## Dependencies
Contents of requirements.txt
        
        
        beautifulsoup4==4.11.1
        regex==2022.7.9
        requests==2.28.1
        urllib3==1.26.11
