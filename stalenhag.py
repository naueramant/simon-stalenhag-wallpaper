#!/usr/bin/env python3

import re, os, sys, random
from urllib import request

BASE = 'https://www.simonstalenhag.se/'
IMAGES_DIR = os.path.expanduser('~/Pictures/Stålenhag/')

def check_dirs():
    if not os.path.isdir(IMAGES_DIR):
        os.mkdir(IMAGES_DIR[:-1])

def local_exists(filename):
    return os.path.isfile(IMAGES_DIR + filename)

def get_images_list():
    contents = request.urlopen(BASE).read()
    images = re.findall(r'bilderbig\/[a-zA-Z0-9_]*\.jpg', str(contents))
    return list(set(images))

def download_image(name):
    request.urlretrieve(BASE + 'bilderbig/' + name, IMAGES_DIR + name)

def get_random_local_image():
    images = os.listdir(IMAGES_DIR)
    images = list(filter(lambda s: os.path.isfile(IMAGES_DIR + s), images))
    images = list(filter(lambda s: s.endswith('.jpg'), images))
    
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
        except:
            print('\r-->', str(index) + ')', name, 'FAILED', end='')
    
        print('')
        index += 1

def set_background(path):
    print('set image', path)
    os.system('gsettings set org.gnome.desktop.background picture-uri file://' + path)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'all':
        get_all_images()
    else: 
        img = None
        
        try:
            img = get_random_image()
        except:
            img = get_random_local_image()
        
        if img:
            set_background(img)
        else:
            print('Failed to find an image')