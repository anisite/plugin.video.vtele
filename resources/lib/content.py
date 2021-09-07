# -*- coding: utf-8 -*-
# encoding=utf8

import sys, re, xbmcaddon, xbmc, datetime, time
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
        
        newItem = {   'genreId': 1, 
                      'nom': 'S'+ str(episode['seasonNumber']) + 'E'+ str(episode['episodeNumber']) + ' - ' + episode['title'],
                      'resume': episode['summary'],
                      'image' : episode['thumbnailImages'][0]['url'],
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
    post_media = '{"operationName":"axisMedia","variables":{"axisMediaId":"'+contentId+'","page":0,"subscriptions":["CANAL_D","CANAL_VIE","INVESTIGATION","NOOVO","VRAK","Z"],"maturity":"ADULT","language":"FRENCH","authenticationState":"UNAUTH","playbackLanguage":"FRENCH"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"'+html.hash_256(contentId)+'"}},"query":"query axisMedia($page: Int, $axisMediaId: ID!, $subscriptions: [Subscription]!, $maturity: Maturity!, $language: Language!, $authenticationState: AuthenticationState!, $playbackLanguage: PlaybackLanguage!) @uaContext(subscriptions: $subscriptions, maturity: $maturity, language: $language, authenticationState: $authenticationState, playbackLanguage: $playbackLanguage) {\n  contentData: axisMedia(id: $axisMediaId) {\n    id\n    axisId\n    title\n    summary\n    description\n    agvotCode\n    qfrCode\n    keywords\n    showSeasonTitle\n    genres {\n      name\n      __typename\n    }\n    originatingNetworkLogoId\n    heroBrandLogoId\n    featuredClip {\n      path\n      axisId\n      __typename\n    }\n    metadataUpgrade {\n      languages\n      packageName\n      userIsSubscribed\n      __typename\n    }\n    adUnit {\n      adultAudience\n      analyticsTitle\n      keyValue {\n        adTarget\n        contentType\n        mediaType\n        pageTitle\n        revShare\n        __typename\n      }\n      title\n      heroBrand\n      pageType\n      product\n      revShare\n      __typename\n    }\n    firstPlayableContent {\n      id\n      title\n      axisId\n      path\n      seasonNumber\n      episodeNumber\n      summary\n      duration\n      authConstraints {\n        authRequired\n        packageName\n        subscriptionName\n        __typename\n      }\n      featureImages: images(formats: THUMBNAIL) {\n        url\n        __typename\n      }\n      flag {\n        title\n        label\n        __typename\n      }\n      __typename\n    }\n    mainContents {\n      ...MainContentsData\n      __typename\n    }\n    featuredEpisode {\n      id\n      path\n      axisId\n      authConstraints {\n        authRequired\n        packageName\n        subscriptionName\n        __typename\n      }\n      __typename\n    }\n    axisPlaybackLanguages {\n      destinationCode\n      __typename\n    }\n    mediaType\n    mediaConstraint {\n      hasConstraintsNow\n      __typename\n    }\n    cast {\n      role\n      castMembers {\n        fullName\n        __typename\n      }\n      __typename\n    }\n    flag {\n      title\n      label\n      __typename\n    }\n    posterImages: images(formats: POSTER) {\n      url\n      __typename\n    }\n    thumbnailImages: images(formats: THUMBNAIL) {\n      url\n      __typename\n    }\n    originNetworkUrl\n    mediaType\n    firstAirYear\n    ratingCodes\n    relatedCollections {\n      title\n      path\n      axisId\n      description\n      collection(mode: NONE) {\n        ...ShowPageRotatorCollectionData\n        __typename\n      }\n      __typename\n    }\n    collection: promotionalContents {\n      ...PromotionalCollectionData\n      __typename\n    }\n    seasons {\n      title\n      id\n      seasonNumber\n      metadataUpgrade {\n        packageName\n        languages\n        userIsSubscribed\n        __typename\n      }\n      __typename\n    }\n    parent {\n      id\n      ... on Section {\n        title\n        rotatorConfig {\n          ...RotatorConfigData\n          __typename\n        }\n        gridConfig {\n          ...GridConfigData\n          __typename\n        }\n        __typename\n      }\n      ... on AdElement {\n        adUnitType {\n          adType\n          height\n          id\n          title\n          width\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    showPageLayout {\n      ... on ShowPageReference {\n        __typename\n        type\n      }\n      ... on Grid {\n        __typename\n        title\n        config {\n          ...GridConfigData\n          __typename\n        }\n        collection(mode: NONE) {\n          ...ShowPageRotatorCollectionData\n          __typename\n        }\n      }\n      ... on Rotator {\n        __typename\n        title\n        config {\n          ...RotatorConfigData\n          __typename\n        }\n        collection {\n          ...ShowPageRotatorCollectionData\n          __typename\n        }\n      }\n      ... on Sponsorship {\n        __typename\n        bannerType: type\n        title\n        label\n        brands {\n          id\n          title\n          image {\n            url\n            width\n            height\n            imageType\n            __typename\n          }\n          link {\n            url\n            linkTarget\n            linkLabel\n            __typename\n          }\n          __typename\n        }\n      }\n      ... on SocialElement {\n        id\n        title\n        label\n        links {\n          id\n          renderAs\n          linkType\n          linkLabel\n          linkTarget\n          url\n          hoverImage {\n            title\n            imageType\n            url\n            __typename\n          }\n          image {\n            id\n            title\n            url\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      ... on Link {\n        ...LinkData\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ShowPageRotatorCollectionData on Collection {\n  page(page: 0) {\n    totalItemCount\n    hasNextPage\n    hasPreviousPage\n    items {\n      __typename\n      id\n      title\n      ... on AxisObject {\n        axisId\n        summary\n        posterImages: images(formats: POSTER) {\n          url\n          __typename\n        }\n        thumbnailImages: images(formats: THUMBNAIL) {\n          url\n          __typename\n        }\n        thumbnailWideImages: images(formats: THUMBNAIL_WIDE) {\n          url\n          __typename\n        }\n        squareImages: images(formats: SQUARE) {\n          url\n          __typename\n        }\n        promoImage: images(formats: PROMO_TEASER) {\n          url\n          __typename\n        }\n        __typename\n      }\n      ... on AxisCollection {\n        path\n        __typename\n      }\n      ... on AxisContent {\n        duration\n        pathSegment\n        seasonNumber\n        episodeNumber\n        path\n        agvotCode\n        authConstraints {\n          authRequired\n          packageName\n          subscriptionName\n          __typename\n        }\n        axisMedia {\n          id\n          title\n          axisId\n          mediaType\n          path\n          genres {\n            name\n            __typename\n          }\n          firstAirYear\n          agvotCode\n          __typename\n        }\n        contentType\n        flag {\n          title\n          label\n          __typename\n        }\n        __typename\n      }\n      ... on AxisMedia {\n        agvotCode\n        firstAirYear\n        genres {\n          name\n          __typename\n        }\n        seasons {\n          id\n          __typename\n        }\n        firstPlayableContent {\n          id\n          axisId\n          path\n          authConstraints {\n            authRequired\n            subscriptionName\n            __typename\n          }\n          flag {\n            title\n            label\n            __typename\n          }\n          __typename\n        }\n        flag {\n          title\n          label\n          __typename\n        }\n        path\n        __typename\n      }\n      ... on Link {\n        ...LinkData\n        __typename\n      }\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PromotionalCollectionData on Collection {\n  page(page: $page) {\n    totalItemCount\n    hasNextPage\n    hasPreviousPage\n    items {\n      id\n      title\n      ... on AxisObject {\n        axisId\n        summary\n        thumbnailImages: images(formats: THUMBNAIL) {\n          url\n          __typename\n        }\n        __typename\n      }\n      ... on AxisContent {\n        axisId\n        agvotCode\n        duration\n        pathSegment\n        seasonNumber\n        episodeNumber\n        path\n        broadcastDate\n        expiresOn\n        startsOn\n        axisMedia {\n          id\n          title\n          axisId\n          mediaType\n          path\n          genres {\n            name\n            __typename\n          }\n          __typename\n        }\n        contentType\n        flag {\n          title\n          label\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment RotatorConfigData on RotatorConfig {\n  displayTitle\n  displayTotalItemCount\n  displayDots\n  style\n  imageFormat\n  lightbox\n  carousel\n  titleLinkMode\n  maxItems\n  disableBadges\n  customTitleLink {\n    ...LinkData\n    __typename\n  }\n  hideMediaTitle\n  __typename\n}\n\nfragment LinkData on Link {\n  urlParameters\n  renderAs\n  linkType\n  linkLabel\n  longLinkLabel\n  linkTarget\n  userMgmtLinkType\n  url\n  id\n  internalContent {\n    id\n    title\n    __typename\n    ... on AceWebContent {\n      path\n      pathSegment\n      __typename\n    }\n    ... on Section {\n      pathSegment\n      id\n      __typename\n    }\n    ... on AxisObject {\n      axisId\n      title\n      __typename\n    }\n    ... on TabItem {\n      id\n      sectionPath\n      __typename\n    }\n  }\n  hoverImage {\n    title\n    imageType\n    url\n    __typename\n  }\n  image {\n    id\n    width\n    height\n    title\n    url\n    __typename\n  }\n  bannerImages {\n    breakPoint\n    image {\n      id\n      title\n      url\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment GridConfigData on GridConfig {\n sortingEnabled\n  availableSortingOptions\n  filterEnabled\n  displayTitle\n  displayTotalItemCount\n  numberOfColumns\n  style\n  imageFormat\n  lightbox\n  paging {\n    pageSize\n    pagingType\n    __typename\n  }\n  hideMediaTitle\n  __typename\n}\n\nfragment MainContentsData on Collection {\n  page {\n    items {\n      id\n      title\n      ... on AxisContent {\n        axisId\n        path\n        seasonNumber\n        episodeNumber\n        summary\n        duration\n        availablePlaybackLanguages\n        authConstraints {\n          authRequired\n          packageName\n          subscriptionName\n          __typename\n        }\n        featureImages: images(formats: THUMBNAIL) {\n          url\n          __typename\n        }\n        __typename\n        flag {\n          title\n          label\n          __typename\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"}'

    jsonMedia = html.get_graphql_data(post_media)
    saisons = jsonMedia['data']['contentData']['seasons']
    log(saisons)

    cover = xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'

    filtres['content']['cover'] = cover

    for saison in saisons:
        newItem = {   'genreId': 2, 
                    'nom': jsonMedia['data']['contentData']['title'] + ' - ' + saison['title'],
                    'resume': jsonMedia['data']['contentData']['summary'] + '\r\n' + jsonMedia['data']['contentData']['description'],
                    'image' : jsonMedia['data']['contentData']['thumbnailImages'][0]['url'] or "DefaultFolder.png",
                    'url' : saison['id'],
                    'filtres' : parse.getCopy(filtres)
                }
                
        newItem['filtres']['content']['url'] = saison['id']
        newItem['filtres']['content']['cover'] = cover
        
        liste.append(newItem)

        
    for item in liste :
        item['isDir']= True
        item['forceSort']= False
        item['nom']= item['nom']
        #item['url'] = item['url'] or None
        item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
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
    
    #i= 1
    
    log("-----------------------------------------------")
    log(emissions)

    log("--content--")
    log(emissions['data']['axisSeason'])

    liste = liste + listerEqualiser(emissions['data']['axisSeason']['episodes'],filtres)

    return liste

# accueil
def dictOfGenres(filtres):

    liste = []
    
    i=0

    newItem = {   'genreId': 1, 
                'nom': u('[COLOR gold][B]Noovo - En direct[/B][/COLOR]'),
                'resume': u('Regarder Noovo en direct'), #getDescription(carte.find_all("a")[0]['href']),
                'image' :  None,
                'fanart':  None,
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

    while True:
        print(i)

        post_grid = '{"operationName":"grid","variables":{"sorting":"DEFAULT","gridId":"contentid/MDRlOTVkOWItYmY3Zi00","page":'+str(i)+',"subscriptions":["CANAL_D","CANAL_VIE","INVESTIGATION","NOOVO","VRAK","Z"],"maturity":"ADULT","language":"FRENCH","authenticationState":"UNAUTH","playbackLanguage":"FRENCH"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"'+html.hash_256('MDRlOTVkOWItYmY3Zi00' + str(i))+'"}},"query":"query grid($gridId: ID!, $page: Int, $mode: CollectionMode, $subscriptions: [Subscription]!, $maturity: Maturity!, $language: Language!, $authenticationState: AuthenticationState!, $playbackLanguage: PlaybackLanguage!, $filterSelection: [FilterSelectionInput], $sorting: Sorting = DEFAULT) @uaContext(subscriptions: $subscriptions, maturity: $maturity, language: $language, authenticationState: $authenticationState, playbackLanguage: $playbackLanguage) {\n  contentData: grid(id: $gridId) {\n    id\n    title\n    config {\n      ...GridConfigData\n      __typename\n    }\n    customLink {\n      linkLabel\n      renderAs\n      internalContent {\n        title\n        id\n        ... on AceWebContent {\n          path\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    collection(mode: $mode, sorting: $sorting) {\n      appliedSortMethod\n      ...GridCollectionData\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment GridCollectionData on Collection {\n  page(page: $page, filterSelection: $filterSelection) {\n    filterSelection {\n      filter\n      selectedIds\n      __typename\n    }\n    filtersResult {\n      filters {\n        filter\n        counts {\n          id\n          count\n          name\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    totalItemCount\n    hasNextPage\n    hasPreviousPage\n    items {\n      id\n      title\n      ... on AxisObject {\n        axisId\n        summary\n        posterImages: images(formats: POSTER) {\n          url\n          __typename\n        }\n        thumbnailImages: images(formats: THUMBNAIL) {\n          url\n          __typename\n        }\n        thumbnailWideImages: images(formats: THUMBNAIL_WIDE) {\n          url\n          __typename\n        }\n        squareImages: images(formats: SQUARE) {\n          url\n          __typename\n        }\n        __typename\n      }\n      ... on AxisCollection {\n        path\n        __typename\n      }\n      ... on AxisContent {\n        axisId\n        duration\n        pathSegment\n        seasonNumber\n        episodeNumber\n        path\n        authConstraints {\n          authRequired\n          packageName\n          subscriptionName\n          __typename\n        }\n        axisMedia {\n          id\n          title\n          axisId\n          mediaType\n          path\n          genres {\n            name\n            __typename\n          }\n          firstAirYear\n          __typename\n        }\n        contentType\n        flag {\n          title\n          label\n          __typename\n        }\n        __typename\n      }\n      ... on AxisMedia {\n        agvotCode\n        qfrCode\n        firstAirYear\n        genres {\n          name\n          __typename\n        }\n        originatingNetworkLogoId\n        heroBrandLogoId\n        seasons {\n          id\n          __typename\n        }\n        metadataUpgrade {\n          userIsSubscribed\n          packageName\n          __typename\n        }\n        firstPlayableContent {\n          id\n          axisId\n          path\n          authConstraints {\n            authRequired\n            subscriptionName\n            __typename\n          }\n          flag {\n            title\n            label\n            __typename\n          }\n          __typename\n        }\n        flag {\n          title\n          label\n          __typename\n        }\n        path\n        __typename\n      }\n      ... on Link {\n        ...LinkData\n        __typename\n      }\n      ... on Article {\n        path\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment GridConfigData on GridConfig {\n  sortingEnabled\n  availableSortingOptions\n  filterEnabled\n  displayTitle\n  displayTotalItemCount\n  numberOfColumns\n  style\n  imageFormat\n  lightbox\n  paging {\n    pageSize\n    pagingType\n    __typename\n  }\n  hideMediaTitle\n  __typename\n}\n\nfragment LinkData on Link {\n  urlParameters\n  renderAs\n  linkType\n  linkLabel\n  longLinkLabel\n  linkTarget\n  userMgmtLinkType\n  url\n  id\n  internalContent {\n    id\n    title\n    __typename\n    ... on AceWebContent {\n      path\n      pathSegment\n      __typename\n    }\n    ... on Section {\n      pathSegment\n      id\n      __typename\n    }\n    ... on AxisObject {\n      axisId\n      title\n      __typename\n    }\n    ... on TabItem {\n      id\n      sectionPath\n      __typename\n    }\n  }\n  hoverImage {\n    title\n    imageType\n    url\n    __typename\n  }\n  image {\n    id\n    width\n    height\n    title\n    url\n    __typename\n  }\n  bannerImages {\n    breakPoint\n    image {\n      id\n      title\n      url\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"}'
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
                        'nom': u(carte['title']),
                        'resume': u(carte['summary']), #getDescription(carte.find_all("a")[0]['href']),
                        'image' :  carte['posterImages'][0]['url'],
                        'fanart':  carte['thumbnailImages'][0]['url'],
                        'isDir' : True,
                        'url' : carte['id'],#correctEmissionPageURL(carte.find_all("a")[0]['href'], u(carte.get_text(strip=True))),
                        'filtres' : parse.getCopy(filtres)
                    }
                    
            newItem['filtres']['content']['url'] = newItem['url']
            
            liste.append(newItem)
        
        i += 1

    for item in liste :
        item['forceSort'] = False
        item['nom'] = item['nom']
        #item['url'] = item['url'] or None
        item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart'] = item['fanart'] or xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        #item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        
    return liste

def dictOfMainDirs(filtres):

    liste = []
    #liste = [{'genreId': -1, 'nom': '-- EN DIRECT --', 'url': DOSSIERS_URL,'resume':'Aucune emission est en direct presentement'}]

    for item in liste :
        item['isDir']= True
        item['forceSort'] = True
        item['nom']= unquote(item['nom'])
        item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
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
