StreamHawk
==========

StreamHawk scans playlists to announce when your favorite artists are streaming.

Compatible Streaming Services
-----------------------------
- SiriusXM
- Soma.fm

BASIC USAGE
===========

Choosing Streams
----------------
Click Streams to see the current list. Mark the checkbox to monitor a stream. Check Play to auto-start favorites (VLC required, Soma.fm streams only). Check Talk and choose voices to announce favorites. Click Arrange to change order.

Managing Streams
----------------
Click Manage to add or remove streams from streaming services Soma.fm and/or SiriusXM. Add up to 24 streams. Streams cannot be added twice. To rename, right-click an added stream.

Updating Streams List
---------------------
Click a streaming service to download and update its full list of available streams.

Monitoring Streams
------------------
Hit SPACEBAR or the PAUSED / WATCHING button to start / stop updating the playlist, in 15/30/45-second intervals. Favorites are shown in bold, and optionally announced and streamed.

Adding Favorite Artists
-----------------------
Double-click the playlist to add new artists. Mark artist/s, and click Add. Click AllMusic info for track details.

Editing Favorite Artists
------------------------
Click Artists to see the full list. Add or delete, keeping one name per line. Streams match by full or partial artist name. Optionally match track names as well with a starting asterisk:
```*Dreadlock Holiday```

CUSTOMIZING
===========

Right-click on StreamHawk and Show Package Contents. See the files in Contents/Resources.

Resetting User Data
-------------------
User data is stored as three JSON files. Delete to reset.
- artists.json – favorite artists
- streams.json – added streams
- user.json - user preferences

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
