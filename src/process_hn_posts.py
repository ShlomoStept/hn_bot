
import requests
import json


'''
    Process_HN_Posts : note - this class is mostly used to more easily pass around objects/data-structures
            The Following methods are used to 
'''
class Process_HN_Posts:
    
    def __init__(self):
        
        self.hn_top_posts_list = None
        
        self.hn_previous_post_list = []
        
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
        
    self.subscription_site_set = set(    [ 'https://www.adweek.com',
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
        Function 1 :  get_top_posts() - sends a request to hackernews to recive the top 500 posts
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

    
    
    # TODO -- change returns to field state, and add function comment
    def get_post_details(self, post_num):
        get_post_str = str(f'https://hacker-news.firebaseio.com/v0/item/{post_num}.json')
        hn_post_request = requests.get(get_post_str)
        print(hn_post_request)
        
        return hn_post_request.json() 
    
    
    
    # TODO -- change returns to field state, and add function comment
    def post_url_has_sub_block(self, post_details):
        post_url = post_details['url']
        if post_url in self.subscription_site_set:
            return True
        else:
            return False
        
        
    
    # TODO -- change returns to field state, and add function comment
    def test_n_posts(self, top_hn_post_list, start, stop):
        for post_num in top_hn_post_list[start:stop]:
            hn_post_detail = self.get_post_details(int(post_num))
            if self.post_url_has_sub_block(hn_post_detail):
                print(f"For {hn_post_detail['url']}, we need to check Internet-Archive")
                return True
            else :
                print(f" {hn_post_detail['url']} , does not have a subscription block")
                return False
            
            
    ## TODO -- some posts do not have a url in the post object dict, additionally some posts have a url in the text field
    
    '''  For example  -- for id # 32393197 last night 
    {'by': 'upbeat_general',
    'descendants': 1,
    'id': 32393197,
    'kids': [32393899],
    'score': 49,
    'text': 'Parts of search and maps appear to be down.<p>Cloud [0] and Workspace [1] dashboards are green.<p>0: https:&#x2F;&#x2F;status.cloud.google.com&#x2F;\n1: https:&#x2F;&#x2F;www.google.com&#x2F;appsstatus&#x2F;dashboard&#x2F;',
    'time': 1660008631,
    'title': 'Google Is Partially Down',
    'type': 'story'}
    
    
    note the &#x2 repeated pattern ->> 0x0002 or --> possibly XML (need to keep in mind to test for binary charchter codes that can occur and clean them before testing for presence of a url)
 '''