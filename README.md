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

Resetting User Data
-------------------
User data is stored as three JSON files. To reset, delete the files.
- artists.json – artists & keywords
- streams.json – added streams
- user.json - app preferences

Customizing StreamHawk
--------------------
Adjust available streams & voices in these JSON files.
- sirius.json – SiriusXM streams
- soma.json – Soma.fm streams
- voices.json – Mac voice options

Adding voices
- StreamHawk starts with 9 male and 9 female MacOS voices.
- To see all available voices, open a Terminal and type: say -v ?
- To add a voice to StreamHawk, add to voices.json

Disclaimer
----------
Not affiliated, associated, authorized, endorsed by, or in any way officially connected with SomaFM.com LLC, Sirius XM Radio Inc., or AllMusic, NetAktion LLC. The official websites can be found respectively at somafm.com, siriusxm.com, and allmusic.com. Channel names are registered trademarks of their respective owners.
