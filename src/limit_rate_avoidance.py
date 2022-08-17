

'''
    In order to avaoid rte limiting and bot getting bloacked
    
    1. proxioes
        - get a list of them 
        - test which ones work
        - save /update the map/list of them
        
    2. changing the user agent 
    3. changing the host
    4. changing Cookies
    5. spoofind the Referer
    
    6. create sessions ?? -->TODO determine if this would be helpfull --> then batch the searching for each site

    7. chances are my ip address is banned so i need to find a good workaround
    
    
    
    8. making a session for reqests :
        a - archive today 
            test 1 - Main Page: Response headers 
                i    -   date : Tue, 16 Aug 2022 21:39:46 GMT
                ii   -   expires :Tue, 16 Aug 2022 21:44:39 GMT
                iii  -   host : https://archive.ph/
                iv   -   x-host : q-archiveweb1
                v    -   x-frame-options:	Deny
                
                                GET / HTTP/2
            test 1 - Main page : request headers
                Host: archive.ph
                User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0
                Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
                Accept-Language: en-US,en;q=0.5
                Accept-Encoding: gzip, deflate, br
                Connection: keep-alive
                Cookie: cf_clearance=fab1288dea7abc5767d25c04239ede29eea774e1-1660671163-JZLJWGLF; _ga=GA1.2.661111166.1660685979
                Upgrade-Insecure-Requests: 1
                Sec-Fetch-Dest: document
                Sec-Fetch-Mode: navigate
                Sec-Fetch-Site: none
                Sec-Fetch-User: ?1
                TE: trailers
                
    
    9. it may be that its getting a captcha and it cant defeat it 
    
        - tricks :
            - avoid using direct links 
            - use proxies, with a cooldown period for each
            - loook into good headers 
            
            
    
'''