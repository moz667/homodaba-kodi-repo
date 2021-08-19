"""
Ejemplo de addon para la integracion de kodi con homodaba.

Infinitas gracias a romanvm ya que en este ejemplo es en el que me he basado:
https://github.com/romanvm/plugin.video.example
"""

import sys

# Python3:
try:
    from urllib.parse import urlencode, parse_qsl
# Python2:
except ImportError:
    from urlparse import parse_qsl
    from urllib import urlencode

import xbmc, xbmcaddon, xbmcgui, xbmcplugin

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
    share_protocol=addon.getSetting('homodaba_share_protocol')
)

SEARCH_CAT = "* 0 - BUSCAR *"
LAST_MOVIES_CAT = "* 1 - NUEVAS *"

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
    xbmcplugin.setPluginCategory(_HANDLE, 'Lista de categorias de HDB')
    xbmcplugin.setContent(_HANDLE, 'videos')

    # Get video categories
    categories = HDB_API.get_categories()

    # Agregamos las categorias manuales
    categories = MANUAL_CATS + categories

    # Iterate through categories
    for category in categories:
        list_item = xbmcgui.ListItem(label=category)
        list_item.setInfo('video', {
            'title': category,
            'genre': category,
            'mediatype': 'video'
        })
        url = get_url(action='listing', category=category)
        is_folder = True
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_HANDLE)

def get_user_input():  
    kb = xbmc.Keyboard('', 'Introduce los terminos a buscar')
    kb.doModal() # Onscreen keyboard appears
    if not kb.isConfirmed():
        return
    query = kb.getText() # User input
    return query

def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    videos = []

    if category == SEARCH_CAT:
        query = get_user_input() # User input via onscreen keyboard
        if query:
            videos = HDB_API.search_videos(query=query)
            
    elif category == LAST_MOVIES_CAT:
        videos = HDB_API.last_movies()
    else:
        # Get the list of videos in the category.
        videos = HDB_API.search_videos(tag=category)
    
    if len(videos) > 0:
        xbmcplugin.setPluginCategory(_HANDLE, category)
        xbmcplugin.setContent(_HANDLE, 'videos')
        populate_list(videos)
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(_HANDLE)


def populate_list(videos):
    # Iterate through videos.
    for video in videos:
        list_item = xbmcgui.ListItem(label=video['title'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {
            "genre": video['genre'],
            "country": video['country'],
            "year": video['year'],
            "rating": video['rating'],
            "cast": video['cast'],
            "director": video['director'],
            "mpaa": video['mpaa'],
            "plot": video['plot'],
            "title": video['title'],
            "originaltitle": video['originaltitle'],
            "writer": video['writer'],
            "tag": video['tag'],
            "imdbnumber": video['imdbnumber'],
            'mediatype': 'video'
        })

        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({
            'thumb': video['thumb'], 
            'icon': video['thumb'], 
            'poster': video['poster'], 
        })

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

