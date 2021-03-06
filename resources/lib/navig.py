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

import sys, xbmcgui, xbmcplugin, xbmcaddon, re, simplejson, xbmc
from . import cache, html, parse
from bs4 import BeautifulSoup

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

ADDON = xbmcaddon.Addon()
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
    if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
        resume = "[B]"+ str(nom) +"[/B][CR]" + unquote(resume)
    if iconimage=='':
        iconimage = ADDON_IMAGES_BASEPATH+'default-folder.png'

    """ function docstring """
    entry_url = sys.argv[0]+"?url="+url+\
        "&mode=1"+\
        "&filters="+quote(simplejson.dumps(filtres))
  
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
    name = show['nom'].decode('utf-8')
    the_url = show['url']
    iconimage = show['image']

    resume = show['resume'].decode('utf-8') #remove_any_html_tags(show['resume'] +'[CR][CR]' + finDisponibilite)
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
    

    
    data = cache.get_cached_content(source_url)
    
    ## Obtenir JSON avec liens RTMP du playlistService
    #video_json = simplejson.loads(\
    #    cache.get_cached_content(\
    #        'http://production.ps.delve.cust.lldns.net/r/PlaylistService/media/%s/getPlaylistByMediaId' % media_uid\
    #    )\
    #)
    #
    #play_list_item =video_json['playlistItems'][0]
    #
    ## Obtient les streams dans un playlist m3u8
    #m3u8_pl=cache.get_cached_content('https://mnmedias.api.telequebec.tv/m3u8/%s.m3u8' % play_list_item['refId'])
    #
    ## Cherche le stream de meilleure qualité
    #uri = obtenirMeilleurStream(m3u8_pl)   

    soup = BeautifulSoup(data, 'html.parser')
    videoXYZ = soup.find("video-js")
    
    if videoXYZ is None:
     video = soup.find("video")
    else:
     video = soup.find("video-js")
    
    
    log("policy key")
    #get_policykey(account, player):
    policyKey = cache.get_policykey(video['data-account'], video['data-player'], video['data-embed'])
    log(policyKey)
    
    #Obtenir le fichier de flux
    uri = THEPLATFORM_CONTENT_URL + video['data-video-id']
    
    content = html.get_url_txt(uri, policyKey)
    jsonData = simplejson.loads(content)
    
    strSrcUrl = ""
    
    bitrate = 0
    
    uri = jsonData['sources'][0]['src']
    
    for source in jsonData['sources']:
        if 'avg_bitrate' in source:
            if source['avg_bitrate'] > bitrate:
                bitrate = source['avg_bitrate']
                uri = source['src']

    
    # lance le stream
    if uri:
        play_item = xbmcgui.ListItem(path=uri)
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
