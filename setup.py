'''
To build OSX application:
    rm -rf /build /dist
    py setup.py p2app
'''
from setuptools import setup

APP = ['app.py']
DATA_FILES = [
    'sirius.json',
    'soma.json',
    'tags.json',
    'voices.json',
    'artists.json',
    'streams.json'
]
OPTIONS = {
    'iconfile': '/Users/scotty/Documents/hawk/img/logo.icns',
    'plist': {
        'CFBundleName': 'StreamHawk',
        'CFBundleDisplayName': 'StreamHawk',
        'CFBundleGetInfoString': 'Scan audio streams for favorite artists',
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
