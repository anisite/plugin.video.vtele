# -*- coding: utf-8 -*-
# version 3.1.0 - By CB, PLafrance & andreq
# version 3.0.0 - By CB
# version 2.0.2 - By SlySen
# version 0.2.6 - By CB
#
# pylint...: --max-line-length 120
# vim......: set expandtab
# vim......: set tabstop=4
#

import sys, xbmcgui, xbmcplugin, xbmcaddon, re, xbmc
from . import html, parse
import inputstreamhelper

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import quote_plus, unquote, quote
    from urllib.request import Request, urlopen
    from io import StringIO as StringIO
else:
    # Python 2 stuff
    from urllib import quote_plus, unquote, quote
    from urllib2 import Request, urlopen
    from StringIO import StringIO

try:
    import json
except ImportError:
    import simplejson as json

ADDON = xbmcaddon.Addon()
BUILD_NUMBER      = int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])
ADDON_IMAGES_BASEPATH = ADDON.getAddonInfo('path')+'/resources/media/images/'
ADDON_FANART = ADDON.getAddonInfo('path')+'/fanart.jpg'
THEPLATFORM_CONTENT_URL = "https://edge.api.brightcove.com/playback/v1/accounts/618566855001/videos/"

__handle__ = int(sys.argv[1])

def ajouterItemAuMenu(items):
    for item in items:
        if item['isDir'] == True:
            ajouterRepertoire(item)
            #xbmc.executebuiltin('Container.SetViewMode(512)') # "Info-wall" view. 
            
        else:
            ajouterVideo(item)
            #xbmc.executebuiltin('Container.SetViewMode('+str(xbmcplugin.SORT_METHOD_DATE)+')')
            #xbmc.executebuiltin('Container.SetSortDirection(0)')

    if items:
        if items[0]['forceSort']  :
            xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
            xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DATE)




def ajouterRepertoire(show):
   
    nom = show['nom']
    url = show['url']
    iconimage =show['image']
    #genreId = show['genreId']
    resume = remove_any_html_tags(show['resume'])
    fanart = show['fanart']
    filtres = show['filtres']

    if resume=='':
        resume = unquote(ADDON.getAddonInfo('id')+' v.'+ADDON.getAddonInfo('version'))

    if iconimage=='':
        iconimage = ADDON_IMAGES_BASEPATH+'default-folder.png'

    """ function docstring """
    entry_url = sys.argv[0]+"?url="+url+\
        "&mode=1"+\
        "&filters="+quote(json.dumps(filtres))
  
    is_it_ok = True
    #liz = xbmcgui.ListItem(nom,iconImage=iconimage,thumbnailImage=iconimage)
    liz = xbmcgui.ListItem(nom)

    liz.setArt({ 'thumb' : iconimage } )

    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title": nom,\
            "plot":resume
        }\
    )
    setFanart(liz,fanart)

    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=True)

    return is_it_ok

def setFanart(liz,fanart):
    if ADDON.getSetting('FanartEnabled') == 'true':
        if ADDON.getSetting('FanartEmissionsEnabled') == 'true':
            liz.setProperty('fanart_image', fanart)
        else:
            liz.setProperty('fanart_image', ADDON_FANART)


def ajouterVideo(show):
    name = show['nom']
    the_url = show['url']
    iconimage = show['image']

    resume = show['resume'] #remove_any_html_tags(show['resume'] +'[CR][CR]' + finDisponibilite)
    duree = show['duree']
    fanart = show['fanart']
    sourceUrl = show['sourceUrl']
    annee = "" #show['startDate'][:4]
    premiere = show['startDate']
    episode = show['episodeNo']
    saison = show['seasonNo']
    
    is_it_ok = True
    entry_url = sys.argv[0]+"?url="+quote_plus(the_url)+"&sourceUrl="+quote_plus(sourceUrl)

    #if resume != '':
    #    if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
    #        resume = '[B]'+name.lstrip()+'[/B]'+'[CR]'+resume.lstrip() 
    #else:
    #    resume = name.lstrip()

    #liz = xbmcgui.ListItem(\
    #    remove_any_html_tags(name), iconImage=ADDON_IMAGES_BASEPATH+"default-video.png", thumbnailImage=iconimage)

    liz = xbmcgui.ListItem(remove_any_html_tags(name))

    liz.setArt({ 'thumb' : iconimage } )

    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title":remove_any_html_tags(name),\
            "Plot":remove_any_html_tags(resume, False),\
            "Duration":duree,\
            "Year":annee,\
            "Premiered":premiere,\
            "Episode":episode,\
            "Season":saison}\
    )
    liz.addContextMenuItems([('Informations', 'Action(Info)')])
    setFanart(liz,fanart)
    liz.setProperty('IsPlayable', 'true')

    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=False)
    return is_it_ok

RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_AFTER_CR = re.compile(r'\n.*')

def jouer_video(source_url):
    """ function docstring """
    check_for_internet_connection()
    uri = None
    
    log("--media_uid--")
    log(source_url)
    video_id = ''

    if source_url == 'direct':
        video_id = '2013891'
    else:
        graph_content = '{"operationName":"axisContent","variables":{"id":"'+source_url+'","subscriptions":["CANAL_D","CANAL_VIE","INVESTIGATION","NOOVO","VRAK","Z"],"maturity":"ADULT","language":"FRENCH","authenticationState":"UNAUTH","playbackLanguage":"FRENCH"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"'+html.hash_256(source_url)+'"}},"query":"query axisContent($id: ID!, $subscriptions: [Subscription]!, $maturity: Maturity!, $language: Language!, $authenticationState: AuthenticationState!, $playbackLanguage: PlaybackLanguage!) @uaContext(subscriptions: $subscriptions, maturity: $maturity, language: $language, authenticationState: $authenticationState, playbackLanguage: $playbackLanguage) {\n  axisContent(id: $id) {\n    axisId\n    id\n    path\n    title\n    duration\n    agvotCode\n    description\n    episodeNumber\n    seasonNumber\n    pathSegment\n    genres {\n      name\n      __typename\n    }\n    axisMedia {\n      id\n      title\n      __typename\n    }\n    adUnit {\n      heroBrand\n      analyticsTitle\n      pageType\n      product\n      revShare\n      title\n      keyValue {\n        adTarget\n        contentType\n        mediaType\n        pageTitle\n        revShare\n        __typename\n      }\n      __typename\n    }\n    authConstraints {\n      authRequired\n      language\n      startDate\n      endDate\n      __typename\n    }\n    axisPlaybackLanguages {\n      destinationCode\n      language\n      duration\n      __typename\n    }\n    originalSpokenLanguage\n    ogFields {\n      ogDescription\n      ogImages {\n        url\n        __typename\n      }\n      ogTitle\n      __typename\n    }\n    seoFields {\n      seoDescription\n      seoTitle\n      seoKeywords\n      __typename\n    }\n    flag {\n      title\n      label\n      __typename\n    }\n    posterImages: images(formats: POSTER) {\n      url\n      __typename\n    }\n    broadcastDate\n    expiresOn\n    startsOn\n    keywords\n    __typename\n  }\n}\n"}'
        media_response = html.get_graphql_data(graph_content)
        video_id = str(media_response['data']['axisContent']['axisId'])

    log(video_id)

    package = html.get_url_txt('https://capi.9c9media.com/destinations/noovo_hub/platforms/desktop/contents/'+video_id+'/contentpackages?$lang=fr&$include=[duration]')
    json_package = json.loads(package)

    package_id = str(json_package['Items'][0]['Id'])

    uri = 'https://capi.9c9media.com/destinations/noovo_hub/platforms/desktop/bond/contents/'+video_id+'/contentpackages/'+package_id+'/manifest.mpd'
    
    #get_policykey(account, player):
    #policyKey = cache.get_policykey(video['data-account'], video['data-player'], video['data-embed'])
    #log(policyKey)
    PROTOCOL = 'mpd'
    DRM = 'com.widevine.alpha'
    listitem = xbmcgui.ListItem(path=uri)
    url = uri
    is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    if is_helper.check_inputstream():
        listitem.setProperty('path', url)
        if BUILD_NUMBER >= 19:
            listitem.setProperty('inputstream', is_helper.inputstream_addon)
        else:
            listitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
        listitem.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
        listitem.setMimeType('application/dash+xml')
        listitem.setProperty('inputstream.adaptive.license_type', DRM)
        listitem.setProperty('inputstream.adaptive.license_key', 'https://license.9c9media.ca/widevine' + '||R{SSM}|')
        #listitem.setProperty('inputstream.stream_headers', 'Authorization=' + BEARER)
    
    # lance le stream
    if uri:
        play_item = listitem
        xbmcplugin.setResolvedUrl(__handle__,True, play_item)
    else:
        xbmc.executebuiltin('Notification(%s,Incapable d''obtenir lien du video,5000,%s')

def check_for_internet_connection():
    """ function docstring """
    if ADDON.getSetting('NetworkDetection') == 'false':
        return
    return

def remove_any_html_tags(text, crlf=True):
    """ function docstring """
    text = RE_HTML_TAGS.sub('', parse.pyStr(text, True))
    text = text.lstrip()
    if crlf == True:
        text = RE_AFTER_CR.sub('', parse.pyStr(text, True))
    return text

def obtenirMeilleurStream(pl):
    maxBW = 0
    bandWidth=None
    uri = None
    for line in pl.split('\n'):
        if re.search('#EXT-X',line):
            bandWidth=None
            try:
                match  = re.search('BANDWIDTH=(\d+)',line)
                bandWidth = int(match.group(1))
            except :
                bandWidth=None
        elif line.startswith('http'):
            if bandWidth!=None:
                if bandWidth>maxBW:
                    maxBW = bandWidth
                    uri = line
    return uri

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))
