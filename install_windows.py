import os, sys, argparse, shutil

# Dependencies
dependencies_script = 'pip install pyinstaller winshell pywin32'
try:
    import pyinstaller, winshell
    from win32com.client import Dispatch
except:
    os.system(dependencies_script)
    import winshell
    from win32com.client import Dispatch

# Uninstall
parser = argparse.ArgumentParser(description='Install Simon Stålenhag wallpaper for Windows')
parser.add_argument('-u', '--uninstall', help='Remove installation', action='store_true')

def remove(path):
    try:
        shutil.rmtree(path)
    except Exception as e:
        return

if parser.parse_args().uninstall:
    print('Uninstalling Stålenhag Wallpaper Application')
    remove(os.path.expanduser('~|Pictures|Stålenhag|'.replace('|', os.sep)))
    remove(os.path.expanduser('~|.stalenhag|'.replace('|', os.sep)))
        
    desktop = winshell.desktop()
    shortcutpath = os.path.join(desktop, "Stalenhag.lnk")
    os.remove(shortcutpath)
    quit()

# Install
print('Installing Stålenhag Wallpaper Application')
install_loc = os.path.expanduser(f'~{os.sep}.stalenhag/install')
install_script = f'pyinstaller --noconfirm --onedir --console --distpath="{install_loc}" "./stalenhag.py"'
# note: --icon "path/asd.ico"
os.system(install_script)
print(f'SUCCESS ---------------------------')
print(f'Executable install in {install_loc}')
# clean
os.remove('stalenhag.spec')
remove('./build')

# Add Shortcut
desktop = winshell.desktop()
path = os.path.join(desktop, "Stalenhag.lnk")
target = f"{install_loc}{os.sep}stalenhag{os.sep}stalenhag.exe"
wDir = f"{install_loc}"
icon = f"{install_loc}{os.sep}stalenhag{os.sep}stalenhag.exe"
shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(path)
shortcut.Targetpath = target
shortcut.WorkingDirectory = wDir
shortcut.IconLocation = icon
shortcut.save()