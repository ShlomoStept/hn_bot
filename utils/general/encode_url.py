'''
    encode_url() :
        Is a Function that encodes the url string so that all websites can intage it properly
'''

def encode_url(url: str) -> str:
    # 1 - first step is to replace spaces " " with %20 
    encoded_url = str(url).strip().replace(" ", "%20")
    # TODO - add other encodinfg steps if nessecary 
    return encoded_url