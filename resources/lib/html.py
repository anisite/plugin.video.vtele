# -*- coding: utf-8 -*-

# version 3.0.0 - By CB
# version 2.0.2 - By SlySen
# version 0.2.6 - By CB

import sys, re, socket
import xbmc, xbmcaddon
import gzip
import hashlib

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import quote_plus, unquote_plus
    from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
    from io import StringIO as StringIO
    import http.cookiejar as cookielib
else:
    # Python 2 stuff
    from urllib import quote_plus, unquote_plus
    from urllib2 import Request, urlopen, build_opener, HTTPCookieProcessor
    from StringIO import StringIO
    import cookielib

try:
    import json
except ImportError:
    import simplejson as json

try:
    unichr
except NameError:
    unichr = chr

# Merci à l'auteur de cette fonction
def unescape_callback(matches):
    """ function docstring """
    html_entities = \
    {
        'quot':'\"', 'amp':'&', 'apos':'\'', 'lt':'<',
        'gt':'>', 'nbsp':' ', 'copy':'©', 'reg':'®',
        'Agrave':'À', 'Aacute':'Á', 'Acirc':'Â',
        'Atilde':'Ã', 'Auml':'Ä', 'Aring':'Å',
        'AElig':'Æ', 'Ccedil':'Ç', 'Egrave':'È',
        'Eacute':'É', 'Ecirc':'Ê', 'Euml':'Ë',
        'Igrave':'Ì', 'Iacute':'Í', 'Icirc':'Î',
        'Iuml':'Ï', 'ETH':'Ð', 'Ntilde':'Ñ',
        'Ograve':'Ò', 'Oacute':'Ó', 'Ocirc':'Ô',
        'Otilde':'Õ', 'Ouml':'Ö', 'Oslash':'Ø',
        'Ugrave':'Ù', 'Uacute':'Ú', 'Ucirc':'Û',
        'Uuml':'Ü', 'Yacute':'Ý', 'agrave':'à',
        'aacute':'á', 'acirc':'â', 'atilde':'ã',
        'auml':'ä', 'aring':'å', 'aelig':'æ',
        'ccedil':'ç', 'egrave':'è', 'eacute':'é',
        'ecirc':'ê', 'euml':'ë', 'igrave':'ì',
        'iacute':'í', 'icirc':'î', 'iuml':'ï',
        'eth':'ð', 'ntilde':'ñ', 'ograve':'ò',
        'oacute':'ó', 'ocirc':'ô', 'otilde':'õ',
        'ouml':'ö', 'oslash':'ø', 'ugrave':'ù',
        'uacute':'ú', 'ucirc':'û', 'uuml':'ü',
        'yacute':'ý', 'yuml':'ÿ'
    }

    entity = matches.group(0)
    val = matches.group(1)

    try:
        if entity[:2] == r'\u':
            return entity.decode('unicode-escape')
        elif entity[:3] == '&#x':
            return unichr(int(val, 16))
        elif entity[:2] == '&#':
            return unichr(int(val))
        else:
            return html_entities[val].decode('utf-8')

    except (ValueError, KeyError):
        pass

def html_unescape(data):
    """ function docstring """
    data = data.decode('utf-8')
    data = re.sub(r'&#?x?(\w+);|\\\\u\d{4}', unescape_callback, data)
    data = data.encode('utf-8')
    return data

def hash_256(contentId):
    hash_object = hashlib.sha256(contentId)
    return hash_object.hexdigest()

def POST_HTML(url, POST, AUTH=False, METHOD="POST"):

    cookiejar = cookielib.LWPCookieJar()
    cookie_handler = HTTPCookieProcessor(cookiejar)
    opener = build_opener(cookie_handler)
    post_data = POST #json.dumps(POST)

    opener.addheaders = [
    ('accept', '*/*'),
    ('origin', 'https://www.noovo.ca'),
    ('user-agent', 'Mozilla/5.0 (Linux; Android 5.0.2; GT-N7105 Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36'),
    ('Content-Type', 'application/json'),
    ('referer', 'https://www.noovo.ca/emissions/'),
    ('accept-encoding','gzip, deflate, br'),
    ('accept-language','fr-CA,fr;q=0.9'),
    ('graphql-client-platform','entpay_web'),
    ('cookie', "AMCVS_BB3937CB5B349FE70A495EAE%40AdobeOrg=1; _fbp=fb.1.1630967386377.767740519; permutive-id=95c7adca-5ddf-4f13-86c6-e6cbbdeeb899; s_cc=true; __gads=ID=571ed3a75e0c6240:T=1630967388:S=ALNI_MZSoIhiNsAr0LCvYqE62OIQf1IEGw; AMCV_BB3937CB5B349FE70A495EAE%40AdobeOrg=-1124106680%7CMCIDTS%7C18877%7CMCMID%7C31863947386878357181033208221602887721%7CMCAAMLH-1631579879%7C7%7CMCAAMB-1631579879%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1630982279s%7CNONE%7CMCSYNCSOP%7C411-18884%7CvVersion%7C5.2.0; s_sq=bellmediaglobalprod%3D%2526c.%2526a.%2526activitymap.%2526page%253Dhttps%25253A%25252F%25252Fwww.noovo.ca%25252F%2526link%253D%2525C3%252589MISSIONS%2526region%253D__next%2526.activitymap%2526.a%2526.c; TS01deed19=01e4e7bd8f0ff324bf4279ad43ae9c1a8e38937efc777e198db0835f94a2d23de0f375f174579e80b9a453cbfbe58bebc47b4ec469; permutive-session=%7B%22session_id%22%3A%223584819f-1794-4ec8-8fd5-ae39142f661b%22%2C%22last_updated%22%3A%222021-09-07T00%3A54%3A33.875Z%22%7D; pvv=30; RT=\"z=1&dm=www.noovo.ca&si=dac735f3-c14d-40c3-86b2-6ce15aec6cb0&ss=kt9bm53n&sl=4&tt=8v0&obo=3&rl=1\"; OptanonConsent=isIABGlobal=false&datestamp=Mon+Sep+06+2021+20%3A59%3A22+GMT-0400+(heure+d%E2%80%99%C3%A9t%C3%A9+de+l%E2%80%99Est)&version=6.19.0&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false&geolocation=CA%3BQC; OptanonAlertBoxClosed=2021-09-07T00:59:22.328Z; mprtcl-v4_F5D8B94B={'gs':{'ie':1|'dt':'us1-e0a1d0f747ea1b4e93a6c56ee6f54e44'|'cgid':'08a51144-8342-4967-80ed-9e86d72470a9'|'das':'805885c7-8aee-4ba3-9402-859b76d9c0be'|'csm':'WyItNTk0MjI3MjYwODU4NjM2ODU1Il0='|'ssd':1630973683025|'sid':'D71D9DE2-08A1-4EAB-87BA-D896997B9FF7'|'les':1630976362228}|'l':0|'-594227260858636855':{'fst':1630967386387}|'cu':'-594227260858636855'}")
    #('X-Requested-With', 'tv.tou.android')
    ]
    
    #if AUTH:
    #    opener.addheaders = [('Authorization', 'Bearer ' +  GET_ACCESS_TOKEN())]
    headers = {}
    headers['Content-Type'] = 'application/json'
    request = Request(url, data=post_data, headers=headers)
    request.get_method = lambda: METHOD
    
    response = opener.open(request)
    
    return handleHttpResponse(response)

def get_url_txt(the_url, pk=None):
    """ function docstring """
    log("--get_url_txt----START--")
    
    req = Request(the_url)
    
    if pk:
        req.add_header('Accept', 'application/json;pk=' + pk)
    else:
        req.add_header(\
                       'User-Agent', \
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'\
                       )
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
        req.add_header('Accept-Language', 'fr-CA,fr-FR;q=0.8,en-US;q=0.6,fr;q=0.4,en;q=0.2')
        req.add_header('Accept-Encoding', 'gzip, deflate')
        req.add_header('Connection', 'keep-alive')
        req.add_header('Pragma', 'no-cache')
        req.add_header('Cache-Control', 'no-cache')
        
    response = urlopen(req)

    data = handleHttpResponse(response)

    return data


def handleHttpResponse(response):

    if sys.version_info.major >= 3:
        if response.info().get('Content-Encoding') == 'gzip':
            f = gzip.GzipFile(fileobj=response)
            data = f.read()
            return data
        else:
            data = response.read()
            return data
    else:
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( response.read() )
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
            return data
        else:
            return response.read()


def is_network_available(url):
    """ function docstring """
    try:
        # see if we can resolve the host name -- tells us if there is a DNS listening
        host = socket.gethostbyname(url)
        # connect to the host -- tells us if the host is actually reachable
        srvcon = socket.create_connection((host, 80), 2)
        srvcon.close()
        return True
    except socket.error:
        return False

def get_graphql_data(toPost):
    data = POST_HTML('https://www.noovo.ca/space-graphql/apq/graphql', toPost)
    return json.loads(data)

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))
