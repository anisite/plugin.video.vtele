# -*- coding: utf-8 -*-
# encoding=utf8

import sys, simplejson, re, xbmcaddon, xbmc, datetime, time
from . import parse, cache, html
from bs4 import BeautifulSoup

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
#import thread
#import threading
#from time import sleep

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

options = {
           "SQ" : "SQ",
           "911" : "911",
           "Code 111" : "code-111",
          }
          
options2 = {
           "SQ" : urljoin(BASE_URL, "emissions/SQ"),
           "911" : urljoin(BASE_URL, "emissions/911"),
           "code-111" : urljoin(BASE_URL, "emissions/code-111"),
          }

# A simple task to do to each response object
def do_something(response):
    log(response.url)

def threaded_function(arg):
    for i in range(arg):
        log("running")
        time.sleep(1)

def u(data):
    return data.encode("utf-8")

def correctEmissionPageURL(url, nom=None):
    log("correctEmissionPageURL - nom")
    log(nom)
    log("correctEmissionPageURL - url")
    log(url)
    
    #if url[0] == "/":
    #    url = BASE_URL + url

    if url[-3:] == ".ca":
        url = url + "/"
    
    if nom is not None:
        if nom in options:
            nom = options[nom]
            #nom = "emissions/" + nom
            url = options2[nom]
            #url = urlparse.urljoin(BASE_URL, nom)
        
    log(url)
        
    return url


num_threads = 0
    
def MyThread1(arg):
    global num_threads
    num_threads += 1
    log("arg" + str(arg))
    cache.get_cached_content(correctEmissionPageURL(arg))
    num_threads -= 1
        
def getDescription(url):
    #log(url) 
    
    #thread = Thread(target = threaded_function, args = (10, ))
    #thread.start()
    #thread.join()
    
    #thread.start_new_thread(MyThread1, (url, ))
    
    return "NULL"
    try:

        log("---url---")
        log(url)
        data = cache.get_cached_content(correctEmissionPageURL(url))
        
        log("---data----")
        #log(data)
        
        soup = BeautifulSoup(data, 'html.parser')
        p = soup.find_all("div", { "class" : "banner-card__body" })
        
        log(p)
        
        if len(p) > 0:
            desc = u(p[0].get_text(strip=True))
            log(desc)
            return desc
    except:
        log("Erreur de getDescription")
    return "Aucune information."

    return data

def listerEqualiser(cartes,filtres):
    log("listerEqualiser")
    #log(nom)
    liste = []
    for carte in cartes :
        carte = carte.parent
        log("----Charger Carte -----")
        #log(u(carte.getText()))
        #log(carte)
        #log(carte.find_all("img")[0]['src'])
        #log("------------------------------")
        
        duration = -1
        durationDiv = carte.find('ul', {"class": 'card__meta'})
        if durationDiv:
            duration = durationDiv.find('li').get_text(strip=True)
            try:
                duration = time.strptime(duration,'%Mm %Ss')
            except:
                try:
                    duration = time.strptime(duration,'%HH %Mm')
                except:
                    duration = time.strptime("0m 0s",'%Mm %Ss')
            duration = datetime.timedelta(hours=duration.tm_hour,minutes=duration.tm_min,seconds=duration.tm_sec).total_seconds()
        
        log(duration)
        
        nom = ""
        try:
            #nom = u(carte.find("div", {'class': re.compile('card__body.*')}).find("a").getText())
            nom = u(carte.find("a", {'class': re.compile('card__title')}).get_text(strip=True))
        except:
            try:
                nom = u(carte.find("div", {'class': re.compile('card__body.*')}).find("a").get_text(strip=True))
            except:
                nom = "no name"
        
        log(nom)
        resume = u(carte.getText(" ",strip=True)) #PATCH
        log("resume: " + str(resume))
        
        img = None
        
        try:
            img = carte.find("img")['src']
        except:
            log("pas d'image")
        
        newItem = {   'genreId': 1, 
                      'nom': nom,
                      'resume': resume,
                      'image' : img,
                      'url' : correctEmissionPageURL(carte.find_all("a")[0]['href']),
                      'sourceUrl' : correctEmissionPageURL(carte.find_all("a")[0]['href']),
                      'duree' : duration,
                      'filtres' : parse.getCopy(filtres)
                  }
                  
        newItem['filtres']['content']['url'] = correctEmissionPageURL(carte.find_all("a")[0]['href'])
        
        liste.append(newItem)

    for item in liste :
        #log("--url--")
        #log(correctEmissionPageURL(carte.find_all("a")[0]['href']))
    
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

        #item['sourceUrl'] = correctEmissionPageURL(carte.find_all("a")[0]['href']) #"55" #episode['streamInfo']['sourceId']
        
        item['url'] = correctEmissionPageURL(carte.find_all("a")[0]['href']) #episode['streamInfo']['sourceId']
        
        
        
        item[EPISODE] = None #'Episode ' + str(episode['episodeNo']).zfill(2)
        #item['fanart'] = None #fanart_url
        #item['nom'] = ''
    return liste

    
def loadListeSaisonOD(filtres):
    log("-----------LISTE SAISON  MODE OD-------------")

    liste = []
    
    parsed = urlparse(filtres['content']['url'])
    log(filtres['content']['url'])
    out = ""
    
    log("parsed.netloc")
    log(parsed.netloc)
    
    
    #if parsed.netloc != BASE_HOST:
    #    out = options[parsed.netloc.replace("." + BASE_HOST, '')]
    #    out = "emissions/" + out
    #    filtres['content']['url'] = urlparse.urljoin(BASE_URL,out)
    
    log(filtres['content']['url'])
    
    data = cache.get_cached_content(filtres['content']['url'])
    soup = BeautifulSoup(data, 'html.parser')
    clip = soup.find_all("div", {'class': re.compile('clip-equalizer')}) #|clip-equalizer
    equalizer = soup.find("section", {'class': re.compile('od_article_list')}) #|clip-equalizer
    cartes = None
    
    log(equalizer)
    
    if equalizer:
        cartes = equalizer.find_all("article")
    
    saisons = soup.find_all("a", {'href': re.compile('.*/episodes')})
    
    liste = []
    for carte in cartes:
        log(carte)
        #log(nom)
 
        newItem = {   'genreId': 1, 
                      'nom': u(carte.find("header").find("h1").get_text(strip=True)),
                      'resume': u(carte.find("div", {"class": "content"}).get_text(strip=True)),
                      'image' : carte.find_all("img")[0]['src'],
                      'url' : correctEmissionPageURL(carte.find_all("a")[0]['href']),
                      'sourceUrl' : correctEmissionPageURL(carte.find_all("a")[0]['href']),
                      'duree' : None,
                      'filtres' : parse.getCopy(filtres)
                  }
                  
        newItem['filtres']['content']['url'] = carte.find_all("a")[0]['href']
        
        liste.append(newItem)

    for item in liste :
        #log("--url--")
        #log(correctEmissionPageURL(carte.find_all("a")[0]['href']))

        item['isDir']= False
        item['forceSort'] = False
        item['nom']= unquote(item['nom'])
        #item['url'] = item['url'] or None
        #item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']="https://occupationdouble.noovo.ca/_/images/bg_banner1.jpg"
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

        #item['sourceUrl'] = correctEmissionPageURL(carte.find_all("a")[0]['href']) #"55" #episode['streamInfo']['sourceId']
        
        item['url'] = correctEmissionPageURL(carte.find_all("a")[0]['href']) #episode['streamInfo']['sourceId']
        
        
        
        item[EPISODE] = None #'Episode ' + str(episode['episodeNo']).zfill(2)
        #item['fanart'] = None #fanart_url
        #item['nom'] = ''
    return liste
    #
    #
    #
    #log(saisons)
    #
    #cover = xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
    #if soup:
    #    coverdiv = soup.find("div", {'class': re.compile('banner__cover')})
    #    if coverdiv:
    #        cover = coverdiv.find("img")['src']
    #filtres['content']['cover'] = cover
    #
    #plot = ""
    #if cartes:
    #    plot = ""
    #else:
    #    plot = " (vide)"
    #    
    #for saison in saisons:
    #    newItem = {   'genreId': 2, 
    #                'nom': u(saison.getText() + plot ),
    #                'resume': "Voir les épisodes de la " + u(saison.getText()),
    #                'image' : "DefaultFolder.png",
    #                'url' : saison['href'],
    #                'filtres' : parse.getCopy(filtres)
    #            }
    #            
    #    newItem['filtres']['content']['url'] = correctEmissionPageURL(saison['href'])
    #    newItem['filtres']['content']['cover'] = cover
    #    
    #    liste.append(newItem)
    #
    #
    #
    #    #newItem = {   'genreId': i, 
    #    #              'nom': "Capsules",
    #    #              'resume': "",
    #    #              'image' : None,
    #    #              'url' : "",
    #    #              'sourceUrl' : "",
    #    #              'filtres' : parse.getCopy(filtres)
    #    #          }
    #    #          
    #    #liste.append(newItem)
    #
    #    
    #for item in liste :
    #    item['isDir']= True
    #    item['forceSort']= False
    #    item['nom']= urllib2.unquote(item['nom'])
    #    #item['url'] = item['url'] or None
    #    item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
    #    item['fanart']= filtres['content']['cover'] #cover #xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
    #    #item['filtres'] = parse.getCopy(filtres)
    #    item['filtres']['content']['genreId'] = item['genreId']
    #    #item['filtres']['content']['cover'] = cover
    #
    #    
    #if clip:
    #    for c in clip:
    #        cartes = c.find_all("div", {"class": "card__thumb"})
    #        log("--cartes--")
    #        #log(cartes)
    #        
    #        liste = liste + listerEqualiser(cartes,filtres)
    ##else:
    ##    newItem = {   'genreId': i, 
    ##                  'nom': "Aucun contenu",
    ##                  'resume': "Désolé",
    ##                  'image' : None,
    ##                  'url' : "",
    ##                  'sourceUrl' : "",
    ##                  'filtres' : parse.getCopy(filtres)
    ##              }
    ##              
    ##    liste.append(newItem)
    #return liste

def loadListeSaison(filtres):
    log("-----------LISTE SAISON-------------")

    liste = []
    
    parsed = urlparse(filtres['content']['url'])
    log(filtres['content']['url'])
    out = ""
    
    log("parsed.netloc")
    log(parsed.netloc)
    
    
    #if parsed.netloc != BASE_HOST:
    #    out = options[parsed.netloc.replace("." + BASE_HOST, '')]
    #    out = "emissions/" + out
    #    filtres['content']['url'] = urlparse.urljoin(BASE_URL,out)
    
    log(filtres['content']['url'])
    
    data = cache.get_cached_content(filtres['content']['url'])
    soup = BeautifulSoup(data, 'html.parser')
    clip = soup.find_all("div", {'class': re.compile('clip-equalizer')}) #|clip-equalizer
    equalizer = soup.find("div", {'class': re.compile('video-equalizer.*')}) #|clip-equalizer
    cartes = None
    
    if equalizer:
        cartes = equalizer.find_all("div", {"class": re.compile('card__thumb.*')})
    
    nav = soup.find_all("div", {'class': re.compile('l-section-header-navigation')})[0]
    saisons = nav.find_all("a", {'href': re.compile('.*/episodes')})
    #saisons = soup.find_all("a", text = re.compile('.*Saison [0-9]{1,2}.*'))
    
    log(saisons)

    cover = xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
    if soup:
        coverdiv = soup.find("div", {'class': re.compile('banner__cover.*')})
        if coverdiv:
            cover = coverdiv.find("img")['src']
    filtres['content']['cover'] = cover
    
    plot = ""
    if cartes:
        plot = ""
    else:
        plot = " (vide)"

    #PATCH OD
    #if "occupation-double" in filtres['content']['url']:
    #    newItem = {   'genreId': 2, 
    #                'nom': u("Afrique du Sud"),
    #                'resume': "Voir les épisodes",
    #                'image' : "DefaultFolder.png",
    #                'url' : "https://noovo.ca/emissions/occupation-double/afrique-du-sud/episodes/",
    #                'filtres' : parse.getCopy(filtres)
    #            }
    #            
    #    newItem['filtres']['content']['url'] = "/emissions/occupation-double/afrique-du-sud/episodes/"
    #    newItem['filtres']['content']['cover'] = cover
    #    
    #    liste.append(newItem)
    #    
    #    newItem = {   'genreId': 2, 
    #                'nom': u("CHEZ NOUS"),
    #                'resume': "Voir les épisodes",
    #                'image' : "DefaultFolder.png",
    #                'url' : "https://noovo.ca/emissions/occupation-double/chez-nous/episodes/",
    #                'filtres' : parse.getCopy(filtres)
    #            }
    #            
    #    newItem['filtres']['content']['url'] = "/emissions/occupation-double/chez-nous/episodes/"
    #    newItem['filtres']['content']['cover'] = cover
    #    
    #    liste.append(newItem)

    for saison in saisons:
        newItem = {   'genreId': 2, 
                    'nom': u(saison.get_text(strip=True) + plot ),
                    'resume': 'Voir les épisodes de la ' + parse.pyStr(saison.get_text(strip=True)),
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
        item['nom']= item['nom']
        #item['url'] = item['url'] or None
        item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']= filtres['content']['cover'] #cover #xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        #item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        #item['filtres']['content']['cover'] = cover

        
    if clip:
        for c in clip:
            cartes = c.find_all("div", {"class": re.compile('card__thumb.*')})
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
    
    i= 1
    
    soup = BeautifulSoup(data, 'html.parser')
    
    avecPagingation = soup.find("a", {'class': re.compile('pagination__arrow--right')})
    
    if filtres['content']['afficherTous']:
        log("---------avec---------pagination------------------")
        #log(avecPagingation)
        #urlNext = avecPagingation.find('a')['data-ajax-action']
        #next = chargerProchainePage(urlNext)
        #log("avecPagingation" + avecPagingation)
        navm = soup.find("nav", {'class': re.compile('pagination')})
        lien = navm.find_all("a", {'class': re.compile('pagination__link.*')})
        
        log(lien)

        for lie in lien[1:] :
            log(lie)
            log(lie['href'])
        
            data = data + cache.get_cached_content(lie['href'])
  
        soup = BeautifulSoup(data, 'html.parser')
        
    sections = soup.find_all("div", {'class': re.compile('video-equalizer')}) #|clip-equalizer
    
    log("-----------------------------------------------")
    log(sections)
    
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
        cartes = section.find_all("div", {"class": re.compile('card__thumb.*')})
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
    
    soup = BeautifulSoup(data, 'html.parser')
    cartes = soup.find_all("div", { "class" : "card" })
    #cartes = soup.find_all("div", {'class': re.compile(r'\card\b')})
    
    i=1

    for carte in cartes :
        #log("carte liste element")
        #log(carte.find_all("a")[0]['href'])
        #log(u(carte.getText()))
        #log(u(carte.getText()))
        #log(carte.find_all("img")[0]['src'])
        #log("------------------------------")
        
        #log(carte.find('img'))
        
        image = carte.find('img')
        
        if(carte.find_all("a")[0]['href'] == "https://noovo.ca/emissions/occupation-double-chez-nous-la-selection-officielle-des-candidats"):
            continue
        
        srcImage = None
        
        if image != None :
            srcImage = image['src']
        
        newItem = {   'genreId': i, 
                      'nom': u(carte.get_text(strip=True)),
                      'resume': "", #getDescription(carte.find_all("a")[0]['href']),
                      'image' : srcImage,
                      'url' : correctEmissionPageURL(carte.find_all("a")[0]['href'], u(carte.get_text(strip=True))),
                      'filtres' : parse.getCopy(filtres)
                  }
                  
        newItem['filtres']['content']['url'] = newItem['url']
        
        liste.append(newItem)

    for item in liste :
        item['isDir'] = True
        item['forceSort'] = True
        item['nom'] = item['nom']
        #item['url'] = item['url'] or None
        item['image'] = item['image'] or xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart'] = xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
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
        item['nom']= unquote(item['nom'])
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
