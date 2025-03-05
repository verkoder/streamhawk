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
Click Streams (or press 's') to see the current list. Mark the checkbox to monitor a stream. Move streams up (⋀) or down (⋁) in the list. Check Play to auto-start favorites (see Playback below). Check Talk and choose voices to announce favorites.

Managing Streams
----------------
Click Manage (or press 'm') to add or remove Soma.fm and SiriusXM streams. Add up to 24 streams. Streams cannot be added twice. To rename, right-click an added stream.

Updating Streams List
---------------------
Click a streaming service to download and update its current list of available streams.

Monitoring Streams
------------------
Hit SPACEBAR or the PAUSED / WATCHING button to start / stop updating the playlist, in 15/30/45-second intervals. Favorites are shown in bold, and optionally announced and/or streamed.

Stream Logos
------------
Press 'l' to see logos of current streams - shown in rows of five, mirroring the layout of the Soma.fm Roku player.

Adding Favorite Artists
-----------------------
Double-click the playlist (or press 'd' or '=') to add new artists. Mark artist/s, and click Add. Click AllMusic info for track details.

Editing Favorite Artists
------------------------
Click Artists (or press 'a') to see the full list. Add or delete, keeping one per line. Streams match by full or partial artist name.

Search Options
--------------
To match not only artists, but track names, use a starting asterisk. The following matches the artist 'Cujo - Traffic' as well as the track name 'Curtis - Scram feat. Cujo'.
```*Cujo```

Require full name matches with a starting equal sign. The following stops a bad 'Orbital' match, but misses a good 'The Orb' match.
```=Orb```

Ignore case with a starting tilde. The following matches 'Dj Food' as it appears on some streams.
```~DJ Food```

Playback
--------
StreamHawk can autostart streams as they play favorite artists. VLC is required, and limited to Soma.fm streams. Play is disabled if VLC cannot be found.

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
