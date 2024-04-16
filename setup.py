'''
To build OSX application:
    rm -rf build/ dist/
    python setup.py py2app
'''
from setuptools import setup

APP = ['app.py']
DATA_FILES = [
    'artists.json',
    'sirius.json',
    'soma.json',
    'streams.json',
    'voices.json'
]
OPTIONS = {
    'iconfile': '/Users/scotty/Documents/hawk/img/logo.icns',
    'plist': {
        'CFBundleName': 'StreamHawk',
        'CFBundleDisplayName': 'StreamHawk',
        'CFBundleGetInfoString': 'StreamHawk scans playlists to announce when your favorite artists are streaming.',
        'CFBundleIdentifier': 'com.scottyvercoe.osx.streamhawk',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHumanReadableCopyright': u'Copyright © 2024 Scotty Vercoe'
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
