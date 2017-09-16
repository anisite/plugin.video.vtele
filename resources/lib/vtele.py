﻿# -*- coding: utf-8 -*-

#Modules general
import os
import re
import sys
from datetime import date
import time
from urllib import quote_plus, unquote_plus
from traceback import print_exc

#modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon

try:
    import json
except ImportError:
    import simplejson as json

import html2text
    
    
ADDON             = Addon( "plugin.video.vtele" )
ADDON_NAME        = ADDON.getAddonInfo( "name" )
ADDON_CACHE       = xbmc.translatePath( ADDON.getAddonInfo( "profile" ) )
CACHE_EXPIRE_TIME = float( ADDON.getSetting( "expiretime" ).replace( "0", ".5" ).replace( "25", "0" ) )
SCRIPT_REFRESH    = os.path.join( ADDON.getAddonInfo( 'path' ), "resources", "lib", "refresh.py" )

LangXBMC    = xbmc.getLocalizedString

import scraper

STRING_FOR_ALL = "[B]CONTENU accessible à TOUS[/B] - Cette émission peut être regardée partout dans le monde."

FAVOURITES_XML = os.path.join( ADDON_CACHE, "favourites.xml" )

G_GENRE     = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "utf-8" )
#ACTION_INFO = not bool( xbmc.getInfoLabel( "ListItem.Episode" ) )

WINDOW_PROGRESS = None
CONTROLS_PROGRESS = {}
def getDialogProgress():
    """global WINDOW_PROGRESS, CONTROLS_PROGRESS
    try:
        # get window
        WINDOW_PROGRESS = xbmcgui.Window( 10101 )
        # give window time to initialize
        xbmc.sleep( 100 )
        # get our controls http://wiki.xbmc.org/index.php?title=List_of_Built_In_Controls#DialogProgress.xml
        #CONTROLS_PROGRESS[ "heading" ] = WINDOW_PROGRESS.getControl( 1 )
        #CONTROLS_PROGRESS[ "line1" ]   = WINDOW_PROGRESS.getControl( 2 )
        #CONTROLS_PROGRESS[ "line2" ]   = WINDOW_PROGRESS.getControl( 3 )
        #CONTROLS_PROGRESS[ "line3" ]   = WINDOW_PROGRESS.getControl( 4 )
        #CONTROLS_PROGRESS[ "bar" ]     = WINDOW_PROGRESS.getControl( 20 )
    except TypeError:
        pass #Non-Existent Control
    except:
        print_exc()"""


def progressUpdate( **kwargs ):
    """OK = False
    if kwargs.get( "line2" ) and CONTROLS_PROGRESS.get( "line2" ):
        try:
            #CONTROLS_PROGRESS[ "line2" ].setLabel( kwargs[ "line2" ] )
            OK = True
        except: print_exc()

    if ( not OK ):
        getDialogProgress()"""


def getWatched():
    watched = {}
    try:
        watched_db = os.path.join( ADDON_CACHE, "watched.db" )
        if os.path.exists( watched_db ):
            watched = eval( open( watched_db ).read() )
    except:
        print_exc()
    return watched


def setWatched( strwatched, remove=False, all=False, refresh=True ):
    if not strwatched: return
    try:
        watched = {}
        watched_db = os.path.join( ADDON_CACHE, "watched.db" )
        if os.path.exists( watched_db ):
            watched = eval( open( watched_db ).read() )

        if not all:
            emissionId, episodeId = strwatched.split( "-" )
            watched[ emissionId ] = watched.get( emissionId ) or []
            # add to watched
            if episodeId not in watched[ emissionId ]:
                watched[ emissionId ].append( episodeId )

            # remove from watched
            if remove and episodeId in watched[ emissionId ]:
                del watched[ emissionId ][ watched[ emissionId ].index( episodeId ) ]

        else:
            emissionId = strwatched
            if remove:
                try: del watched[ emissionId ]
                except: pass
            else:
                all_id = scraper.getAllEpisodesId( emissionId )
                watched[ emissionId ] = all_id

        file( watched_db, "w" ).write( "%r" % watched )
    except:
        print_exc()
    if refresh:
        xbmc.executebuiltin( 'Container.Refresh' )


class Info:
    def __init__( self, *args, **kwargs ):
        # update dict with our formatted argv
        try: exec "self.__dict__.update(%s)" % ( sys.argv[ 2 ][ 1: ].replace( "&", ", " ).replace("%22",'"'), )
        except: print_exc()
        # update dict with custom kwargs
        self.__dict__.update( kwargs )

    def __getattr__( self, namespace ):
        return self[ namespace ]

    def __getitem__( self, namespace ):
        return self.get( namespace )

    def __setitem__( self, key, default="" ):
        self.__dict__[ key ] = default

    def get( self, key, default="" ):
        return self.__dict__.get( key, default )#.lower()

    def isempty( self ):
        return not bool( self.__dict__ )

    def IsTrue( self, key, default="false" ):
        return ( self.get( key, default ).lower() == "true" )


if re.search( '(GetCarrousel|"carrousel")', sys.argv[ 2 ] ):
    from GuiView import GuiView as viewtype
else:
    from PluginView import PluginView as viewtype

class Main( viewtype ):
    def __init__( self ):
        viewtype.__init__( self )

        self.args = Info()
        self.watched = getWatched()

        if self.args.isempty():
            self._add_directory_root()

        elif self.args.GetCarrousel:
             self._add_directory_carrousel( self.args.GetCarrousel )

        elif self.args.PID:
            start_player = True
            startoffset  = None
            if self.args.ChapterStartTimes:
                try:
                    chapters = [ "00:00:00" ] + self.args.ChapterStartTimes.split( "," )
                    selected = xbmcgui.Dialog().select( "Chapters Start Times",
                        [ "%s %i (%s)" % ( LangXBMC( 21396 ), i+1, c )  for i, c in enumerate( chapters ) ] )
                    if selected != -1:
                        h, m, s = chapters[ selected ].split( ":" )
                        startoffset = str( eval( "(%s*60*60)+(%s*60)+%s" % ( h, m, s ) ) )
                    else:
                        start_player = False
                except:
                    print_exc()
            if start_player:
                import vtelePlayer as player
                try: player.playVideo( self.args.PID, startoffset=startoffset )
                except: print_exc()

        elif self.args.emissionId:
             self._add_directory_episodes( self.args.emissionId )

        elif self.args.GetPageGenre:
             self._add_directory_genre( self.args.GetPageGenre )

        elif self.args.webbrowser:
            import webbrowser
            webbrowser.open( unquote_plus( self.args.webbrowser ) )

        elif self.args.addtofavourites or self.args.removefromfavourites:
            #add to my favourites
            favourite = unquote_plus( self.args.addtofavourites or self.args.removefromfavourites )
            if os.path.exists( FAVOURITES_XML ):
                favourites = open( FAVOURITES_XML ).read()
            else:
                favourites = '<favourites>\n</favourites>\n'
            if self.args.removefromfavourites or favourite not in favourites:
                if self.args.removefromfavourites:
                    favourites = favourites.replace( '  %s\n' % favourite, '' )
                    refresh = True
                else:
                    favourites = favourites.replace( '</favourites>', '  %s\n</favourites>' % favourite )
                    refresh = False
                file( FAVOURITES_XML, "w" ).write( favourites )
                if refresh:
                    if favourites == '<favourites>\n</favourites>\n':
                        try: os.remove( FAVOURITES_XML )
                        except: pass
                        xbmc.executebuiltin( 'Action(ParentDir)' )
                        xbmc.sleep( 1000 )
                    xbmc.executebuiltin( 'Container.Refresh' )

        elif self.args.setwatched or self.args.setunwatched:
            strwatched = self.args.setwatched or self.args.setunwatched
            setWatched( strwatched, bool( self.args.setunwatched ), self.args.all )

        elif self.args.category == "direct":
            self._add_directory_direct()

        elif self.args.category in [ "outdated", "repertoire", "plusrecents" ]:
            self._add_directory_emissions( self.args.category == "outdated" )

        elif self.args.category == "collection":
            self._add_directory_collection()

        elif self.args.category == "recherche":
            self._add_directory_search()

        elif self.args.category == "myfavourites":
            self._add_directory_favourites()

        elif self.args.category == "countries":
            self._add_directory_countries()

        else:
            #show home
            section = {
                "favoris":     "EpisodesFavoris",      #<type 'list'>
                "adecouvrir":  "SelectionADecouvrir",  #<type 'dict'>
                "carrousel":   "SelectionCarrousel",   #<type 'dict'>
                "plusrecents": "SelectionPlusRecents", #<type 'dict'>
                }.get( self.args.category )
            if section:
                self._add_directory_accueil( section )
            else:
                self._end_of_directory( False )

    def _add_directory_root( self ):
        OK = False
        live_str = "Impossible de récupérer l'émission en direct"
        live_img = "null"
        listitems = []
        try:
            uri = sys.argv[ 0 ]
            live = scraper.getLive( 'live' )
            #print live['emiCourNom'].encode("utf-8") + ' - ' + live['nomEmiSuiv'].encode("utf-8")
            
            if live['emiCourNom'] <> "":
                live_str = 'Présentement en onde, ' + live['emiCourNom'].encode("utf-8")
                live_img = 'DefaultAddonVisualization.png'
            else:
                #repls = ('sunday', 'dimanche'), ('monday', 'lundi'), ('tuesday', 'mardi'), ('wednesday', 'mercredi'), ('thursday', 'jeudi'), ('friday', 'vendredi'), ('saturday', 'samedi')
                #s = live['dateSuiv'].encode("utf-8").lower()
                #s = reduce(lambda a, kv: a.replace(*kv), repls, s)
                
                dateTimeSplitted = live['dateCompleteSuiv'].encode("utf-8").lower().split(' ');
                dateOnlySplitted = dateTimeSplitted[0].split('/');  #['2014', '10', '09']

                d0 = date(int(dateOnlySplitted[0]), int(dateOnlySplitted[1]), int(dateOnlySplitted[2]))
                d1 = date.today()
                delta = d0 - d1
                
                repls = (':00:00', ':00'), (':30:00', ':30')
                s = dateTimeSplitted[1]
                heures = reduce(lambda a, kv: a.replace(*kv), repls, s)
                
                textDate = ""
                d = delta.days
                
                if d == 0:
                    textDate = "aujourd'hui"
                elif d == 1:
                    textDate = "demain"
                elif d == 2:
                    textDate = "après demain"
                elif d > 2:
                    textDate = "dans " + str(d) + " jours"
                
                #a = datetime.strptime(dateSplitted[0], date_format)
                #a = datetime.strptime(time.strftime("%Y/%m/%d"), date_format)
                live_str = live['nomEmiSuiv'].encode("utf-8") + ', ' + textDate + ', ' + heures
                live_img = live['imgSuiv'].encode("utf-8")
             
        except:
            pass
                
        items = [
            #( ( uri, 'genres'      ), ( LangXBMC( 135 ),          '', 'DefaultAddonRepository.png'       ) ),
            ( ( uri, 'repertoire'  ), ( 'Émissions',          '', 'DefaultAddonSubtitles.png'        ) ),
            ( ( uri, 'direct'   ),    ( live_str,          '', 'http://image-v.com/tele/en-direct/large/' + live_img    ) ),
            #( ( uri, 'collection'  ), ( 'Collections',            '', 'DefaultMusicAlbums.png'           ) ),
            #( ( uri, 'adecouvrir'  ), ( 'À Découvrir',            '', 'DefaultMusicArtists.png'          ) ),
            #( ( uri, 'favoris'     ), ( 'Les Favoris Sur TouTV',  '', 'DefaultAddonScreensaver.png'      ) ),
            #( ( uri, 'carrousel'   ), ( 'Carrousel TouTV',        '', 'DefaultAddonVisualization.png'    ) ),
            #( ( uri, 'outdated'    ), ( 'A à Z + Outdated',       '', 'DefaultMusicYears.png'            ) ),
            #( ( uri, 'plusrecents' ), ( LangXBMC( 20387 ),        '', 'DefaultRecentlyAddedEpisodes.png' ) ),
            #( ( uri, 'recherche'   ), ( LangXBMC( 137 ),          '', 'DefaultAddonWebSkin.png'          ) ),
            ]
        if os.path.exists( FAVOURITES_XML ):
            fav = ( uri, 'myfavourites' ), ( 'Mes Favoris',       '', 'DefaultAddonScreensaver.png'      )
            items.append( fav )
        fanart = ADDON.getAddonInfo( "fanart" )

        for uri, item in items:
            listitem = xbmcgui.ListItem( *item )
            listitem.setProperty( "fanart_image", fanart )
            self._add_context_menu_items( [], listitem )
            url = '%s?category="%s"' % uri
            listitems.append( ( url, listitem, True ) )


        if listitems:
            OK = self._add_directory_items( listitems )
        # fake content movies to show container.foldername
        self._set_content( OK, "movies", False )

    def _add_directory_emissions( self, plusoutdated=False ):
        OK = False
        listitems = []
        try:
            full_emissions = scraper.getEmissionsWithFullDescription()
            emissions = full_emissions[ "Emissions" ]

            if plusoutdated:
                outdated = full_emissions[ "Outdated" ]
                for out in outdated:
                    out[ "premiered" ] = "(Outdated)"
                emissions += outdated

            getDialogProgress()

            #emissions.append({'vod': '*', 'nom': '911', 'uid': '219', 'dateDiffusion': '', 'nomListe': '911', 'live': 'yes', 'webtele': 'yes'})

            totals = len( emissions )
             
            for emission in emissions:
                print emission
                genre = emission[ "source" ]
                try: genre = genre[ "title" ]
                except: pass
                filter = self.args.filter
                if self.args.genre and filter == "byGenre" and self.args.genre != genre.encode( "utf-8" ):
                    totals -= 1
                    continue
                country = emission.get( "Country" ) or emission.get( "Pays" ) or ""
                if self.args.country and filter == "byCountry" and self.args.country != country.encode( "utf-8" ):
                    totals -= 1
                    continue

                #set emission base infos
                title = emission.get( "title" ) #or emission[ "nomListe" ]
                #fix title for context menu
                emission[ "Title" ] = title
                self._progress_update( title )

                emissionId = emission.get( "slug" )
                
                watched = len( self.watched.get( str( emissionId ) ) or [] )
                NombreEpisodes = int( emission.get( "NombreEpisodes" ) or "1" )
                unwatched = NombreEpisodes - watched
                outdated = emission.get( "premiered" ) == "(Outdated)"
                if outdated:
                    unwatched = 0
                    NombreEpisodes = 0

                #year = ( emission.get( "AnneeProduction" ) or emission[ "Year" ] or "0" )
                #GeoTargeting = emission.get( "IsGeolocalise" ) or emission[ "GeoTargeting" ]

                infoLabels = {
                    "tvshowtitle": title,
                    "title":       title,
                    #"genre":       genre,
                    #"year":        int( year.split()[ 0 ] ),
                    "tagline":     emission.get( "source" ),#( STRING_FOR_ALL, "" )[ bool( GeoTargeting ) ],
                    #"duration":    emission.get( "CategorieDuree" ) or "",
                    #"episode":     4,#NombreEpisodes,
                    "season":      len(emission.get( "seasons" )),
                    "plot":        html2text.html2text(emission[ "og"]['description']) or "",
                    #"premiered":   emission.get( "premiered" ) or "",
                    }
                thumb = "" #emission[ "ImagePromoNormalK" ] or ""
                
                try: fanart = emission[ "image" ]['url']
                except: fanart = "" #all request keys error

                #if not infoLabels[ "premiered" ]:
                #    infoLabels[ "premiered" ] = scraper.getPremiered( emissionId )

                infoLabels[ "plot" ] = infoLabels[ "plot" ].encode( "utf-8" )
                #if not GeoTargeting:
                #    try:
                #        if infoLabels[ "plot" ]: infoLabels[ "plot" ] += "[CR][CR]"
                #        infoLabels[ "plot" ] +=  STRING_FOR_ALL
                #    except:
                #        pass

                plot_plus = html2text.html2text(emission[ "og"]['description'] )
                #if plot_plus: infoLabels[ "plot" ] = plot_plus.encode( "utf-8" ) + "[CR][CR]" + infoLabels[ "plot" ]

                # set listitem
                listitem = xbmcgui.ListItem( title, "", "DefaultTVShows.png", thumb )
                listitem.setProperty( "fanart_image", fanart )

                listitem.setProperty( "WatchedEpisodes", str( watched ) )
                listitem.setProperty( "UnWatchedEpisodes", str( unwatched ) )

                playCount = ( 0, 1 )[ not unwatched and not outdated ]
                overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_WATCHED )[ playCount ]
                infoLabels.update( { "playCount": playCount, "overlay": overlay } )

                listitem.setInfo( "Video", infoLabels )
                self._add_emission_context_menu( emission, listitem, bool( playCount ), outdated )

                url = '%s?emissionId="%s"' % ( sys.argv[ 0 ], emissionId )
                #listitems.append( ( url, listitem, bool( NombreEpisodes ) ) )
                OK = self._add_directory_item( url, listitem, bool( NombreEpisodes ), totals )
        except:
            print_exc()

        #if listitems:
        #    OK = self._add_directory_items( listitems )
        OK = OK or bool( self.args.country )
        self._set_content( OK, "tvshows" )
        
    #PARTIE DE CHARGEMENT PAR SAISONS
    def _add_directory_episodes( self, uId ):
        OK = False
        listitems = []
        nbSaisons = 0
        try:
            # obtenir les saisons
            saisons = scraper.getSaisons( uId )
            #print saisons
            for saison in saisons['seasons']:
                nbSaisons = nbSaisons + 1
                #print saison['nom'] + " - saison"
                # obtenir les épisodes
                #episodes = scraper.getSaison( uId, saison['slug'] )
                getDialogProgress()
                totals = len( saison )
                for episode in saison['episodes']:
                    # set listitem
                    #if 'playlist' in episode:
                    #episode[ "SeasonNumber" ] = "2"
                    #episode[ "titre" ] = saison['title'] + " - " + episode[ "title" ]
                    url, listitem = self._get_episode_listitem( episode, saison, False )
                    #else:
                    #    OK = self._add_directory_emissions( False )
                    #listitems.append( ( url, listitem, False ) )
                    OK = self._add_directory_item( url, listitem, False, totals )

            #if nbSaisons == 0:
            #    episodes = scraper.getPageEmission( uId )
            #    getDialogProgress()
            #    totals = len( episodes )
            #    for episode in episodes:
            #        nbSaisons = nbSaisons + 1
            #        # set listitem
            #        #if 'playlist' in episode:
            #        episode[ "SeasonNumber" ] = "0"
            #        #episode[ "titre" ] = saison['nom'] + " - " + episode[ "titre" ]
            #        url, listitem = self._get_episode_listitem( episode, None, False )
            #        #else:
            #        #    OK = self._add_directory_emissions( False )
            #        #listitems.append( ( url, listitem, False ) )
            #        OK = self._add_directory_item( url, listitem, False, totals )
            #if nbSaisons == 0:    
            #    dialog = xbmcgui.Dialog()
            #    dialog.ok("Émission non disponible", "Malheureusement, aucune vidéo n'est disponible","pour cette émission.")

        except:
            print_exc()

        #if listitems:
        #    OK = self._add_directory_items( listitems )
        if not OK:#elif ACTION_INFO:
            xbmc.executebuiltin( "Action(info)" )
            return
        self._set_content( OK, "episodes" )
   
    def _add_directory_direct( self ):
        self._set_content( False, "episodes" )
        xbmc.Player().play("rtmp://cp101680.live.edgefcs.net/live/livev_1@50832 swfUrl=http://admin.brightcove.com/viewer/us20121128.1314/federatedVideoUI/BrightcovePlayer.swf pageurl=http://vtele.ca/en-direct/ app=live swfVfy=1 live=1")
        #video_json = getVideo( '4865714967001' )
        #print video_json
        #xbmc.Player().play(video_json["videoFullLength"]["url"] + "/manifest.f4m?videoId=4865714967001&lineUpId=&pubId=618566855001&playerId=4697217677001&affiliateId=&g=JTILQWBFROJK&hdcore=3.4.0")
        #xbmc.Player().play("rtmp://cp101680.live.edgefcs.net/live/livev_1@50832 swfUrl=http://admin.brightcove.com/viewer/us20160520.1717/BrightcoveBootloader.swf pageurl=http://vtele.ca/en-direct/ app=live swfVfy=1 live=1")
   
        
    def _progress_update( self, line2 ):
        progressUpdate( line2=line2 )

    def _get_episode_listitem( self, episode, saison, gototvshow=True, genreTitle=None ):
        title = saison[ "title" ] + ' - ' +episode['contents'][0][ "title" ]
        #if title.strip( "#" ).isdigit():
        #    title = episode[ "Show" ] + " - " + episode[ "SeasonAndEpisodeLong" ]
        #episode[ "Title" ] = title
        #
        self._progress_update( episode[ "title" ] )
        thumb = episode['contents'][0][ "image" ]['url-page-header'] or ""
        listitem = xbmcgui.ListItem( episode[ "title" ], "", "DefaultTVShows.png", thumb )

        #fanart = episode[ "ImageBackground" ] or episode[ "ImagePlayerLargeA" ]
        #listitem.setProperty( "fanart_image", fanart or "" )
        listitem.setProperty( "thumb", thumb )#used in carrousel mode

        #set property for player set watched
        strwatched = "%s-%s" % ( str( episode.get( "CategoryId" ) ), episode['contents'][0][ "id" ] )
        listitem.setProperty( "strwatched", strwatched )
        listitem.setProperty( "PID", episode['contents'][0][ "brightcoveId" ] )

        #genreTitle = genreTitle or G_GENRE or episode[ "GenreTitle" ] or "" # pas bon tout le temps pour episode[ "GenreTitle" ]
        infoLabels = {
            "tvshowtitle": episode[ "title" ],
            "title":       title,
            #"genre":       genreTitle,
            "plot":        html2text.html2text(episode['contents'][0]['description']) or "",
            "season":      saison[ "seasonNumber" ] or -1
            #"episode":     episode[ "EpisodeNumber" ] or -1,
            #"year":        int( episode[ "Year" ] or "0" ),
            #"Aired":       episode[ "AirDateLongString" ] or "",
            #"mpaa":        episode[ "Rating" ] or "",
            #"duration":    episode[ "LengthString" ] or "",
            #"studio":      episode[ "Copyright" ] or "",
            #"castandrole": scraper.setCastAndRole( episode ) or [],
            #"writer":      episode[ "PeopleWriter" ] or episode[ "PeopleAuthor" ] or "",
            #"director":    episode[ "PeopleDirector" ] or "",
            }
        # set overlay watched
        watched = str( episode['contents'][0][ "id" ] ) in self.watched.get( str( episode.get( "CategoryId" ) ), [] )
        overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_WATCHED )[ watched ]
        infoLabels.update( { "playCount": ( 0, 1 )[ watched ], "overlay": overlay } )

        listitem.setInfo( "Video", infoLabels )
        self._add_episode_context_menu( episode, listitem, gototvshow, watched )

        url = '%s?PID="%s"' % ( sys.argv[ 0 ], episode['contents'][0][ "brightcoveId" ] )

        return url, listitem
    '''
    ' Section de gestion des menus
    '''
    def _add_emission_context_menu( self, emission, listitem, watched=False, hidewatched=False ):

        try:
            c_items = [ ( LangXBMC( 20351 ), "Action(Info)" ) ]

            if emission.get( "slug" ):
                #add to my favoris
                format = '<favourite tvshowtitle="%s" emissionId="%s" />'
                favourite = format % ( emission[ "title" ], str( emission[ "slug" ] ), )
                uri = '%s?addtofavourites=\"%s\"' % ( sys.argv[ 0 ], quote_plus( favourite.encode( "utf-8" ) ) )

                if self.args.category == "myfavourites":
                    c_items += [ ( "Retirer de mes favoris", "RunPlugin(%s)" % uri.replace( "addto", "removefrom" ) ) ]
                else:
                    c_items += [ ( "Ajouter à mes favoris vtele", "RunPlugin(%s)" % uri ) ]

            #
            if not hidewatched:
                if not watched:
                    i_label, action = 16103, "setwatched"
                else:
                    i_label, action = 16104, "setunwatched"
                uri = '%s?%s="%s"&all=True' % ( sys.argv[ 0 ], action, str( emission[ "slug" ] ) )
                c_items += [ ( LangXBMC( i_label ), "RunPlugin(%s)" % uri ) ]
            '''
            if emission.get( "Url" ):
                # view emission on sitequote_plus
                try:
                    url = "%s/%s" % ( scraper.TOU_TV_URL, emission[ "Url" ].strip( "/" ) )
                    uri = '%s?webbrowser=\"%s\"' % ( sys.argv[ 0 ], quote_plus( url ) )
                    c_items += [ ( "Visit Emission", "RunPlugin(%s)" % uri ) ]
                except:
                    pass
'''
            self._add_context_menu_items( c_items, listitem )
        except:
            print_exc()

    def _add_episode_context_menu( self, episode, listitem, gototvshow=True, watched=False ):
        c_items = []
        try:
            uri = '%s?PID=\"%s\"' % ( sys.argv[ 0 ], episode['contents'][0][ "brightcoveId" ] )
            c_items += [ ( LangXBMC( 13358 ), "RunPlugin(%s)" % uri ) ]

            if episode.get( "ChapterStartTimes" ):
                uri = '%s?PID=\"%s\"&ChapterStartTimes=\"%s\"' % ( sys.argv[ 0 ], episode[ "PID" ], episode[ "ChapterStartTimes" ] )
                c_items += [ ( "Chapters", "RunPlugin(%s)" % uri ) ]

            c_items += [ ( LangXBMC( 20352 ), "Action(Info)" ) ]

            if episode.get( "CategoryId" ):
                if gototvshow:
                    uri = '%s?emissionId=\"%s\"' % ( sys.argv[ 0 ], str( episode[ "CategoryId" ] ) )
                    c_items += [ ( LangXBMC( 20384 ).replace( "une ", "" ), "Container.Update(%s)" % uri ) ]

                #add to my favoris
                format = '<favourite tvshowtitle="%s" title="%s" emissionId="%s" episodeId="%s" />'
                favourite = format % ( episode[ "Show" ], episode[ "Title" ], str( episode[ "CategoryId" ] ), str( episode[ "Id" ] ) )
                uri = '%s?addtofavourites=\"%s\"' % ( sys.argv[ 0 ], quote_plus( favourite.encode( "utf-8" ) ) )

                if self.args.category == "myfavourites":
                    c_items += [ ( "Retirer de mes favoris", "RunPlugin(%s)" % uri.replace( "addto", "removefrom" ) ) ]
                else:
                    c_items += [ ( "Ajouter à mes favoris vtele", "RunPlugin(%s)" % uri ) ]
            #
            if not watched:
                i_label, action = 16103, "setwatched"
            else:
                i_label, action = 16104, "setunwatched"
            uri = '%s?%s="%s"' % ( sys.argv[ 0 ], action, listitem.getProperty( "strwatched" ) )
            c_items += [ ( LangXBMC( i_label ), "RunPlugin(%s)" % uri ) ]

            self._add_context_menu_items( c_items, listitem )
        except:
            print_exc()

    def _add_context_menu_items( self, c_items, listitem, replaceItems=True ):
        c_items += [ ( "Refresh Emissions", "RunScript(%s)" % SCRIPT_REFRESH ) ]

        #c_items += [ ( "Go to Root", "Container.Update(%s,replace)" % ( sys.argv[ 0 ], ) ) ]

        c_items += [ ( LangXBMC( 1045 ), "Addon.OpenSettings(plugin.video.vtele)" ) ]

        listitem.addContextMenuItems( c_items, replaceItems )


if ( __name__ == "__main__" ):
    Main()
