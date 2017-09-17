# -*- coding: utf-8 -*-
# encoding=utf8

import urllib2, simplejson, parse, cache, re, xbmcaddon, html, xbmc
from BeautifulSoup import BeautifulSoup

BASE_URL = 'https://noovo.ca'
AZ_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/Az'
DOSSIERS_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/folders'
#POPULAIRE_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/populars/'
MEDIA_BUNDLE_URL = BASE_URL + 'MediaBundle/'

SEASON = 'Saison'
EPISODE = 'Episode'
LABEL = 'label'
FILTRES = '{"content":{"genreId":"","mediaBundleId":-1},"show":{"' + SEASON + '":"","' + EPISODE + '":"","' + LABEL + '":""},"fullNameItems":[],"sourceId":""}'
INTEGRAL = 'Integral'

def u(data):
    return data.encode("utf-8")

def correctEmissionPageURL(url):
    if url[-3:] == ".ca":
        url = url + "/"
    return url
    
def getDescription(url):
    log(url) 
    return "NULL"
    try:

        log("---url---")
        log(url)
        data = cache.get_cached_content(correctEmissionPageURL(url))
        
        log("---data----")
        #log(data)
        
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        p = soup.findAll("div", { "class" : "banner-card__body" })
        
        log(p)
        
        if len(p) > 0:
            desc = u(p[0].getText())
            log(desc)
            return desc
    except:
        log("Erreur de getDescription")
    return "Aucune information."


def loadEmission(filtres):
    log("loadEmission")
    log(filtres)
    
    liste = []
    
    data = cache.get_cached_content(filtres['content']['url'])
    
    log("---data----")
    #log(data)
    
    i= 1
    
    soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    cartes = soup.findAll("div", {"class": "card__thumb"})
    
    log("--cartes--")
    #log(cartes)
    
    for carte in cartes :
        #log(u(carte.getText()))
        #log(carte.findAll("img")[0]['src'])
        #log("------------------------------")
        newItem = {   'genreId': i, 
                      'nom': u(carte.findAll("img")[0]['alt']),
                      'resume': getDescription(carte.findAll("a")[0]['href']),
                      'image' : BASE_URL + carte.findAll("img")[0]['src'],
                      'url' : correctEmissionPageURL(carte.findAll("a")[0]['href']),
                      'sourceUrl' : correctEmissionPageURL(carte.findAll("a")[0]['href']),
                      'filtres' : parse.getCopy(filtres)
                  }
                  
        newItem['filtres']['content']['url'] = carte.findAll("a")[0]['href']
        
        liste.append(newItem)

    for item in liste :
        log("--url--")
        log(correctEmissionPageURL(carte.findAll("a")[0]['href']))
    
        item['isDir']= False
        item['nom']= urllib2.unquote(item['nom'])
        #item['url'] = item['url'] or None
        item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        #item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        item['isDir'] = False
        item[LABEL] = None # nomBloc
        item['categoryType'] = None #episode['categoryType']
        item['url'] = None #episode['permalink']
        #item['image'] = None #getThumbnails(episode)
        item['genreId'] = ''
        item['nomComplet'] = item['nom'] #episode['view']['title']
        #item['resume'] =None # episode['view']['description']
        item[SEASON] = None #'Saison ' + str(episode['seasonNo'])
        item['duree'] = None #episode['duration']/1000

        item['seasonNo'] = None #episode['seasonNo']
        item['episodeNo'] =None #episode['episodeNo']
        item['startDate'] = None #episode['startDate']
        item['endDate'] = None #episode['endDate']
        item['endDateTxt'] = None #episode['view']['endDate']

        item['streamInfo'] = None #episode['streamInfo']

        item['nomDuShow'] = None #mainShowName

        #item['sourceUrl'] = correctEmissionPageURL(carte.findAll("a")[0]['href']) #"55" #episode['streamInfo']['sourceId']
        
        item['url'] = correctEmissionPageURL(carte.findAll("a")[0]['href']) #episode['streamInfo']['sourceId']
        
        
        
        item[EPISODE] = None #'Episode ' + str(episode['episodeNo']).zfill(2)
        item['fanart'] = None #fanart_url
        #item['nom'] = ''
    
    return liste

    
def dictOfGenres(filtres):
    liste = []
    
    data = cache.get_cached_content(BASE_URL + "/emissions")
    
    log("---data----")
    #log(data)
    
    soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    cartes = soup.findAll("div", { "class" : "card" })
    
    i=1
    
    for carte in cartes :
        #log(u(carte.getText()))
        #log(carte.findAll("img")[0]['src'])
        #log("------------------------------")
        newItem = {   'genreId': i, 
                      'nom': u(carte.getText()),
                      'resume': getDescription(carte.findAll("a")[0]['href']),
                      'image' : BASE_URL + carte.findAll("img")[0]['src'],
                      'url' : correctEmissionPageURL(carte.findAll("a")[0]['href']),
                      'filtres' : parse.getCopy(filtres)
                  }
                  
        newItem['filtres']['content']['url'] = carte.findAll("a")[0]['href']
        
        liste.append(newItem)

    for item in liste :
        item['isDir']= True
        item['nom']= urllib2.unquote(item['nom'])
        #item['url'] = item['url'] or None
        item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        #item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']

    log(liste)
        
    return liste

def dictOfMainDirs(filtres):

    liste = [{'genreId': -1, 'nom': '-- EN DIRECT --', 'url': DOSSIERS_URL,'resume':'Aucune emission est en direct presentement'}]

    for item in liste :
        item['isDir']= True
        item['nom']= urllib2.unquote(item['nom'])
        item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        item['filtres']= parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        item['filtres']['show']={}
        item['filtres']['fullNameItems'].append('nomDuShow')        
    return liste

def formatListe(liste, filtres):
    newListe = []
    for item in liste:
        newItem = {}
        newItem['isDir'] = True
        newItem['nom'] = item['view']['title']
        newItem['mediaBundleId'] = item['mediaBundleId']
        newItem['url'] = MEDIA_BUNDLE_URL + str(item['mediaBundleId'])
        newItem['image'] = getThumbnails(item)
        newItem['genreId'] = ''
        newItem['nomComplet'] = item['view']['title']
        newItem['resume'] = item['view']['description']
        newItem['fanart'] = getFanArt(item)
        newItem['filtres'] = parse.getCopy(filtres)
        newItem['filtres']['content']['mediaBundleId'] = item['mediaBundleId']
        newListe.append(newItem)

    return newListe

def getListeOfVideo(mediaBundleId, filtres):
    show = getShow(mediaBundleId)
    fanart_url = getFanArt(show)
    mainShowName = show['view']['title']
    
    newListe = []
    for bloc in show['mediaGroups']:
        if bloc['label'] == None:
            nomBloc = 'Contenu'
        else:
            nomBloc = bloc['label']
        
        for episode in bloc['medias']:
            newItem = {}
            newItem['isDir'] = False
            newItem[LABEL] = nomBloc
            newItem['categoryType'] = episode['categoryType']
            newItem['url'] = episode['permalink']
            newItem['image'] = getThumbnails(episode)
            newItem['genreId'] = ''
            newItem['nomComplet'] = episode['view']['title']
            newItem['resume'] = episode['view']['description']
            newItem[SEASON] = 'Saison ' + str(episode['seasonNo'])
            newItem['duree'] = episode['duration']/1000

            
            newItem['seasonNo'] = episode['seasonNo']
            newItem['episodeNo'] =episode['episodeNo']
            newItem['startDate'] = episode['startDate']
            newItem['endDate'] = episode['endDate']
            newItem['endDateTxt'] = episode['view']['endDate']


            newItem['streamInfo'] = episode['streamInfo']

            newItem['nomDuShow'] = mainShowName
            
            newItem['sourceId'] = episode['streamInfo']['sourceId']
            newItem[EPISODE] = 'Episode ' + str(episode['episodeNo']).zfill(2)
            newItem['fanart'] = fanart_url
            newItem['nom'] = ''

            for tag in filtres['fullNameItems']:
                newItem['nom'] = newItem['nom'] + newItem[tag] + ' - '

            newItem['nom'] = newItem['nom'] + episode['view']['title']
            newListe.append(newItem)

    return newListe

def get_liste(categorie):
    if categorie >= 0:
        liste = getJsonBlock(AZ_URL, 0)
        if categorie == 0:
            return liste
        listeFiltree = []
        for show in liste:
            if isGenre(categorie, show):
                listeFiltree.append(show)

        return listeFiltree
    if categorie == -1:
        return getJsonBlock(DOSSIERS_URL, 1)
    return {}

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

def getThumbnails(show):
    thumbLink = show['view']['thumbImg']
    thumbLink = re.sub('{w}', '320', thumbLink)
    thumbLink = re.sub('{h}', '180', thumbLink)
    return thumbLink

def getFanArt(show):
    thumbLink = show['view']['headerImg']
    thumbLink = re.sub('{w}', '1280', thumbLink)
    thumbLink = re.sub('{h}', '720', thumbLink)
    return thumbLink

def getShow(mediaBundleId):
    database = simplejson.loads(cache.get_cached_content(MEDIA_BUNDLE_URL + str(mediaBundleId)))
    return database['data']

def getJsonBlock(url, block):
    try:
        dataBlock = simplejson.loads(cache.get_cached_content(url))
        dataBlock = dataBlock['data'][block]['items']
    except ValueError:
        dataBlock = []
    finally:
        return dataBlock

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))
