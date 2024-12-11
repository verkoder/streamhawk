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
Click Streams to see the current list. Mark the checkbox to monitor a stream. Check Play to auto-start favorites (VLC required, Soma.fm streams only). Check Talk and choose voices to announce favorites. Click Arrange to change order.

Adding Streams
--------------
Click Manage to add Soma.fm and SiriusXM streams. To rename, right-click an added stream.

Download Streams List
---------------------
Click a provider to download & update its list of available streams.

Monitoring Streams
------------------
Hit SPACEBAR or the PAUSED / WATCHING button to start / stop updating the playlist, in 15/30/45-second intervals. Favorites are shown in bold, and optionally announced and streamed.

Adding Favorite Artists
-----------------------
Double-click the playlist to add new artists. Mark artist/s, and click Add. Click AllMusic info for details.

Editing Favorite Artists
------------------------
Click Artists to see the full list. Add or delete, keeping one per line. You can use full artist names, partial names, song titles, or keywords.

CUSTOMIZING
===========

Right-click on StreamHawk and Show Package Contents. See the files in Contents/Resources.

Resetting User Data
-------------------
User data is stored as three JSON files. Delete to reset.
- artists.json – artists & keywords
- streams.json – added streams
- user.json - app preferences

Customizing Streams
-------------------
Adjust available streams in these JSON files.
- sirius.json
- soma.json

Adding voices
-------------
StreamHawk starts with 9 male and 9 female MacOS voices. To see all available voices, open a Terminal and type:
```say -v ?```
To include a voice in the pulldown list, add to the JSON file: 
- voices.json

Disclaimer
----------
Not affiliated, associated, authorized, endorsed by, or in any way officially connected with SomaFM.com LLC, Sirius XM Radio Inc., or AllMusic, NetAktion LLC. The official websites can be found respectively at somafm.com, siriusxm.com, and allmusic.com. Channel names are registered trademarks of their respective owners.
