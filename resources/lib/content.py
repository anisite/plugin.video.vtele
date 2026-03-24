# -*- coding: utf-8 -*-
# encoding=utf8

import sys, re, xbmcaddon, xbmc, xbmcplugin, datetime, time
from . import parse, html

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import unquote, quote_plus, unquote_plus, urljoin, urlparse
    from urllib.request import Request, urlopen
    from io import StringIO as StringIO
else:
    # Python 2 stuff
    from urlparse import urljoin, urlparse
    from urllib import quote_plus, unquote_plus, unquote
    from urllib2 import Request, urlopen
    from StringIO import StringIO

try:
    import json
except ImportError:
    import simplejson as json

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("noovo.plugin", 48) # (Your plugin name, Cache time in hours)

BASE_HOST = 'noovo.ca'
BASE_URL = 'https://' + BASE_HOST
__handle__ = int(sys.argv[1])

AZ_URL = ''
DOSSIERS_URL = ''
MEDIA_BUNDLE_URL = BASE_URL + 'MediaBundle/'

SEASON = 'Saison'
EPISODE = 'Episode'
LABEL = 'label'
FILTRES = '{"content":{"genreId":"","mediaBundleId":-1,"afficherTous":false},"show":{"' + SEASON + '":"","' + EPISODE + '":"","' + LABEL + '":""},"fullNameItems":[],"sourceId":""}'
INTEGRAL = 'Integral'

# A simple task to do to each response object
def do_something(response):
    log(response.url)

def threaded_function(arg):
    for i in range(arg):
        log("running")
        time.sleep(1)

def u(data):
    return data.encode("utf-8")

num_threads = 0

def listerEqualiser(cartes,filtres):
    log("listerEqualiser")
    liste = []
    for episode in cartes :
        log("----Charger Carte -----")
        
        # Safety check for thumbnailImages
        thumbnail_url = ''
        if 'thumbnailImages' in episode and len(episode['thumbnailImages']) > 0:
            thumbnail_url = episode['thumbnailImages'][0]['url']
        else:
            log("ATTENTION: thumbnailImages vide ou absent pour episode " + str(episode.get('id', 'UNKNOWN')))
        
        newItem = {   'genreId': 1, 
                      'nom': 'S'+ str(episode['seasonNumber']) + 'E'+ str(episode['episodeNumber']) + ' - ' + episode['title'],
                      'resume': episode['summary'],
                      'image' : thumbnail_url,
                      'url' : episode['id'],
                      'sourceUrl' : episode['id'],
                      'duree' : episode['duration'],
                      'filtres' : parse.getCopy(filtres)
                  }
                  
        newItem['filtres']['content']['url'] = episode['id']
        
        liste.append(newItem)

    for item in liste :
    
        item['isDir']= False
        item['forceSort'] = False
        item['nom']= item['nom']
        #item['url'] = item['url'] or None
        #item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=filtres['content']['cover']
        #item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        item[LABEL] = None # nomBloc
        item['categoryType'] = None #episode['categoryType']
        #item['url'] = None #episode['permalink']
        #item['image'] = None #getThumbnails(episode)
        item['genreId'] = ''
        item['nomComplet'] = item['nom'] #episode['view']['title']
        #item['resume'] =None # episode['view']['description']
        item[SEASON] = 'Saison ' + str(episode['seasonNumber'])
        #item['duree'] = 300 #None #episode['duration']/1000

        item['seasonNo'] = episode['seasonNumber']
        item['episodeNo'] = episode['episodeNumber']
        item['startDate'] = None #episode['startDate']
        item['endDate'] = None #episode['endDate']
        item['endDateTxt'] = None #episode['view']['endDate']

        item['streamInfo'] = None #episode['streamInfo']

        item['nomDuShow'] = None #mainShowName

        #item['sourceUrl'] = correctEmissionPageURL(carte.find_all("a")[0]['href']) #"55" #episode['streamInfo']['sourceId']
        
        #item['url'] = carte #episode['streamInfo']['sourceId']
        
        
        
        item[EPISODE] = None #'Episode ' + str(episode['episodeNo']).zfill(2)
        #item['fanart'] = None #fanart_url
        #item['nom'] = ''
    return liste

def loadListeSaison(filtres):
    log("-----------LISTE SAISON-------------")

    liste = []

    contentId = filtres['content']['url']
    log(contentId)
    post_media = '{"operationName":"axisMedia","variables":{"axisMediaId":"'+contentId+'","subscriptions":["CANAL_D","CANAL_VIE","INVESTIGATION","NOOVO","VRAK","Z"],"maturity":"ADULT","language":"FRENCH","authenticationState":"UNAUTH","playbackLanguage":"FRENCH"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"'+html.hash_256(contentId)+'"}},"query":"query axisMedia($axisMediaId: ID!, $subscriptions: [Subscription]!, $maturity: Maturity!, $language: Language!, $authenticationState: AuthenticationState!, $playbackLanguage: PlaybackLanguage!) @uaContext(subscriptions: $subscriptions, maturity: $maturity, language: $language, authenticationState: $authenticationState, playbackLanguage: $playbackLanguage) {\n  contentData: axisMedia(id: $axisMediaId) {\n    id\n    axisId\n    title\n    summary\n    description\n    genres {\n      name\n      __typename\n    }\n    posterImages: images(formats: POSTER) {\n      url\n      __typename\n    }\n    thumbnailImages: images(formats: THUMBNAIL) {\n      url\n      __typename\n    }\n    seasons {\n      title\n      id\n      seasonNumber\n      metadataUpgrade {\n        packageName\n        languages\n        userIsSubscribed\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}'

    jsonMedia = html.get_graphql_data(post_media)
    saisons = jsonMedia['data']['contentData']['seasons']
    log(saisons)

    cover = xbmcaddon.Addon().getAddonInfo('path')+'/resources/fanart.jpg'

    filtres['content']['cover'] = cover
    filtres['content']['tvshow'] = jsonMedia['data']['contentData']['title']
    xbmcplugin.setPluginCategory(__handle__, jsonMedia['data']['contentData']['title'])

    for saison in saisons:
        newItem = {   'genreId': 2, 
                    'nom': saison['title'],
                    'resume': jsonMedia['data']['contentData']['summary'] + '\r\n' + jsonMedia['data']['contentData']['description'],
                    'image' : jsonMedia['data']['contentData']['thumbnailImages'][0]['url'] or "DefaultFolder.png",
                    'url' : saison['id'],
                    'filtres' : parse.getCopy(filtres)
                }
                
        newItem['filtres']['content']['url'] = saison['id']
        newItem['filtres']['content']['cover'] = cover
        newItem['filtres']['content']['saison'] = saison['title']

        
        liste.append(newItem)

        
    for item in liste :
        item['isDir']= True
        item['forceSort']= False
        item['nom']= item['nom']
        #item['url'] = item['url'] or None
        item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/resources/icon.png'
        item['fanart']= filtres['content']['cover'] #cover #xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        #item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        #item['filtres']['content']['cover'] = cover


    return liste

def loadEmission(filtres):
    log("loadEmission")
    log(filtres)
    
    liste = []
    
    contentId = filtres['content']['url']
    log(contentId)

    post_season = '{"operationName":"season","variables":{"subscriptions":["CANAL_D","CANAL_VIE","INVESTIGATION","NOOVO","VRAK","Z"],"maturity":"ADULT","language":"FRENCH","authenticationState":"UNAUTH","playbackLanguage":"FRENCH","seasonId":"'+contentId+'"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"'+html.hash_256(contentId)+'"}},"query":"query season($seasonId: ID!, $subscriptions: [Subscription]!, $maturity: Maturity!, $language: Language!, $authenticationState: AuthenticationState!, $playbackLanguage: PlaybackLanguage!) @uaContext(subscriptions: $subscriptions, maturity: $maturity, language: $language, authenticationState: $authenticationState, playbackLanguage: $playbackLanguage) {\n  axisSeason(id: $seasonId) {\n    episodes {\n      path\n      id\n      axisId\n      title\n      duration\n      seasonNumber\n      contentType\n      availablePlaybackLanguages\n      axisPlaybackLanguages {\n        language\n        __typename\n      }\n      authConstraints {\n        authRequired\n        packageName\n        subscriptionName\n        __typename\n      }\n      thumbnailImages: images(formats: THUMBNAIL) {\n        url\n        __typename\n      }\n      episodeNumber\n      description\n      summary\n      __typename\n      flag {\n        title\n        label\n        __typename\n      }\n    }\n    __typename\n  }\n}\n"}'
    
    emissions = html.get_graphql_data(post_season)
    
    log("-----------------------------------------------")
    log(emissions)

    log("--content--")
    log(emissions['data']['axisSeason'])
    xbmcplugin.setPluginCategory(__handle__, filtres['content']['tvshow'])

    liste = liste + listerEqualiser(emissions['data']['axisSeason']['episodes'], filtres)

    return liste

# accueil
def dictOfGenres(filtres):

    liste = []
    
    i=0

    while True:
        print(i)

        post_grid = '{"operationName":"grid","variables":{"sorting":"DEFAULT","gridId":"contentid/MDRlOTVkOWItYmY3Zi00","page":'+str(i)+',"subscriptions":["CANAL_D","CANAL_VIE","INVESTIGATION","NOOVO","VRAK","Z"],"maturity":"ADULT","language":"FRENCH","authenticationState":"UNAUTH","playbackLanguage":"FRENCH"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"'+html.hash_256('MDRlOTVkOWItYmY3Zi00' + str(i))+'"}},"query":"query grid($gridId: ID!, $page: Int, $mode: CollectionMode, $subscriptions: [Subscription]!, $maturity: Maturity!, $language: Language!, $authenticationState: AuthenticationState!, $playbackLanguage: PlaybackLanguage!, $filterSelection: [FilterSelectionInput], $sorting: Sorting = DEFAULT) @uaContext(subscriptions: $subscriptions, maturity: $maturity, language: $language, authenticationState: $authenticationState, playbackLanguage: $playbackLanguage) {\n  contentData: grid(id: $gridId) {\n    id\n    title\n    collection(mode: $mode, sorting: $sorting) {\n      appliedSortMethod\n      page(page: $page, filterSelection: $filterSelection) {\n        totalItemCount\n        hasNextPage\n        hasPreviousPage\n        items {\n          id\n          title\n          __typename\n          ... on AxisObject {\n            axisId\n            summary\n            posterImages: images(formats: POSTER) {\n              url\n              __typename\n            }\n            thumbnailImages: images(formats: THUMBNAIL) {\n              url\n              __typename\n            }\n            __typename\n          }\n          ... on AxisMedia {\n            axisId\n            summary\n            posterImages: images(formats: POSTER) {\n              url\n              __typename\n            }\n            thumbnailImages: images(formats: THUMBNAIL) {\n              url\n              __typename\n            }\n            firstPlayableContent {\n              id\n              axisId\n              authConstraints {\n                authRequired\n                subscriptionName\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          ... on AxisContent {\n            axisId\n            duration\n            seasonNumber\n            episodeNumber\n            axisMedia {\n              id\n              title\n              axisId\n              __typename\n            }\n            __typename\n          }\n          ... on AceWebContent {\n            path\n            __typename\n          }\n          ... on AceContent {\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}'
        #test = html.get_graphql_data(post_grid)
        test = cache.cacheFunction(html.get_graphql_data, post_grid)

        log("---data----")

        if 'errors' in test:
            break

        cartes = test['data']['contentData']['collection']['page']['items']

        for carte in cartes :
            log(carte)
            
            #Retirer les elements interdits d'accès
            if 'firstPlayableContent' not in carte or carte['firstPlayableContent'] is None:
                continue

            if 'authConstraints' in carte['firstPlayableContent']:
                if len(carte['firstPlayableContent']['authConstraints']) > 0 and carte['firstPlayableContent']['authConstraints'][0]['authRequired']:
                    continue

            newItem = {   'genreId': i+1, 
                        'nom': carte['title'],
                        'resume':  carte.get('summary', ''),
                        'image' :  carte['posterImages'][0]['url'] if carte['posterImages'] and carte['posterImages'][0].get('url') else '',
                        'fanart':  carte['thumbnailImages'][0]['url'] if carte['thumbnailImages'] and carte['thumbnailImages'][0].get('url') else '',
                        'isDir' : True,
                        'url' : carte['id'],
                        'filtres' : parse.getCopy(filtres)
                    }
                    
            newItem['filtres']['content']['url'] = newItem['url']
            
            liste.append(newItem)
        
        i += 1

    for item in liste :
        item['forceSort'] = False
        item['nom'] = item['nom']
        #item['url'] = item['url'] or None
        item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/resources/icon.png'
        item['fanart'] = item['fanart'] or xbmcaddon.Addon().getAddonInfo('path')+'/resources/fanart.jpg'
        #item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId'] 

    return liste

def dictOfMainDirs(filtres):

    liste = []
    #liste = [{'genreId': -1, 'nom': '-- EN DIRECT --', 'url': DOSSIERS_URL,'resume':'Aucune emission est en direct presentement'}]

    newItem = {   'genreId': 1, 
                'nom': '[COLOR gold][B]Noovo - En direct[/B][/COLOR]',
                'resume': 'Regarder Noovo en direct', #getDescription(carte.find_all("a")[0]['href']),
                'isDir' : False,
                'duree' : -1,
                'sourceUrl': 'direct',
                'startDate' : None,
                'episodeNo' : 0,
                'seasonNo' : 0,
                'url' : 'direct',#correctEmissionPageURL(carte.find_all("a")[0]['href'], u(carte.get_text(strip=True))),
                'filtres' : parse.getCopy(filtres)
            }
            
    newItem['filtres']['content']['url'] = newItem['url']
    
    liste.append(newItem)

    for item in liste :
        item['forceSort'] = False
        item['nom']= item['nom']
        item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/resources/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/resources/fanart.jpg'
        item['filtres']= parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        item['filtres']['show']={}
        item['filtres']['fullNameItems'].append('nomDuShow')        
    return liste

def isGenre(genreValue, show):
    genres = show['genres']
    for genre in genres:
        if genre['genreId'] == genreValue:
            return True

    return False

def isIntegral(show):
    if show['categoryType']==INTEGRAL:
        return True
    else:
        return False

def getFanArt(show):
    thumbLink = show['view']['headerImg']
    thumbLink = re.sub('{w}', '1280', thumbLink)
    thumbLink = re.sub('{h}', '720', thumbLink)
    return thumbLink

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))
