from setuptools import setup
# TO BUILD APP:
#   rm -rf /build /dist
#   py setup.py p2app

APP = ['StreamHawk.py']
DATA_FILES = [
    './app/sirius.json',
    './app/soma.json',
    './app/tags.json',
    './app/voices.json',
    './user/artists.json',
    './user/streams.json'
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
