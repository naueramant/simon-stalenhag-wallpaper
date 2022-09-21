#!/usr/bin/env python3

import re, os, sys, random, json, argparse
from enum import Enum
from urllib import request
from pathlib import Path

BASE = 'http://www.simonstalenhag.se/'

class Pages(Enum):
    ALL = ''
    STEEL_MEADOW = BASE
    PALEOART = f'{BASE}paleo.html'
    COMMISIONS = f'{BASE}other.html'
    TALES_FROM_THE_LOOP = f'{BASE}tftl.html'
    THINGS_FROM_THE_FLOOD = f'{BASE}tftf.html'
    THE_ELECTRIC_STATE = f'{BASE}es.html'
    LABYRINTH = f'{BASE}labyrinth.html'

class Collections(Enum):
    ALL = 'ALL'
    STEEL = 'STEEL_MEADOW'
    PALEO = 'PALEOART'
    OTHERS = 'COMMISIONS'
    TALES = 'TALES_FROM_THE_LOOP'
    THINGS = 'THINGS_FROM_THE_FLOOD'
    ELECTRIC = 'THE_ELECTRIC_STATE'
    LAB = 'LABYRINTH'

# OS values

PLATFORM = sys.platform
IMAGES_DIR = os.path.expanduser('~|Pictures|Stålenhag|'.replace('|', os.sep))
CONFIG_DIR = os.path.expanduser('~|.stalenhag|'.replace('|', os.sep))
CONFIG_FILE = os.path.expanduser('~|.stalenhag|config.json'.replace('|', os.sep))
if 'win' not in PLATFORM:
    DESKTOP = os.environ["DESKTOP_SESSION"]
    import dbus
else:
    import ctypes

def check_dirs():
    if not os.path.isdir(IMAGES_DIR):
        os.mkdir(IMAGES_DIR[:-1])
    if not os.path.isdir(CONFIG_DIR):
        os.mkdir(CONFIG_DIR[:-1])
    if not os.path.isfile(CONFIG_FILE):
        setup_config()

def setup_config():

    c = {
        'current': '',
        'favorites': [],
        'collections': ['ALL']
    }

    save_config(c)

def get_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def clear_config():
    try:
        os.remove(CONFIG_FILE)
    except FileNotFoundError:
        return

def save_config(config: dict):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def local_exists(filename):
    return os.path.isfile(IMAGES_DIR + filename)

def get_images_list(prints=False):
    collections = getCollections()
    if prints:
        print(f'Collections: {getCollectionNames(collections)}')
        print('-----------------------------------')
    urls = [page.value for _, page in Pages.__members__.items()][1:] if collections[0] == Pages.ALL else [collection.value for collection in collections]
    images = []
    for url in urls:
        contents = request.urlopen(url).read()
        search = r'(?:bilder|paleo|other|tftl|tftf)big\/[a-zA-Z0-9_]*\.jpg'
        collectionImages = re.findall(search, str(contents))
        images.extend(collectionImages)

    return list(set(images))

def download_image(image):
    url = f'{BASE}{image}'
    request.urlretrieve(url, IMAGES_DIR + image.replace('/', '-'))

def get_random_local_image(favorites=False):
    images = []
    if not favorites:
        images = os.listdir(IMAGES_DIR)
        images = list(filter(lambda s: os.path.isfile(IMAGES_DIR + s), images))
        images = list(filter(lambda s: s.endswith('.jpg'), images))
    else:
        config = get_config()
        images = list(filter(lambda s:  config['current'] not in s, config['favorites']))

    if images:
        return IMAGES_DIR + random.choice(images)
    else:
        return None

def get_random_image():
    check_dirs()

    images = get_images_list()
    name = random.choice(images)

    if not local_exists(name):
        download_image(name)

    return IMAGES_DIR + name.replace('/', '-')

def get_filtered_image(filter_term):
    check_dirs()
    images = get_images_list()
    images_filtered = list(filter(lambda name: filter_term in name, images))
    if len(images_filtered) > 0:
        print("Found " + str(len(images_filtered)) + " images.")
        name = random.choice(images_filtered)
        if not local_exists(name):
            download_image(name)
        return IMAGES_DIR + name.replace('/', '-')
    else:
        print("No images found with search term: " + filter_term)

def setCollections(collections):
    check_dirs()
    local = get_config()
    local['collections'] = collections
    save_config(local)

def getCollections():
    check_dirs()
    collections = get_config()['collections']
    if any([collection == Collections.ALL.name for collection in collections]):
        return [Pages.ALL]
    return [Pages[Collections[collection].value] for collection in collections]

def getCollectionNames(collections=None):
    if not collections:
        collections = getCollections()
    return ", ".join([collection.name.lower().capitalize().replace("_", " ") for collection in collections])

def get_all_images():
    check_dirs()

    images = get_images_list()

    print('Found', len(images), 'images')

    index = 1
    for name in images:
        print(f'{index}: {name} --> Downloading', end='')

        try:
            download_image(name)
            print(f'\r{index}: {name} --> Success    ', end='')

        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print(e)
            # print(f'\r{index}: {name} --> Failed     ', end='')

        print('')
        index += 1

jscript = """
var allDesktops = desktops();
print (allDesktops);
for (i=0;i<allDesktops.length;i++) {
    d = allDesktops[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
    d.writeConfig("Image", "file://%s")
}
"""

def save_current_background(path):
    c = get_config()
    c['current'] = path.replace(IMAGES_DIR, '')
    save_config(c)

def set_background(path):
    if path:
        save_current_background(path)
        print('Setting image: ', path)

        if 'win' in PLATFORM:
            path = Path(path).parts
            ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.join(*path), 0)
        elif DESKTOP  == 'plasma':
            bus = dbus.SessionBus()
            plasma = dbus.Interface(bus.get_object('org.kde.plasmashell', '/PlasmaShell'), dbus_interface='org.kde.PlasmaShell')
            plasma.evaluateScript(jscript % path)
        else:
            os.system('gsettings set org.gnome.desktop.background picture-uri file://' + path)
            os.system('gsettings set org.gnome.desktop.background picture-uri-dark file://' + path)
    else:
        print('Failed to find a new image')

def save_to_favorites():
    c = get_config()
    favorites = c['favorites']
    current = c['current']
    if current not in favorites:
        favorites.append(current)
        save_config(c)
    else:
        print("This wallpaper is already favorited")

def clear_favorites():
    c = get_config()
    c['favorites'] = []
    save_config(c)

def list_wallpapers(favorites=False):
    if favorites:
        print('Favorites:')
        c = get_config()
        fav = c['favorites']
        if len(fav) > 0:
            for img in c['favorites']:
                print('Image name: ' + img)
        else:
            print('No favorites. Use "stalenhag save" to save current background.')
    else:
        print(f'Wallpapers online - ', end='')
        for w in get_images_list(prints=True):
            print("Image name: " + w)



parser = argparse.ArgumentParser(description='Set and manage Simon Stålenhag wallpaper.', prog='stalenhag', epilog="Cheers to Simon for making his awesome art available!")
parser.add_argument('-a', '--all', help='Download all images to local directory', action='store_true')
parser.add_argument('--timerstop', help='Stop Systemd timer', action='store_true')
parser.add_argument('--timerstart', help='Start Systemd timer', action='store_true')
parser.add_argument('-s', '--save', help='Save current wallpaper to favorites', action='store_true')
parser.add_argument('-c', '--clear', help='Clear favorites list', action='store_true')
parser.add_argument('-l', '--list', help='List wallpapers online', action='store_true')
parser.add_argument( '--listfav', help='List favorite wallpapers', action='store_true')
parser.add_argument( '-f', '--filter', help='Filter/search for specific wallpapers', action='store')
parser.add_argument( '--collections', nargs='*', help='Set the default base of images')
parser.add_argument( '--fav', '--favorite', help='Set random wallpaper from favorites', action='store_true')
parser.add_argument( '--clearconfig' , help='Remove config file', action='store_true')

windows_bundled = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def run():
    if windows_bundled:
        parser.print_usage()
        response = input('Set arguments: ')
        try:
            args = parser.parse_args(response.split())
        except:
            return

    else:
        args = parser.parse_args()

    # handle args
    if args.all:
        get_all_images()
    elif args.timerstop:
        if 'win' in PLATFORM:
            print('System timing is not implemented for Windows')
            return()
        print('Stopping systemd timer')
        os.system("systemctl stop --user stalenhag.service stalenhag.timer")
        os.system("systemctl disable --user stalenhag.service stalenhag.timer")
    elif args.timerstart:
        if 'win' in PLATFORM:
            print('System timing is not implemented for Windows')
            return()
        print('Starting systemd timer')
        os.system("systemctl enable --user stalenhag.service stalenhag.timer")
        os.system("systemctl start --user stalenhag.service stalenhag.timer")
    elif args.save:
        print('Saving current background to favorites')
        save_to_favorites()
    elif args.clear:
        print('Clearing favorites')
        clear_favorites()
    elif args.listfav:
        list_wallpapers(favorites=True)
    elif args.list:
        list_wallpapers()
    elif args.fav:
        print('Setting background from favorites')
        img = get_random_local_image(favorites=True)
        set_background(img)
    elif args.filter:
            img = get_filtered_image(args.filter)
            set_background(img)
    elif args.clearconfig:
        clear_config()
    elif args.collections is not None:
        collections = [collection.upper() for collection in args.collections]
        collection_names = [name for name, _ in Collections.__members__.items()]
        error = len(collections) == 0 or not all([collection in collection_names for collection in collections])
        if error:
            print('Please choose a collections from: ')
            for name in collection_names:
                print(f'\t{name.lower()}')
            print(f'Current collections: {getCollectionNames()}')
        else:
            setCollections(collections)
            print(f'Wallpapers will be downloaded from: {getCollectionNames()}')
    # set background
    if not any(vars(args).values()):
        try:
            img = get_random_image()
        except:
            img = get_random_local_image()

        set_background(img)
try:
    run()
    while windows_bundled:
        run()
except Exception as e:
    response = input(f'Failed with: {e}\nPress any button to quit.')


