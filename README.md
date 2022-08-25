# hn_bot - HackerNews Archive Finding Bot 
Searches all HackerNews top posts for links to websites that require a subscription, then find & posts a link to an archived snapshot of the article

## Process 
The Program follows the following 4 steps : (until a bug/server crash)
1. It grabs all the top, new and, best posts on HackerNews
    
2. Determines which posts contain links to articles on websites that have subscription blocks 
    - after x articles they require you to pay to read) 
    
3. Find the Archived snapshots of the articles.
    - Mainly using WaybackMachine, since archive.today (archive.ph), utalizes cloudfare - whose bot detector is very robust
    
4. Post a link to the Archived snapshot as a Post Commment on HackerNews
    
    
    

## State Of Project 
The program works perfectly, Unfourtunatly **@dang** ( HackerNews's Infamous moderator ) blocked my bot, because bot = bad 🙄

## Future Plans
I had fun exploring creating a bot, using API's and learned a lot about an area of computer science that i knew nothing about beforehand. 
So I'm not going to fight **@dang** even though hes killing my project.

- i hope someone finds this project usefull or fun, feel free to expand on this and build something cool (or even something that evades detection 😉

## Dependencies
> beautifulsoup4==4.11.1

> regex==2022.7.9

> requests==2.28.1

> urllib3==1.26.11
