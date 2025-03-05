import re
import requests
import sys
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from glob import glob
from os import system
from urllib.parse import quote_plus

from loader import SITES, SOMA, hawk_error, jdump, jload
from providers import get_sirius, get_soma


def case(x):
    'ignore case and search chars to sort'
    return str.casefold(x.replace('*', '').replace('=', '').replace('~', ''))

def key_commands(root, win):
    'in all windows except Artists'
    root.bind('<space>', win.toggle)
    root.bind('s', lambda x: win.popup())
    root.bind('a', lambda x: win.popup('Artists'))
    root.bind('d', lambda x: win.popup('AddArtist'))
    root.bind('=', lambda x: win.popup('AddArtist'))
    root.bind('l', lambda x: win.popup('Logos'))
    root.bind('m', lambda x: win.popup('Manage'))

# PRINT/TALK/WATCH THREADS
class Thread(threading.Thread):
    target = lambda: None

# POPUP WINDOWS
class Popup(tk.Toplevel):
    def destroy(self):
        self.parent.win = False
        super().destroy()

    def close(self, evt=None):
        self.parent.focus_set()
        self.parent.win = False
        super().destroy()

class AddArtist(Popup):
    def __init__(self, parent, tracks, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.tracks = tracks
        self.artists = jload('artists')
        self.title('Add Artist')
        half = len([x for x in self.parent.streams if x['active']])
        half = half // 2 + half % 2
        self.geometry(f'820x{100 + 40 * half}+0+85')
        self.minsize(350, 150)
        self.configure(background='black')
        self.bind('<Escape>', self.close)
        key_commands(self, parent)

        nav = tk.LabelFrame(self, background='black', pady=5, border=0) # AddArtist nav: Add/Cancel buttons
        nav.pack()
        btn_add = ttk.Button(nav, text='Add', command=self.add)
        btn_cancel = ttk.Button(nav, text='Cancel', command=self.destroy)
        btn_add.grid(row=0, column=0, padx=5)
        btn_cancel.grid(row=0, column=1, padx=5)
        art_frame = tk.LabelFrame(self, padx=5, pady=5, background='white') # AddArtist: name/checkbox/URL list
        art_frame.pack()
        col = 0
        for i,(art,song) in enumerate(self.tracks): # thru tracks...
            row = i
            if row >= half: # make columns
                row -= half
                col = 2
            setattr(self, f'var_{i}', tk.BooleanVar())
            setattr(self, f'url_{i}', ttk.Button(art_frame, text='AllMusic info'))
            getattr(self, f'url_{i}').url = f'https://www.allmusic.com/search/all/{quote_plus(f"{art} {song}")}'
            getattr(self, f'url_{i}').bind('<Button>', lambda evt: webbrowser.open_new(evt.widget.url))
            setattr(self, f'box_{i}', tk.Checkbutton(art_frame, text=art[:40], variable=getattr(self, f'var_{i}')))
            box = getattr(self, f'box_{i}')
            box.deselect()
            if art in self.artists:
                box.config(state=tk.DISABLED) # disable added artist
            box.grid(row=row+1, column=col, padx=5, sticky=tk.W)
            getattr(self, f'url_{i}').grid(row=row+1, column=col+1, padx=5, pady=5, ipadx=5, sticky=tk.E)

    def add(self):
        'add/save chosen artists'
        self.artists += [x for i,(x,_) in enumerate(self.tracks) if getattr(self, f'var_{i}').get()]
        jdump(sorted(self.artists, key=case), 'artists')
        self.parent.watched_artists()
        self.destroy()

class Artists(Popup):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.title('Artists')
        self.geometry(f'400x800+585+0')
        self.minsize(350, 150)
        self.configure(background='black')
        self.bind('<Escape>', self.close)

        nav = tk.LabelFrame(self, background='black', pady=5, border=0) # Artists nav: Save/Cancel buttons
        nav.pack()
        tips = ttk.Label(nav, text='Starting flags:\n =Exact match\n ~Ignore case\n *Match title',
                              background='black', foreground='white', font=('Courier', 14))
        btn_save = ttk.Button(nav, text='Save', command=self.save)
        btn_cancel = ttk.Button(nav, text='Cancel', command=self.destroy)
        btn_save.grid(row=0, column=0, padx=5)
        btn_cancel.grid(row=0, column=1, padx=5)
        tips.grid(row=0, column=2, padx=5)

        art_frame = tk.LabelFrame(self, padx=5, background='black', border=0) # Artists: text box
        art_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.text = scrolledtext.ScrolledText(art_frame, height=35, width=50)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.text.insert(tk.END, '\n'.join(jload('artists')))

    def save(self):
        'parse/save artists text'
        artists = [x.strip() for x in self.text.get(1.0, tk.END).split('\n')]
        jdump(sorted([x for x in set(artists) if x], key=case), 'artists')
        self.parent.watched_artists()
        self.destroy()

class Streams(Popup):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.title('Streams')
        self.half = len(self.parent.streams)
        self.half = self.half // 2 + self.half % 2
        self.geometry(f'750x{85 + 32 * self.half}+585+0')
        self.resizable(False, False)
        self.configure(background='black')
        self.bind('<Escape>', self.close)
        key_commands(self, parent)

        nav = tk.LabelFrame(self, background='black', pady=5, border=0) # Streams nav: Play/Talk/Drone boxes, Save/Close/Manage buttons
        nav.pack()
        btn_talk = ttk.Checkbutton(nav, text='Talk', variable=self.parent.talk)
        self.btn_autoplay = ttk.Checkbutton(nav, text='Play', variable=self.parent.autoplay)
        btn_save = ttk.Button(nav, text='Save', command=self.save)
        btn_close = ttk.Button(nav, text='Close', command=self.destroy)
        btn_manage = ttk.Button(nav, text='Manage Streams', command=lambda: self.parent.popup('Manage'))
        btn_talk.grid(row=0, column=0, padx=5)
        self.btn_autoplay.grid(row=0, column=1, padx=(5, 40))
        btn_save.grid(row=0, column=2, padx=5)
        btn_close.grid(row=0, column=3, padx=5)
        btn_manage.grid(row=0, column=4, padx=50, ipadx=15)
        if not self.parent.user.get('player'):
            self.btn_autoplay.configure(state='disabled')
            self.btn_autoplay.bind('<Button-1>', lambda x: hawk_error('Play unavailable:\nInstall VLC to play Soma.fm streams'))

        self.sho_frame = tk.LabelFrame(self, background='white', text='Move / Voice / Watch Streams', padx=15, pady=5, border=1) # Streams: vox/box/names
        self.sho_frame.pack(anchor=tk.CENTER)
        self.size = len(self.parent.streams) - 1
        self.arrange()

    def arrange(self, evt=None):
        'order streams & update display'
        if evt:
            show = self.parent.streams.pop(evt.widget.indx)
            self.parent.streams.insert(evt.widget.indx + (-1 if evt.widget.cget('text') == '⋀' else 1), show)
        col = 0
        vox = jload('voices')
        for i,show in enumerate(self.parent.streams): # thru added streams...
            if i >= self.half: # make columns
                i -= self.half
                col = 4
            sho = show['name']
            setattr(self, sho, tk.BooleanVar())
            setattr(self, f'box_{sho}', tk.Checkbutton(self.sho_frame, text=sho, width=25, justify=tk.LEFT, variable=getattr(self, sho)))
            if show['active']:
                getattr(self, f'box_{sho}').select()
            else:
                getattr(self, f'box_{sho}').deselect()
            setattr(self, f'vox_{sho}', tk.StringVar())
            setattr(self, f'opt_{sho}', ttk.OptionMenu(self.sho_frame, getattr(self, f'vox_{sho}'), vox[0], *vox))
            getattr(self, f'vox_{sho}').set(show['voice'])
            getattr(self, f'box_{sho}').bind('<Button-1>', self.audition)
            if i != 0 or col == 4:
                setattr(self, f'u_{sho}', ttk.Label(self.sho_frame, text='⋀'))
                getattr(self, f'u_{sho}').grid(row=i, column=col)
                btn = getattr(self, f'u_{sho}')
                btn.bind('<Button-1>', self.arrange)
                btn.indx = i + (self.half if col == 4 else 0)
                btn.grid(row=i, column=col, padx=5)
            if col == 0 or i + self.half != self.size:
                setattr(self, f'd_{sho}', ttk.Label(self.sho_frame, text='⋁'))
                getattr(self, f'd_{sho}').grid(row=i, column=col+1)
                btn = getattr(self, f'd_{sho}')
                btn.bind('<Button-1>', self.arrange)
                btn.indx = i + (self.half if col == 4 else 0)
                btn.grid(row=i, column=col+1, padx=5)
            getattr(self, f'opt_{sho}').grid(row=i, column=col+2)
            getattr(self, f'box_{sho}').grid(row=i, column=col+3, sticky=tk.W)
            getattr(self, f'opt_{sho}').config(width=8)
        self.sho_frame.update()

    def audition(self, btn):
        'demo chosen voice for stream'
        if self.parent.talk.get():
            name = btn.widget.cget('text')
            if not getattr(self, name).get():
                system(f'say -v {getattr(self, f"vox_{name}").get()} "artist on {name}"')

    def save(self):
        'save streams active/voice & user prefs'
        for show in self.parent.streams:
            show['active'] = getattr(self, show['name']).get()
            show['voice'] = getattr(self, f'vox_{show["name"]}').get()
        jdump(self.parent.streams, 'streams')
        self.parent.user['autoplay'] = self.parent.autoplay.get()
        self.parent.user['talk'] = self.parent.talk.get()
        jdump(self.parent.user, 'user')
        self.parent.resize()

class Logos(Popup):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.title('Stream Logos')
        self.geometry(f'855x{(len(self.parent.streams) // 5) * 175}+585+0')
        self.resizable(False, False)
        self.configure(background='black')
        self.bind('<Escape>', self.close)
        key_commands(self, parent)
        logos = {x.split('/')[-1][:-4]: x for x in glob('*.gif')}
        if not 'live' in logos:
            return hawk_error('No logos!')
        streams = {x['id']: x for x in self.parent.streams}
        for chan in streams.keys(): # live.gif on missing channels
            streams[chan]['logo'] = logos[chan if chan in logos else 'live']
        col = 0
        for i,(chan,stream) in enumerate(streams.items()):
            img = tk.PhotoImage(file=stream['logo'])
            pic = tk.Label(self, background='black', image=img)
            pic.image = img
            pic.grid(row=i // 5, column=col)
            col += 1
            if col == 5:
                col = 0

class Manage(Popup):
    soma = jload('soma')
    sirius = jload('sirius')
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.title('Manage Streams')
        self.geometry('800x600+585+0')
        self.resizable(False, False)
        self.configure(background='black')
        self.bind('<Escape>', self.close)
        key_commands(self, parent)

        nav = tk.LabelFrame(self, background='black', pady=5, border=0) # Manage nav: Close/Remove/Soma/Sirius buttons
        nav.pack()
        btn_close = ttk.Button(nav, text='Close', command=self.parent.popup)
        btn_remove = ttk.Button(nav, text='Remove Selected', command=self.remove)
        txt_update = ttk.Label(nav, text='Update:', background='black', foreground='white')
        btn_soma = ttk.Button(nav, text='Soma.fm', command=lambda: self.update('soma'))
        btn_sirius = ttk.Button(nav, text='SiriusXM', command=lambda: self.update('sirius'))
        btn_close.grid(row=0, column=0, padx=75)
        btn_remove.grid(row=0, column=1, padx=5, ipadx=5)
        txt_update.grid(row=0, column=2, padx=10)
        btn_soma.grid(row=0, column=3, padx=2)
        btn_sirius.grid(row=0, column=4, padx=2)

        meta = tk.LabelFrame(self, background='black', pady=5, border=0) # Manage: Soma/Added/Sirius frames
        meta.pack()
        ids = [x['id'] for x in self.parent.streams]
        self.soma_var = tk.StringVar(value=[(f'‣ {x}' if y in ids else x) for x,y in self.soma.items()])
        soma_frame = tk.LabelFrame(meta, text=f'Soma.fm ({len(self.soma)})', padx=5, pady=5,
                                   background='white', border=0, font='Calibri 14 bold') # Soma: listbox & Add button
        soma_frame.grid(row=1, column=0)
        self.list_soma = tk.Listbox(soma_frame, listvariable=self.soma_var, selectmode='multiple', height=30, width=18)
        self.list_soma.grid(row=0, column=0)
        adbtn_soma = ttk.Button(soma_frame, text='Add >>', command=lambda: self.add('soma'))
        adbtn_soma.grid(row=0, column=1, padx=5, sticky=tk.E)

        self.added_var = tk.StringVar(value=[x['name'] for x in self.parent.streams])
        self.added_frame = tk.LabelFrame(meta, text=f'Added Streams ({len(self.parent.streams)})', padx=5, pady=5,
                                     background='white', border=0, font='Calibri 14 bold') # Added Streams: listbox
        self.added_frame.grid(row=1, column=2)
        self.list_shows = tk.Listbox(self.added_frame, listvariable=self.added_var, selectmode='multiple', height=30, width=18)
        self.list_shows.bind('<Button-2>', self.rename)
        self.list_shows.pack()

        self.sirius_var = tk.StringVar(value=[(f'‣ {x}' if y in ids else x) for x,y in self.sirius.items()])
        sirius_frame = tk.LabelFrame(meta, text=f'SiriusXM ({len(self.sirius)})'.rjust(43), padx=5, pady=5,
                                     background='white', border=0, font='Calibri 14 bold') # Sirius: listbox & Add button
        sirius_frame.grid(row=1, column=4)
        self.list_sirius = tk.Listbox(sirius_frame, listvariable=self.sirius_var, selectmode='multiple', height=30, width=22)
        self.list_sirius.grid(row=0, column=1)
        adbtn_sirius = ttk.Button(sirius_frame, text='<< Add', command=lambda: self.add('sirius'))
        adbtn_sirius.grid(row=0, column=0, padx=5, sticky=tk.W)

    def add(self, site):
        'add/save chosen streams w/ limit warning'
        size = len(self.parent.streams)
        if size == 24:
            hawk_error('Limit of 24 streams')
        else:
            ids = [x['id'] for x in self.parent.streams]
            shows = getattr(self, site)
            picks = getattr(self, f'list_{site}').curselection()
            rows = list(shows.keys())
            adds = [rows[x] for x in picks]
            adds = [dict(active=True,
                        id=shows[x],
                        name=x,
                        site=SITES[site],
                        voice='Alex') for x in adds if not shows[x] in ids]
            if size + len(adds) > 24:
                hawk_error('Limit of 24 streams - not all were added')
                adds = adds[:24-len(self.parent.streams)]
            self.parent.streams.extend(adds)
            self.save()

    def remove(self):
        'remove/save chosen streams'
        rows = [x['name'] for x in self.parent.streams]
        dels = [rows[x] for x in self.list_shows.curselection()]
        self.parent.streams = [x for x in self.parent.streams if not x['name'] in dels]
        self.save()
    
    def rename(self, evt):
        'rename/save chosen stream'
        rows = evt.widget.curselection()
        if len(rows) == 1:
            ol = evt.widget.get(rows[0])
            nu = simpledialog.askstring('Rename Stream', f'Change "{ol}" to:', initialvalue=ol, parent=self)
            if nu and nu != ol:
                self.parent.streams[rows[0]]['name'] = nu
                self.save()

    def save(self):
        'save/count/mark added streams'
        jdump(self.parent.streams, 'streams')
        adds = [x['id'] for x in self.parent.streams]
        self.added_frame.configure(text=f'Added Streams ({len(adds)})')
        self.added_var.set([x['name'] for x in self.parent.streams])
        for site in ('soma', 'sirius'): # mark listbox contents
            getattr(self, f'{site}_var').set([(f'‣ {x}' if y in adds else x) for x,y in getattr(self, site).items()])
        self.parent.resize()

    def update(self, site):
        'download/save all available streams by streaming service'
        self.destroy()
        messagebox.showerror('StreamHawk Download', f'Updating {site.title()} streams...')
        globals()[f'get_{site}']() # download streams to json
        setattr(self, site, jload(site)) # load from json, update app
        self.parent.popup('Manage')

# MAIN WINDOW
class Hawk(tk.LabelFrame):
    artists = []
    height = 112
    playlist = {}
    soma = {}
    watching = False
    win = False
    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, padx=2, pady=2, border=0) # StreamHawk body: Pause/Artists/Streams/Seconds/Quit buttons, text
        self.parent = parent
        self.printer = Thread()
        self.speaker = Thread()
        self.streamer = Thread()
        self.watcher = Thread()
        self.second = tk.StringVar()

        self.streams = jload('streams') # load streams & user prefs
        self.user = jload('user')
        self.talk = tk.BooleanVar()
        self.autoplay = tk.BooleanVar()
        self.talk.set(self.user.get('talk', True))
        self.autoplay.set(self.user.get('autoplay', False))
        vlc = [x for x in glob('/Applications/*.app') if 'VLC' in x]
        self.user['player'] = vlc[0] if vlc else ''
        jdump(self.user, 'user')

        self.btn_pause = ttk.Button(self, text='PAUSED', style='paused.TButton', command=self.toggle)
        btn_artists = ttk.Button(self, text='for Artists', command=lambda: self.popup('Artists'))
        btn_shows = ttk.Button(self, text='in Streams', command=self.popup)
        opt_seconds = ttk.OptionMenu(self, self.second, 'every 15 sec', *[f'every {x} sec' for x in (15, 30, 45)])
        opt_seconds.config(width=9)
        btn_quit = ttk.Button(self, text='QUIT', command=self.parent.destroy)
        self.text = tk.Text(self, height=4, font='Calibri 11')
        self.text.tag_configure('bold', font='Calibri 11 bold')
        self.text.configure(state='disabled', wrap='none')
        self.text.bind('<Double-Button-1>', lambda x: self.popup('AddArtist'))

        self.btn_pause.grid(row=0, column=0, sticky=tk.EW, ipadx=12)
        btn_artists.grid(row=0, column=1, sticky=tk.EW)
        btn_shows.grid(row=0, column=2, sticky=tk.EW)
        opt_seconds.grid(row=0, column=3, sticky=tk.EW)
        btn_quit.grid(row=0, column=4, sticky=tk.EW, ipadx=12)
        self.text.grid(row=1, column=0, columnspan=5, sticky=tk.EW)

    def current_streams(self):
        'get active streams ID/track dict (Soma web call)'
        shows = [x for x in self.streams if x['active']]
        self.soma = {x['id']: '' for x in shows if x['site'] == 'Soma.fm'}
        if self.soma:
            response = requests.get(SOMA) # Soma: tracks playing on all streams
            if response.status_code == 200:
                self.soma = {x['id']: x['lastPlaying'] for x in response.json()['channels'] if x['id'] in self.soma}
        return shows

    def playing_on(self, show):
        'current artist/track on stream (Sirius web call)'
        if show['site'] == 'Soma.fm': # Soma: get show in dict
            return self.soma[show['id']]
        elif show['site'] == 'SiriusXM': # Sirius: track playing on this stream
            response = requests.get(f'https://xmplaylist.com/api/station/{show["id"]}')
            if response.status_code == 200:
                tune = response.json()[0].get('track', {})
                if 'name' in tune and 'artists' in tune:
                    return f'{", ".join(tune["artists"])} - {tune["name"]}'
        return ''

    def popup(self, win='Streams'):
        'open a window'
        self.focus_set() # so spacebar won't reopen
        if self.win:
            self.win.destroy()
        if win == 'AddArtist':
            tracks = [x.replace('**', '').split(' - ') for x in self.playlist.values() if ' - ' in x]
            if tracks:
                self.win = AddArtist(self, tracks)
        else: # Artists/Logos/Manage/Streams
            self.win = globals()[win](self)

    def refresh(self):
        'print playlist with matches in bold'
        self.text.configure(state='normal')
        self.text.delete(1.0, tk.END)
        for show,tune in self.playlist.items():
            if tune.endswith('**'):
                self.text.insert(tk.END, f'    {show}\t\t\t{tune[:-2]}\n', 'bold')
            elif tune:
                self.text.insert(tk.END, f'    {show}\t\t\t{tune}\n')
        self.text.configure(state='disabled')

    def resize(self, freshen=True):
        'fit window to active streams, truncate current playlist til next watch'
        self.playlist = {x['name']: self.playlist.get(x['name'], '') for x in self.streams if x['active']}
        self.height = 60 + 14 * max((len(self.playlist), 1))
        self.parent.geometry(f'585x{self.height}')
        self.text.configure(height=max(len(self.playlist)+1, 4))
        if freshen:
            self.refresh()

    def speak(self, artist, show, lastmatch):
        'announce/autoplay matching stream'
        if lastmatch and self.autoplay.get() and (show['site'] == 'Soma.fm'):
            self.streamer = Thread(target=lambda: self.stream(show['id']))
            self.streamer.start()
        if self.talk.get():
            system(f'say -v {show["voice"]} "{artist} on {show["name"]}"') # speak

    def stream(self, show_id):
        'open Soma.fm stream in VLC'
        system(f'open -a {self.user["player"]} https://somafm.com/{show_id}.pls')

    def toggle(self, evt=None):
        'toggle watch monitor on/off'
        if not self.streams:
            return hawk_error('No added streams!\n\nClick Streams > Manage to add streams.')
        elif not True in {x['active'] for x in self.streams}:
            return hawk_error('No active streams!\n\nClick Streams and mark active streams.')
        if self.watching:
            self.btn_pause.configure(style='paused.TButton', text='PAUSED')
            self.watching = False
            self.watcher = Thread()
        else:
            self.btn_pause.configure(style='active.TButton', text='WATCHING')
            self.watching = True
            self.watcher = Thread(target=self.watch)
            self.watcher.start()

    def watch(self):
        'monitor active streams for matches'
        if self.watching:
            news = []
            for show in self.current_streams():
                track = self.playing_on(show)
                if track:
                    byline = track.split(' - ')[0]
                    for art,regx in self.artists:
                        find = regx.fullmatch(byline) if art[0] == '=' else \
                            regx.search(track if art[0] == '*' else byline) # fullmatch/track/byline search
                        if find: # matched track
                            if self.playlist.get(show['name']) != f'{track}**': # unseen
                                self.playlist[show['name']] = f'{track}**' # flag as seen
                                news.append((art.replace('*', '').replace('=', '').replace('~', ''), show)) # new matches
                            break
                    else: # normal track
                        self.playlist[show['name']] = track # reset current show
            self.printer = Thread(target=self.refresh) # print playlist
            self.printer.start()
            if news: # play/announce new matches
                for i,(art,sho) in enumerate(news):
                    self.speaker = Thread(target=lambda: self.speak(art, sho, (i == len(news) - 1)))
                    self.speaker.start()
            self.parent.after(int(self.second.get()[6:8])*980, self.watch)

    def watched_artists(self):
        'update artists name/regex search list'
        self.artists = [
            (x, re.compile(f'(?{"i" if x[0]=="~" else ""}s)' +
                re.sub('\s+', '\s*', x.replace('*', '').replace('=', '').replace('~', '').replace('.', '\.')))
             ) for x in jload('artists')
        ]

if __name__ == '__main__':
    root = tk.Tk()
    bar = tk.Menu(root)
    menu = tk.Menu(bar, tearoff=0)
    menu.add_command(label='Using StreamHawk', command=lambda: webbrowser.open_new('http://scottyvercoe.com/streamhawk/'))
    bar.add_cascade(label='Guide', menu=menu)
    root.createcommand('tkAboutDialog', lambda: root.tk.call('tk::mac::standardAboutPanel'))
    root.configure(bg='black', menu=bar)
    root.geometry(f'585x112+0+0')
    root.resizable(False, False)
    root.title('StreamHawk')
    hawk = Hawk(root)
    key_commands(root, hawk)
    style = ttk.Style()
    style.theme_use('clam')
    BOLD = ('Calibri', 12, 'bold')
    GRAY = dict(background='black', foreground='lightgray')
    GREEN = [('active', 'darkgreen'), ('!disabled', 'black')]
    WHITE = [('active', 'white'), ('!disabled', 'lightgray')]
    style.configure('TButton', font=BOLD, **GRAY)
    style.map('TButton', background=GREEN, foreground=WHITE)
    style.configure('paused.TButton', font=BOLD, **GRAY)
    style.map('paused.TButton', background=[('active', 'darkgreen'), ('!disabled', 'darkred')], foreground=WHITE)
    style.configure('active.TButton', font=BOLD, **GRAY)
    style.map('active.TButton', background=[('active', 'darkgreen'), ('!disabled', 'darkgreen')], foreground=WHITE)
    style.configure('TMenubutton', font=BOLD, **GRAY)
    style.map('TMenubutton', background=GREEN, foreground=WHITE)
    style.configure('TCheckbutton', font=BOLD, **GRAY)
    style.map('TCheckbutton', background=GREEN, foreground=WHITE)
    style.configure('TLabelFrame', font=BOLD, **GRAY)
    style.map('TLabelFrame', background=GREEN, foreground=WHITE)
    hawk.pack(padx=5, pady=5)
    hawk.resize(False)
    hawk.watched_artists()
    hawk.toggle()
    root.mainloop()
    sys.exit()
