# -*- coding: utf-8 -*-
# encoding=utf8

import urllib2, simplejson, parse, cache, re, xbmcaddon, html, xbmc, datetime, time
from BeautifulSoup import BeautifulSoup

#import thread
#import threading
#from time import sleep

BASE_URL = 'https://noovo.ca'
AZ_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/Az'
DOSSIERS_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/folders'
#POPULAIRE_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/populars/'
MEDIA_BUNDLE_URL = BASE_URL + 'MediaBundle/'

SEASON = 'Saison'
EPISODE = 'Episode'
LABEL = 'label'
FILTRES = '{"content":{"genreId":"","mediaBundleId":-1,"afficherTous":false},"show":{"' + SEASON + '":"","' + EPISODE + '":"","' + LABEL + '":""},"fullNameItems":[],"sourceId":""}'
INTEGRAL = 'Integral'

# A simple task to do to each response object
def do_something(response):
    print response.url

def threaded_function(arg):
    for i in range(arg):
        print "running"
        sleep(1)

def u(data):
    return data.encode("utf-8")

def correctEmissionPageURL(url):
    if url[-3:] == ".ca":
        url = url + "/"
    return url


num_threads = 0
    
def MyThread1(arg):
    global num_threads
    num_threads += 1
    print "arg" + str(arg)
    cache.get_cached_content(correctEmissionPageURL(arg))
    num_threads -= 1
        
def getDescription(url):
    #log(url) 
    
    #thread = Thread(target = threaded_function, args = (10, ))
    #thread.start()
    #thread.join()
    
    #thread.start_new_thread(MyThread1, (url, ))
    
    #print "next...exiting"
    
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

def chargerProchainePage(url):
    #log(url)
    data = cache.get_cached_content(url)
    soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    avecPagingation = soup.find("nav", {'class': re.compile('pagination-more.*')})
    if avecPagingation:
        data = data + chargerProchainePage(avecPagingation.find('a')['data-ajax-action'])
    
    return data

def listerEqualiser(cartes,filtres):
    liste = []
    for carte in cartes :
        carte = carte.parent
        #log(u(carte.getText()))
        #log(carte.findAll("img")[0]['src'])
        #log("------------------------------")
        
        duration = -1
        durationDiv = carte.find('ul', {"class": 'card__meta'})
        if durationDiv:
            duration = durationDiv.find('li').getText()
            try:
                duration = time.strptime(duration,'%M m %S s')
            except:
                try:
                    duration = time.strptime(duration,'%H H %M m')
                except:
                    duration = -1
            duration = datetime.timedelta(hours=duration.tm_hour,minutes=duration.tm_min,seconds=duration.tm_sec).total_seconds()
        
        
        newItem = {   'genreId': 1, 
                      'nom': u(carte.find("div", {"class": "card__body"}).find("a").getText()),
                      'resume': u(carte.find("div", {"class": "card__typography"}).getText()),
                      'image' : BASE_URL + carte.findAll("img")[0]['src'],
                      'url' : correctEmissionPageURL(carte.findAll("a")[0]['href']),
                      'sourceUrl' : correctEmissionPageURL(carte.findAll("a")[0]['href']),
                      'duree' : duration,
                      'filtres' : parse.getCopy(filtres)
                  }
                  
        newItem['filtres']['content']['url'] = correctEmissionPageURL(carte.findAll("a")[0]['href'])
        
        liste.append(newItem)

    for item in liste :
        #log("--url--")
        #log(correctEmissionPageURL(carte.findAll("a")[0]['href']))
    
        item['isDir']= False
        item['forceSort'] = False
        item['nom']= urllib2.unquote(item['nom'])
        #item['url'] = item['url'] or None
        #item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=filtres['content']['cover']
        #item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        item[LABEL] = None # nomBloc
        item['categoryType'] = None #episode['categoryType']
        item['url'] = None #episode['permalink']
        #item['image'] = None #getThumbnails(episode)
        item['genreId'] = ''
        item['nomComplet'] = item['nom'] #episode['view']['title']
        #item['resume'] =None # episode['view']['description']
        item[SEASON] = None #'Saison ' + str(episode['seasonNo'])
        #item['duree'] = 300 #None #episode['duration']/1000

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
        #item['fanart'] = None #fanart_url
        #item['nom'] = ''
    return liste

def loadListeSaison(filtres):
    liste = []
    data = cache.get_cached_content(filtres['content']['url'])
    soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    clip = soup.findAll("div", {'class': re.compile('clip-equalizer')}) #|clip-equalizer
    equalizer = soup.find("div", {'class': re.compile('video-equalizer')}) #|clip-equalizer
    cartes = None
    if equalizer:
        cartes = equalizer.findAll("div", {"class": "card__thumb"})
    
    saisons = soup.findAll("a", {'href': re.compile('.*/saisons/.*')})
    
    log(saisons)

    cover = xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
    if soup:
        coverdiv = soup.find("div", {'class': re.compile('banner__cover')})
        if coverdiv:
            cover = BASE_URL + coverdiv.find("img")['src']
    filtres['content']['cover'] = cover
    
    plot = ""
    if cartes:
        plot = ""
    else:
        plot = " (vide)"
        
    for saison in saisons:
        newItem = {   'genreId': 2, 
                    'nom': u(saison.getText() + plot ),
                    'resume': "Voir les épisodes de la " + u(saison.getText()),
                    'image' : "DefaultFolder.png",
                    'url' : saison['href'],
                    'filtres' : parse.getCopy(filtres)
                }
                
        newItem['filtres']['content']['url'] = correctEmissionPageURL(saison['href'])
        newItem['filtres']['content']['cover'] = cover
        
        liste.append(newItem)



        #newItem = {   'genreId': i, 
        #              'nom': "Capsules",
        #              'resume': "",
        #              'image' : None,
        #              'url' : "",
        #              'sourceUrl' : "",
        #              'filtres' : parse.getCopy(filtres)
        #          }
        #          
        #liste.append(newItem)

        
    for item in liste :
        item['isDir']= True
        item['forceSort']= False
        item['nom']= urllib2.unquote(item['nom'])
        #item['url'] = item['url'] or None
        item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']= filtres['content']['cover'] #cover #xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        #item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        #item['filtres']['content']['cover'] = cover

        
    if clip:
        for c in clip:
            cartes = c.findAll("div", {"class": "card__thumb"})
            log("--cartes--")
            #log(cartes)
            
            liste = liste + listerEqualiser(cartes,filtres)
    #else:
    #    newItem = {   'genreId': i, 
    #                  'nom': "Aucun contenu",
    #                  'resume': "Désolé",
    #                  'image' : None,
    #                  'url' : "",
    #                  'sourceUrl' : "",
    #                  'filtres' : parse.getCopy(filtres)
    #              }
    #              
    #    liste.append(newItem)
    return liste

def loadEmission(filtres):
    log("loadEmission")
    log(filtres)
    
    liste = []
    
    data = cache.get_cached_content(BASE_URL + filtres['content']['url'])
    
    log("---data----")
    #log(data)
    
    i= 1
    
    soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    
    avecPagingation = soup.find("nav", {'class': re.compile('pagination-more.*')})
    
    if filtres['content']['afficherTous']:
        log("---------avec---------pagination------------------")
        #log(avecPagingation)
        urlNext = avecPagingation.find('a')['data-ajax-action']
        next = chargerProchainePage(urlNext)
        soup = BeautifulSoup(data + next, convertEntities=BeautifulSoup.HTML_ENTITIES)
    
    sections = soup.findAll("div", {'class': re.compile('video-equalizer')}) #|clip-equalizer
    
    print "-----------------------------------------------"
    print sections
    
    if avecPagingation and not filtres['content']['afficherTous']:
        newItem = {   'genreId': i, 
                      'nom': "Afficher tous les épisodes de la saison",
                      'resume': "Voir la liste complète des épisodes",
                      'image' : None,
                      'url' : "",
                      'sourceUrl' : "",
                      'isDir' : True,
                      'fanart' : xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg',
                      'filtres' : parse.getCopy(filtres),
                      'forceSort' : False
                  }
        newItem['filtres']['content']['afficherTous'] = True
        

    for section in sections :
        cartes = section.findAll("div", {"class": "card__thumb"})
        log("--cartes--")
        #log(cartes)
        liste = liste + listerEqualiser(cartes,filtres)
    
    if avecPagingation and not filtres['content']['afficherTous']:
        liste.append(newItem)
    
    return liste

    
def dictOfGenres(filtres):

    liste = []
    
    data = cache.get_cached_content(BASE_URL + "/emissions")
    
    log("---data----")
    #log(data)
    
    soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    cartes = soup.findAll("div", { "class" : "card" })
    #cartes = soup.findAll("div", {'class': re.compile(r'\card\b')})
    
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
                  
        newItem['filtres']['content']['url'] = correctEmissionPageURL(carte.findAll("a")[0]['href'])
        
        liste.append(newItem)

    for item in liste :
        item['isDir']= True
        item['forceSort'] = True
        item['nom']= urllib2.unquote(item['nom'])
        #item['url'] = item['url'] or None
        item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        #item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']

    #log(liste)
        
    #while num_threads > 0:
    #    pass
        
    return liste

def dictOfMainDirs(filtres):

    liste = []
    #liste = [{'genreId': -1, 'nom': '-- EN DIRECT --', 'url': DOSSIERS_URL,'resume':'Aucune emission est en direct presentement'}]

    for item in liste :
        item['isDir']= True
        item['forceSort'] = True
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
