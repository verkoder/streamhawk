'''
To build OSX application:
    rm -rf build/ dist/
    python setup.py py2app
Icon from: https://icons8.com/icons/set/hawk
Logos from: https://somafm.com/logos/256/
'''
from glob import glob
from setuptools import setup

APP = ['app.py']
DATA_FILES = [
    'artists.json',
    'sirius.json',
    'soma.json',
    'streams.json',
    'voices.json',
] + glob('./logos/*.gif')
OPTIONS = {
    'iconfile': '/Users/scotty/Documents/hawk/img/logo.icns',
    'plist': {
        'CFBundleName': 'StreamHawk',
        'CFBundleDisplayName': 'StreamHawk',
        'CFBundleGetInfoString': 'StreamHawk scans playlists to announce when your favorite artists are streaming.',
        'CFBundleIdentifier': 'com.scottyvercoe.osx.streamhawk',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHumanReadableCopyright': u'Copyright © 2024 - 2025, Scotty Vercoe, All Rights Reserved'
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
