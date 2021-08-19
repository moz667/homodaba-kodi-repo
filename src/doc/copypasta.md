```python
"""
Ejemplo de addon para la integracion de kodi con homodaba.

Infinitas gracias a romanvm ya que en este ejemplo es en el que me he basado:
https://github.com/romanvm/plugin.video.example
"""

import sys

# Python3:
try:
    from urllib.parse import parse_qsl
# Python2:
except ImportError:
    from urlparse import parse_qsl

import xbmcaddon, xbmcgui, xbmcplugin

from resources.lib.homodaba import HDBApi

ADDON_ID = "plugin.homodaba.movies"

# Get the plugin url in plugin:// notation.
_URL = sys.argv[0]
# Get the plugin handle as an integer number.
_HANDLE = int(sys.argv[1])

addon = xbmcaddon.Addon(id=ADDON_ID)

HDB_API = HDBApi(
    url_base=addon.getSetting('homodaba_url'),
    username=addon.getSetting('homodaba_username'),
    api_key=addon.getSetting('homodaba_api_key'),
    protocol=addon.getSetting('homodaba_share_protocol')
)

SEARCH_CAT = "* BUSCAR *"
LAST_MOVIES_CAT = "* NUEVAS *"

MANUAL_CATS = [SEARCH_CAT, LAST_MOVIES_CAT]

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{}?{}'.format(_URL, urlencode(kwargs))

def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_HANDLE, 'My Video Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')

    # Get video categories
    categories = HDB_API.get_categories()

    categories = MANUAL_CATS + categories

    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        """
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
                          'icon': VIDEOS[category][0]['thumb'],
                          'fanart': VIDEOS[category][0]['thumb']})
        """
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_HANDLE, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')

    if category == SEARCH_CAT:
        # TODO: search
    elif category == LAST_MOVIES_CAT:
        # TODO: last movies cat
    else:
        # Get the list of videos in the category.
        populate_list(
            HDB_API.search_videos(tag=category)
        )
    
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)


def populate_list(videos):
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['title'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': video['title'],
                                    # 'genre': video['genre'],
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4
        url = get_url(action='play', video=video['file'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            print("[%s] Parametro invalido '%s'." % (ADDON_ID, paramstring))
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])

"""
https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14

Info label	Description
genre	string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
country	string (Germany) or list of strings (["Germany", "Italy", "France"])
year	integer (2009)
episode	integer (4)
season	integer (1)
sortepisode	integer (4)
sortseason	integer (1)
episodeguide	string (Episode guide)
showlink	string (Battlestar Galactica) or list of strings (["Battlestar Galactica", "Caprica"])
top250	integer (192)
setid	integer (14)
tracknumber	integer (3)
rating	float (6.4) - range is 0..10
userrating	integer (9) - range is 1..10 (0 to reset)
watched	deprecated - use playcount instead
playcount	integer (2) - number of times this item has been played
overlay	integer (2) - range is 0..7. See Overlay icon types for values
cast	list (["Michal C. Hall","Jennifer Carpenter"]) - if provided a list of tuples cast will be interpreted as castandrole
castandrole	list of tuples ([("Michael C. Hall","Dexter"),("Jennifer Carpenter","Debra")])
director	string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
mpaa	string (PG-13)
plot	string (Long Description)
plotoutline	string (Short Description)
title	string (Big Fan)
originaltitle	string (Big Fan)
sorttitle	string (Big Fan)
duration	integer (245) - duration in seconds
studio	string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
tagline	string (An awesome movie) - short description of movie
writer	string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
tvshowtitle	string (Heroes)
premiered	string (2005-03-04)
status	string (Continuing) - status of a TVshow
set	string (Batman Collection) - name of the collection
setoverview	string (All Batman movies) - overview of the collection
tag	string (cult) or list of strings (["cult", "documentary", "best movies"]) - movie tag
imdbnumber	string (tt0110293) - IMDb code
code	string (101) - Production code
aired	string (2008-12-07)
credits	string (Andy Kaufman) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]) - writing credits
lastplayed	string (Y-m-d h:m:s = 2009-04-05 23:16:04)
album	string (The Joshua Tree)
artist	list (['U2'])
votes	string (12345 votes)
path	string (/home/user/movie.avi)
trailer	string (/home/user/trailer.avi)
dateadded	string (Y-m-d h:m:s = 2009-04-05 23:16:04)
mediatype	string - "video", "movie", "tvshow", "season", "episode" or "musicvideo"
dbid	integer (23) - Only add this for items which are part of the local db. You also need to set the correct 'mediatype'!
"""

```