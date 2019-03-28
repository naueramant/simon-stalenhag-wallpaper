#!/usr/bin/env python3

import re, os, sys, random, dbus, json
from urllib import request

BASE = 'https://www.simonstalenhag.se/'
IMAGES_DIR = os.path.expanduser('~/Pictures/Stålenhag/')
CONFIG_DIR = os.path.expanduser('~/.stalenhag/')
CONFIG_FILE = os.path.expanduser('~/.stalenhag/config.json')
DESKTOP = os.environ["DESKTOP_SESSION"]

def check_dirs():
    if not os.path.isdir(IMAGES_DIR):
        os.mkdir(IMAGES_DIR[:-1])
    if not os.path.isdir(CONFIG_DIR):
        os.mkdir(CONFIG_DIR[:-1])
        setup_config()

def setup_config():

    c = {
        'current': '',
        'favorites': []
    }

    save_config(c)

def get_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config: dict):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def local_exists(filename):
    return os.path.isfile(IMAGES_DIR + filename)

def get_images_list():
    contents = request.urlopen(BASE).read()
    images = re.findall(r'bilderbig\/[a-zA-Z0-9_]*\.jpg', str(contents))
    return list(set(images))

def download_image(name):
    request.urlretrieve(BASE + 'bilderbig/' + name, IMAGES_DIR + name)

def get_random_local_image(favorites=False):

    images = []

    if not favorites:
        images = os.listdir(IMAGES_DIR)
        images = list(filter(lambda s: os.path.isfile(IMAGES_DIR + s), images))
        images = list(filter(lambda s: s.endswith('.jpg'), images))
    else:
        config = get_config()
        images = list(filter(lambda s:  s != config['current'], config['favorites']))
    
    if images:
        return IMAGES_DIR + random.choice(images)
    else:
        return None

def get_random_image():
    check_dirs()
    
    images = get_images_list()
    img = random.choice(images)
    name = img[10:]

    if not local_exists(name):
        download_image(name)

    return IMAGES_DIR + name
    
def get_all_images():
    check_dirs()

    images = get_images_list()

    print('Found', len(images), 'images')

    index = 1
    for img in images:
        name = img[10:]
        print(str(index) + ')', name, end='')
        
        try:
            download_image(name)

        except KeyboardInterrupt:
            exit()    
        except:
            print('\r-->', str(index) + ')', name, 'FAILED', end='')
    
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
    img = re.findall(r'.*\/([a-zA-Z0-9_]*\.jpg)', path)[0]
    c['current'] = img
    save_config(c)

def set_background(path):
    if path:
        save_current_background(path)
        print('Setting image: ', path)

        if DESKTOP == 'plasma':
            bus = dbus.SessionBus()
            plasma = dbus.Interface(bus.get_object('org.kde.plasmashell', '/PlasmaShell'), dbus_interface='org.kde.PlasmaShell')
            plasma.evaluateScript(jscript % path)
        else:
            os.system('gsettings set org.gnome.desktop.background picture-uri file://' + path)
    else:
        print('Failed to find a new image')

def save_to_favorites():
    c = get_config()
    favorites = c['favorites']
    current = c['current']
    favorites.append(current)
    save_config(c)

def clear_favorites():
    c = get_config()
    c['favorites'] = []
    save_config(c)

def list_favorites():
    c = get_config()
    fav = c['favorites']
    if len(fav) > 0:
        for img in c['favorites']:
            print('Image name: ' + img)
    else:
        print('No favorites. Use "stalenhag save" to save current background.')

def helper():
    print('''
    Usage: stalenhag [OPTION]
    Set and manage favorite Simon Stålenhag wallpapers.

        stalenhag                   Set random wallpaper

        all                         Download all images to local directory
        timerstart, timerstart      Start or stop Systemd timer
        save                        Save current wallpaper to favorites
        list                        List favorite wallpapers
        clear                       Clear favorites list.

        -f                          Set random wallpaper from favorites
        -h, --help                  Get help!
    ''')


if __name__ == "__main__":

    img = None

    if len(sys.argv) == 2:
        if sys.argv[1] == 'all':
            get_all_images()
        elif sys.argv[1] == 'timerstop':
            print('Stopping systemd timer')
            os.system("systemctl stop --user stalenhag.service stalenhag.timer")
            os.system("systemctl disable --user stalenhag.service stalenhag.timer")
        elif sys.argv[1] == 'timerstart':
            print('Starting systemd timer')
            os.system("systemctl enable --user stalenhag.service stalenhag.timer")
            os.system("systemctl start --user stalenhag.service stalenhag.timer")
        elif sys.argv[1] == 'save':
            print('Saving current background to favorites')
            save_to_favorites()
        elif sys.argv[1] == 'clear':
            print('Clearing favorites')
            clear_favorites()
        elif sys.argv[1] == 'list':
            print('Favorites:')
            list_favorites()
        elif sys.argv[1] == '-f':
            print('Setting background from favorites')
            img = get_random_local_image(favorites=True)
            set_background(img)
        elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
            helper()
        else:
            helper()
    elif len(sys.argv) > 2:
        helper()
    else: 
        try:
            img = get_random_image()
        except:
            img = get_random_local_image()
        
        set_background(img)