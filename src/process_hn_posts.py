
import requests
import json
from urllib.parse import urlparse
import regex as reg


'''
    Process_HN_Posts : note - this class is mostly used to more easily pass around objects/data-structures
            The Following methods are used to 
'''
class Process_HN_Posts:
    
    def __init__(self):
        
        self.hn_top_posts_list = None
        
        self.completed_post_set = set()    # set of the posts which have aready been processed

        self.hn_url_sub_post_list = []     # a list of tuples (<id_num>, <url>, <detail_map>) for all the posts with urls to websites that require subscription 
        
        self.hn_failed_request_list = []   # list of lists of form -> [<id>, <requests-response>, <request-attemp-num>, <api-called>] 

        # these are tobe used when testing each post (determine if this is needed)
        self.curr_post_id = None
        self.curr_post_details = None
        self.curr_post_url = None
        #self.curr_post_stat = None

        self.request_response_description_map = {    100 : 'continue',
                                                101 : 'switching_protocols',
                                                102 : 'processing',
                                                103 : 'checkpoint',
                                                122 : 'request_uri_too_long',
                                                200 : 'ok',
                                                201 : 'created',
                                                202 : 'accepted',
                                                203 : 'non_authoritative_information',
                                                204 : 'no_content',
                                                205 : 'reset_content, reset',
                                                206 : 'partial_content, partial',
                                                207 : 'multiple_status',
                                                208 : 'already_reported',
                                                226 : 'im_used',
                                                300 : 'multiple_choices',
                                                301 : 'moved_permanently',
                                                302 : 'found',
                                                303 : 'see_other',
                                                304 : 'not_modified',
                                                305 : 'use_proxy',
                                                306 : 'switch_proxy',
                                                307 : 'temporary_redirect',
                                                308 : 'permanent_redirect',
                                                400 : 'bad_request',
                                                401 : 'unauthorized',
                                                402 : 'payment_required',
                                                403 : 'forbidden',
                                                404 : 'not_found',
                                                405 : 'method_not_allowed',
                                                406 : 'not_acceptable',
                                                407 : 'proxy_authentication_required',
                                                408 : 'request_timeout',
                                                409 : 'conflict',
                                                410 : 'gone',
                                                411 : 'length_required',
                                                412 : 'precondition_failed',
                                                413 : 'request_entity_too_large',
                                                414 : 'request_uri_too_large',
                                                415 : 'unsupported_media_type',
                                                416 : 'requested_range_not_satisfiable',
                                                417 : 'expectation_failed',
                                                418 : 'im_a_teapot',
                                                421 : 'misdirected_request',
                                                422 : 'unprocessable_entity',
                                                423 : 'locked',
                                                424 : 'failed_dependency',
                                                425 : 'unordered_collection',
                                                426 : 'upgrade_required',
                                                428 : 'precondition_required',
                                                429 : 'too_many_requests',
                                                431 : 'header_fields_too_large',
                                                444 : 'no_response',
                                                449 : 'retry',
                                                450 : 'blocked_by_windows_parental_controls',
                                                451 : 'unavailable_for_legal_reasons',
                                                499 : 'client_closed_request',
                                                500 : 'internal_server_error',
                                                501 : 'not_implemented',
                                                502 : 'bad_gateway',
                                                503 : 'service_unavailable',
                                                504 : 'gateway_timeout',
                                                505 : 'http_version_not_supported',
                                                506 : 'variant_also_negotiates',
                                                507 : 'insufficient_storage',
                                                509 : 'bandwidth_limit_exceeded',
                                                510 : 'not_extended',
                                                511 : 'network_authentication_required'
                                            }
        
        self.subscription_site_set = set(    
                                [ 'https://www.adweek.com',
                                    'https://www.ad.nl',
                                    'https://www.americanbanker.com',
                                    'https://www.ambito.com',
                                    'https://www.baltimoresun.com',
                                    'https://www.barrons.com',
                                    'https://www.bloombergquint.com',
                                    'https://www.bloomberg.com',
                                    'https://www.bndestem.nl',
                                    'https://www.bostonglobe.com',
                                    'https://www.bd.nl',
                                    'https://www.brisbanetimes.com.au',
                                    'https://www.businessinsider.com',
                                    'https://www.caixinglobal.com',
                                    'https://www.centralwesterndaily.com.au',
                                    'https://cen.acs.org',
                                    'https://www.chicagotribune.com',
                                    'https://www.corriere.it',
                                    'https://www.chicagobusiness.com',
                                    'https://www.dailypress.com',
                                    'https://www.gelderlander.nl',
                                    'https://www.groene.nl',
                                    'https://www.destentor.nl',
                                    'https://speld.nl',
                                    'https://www.tijd.be',
                                    'https://www.volkskrant.nl',
                                    'https://www.demorgen.be',
                                    'https://www.denverpost.com',
                                    'https://www.df.cl',
                                    'https://www.editorialedomani.it',
                                    'https://www.dynamed.com',
                                    'https://www.ed.nl',
                                    'https://www.elmercurio.com',
                                    'https://www.elpais.com',
                                    'https://www.elperiodico.com',
                                    'https://www.elu24.ee',
                                    'https://www.britannica.com',
                                    'https://www.estadao.com.br',
                                    'https://www.examiner.com.au',
                                    'https://www.expansion.com',
                                    'https://www.fnlondon.com',
                                    'https://www.financialpost.com',
                                    'https://www.ft.com',
                                    'https://www.firstthings.com',
                                    'https://www.foreignpolicy.com',
                                    'https://www.fortune.com',
                                    'https://www.genomeweb.com',
                                    'https://www.glassdoor.com',
                                    'https://www.globes.co.il',
                                    'https://www.grubstreet.com',
                                    'https://www.haaretz.co.il',
                                    'https://www.haaretz.com',
                                    'https://harpers.org',
                                    'https://www.courant.com',
                                    'https://www.hbr.org',
                                    'https://www.hbrchina.org',
                                    'https://www.heraldsun.com.au',
                                    'https://fd.nl',
                                    'https://www.historyextra.com',
                                    'https://www.humo.be',
                                    'https://www.ilmanifesto.it',
                                    'https://www.inc.com',
                                    'https://www.interest.co.nz',
                                    'https://www.investorschronicle.co.uk',
                                    'https://www.lecho.be',
                                    'https://labusinessjournal.com',
                                    'https://www.lanacion.com.ar',
                                    'https://www.repubblica.it',
                                    'https://www.lastampa.it',
                                    'https://www.latercera.com',
                                    'https://www.lavoixdunord.fr',
                                    'https://www.ledevoir.com',
                                    'https://www.leparisien.fr',
                                    'https://www.lesechos.fr',
                                    'https://www.loebclassics.com',
                                    'https://www.lrb.co.uk',
                                    'https://www.latimes.com',
                                    'https://sloanreview.mit.edu',
                                    'https://www.technologyreview.com',
                                    'https://www.medium.com',
                                    'https://www.medscape.com',
                                    'https://mexiconewsdaily.com',
                                    'https://www.mv-voice.com',
                                    'https://www.nationalgeographic.com',
                                    'https://www.nydailynews.com',
                                    'https://www.nrc.nl',
                                    'https://www.ntnews.com.au',
                                    'https://www.nationalpost.com',
                                    'https://www.nzz.ch',
                                    'https://www.nymag.com',
                                    'https://www.nzherald.co.nz',
                                    'https://www.ocregister.com',
                                    'https://www.orlandosentinel.com',
                                    'https://www.pzc.nl',
                                    'https://www.paloaltoonline.com',
                                    'https://www.parool.nl',
                                    'https://www.postimees.ee',
                                    'https://qz.com',
                                    'https://www.quora.com',
                                    'https://quotidiani.gelocal.it',
                                    'https://republic.ru',
                                    'https://www.reuters.com',
                                    'https://www.sandiegouniontribune.com',
                                    'https://www.sfchronicle.com',
                                    'https://www.scientificamerican.com',
                                    'https://seekingalpha.com',
                                    'https://slate.com',
                                    'https://sofrep.com',
                                    'https://www.statista.com',
                                    'https://www.startribune.com',
                                    'https://www.stuff.co.nz',
                                    'https://www.sun-sentinel.com',
                                    'https://www.techinasia.com',
                                    'https://www.telegraaf.nl',
                                    'https://www.adelaidenow.com.au',
                                    'https://www.theadvocate.com.au',
                                    'https://www.theage.com.au',
                                    'https://www.the-american-interest.com',
                                    'https://www.theathletic.com',
                                    'https://www.theathletic.co.uk',
                                    'https://www.theatlantic.com',
                                    'https://www.afr.com',
                                    'https://www.theaustralian.com.au',
                                    'https://www.bizjournals.com',
                                    'https://www.canberratimes.com.au',
                                    'https://www.thecourier.com.au',
                                    'https://www.couriermail.com.au',
                                    'https://www.thecut.com',
                                    'https://www.dailytelegraph.com.au',
                                    'https://www.thediplomat.com',
                                    'https://www.economist.com',
                                    'https://www.theglobeandmail.com',
                                    'https://www.theherald.com.au',
                                    'https://www.thehindu.com',
                                    'https://www.irishtimes.com',
                                    'https://www.kansascity.com',
                                    'https://www.mercurynews.com',
                                    'https://www.themercury.com.au',
                                    'https://www.mcall.com',
                                    'https://www.thenation.com',
                                    'https://www.thenational.scot',
                                    'https://www.newstatesman.com',
                                    'https://www.nytimes.com',
                                    'https://www.newyorker.com',
                                    'https://www.news-gazette.com',
                                    'https://www.theolivepress.es',
                                    'https://www.inquirer.com',
                                    'https://www.thesaturdaypaper.com.au',
                                    'https://www.seattletimes.com',
                                    'https://www.spectator.com.au',
                                    'https://www.spectator.co.uk',
                                    'https://www.smh.com.au',
                                    'https://www.telegraph.co.uk',
                                    'https://www.thestar.com',
                                    'https://www.wsj.com',
                                    'https://www.washingtonpost.com',
                                    'https://www.thewrap.com',
                                    'https://www.themarker.com',
                                    'https://www.the-tls.co.uk',
                                    'https://www.towardsdatascience.com',
                                    'https://www.trouw.nl',
                                    'https://www.tubantia.nl',
                                    'https://www.vanityfair.com',
                                    'https://www.vn.nl',
                                    'https://www.vulture.com',
                                    'https://journalnow.com',
                                    'https://www.wired.com',
                                    'https://www.worldpoliticsreview.com',
                                    'https://www.zeit.de' ]
                                )
      
    

    '''
        helper function :
          
                1 - add_completed_post() - adds a post to the completed list
                        Note : this will be used to ensure that posts arent tested twice -> once processing has succedded in part-2
                        
    '''
    def add_completed_post(self, url_):
      self.completed_post_set.add(url_)
    


    
    
    '''
        Function 1 :  
                get_top_posts() - sends a request to hackernews to recive the top 500 posts
                        Note : the request is not garentted to succeed - you must check this before proceeding 
                        
                        TODO - test and determine best course of action for different error codes 
    '''
    def get_top_posts(self):
        
        hn_ts_request = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json')

        if hn_ts_request.status_code == 200:
            self.hn_top_posts_list  =  hn_ts_request.json()   # this line is redundant but serves as a comment
        else:
            print(f"Error: request status code is : {hn_ts_request.status_code},  {self.request_response_description_map[int(hn_ts_request.status_code)]}") 
            self.hn_top_posts_list = [-1]

    

    '''
        Function 2 :  
                get_post_details() - sends a request to hackernews to recive the post details for the post_num supplied
                        Note : the request is not garentted to succeed - you must check this before proceeding 
                        
                        TODO - test and determine best course of action for different error codes 
    '''
    def get_post_details(self):

        get_post_str = str(f'https://hacker-news.firebaseio.com/v0/item/{self.curr_post_id}.json')
        hn_post_request = requests.get(get_post_str)
        
        
        if hn_post_request.status_code == 200:
            self.curr_post_details  =  hn_post_request.json()   
        
        else:
            print(f"Error: request status code is : {hn_post_request.status_code},  {self.request_response_description_map[int(hn_post_request.status_code)]}") 
            self.curr_post_details = hn_post_request.status_code
    
    



    
    '''
        Function 3 : 
                get_post_url() - obtains the url linked to in the post, if it exists
                
                        Notes : 
                            i   - the url is not garnetted to be in the dict, 
                            ii  - the text (post text) might contain the url in it

    '''

    # https://github.com/lipoja/URLExtract
    def get_post_url(self):

      if "url" in self.curr_post_details:
          post_url = self.curr_post_details['url']
          return [post_url]

      elif "text" in self.curr_post_details:

        # TODO -- what to do if there are multiple urls
        post_text = self.curr_post_details["text"]

        http_list = reg.findall(r'(https?://[^\s]+)', post_text)
        www_list = reg.findall(r'(?:www[^\s]+)', post_text)
        
        post_url_list = http_list + [ 'http://'+www  for www in www_list]
        return post_url_list
      else :
        return []




    '''
        Function 4 :  
            get_core_url_list() - returns a list of all the possible url, equivelants/derivatives for the given url

                        notes :
                            i - since urls can be modified, be a subdomain, or have slightly different flavors, but still lead to the same core site
                                its important to extract out all the possible url_flavors to test against the set of urls that require subscriptions
                                    
    '''
    def get_core_url_list(self, url_):
      core_url_list = []
      
      # a - parse the url
      parsed_url = urlparse(url_)
      
      # b - get the base url, without any modifications
      base_url = parsed_url.netloc
      core_url_list.append(base_url)

      # c - base without leading subdomain
      base_no_subd = base_url
      while base_no_subd.count(".") > 1 :
        base_no_subd = base_no_subd[ base_no_subd.find('.')+1 : ] # take off subdomains untill theres only <base>.<com/net/...>
      core_url_list.append(base_no_subd)

      # d - base and base_no_subd with just www.
      core_url_list.append("www." + base_no_subd)
      core_url_list.append("www." + base_url)


      # e - base and base_no_subd with just https://
      core_url_list.append("https://" + base_no_subd)
      core_url_list.append("https://" + base_url)


      # f - base and base_no_subd with just http://  --> no websites with a http for now --> so skip this  
      #core_url_list.append("http://" + base_no_subd)
      #core_url_list.append("http://" + base_url)

      # g - base and base_no_subd with  https://www.
      core_url_list.append("https://www." + base_no_subd)
      core_url_list.append("https://www." + base_url)

      return core_url_list




    '''
        Function 5 :  
                post_has_sub_block() - returns True if the url* is in the set of urls that requires subscritptions, otherwise False
                    
                    note: * if any of the urls in the diff_url-flavor-list, is in the set (i.e. if the core/parent site is in the sub-set)
    '''
    # TODO -- change returns to field state, and add function comment
    def post_has_sub_block(self):
      post_url_list = self.get_post_url()

        # TODO - Curretly we return the first bad-url on list, but might want to search all
      for post_url_ in post_url_list :
        possible_url_list =  self.get_core_url_list(post_url_)

        for possible_url in possible_url_list:
          if possible_url in self.subscription_site_set:
            return (True, post_url_)
            
      return (False, post_url_list)
        
        


    '''
        Function 6 :  
            test_n_posts() - for each posts in the top_post_list, from start->stop , we process it 
                                a - if the url exists and is in the set, we add the (id,url,post_details) 
                                        to the hn_url_sub_post_list, for further processing in part 2
                                
                                b - TODO --> if the request fails, we add this to the  hn_failed_request_list, to possiby process later <-- TODO
                                
                                c - for all other cases (i.e. if the post does not contain a url or the url is not in the set of website_urls that need a subscritption)
                                        we add this to the --> completed_post_set
    '''
    # TODO -- change returns to field state, and add function comment
    def test_n_posts(self, start, stop):

      # a - for each post-id in the list of the top hn posts from start->stop
      for post_num in self.hn_top_posts_list[start:stop]:
        self.curr_post_id = post_num

        # b - make sure that the post-id was not already processed previously
        if self.curr_post_id not in self.completed_post_set:
          
          # c - next call the hn api to get the post details
          self.get_post_details()
          
          # c-1 : if the post returns an error : add to list of errors with the error number --> to be processed later after a try
          #       save as a list [<id>, <requests-response>, <request-attemp-num>, <api-called>] 
          if type(self.curr_post_details) != type({}) :
            self.hn_failed_request_list.apppend([self.curr_post_id, self.curr_post_details, 1, "details" ])

          # c-2 : if the the post returns a ok resonsem evaluate the details
          else:
            
            # d : first determine if the current post url is in the set of webstes the require a subscription
            has_sub_block, url = self.post_has_sub_block()

            # d-1 : if yes, then add a tuple if  (id, url, post_details)  to the list of urls -> to process (find internet-archive snapshots)
            if has_sub_block:
              self.hn_url_sub_post_list.append( (self.curr_post_id, url, self.curr_post_details) )
            
            # d-2 : otherwise add it to the completed post set and move on, (if the url is not present maybe add some other process)
            else :      
              self.completed_post_set.add(self.curr_post_id)
              
        
'''
    TODO --> 
        1. processing logic for different request failure responses
            
        2. possible text processing : note the &#x2 repeated pattern ->> 0x0002 or --> possibly XML (need to keep in mind to test for binary charchter codes that can occur and clean them before testing for presence of a url)
'''