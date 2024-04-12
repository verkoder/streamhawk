StreamHawk
==========

StreamHawk scans playlists to announce when your favorite artists are streaming.

Compatible Streams
------------------
- SiriusXM
- Soma.fm

BASIC USAGE
===========

Choosing Streams
----------------
- Click Streams to see the current list.
- Mark the checkbox to watch a stream.
- To announce favorites, check Talk and choose voices.
- To change stream order, save, and click Arrange.

Adding Streams
--------------
- Click Manage to add Soma.fm & SiriusXM streams (up to 24 total).
- To rename, right-click an added stream.

Watching Streams
----------------
- Hit the PAUSED / WATCHING button to start / stop watching streams. An updating playlist appears below.
- Choose to monitor in 15/30/45-second intervals.
- Favorites are announced, and shown in bold.

Adding Artists
--------------
- Double-click the playlist to add new artists. 
- Mark artist/s, and click Add.
- Click AllMusic info for details.

Editing Artists
---------------
- Click Artists to see the full list. 
- Add or delete, keeping one per line.
- You can use full artist names, partial names, song titles, or keywords.

CUSTOMIZING
===========

Right-click on StreamHawk and Show Package Contents. See the files in Contents/Resources.

Resetting User Preferences
--------------------------
User preferences are stored as two JSON files. To reset, delete both files.
- artists.json – artists & keywords
- streams.json – added streams

Extending StreamHawk
--------------------
Customize and extend StreamHawk via these JSON files.
- sirius.json – SiriusXM streams
- soma.json – Soma.fm streams
- tags.json – site regexes
- voices.json – Mac voice options

Adding voices
- StreamHawk starts with 9 male and 9 female MacOS voices.
- To see all available voices, open a Terminal and type: say -v ?
- To add a voice to StreamHawk, add to voices.json

Handling other sites
--------------------
- find a stream’s live playlist & inspect its HTML
- make a regex with match.group(1) => “Artist – Song”
- add site name/regex pattern as key/value pair to tags.json, for example:
```
{
    "Soma.fm": "Now Playing: (.?)</p>",
    "MySite": "Spinning (.*?)<br>"
}
```

To watch streams, add to streams.json, for example:
```
[
    {
        "active": true,
        "id": "http://mysite.net/reggae/",
        "name": "My Reggae Radio",
        "site": "MySite",
        "voice": "Paulina"
    }
]
```

Ensure site value in streams.json matches a key in tags.json
