# -*- coding: utf-8 -*-

import os, urllib, sys, traceback, xbmcplugin, xbmcaddon, xbmc, xbmcgui

from resources.lib import content, parse, navig

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import quote_plus, unquote_plus, unquote
else:
    # Python 2 stuff
    from urllib import quote_plus, unquote_plus, unquote

try:
    import json
except ImportError:
    import simplejson as json

ADDON = xbmcaddon.Addon()
_HANDLE = int(sys.argv[1])

def peupler():
    if filtres['content']['genreId']!='':
        creer_liste_filtree()
        set_content('episodes')
        #xbmc.executebuiltin('Container.SetViewMode(54)') # "Info-wall" view.
    else:
        creer_menu_categories()
        set_content('tvshows')
        xbmc.executebuiltin('Container.SetViewMode(54)') # "Info-wall" view.


def creer_menu_categories():
    """ function docstring """
    navig.ajouterItemAuMenu(content.dictOfMainDirs(filtres))
    navig.ajouterItemAuMenu(content.dictOfGenres(filtres))

def creer_liste_filtree():
    """ function docstring """
    log("---creer_liste_filtree--START----")
    log(filtres['content']['url'])

    if "contentid/axis-media-" in filtres['content']['url'] :
        navig.ajouterItemAuMenu(content.loadListeSaison(filtres))
    elif "contentid/axis-season-" in filtres['content']['url'] :
        navig.ajouterItemAuMenu(content.loadEmission(filtres))
    else:
        nothing = 1

def creer_liste_videos():
    """ function docstring """
    log("---creer_liste_videos--START----")
    navig.ajouterItemAuMenu(parse.ListeVideosGroupees(filtres))

def get_params():
    """ function docstring """
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params)-1] == '/':
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for k in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[k].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

def set_content(content):
    """ function docstring """
    xbmcplugin.setContent(int(sys.argv[1]), content)
    return

def set_sorting_methods(mode):
    pass
    #if xbmcaddon.Addon().getSetting('SortMethodTvShow') == '1':
    #    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    #    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)
    #return

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))


# ---
log('--- init -----------------')
# ---

PARAMS = get_params()

URL = None
MODE = None
SOURCE_URL = ''
FILTERS = ''
filtres = {}

try:
    URL = unquote_plus(PARAMS["url"])
    log("PARAMS['url']:"+URL)
except Exception:
    pass
try:
    MODE = int(PARAMS["mode"])
    log("PARAMS['mode']:"+str(MODE))
except Exception:
    pass
try:
    FILTERS = unquote_plus(PARAMS["filters"])
except Exception:
    FILTERS = content.FILTRES
try:
    SOURCE_URL = unquote_plus(PARAMS["sourceUrl"])
except Exception:
    pass

filtres = json.loads(FILTERS)
   
if SOURCE_URL !='':
    navig.jouer_video(SOURCE_URL)

elif MODE == 99:
    ADDON.openSettings()
    
else:
    peupler()
    #set_content('episodes')


if MODE != 99:
    #set_sorting_methods(MODE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if MODE != 4 and xbmcaddon.Addon().getSetting('DeleteTempFiFilesEnabled') == 'true':
    PATH = xbmc.translatePath('special://temp').decode('utf-8')
    FILENAMES = next(os.walk(PATH))[2]
    for i in FILENAMES:
        if ".fi" in i:
            os.remove(os.path.join(PATH, i))