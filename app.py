import json
import requests
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from glob import glob
from os import system
from time import sleep
from urllib.parse import quote_plus


SITES = {'soma': 'Soma.fm',
         'sirius': 'SiriusXM'}
SOMA = 'http://api.somafm.com/channels.json'

def hawk_error(msg):
    messagebox.showerror('StreamHawk Error', msg)

def jload(name):
    try:
        with open(f'{name}.json') as f:
            return json.load(f)
    except FileNotFoundError:
        data = [] if name in ('artists', 'streams') else {}
        json.dump(data, open(f'{name}.json', 'w'), indent=4)
        return data
    except json.JSONDecodeError as err:
        hawk_error(f'Error in "{name}.json" file:\n{err}')

def jdump(data, name):
    try:
        with open(f'{name}.json', 'w') as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        hawk_error(f'Missing file: "{name}.json"')

# POPUP WINDOWS
class Popup(tk.Toplevel):
    def destroy(self):
        self.parent.win = False
        super().destroy()

class AddArtist(Popup):
    def __init__(self, parent, tunes, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.tunes = tunes
        self.artists = jload('artists')
        self.title('Add Artist')
        self.geometry(f'485x{25 + self.parent.height * 3}+50+{self.parent.height + 44}')
        self.minsize(350, 150)
        self.configure(background='black')

        nav = tk.LabelFrame(self, background='black', pady=5, border=0)
        nav.pack()
        btn_add = ttk.Button(nav, text='Add', command=self.add)
        btn_cancel = ttk.Button(nav, text='Cancel', command=self.destroy)
        btn_add.grid(row=0, column=0, padx=5)
        btn_cancel.grid(row=0, column=1, padx=5)

        art_frame = tk.LabelFrame(self, padx=5, pady=5, background='white')
        art_frame.pack()
        for i,(art,song) in enumerate(self.tunes):
            setattr(self, f'var_{i}', tk.BooleanVar())
            setattr(self, f'url_{i}', ttk.Button(art_frame, text='AllMusic info'))
            getattr(self, f'url_{i}').url = f'https://www.allmusic.com/search/all/{quote_plus(f"{art} {song}")}'
            getattr(self, f'url_{i}').bind('<Button>', lambda evt: webbrowser.open_new(evt.widget.url))
            setattr(self, f'box_{i}', tk.Checkbutton(art_frame, text=art, variable=getattr(self, f'var_{i}')))
            box = getattr(self, f'box_{i}')
            box.deselect()
            if art in self.artists:
                box.config(state=tk.DISABLED)
            box.grid(row=i+1, column=0, padx=5, sticky=tk.W)
            getattr(self, f'url_{i}').grid(row=i+1, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky=tk.E)

    def add(self):
        self.artists += [x for i,(x,_) in enumerate(self.tunes) if getattr(self, f'var_{i}').get()]
        jdump(sorted(self.artists), 'artists')
        self.destroy()

class Artists(Popup):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.title('Artists')
        self.geometry(f'385x600+100+{self.parent.height + 44}')
        self.minsize(350, 150)
        self.configure(background='black')

        nav = tk.LabelFrame(self, background='black', pady=5, border=0)
        nav.pack()
        btn_save = ttk.Button(nav, text='Save', command=self.save)
        btn_cancel = ttk.Button(nav, text='Cancel', command=self.destroy)
        btn_save.grid(row=0, column=0, padx=5)
        btn_cancel.grid(row=0, column=2, padx=5)

        art_frame = tk.LabelFrame(self, padx=5, background='black', border=0)
        art_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.text = scrolledtext.ScrolledText(art_frame, height=35, width=50)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.text.insert(tk.END, '\n'.join(jload('artists')))

    def save(self):
        artists = [x.strip() for x in self.text.get(1.0, tk.END).split('\n')]
        jdump(sorted([x for x in set(artists) if x]), 'artists')
        self.destroy()

class Streams(Popup):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.title('Streams')
        half = len(self.parent.streams)
        half = half // 2 + half % 2
        self.geometry(f'750x{85 + 32 * half}+585+0')
        self.resizable(False, False)
        self.configure(background='black')

        nav = tk.LabelFrame(self, background='black', pady=5, border=0)
        nav.pack()
        btn_autoplay = ttk.Checkbutton(nav, text='Play', variable=self.parent.autoplay)
        btn_talk = ttk.Checkbutton(nav, text='Talk', variable=self.parent.talk)
        btn_save = ttk.Button(nav, text='Save', command=self.save)
        btn_close = ttk.Button(nav, text='Close', command=self.destroy)
        lab_manage = ttk.Label(nav, text='Manage', background='black', foreground='white')
        lab_manage.bind('<Button-1>', lambda x: self.parent.popup('Manage'))
        lab_order = ttk.Label(nav, text='Arrange', background='black', foreground='white')
        lab_order.bind('<Button-1>', lambda x: self.parent.popup('Arrange'))
        btn_autoplay.grid(row=0, column=0, padx=5)
        btn_talk.grid(row=0, column=1, padx=5)
        btn_save.grid(row=0, column=2, padx=5)
        btn_close.grid(row=0, column=3, padx=5)
        lab_manage.grid(row=0, column=4, padx=5)
        lab_order.grid(row=0, column=5, padx=5)
        if not self.parent.user.get('player'):
            btn_autoplay.configure(state='disabled')
            btn_autoplay.bind('<Button-1>', lambda x: hawk_error('Play unavailable:\nInstall VLC to play Soma.fm streams'))

        col = 0
        vox = jload('voices')
        sho_frame = tk.LabelFrame(self, text='Voices / Active Streams', background='white', padx=5, pady=5, border=1)
        sho_frame.pack(anchor=tk.CENTER)
        for i,show in enumerate(self.parent.streams):
            if i >= half:
                i -= half
                col = 2
            setattr(self, show['name'], tk.BooleanVar())
            setattr(self, f'box_{show["name"]}', tk.Checkbutton(sho_frame, text=show['name'], width=25, justify=tk.LEFT,
                                                                variable=getattr(self, show['name'])))
            if show['active']:
                getattr(self, f'box_{show["name"]}').select()
            else:
                getattr(self, f'box_{show["name"]}').deselect()
            setattr(self, f'vox_{show["name"]}', tk.StringVar())
            setattr(self, f'opt_{show["name"]}', ttk.OptionMenu(sho_frame, getattr(self, f'vox_{show["name"]}'), vox[0], *vox))
            getattr(self, f'vox_{show["name"]}').set(show['voice'])
            getattr(self, f'box_{show["name"]}').bind('<Button-1>', self.audition)
            getattr(self, f'box_{show["name"]}').grid(row=i, column=col+1, sticky=tk.W)
            getattr(self, f'opt_{show["name"]}').grid(row=i, column=col)
            getattr(self, f'opt_{show["name"]}').config(width=15)

    def audition(self, btn):
        if self.parent.talk.get():
            name = btn.widget.cget('text')
            if not getattr(self, name).get():
                system(f'say -v {getattr(self, f"vox_{name}").get()} "artist on {name}"')

    def save(self):
        for show in self.parent.streams:
            show['active'] = getattr(self, show['name']).get()
            show['voice'] = getattr(self, f'vox_{show["name"]}').get()
        jdump(self.parent.streams, 'streams')
        self.parent.user['autoplay'] = self.parent.autoplay.get()
        self.parent.user['talk'] = self.parent.talk.get()
        jdump(self.parent.user, 'user')
        self.parent.resize()

class Manage(Popup):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.title('Manage Streams')
        self.geometry('800x600+585+0')
        self.resizable(False, False)
        self.configure(background='black')

        nav = tk.LabelFrame(self, background='black', pady=5, border=0)
        nav.pack()
        btn_delete = ttk.Button(nav, text='Delete Selected', command=self.delete)
        btn_close = ttk.Button(nav, text='Close', command=self.parent.popup)
        btn_delete.grid(row=0, column=0, padx=5, ipadx=20)
        btn_close.grid(row=0, column=1, padx=5)

        meta = tk.LabelFrame(self, background='black', pady=5, border=0)
        meta.pack()
        self.soma = jload('soma')
        self.sirius = jload('sirius')

        soma_var = tk.StringVar(value=list(self.soma.keys()))
        soma_frame = tk.LabelFrame(meta, text='Soma.fm Streams', padx=5, pady=5, background='white', border=0,
                                   font='Calibri 14 bold')
        soma_frame.grid(row=1, column=0)
        self.list_soma = tk.Listbox(soma_frame, listvariable=soma_var, selectmode='multiple', height=30, width=18)
        self.list_soma.grid(row=0, column=0)
        adbtn_soma = ttk.Button(soma_frame, text='Add >>', command=lambda: self.add('soma'))
        adbtn_soma.grid(row=0, column=1, padx=5, sticky=tk.E)

        self.stream_var = tk.StringVar(value=[x['name'] for x in self.parent.streams])
        stream_frame = tk.LabelFrame(meta, text='Added Streams', padx=5, pady=5, background='white', border=0,
                                     font='Calibri 14 bold')
        stream_frame.grid(row=1, column=2)
        self.list_shows = tk.Listbox(stream_frame, listvariable=self.stream_var, selectmode='multiple', height=30, width=18)
        self.list_shows.bind('<Button-2>', self.rename)
        self.list_shows.pack()

        sirius_var = tk.StringVar(value=list(self.sirius.keys()))
        sirius_frame = tk.LabelFrame(meta, text='SiriusXM Streams'.rjust(45), padx=5, pady=5, background='white', border=0,
                                    font='Calibri 14 bold')
        sirius_frame.grid(row=1, column=4)
        self.list_sirius = tk.Listbox(sirius_frame, listvariable=sirius_var, selectmode='multiple', height=30, width=22)
        self.list_sirius.grid(row=0, column=1)
        adbtn_sirius = ttk.Button(sirius_frame, text='<< Add', command=lambda: self.add('sirius'))
        adbtn_sirius.grid(row=0, column=0, padx=5, sticky=tk.W)

    def add(self, site):
        size = len(self.parent.streams)
        if size == 24:
            hawk_error('Limit of 24 streams')
        else:
            ids = [x['id'] for x in self.parent.streams]
            shows = getattr(self, site)
            picks = getattr(self, f'list_{site}').curselection()
            rows = list(shows.keys())
            adds = [rows[x] for x in picks]
            adds = [dict(active=False,
                        id=shows[x],
                        name=x,
                        site=SITES[site],
                        voice='Alex') for x in adds if not shows[x] in ids]
            if size + len(adds) > 24:
                hawk_error('Limit of 24 streams - not all were added')
                adds = adds[:24-len(self.parent.streams)]
            self.parent.streams.extend(adds)
            self.save()

    def delete(self):
        rows = [x['name'] for x in self.parent.streams]
        dels = [rows[x] for x in self.list_shows.curselection()]
        self.parent.streams = [x for x in self.parent.streams if not x['name'] in dels]
        self.save()

    def rename(self, evt):
        rows = evt.widget.curselection()
        if len(rows) == 1:
            ol = evt.widget.get(rows[0])
            nu = simpledialog.askstring('Rename Stream', f'Change "{ol}" to:', initialvalue=ol, parent=self)
            if nu:
                self.parent.streams[rows[0]]['name'] = nu
                self.save()

    def save(self):
        self.stream_var.set([x['name'] for x in self.parent.streams])
        jdump(self.parent.streams, 'streams')
        self.parent.resize()

class Arrange(Popup):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.title('Arrange Streams')
        self.geometry(f'540x{70 + 32 * max((len(self.parent.streams), 1))}+585+0')
        self.minsize(350, 150)
        self.configure(background='black')

        nav = tk.LabelFrame(self, background='black', pady=5, border=0)
        nav.pack()
        btn_save = ttk.Button(nav, text='Save', command=self.save)
        btn_close = ttk.Button(nav, text='Close', command=self.parent.popup)
        btn_save.grid(row=0, column=0, padx=5)
        btn_close.grid(row=0, column=2, padx=5)

        self.sho_frame = tk.LabelFrame(self, padx=5, pady=5, background='white', border=0)
        self.sho_frame.pack(anchor=tk.CENTER)
        self.size = len(self.parent.streams) - 1
        self.arrange()

    def arrange(self, evt=None):
        if evt:
            show = self.parent.streams.pop(evt.widget.indx)
            self.parent.streams.insert(evt.widget.indx + (-1 if evt.widget.cget('text') == 'Up' else 1), show)
        for i,show in enumerate(self.parent.streams):
            lbl = tk.Label(self.sho_frame, text=show['name'].ljust(45))
            lbl.grid(row=i, column=0, sticky=tk.W, padx=5)
            if i != 0:
                setattr(self, f'u_{show["name"]}', ttk.Button(self.sho_frame, text='Up'))
                btn = getattr(self, f'u_{show["name"]}')
                btn.bind('<Button-1>', self.arrange)
                btn.indx = i
                btn.grid(row=i, column=1, padx=10)
            if i != self.size:
                setattr(self, f'd_{show["name"]}', ttk.Button(self.sho_frame, text='Down'))
                btn = getattr(self, f'd_{show["name"]}')
                btn.bind('<Button-1>', self.arrange)
                btn.indx = i
                btn.grid(row=i, column=2, padx=10)
        self.sho_frame.update()

    def save(self):
        jdump(self.parent.streams, 'streams')
        self.parent.popup()

# MAIN WINDOW
class Hawk(tk.LabelFrame):
    changed = False
    height = 112
    play = {}
    soma = {}
    threaded = False
    win = False
    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, padx=2, pady=2, border=0)
        self.parent = parent
        self.thread = threading.Thread(target=lambda: None)
        self.thread._stop_event = threading.Event()
        self.second = tk.StringVar()

        self.streams = jload('streams')
        self.user = jload('user')
        self.autoplay = tk.BooleanVar()
        self.talk = tk.BooleanVar()
        self.autoplay.set(self.user.get('autoplay', False))
        self.talk.set(self.user.get('talk', True))
        vlc = [x for x in glob('/Applications/*.app') if 'VLC' in x]
        self.user['player'] = vlc[0] if vlc else ''
        jdump(self.user, 'user')

        self.btn_pause = ttk.Button(self, text='PAUSED', style='paused.TButton', command=self.thread_stop)
        btn_artists = ttk.Button(self, text='for Artists', command=lambda: self.popup('Artists'))
        btn_shows = ttk.Button(self, text='in Streams', command=self.popup)
        opt_seconds = ttk.OptionMenu(self, self.second, 'every 15 sec', *[f'every {x} sec' for x in (15, 30, 45)])
        opt_seconds.config(width=9)
        btn_quit = ttk.Button(self, text='QUIT', command=self.quit)
        self.text = tk.Text(self, height=4, font='Calibri 11')
        self.text.tag_configure('bold', font='Calibri 11 bold')
        self.text.configure(state='disabled')
        self.text.bind("<Double-Button-1>", lambda x: self.popup('AddArtist'))

        self.btn_pause.grid(row=0, column=0, sticky=tk.EW, ipadx=12)
        btn_artists.grid(row=0, column=1, sticky=tk.EW)
        btn_shows.grid(row=0, column=2, sticky=tk.EW)
        opt_seconds.grid(row=0, column=3, sticky=tk.EW)
        btn_quit.grid(row=0, column=4, sticky=tk.EW, ipadx=12)
        self.text.grid(row=1, column=0, columnspan=5, sticky=tk.EW)

    def announce(self, artist, show):
        if self.autoplay.get() and show['site'] == 'Soma.fm':
            system(f'open {self.user["player"]} --args https://somafm.com/{show["id"]}.pls')
        if self.talk.get():
            system(f'say -v {show["voice"]} "{artist} on {show["name"]}"')

    def currently_on(self, show):
        if show['site'] == 'SiriusXM':
            response = requests.get(f'https://xmplaylist.com/api/station/{show["id"]}')
            if response.status_code == 200:
                tune = response.json()[0].get('track', {})
                if 'name' in tune and 'artists' in tune:
                    return f'{", ".join(tune["artists"])} - {tune["name"]}'
        elif show['site'] == 'Soma.fm':
            return self.soma[show['id']]
        return ''

    def get_shows(self):
        self.changed = False
        shows = [x for x in self.streams if x['active']]
        self.soma = {x['id']: '' for x in shows if x['site'] == 'Soma.fm'}
        if self.soma:
            response = requests.get(SOMA)
            if response.status_code == 200:
                self.soma = {x['id']: x['lastPlaying'] for x in response.json()['channels'] if x['id'] in self.soma}
        return shows

    def monitor(self):
        if not True in {x['active'] for x in self.streams}:
            return hawk_error('No active streams!')

        artists = jload('artists')
        while not self.thread._stop_event.is_set():
            for show in self.get_shows():
                tune = self.currently_on(show)
                if tune:
                    fave = False
                    for artist in artists:
                        if artist in tune:
                            fave = True
                            if self.play.get(show['name']) != f'{tune}**':
                                self.announce(artist, show)
                            break
                    self.play[show['name']] = tune + ('**' if fave else '')
                    self.refresh()
            for _ in range(int(self.second.get()[6:8]) * 5):
                if self.thread._stop_event.is_set() or self.changed:
                    break
                sleep(0.2)

    def popup(self, win='Streams'):
        if win == 'Arrange' and len(self.streams) <= 1:
            return hawk_error('Nothing to arrange!')
        if self.win:
            self.win.destroy()
        if win == 'AddArtist':
            tunes = [x.replace('**', '').split(' - ') for x in self.play.values() if ' - ' in x]
            if tunes:
                self.win = AddArtist(self, tunes)
        else:
            self.win = globals()[win](self)

    def quit(self):
        self.thread._stop_event.set()
        sleep(0.2)
        self.parent.quit()

    def refresh(self):
        self.text.configure(state='normal')
        self.text.delete(1.0, tk.END)
        for show,tune in self.play.items():
            if tune.endswith('**'):
                self.text.insert('end', f'{show}\t\t{tune[:-2][:85]}\n', 'bold')
            elif tune:
                self.text.insert('end', f'{show}\t\t{tune[:85]}\n')
        self.text.configure(state='disabled')

    def resize(self):
        self.play = {x['name']: '' for x in self.streams if x['active']}
        self.changed = True
        self.height = 56 + 14 * max((len(self.play), 1))
        self.parent.geometry(f'585x{self.height}')
        self.text.configure(height=max(len(self.play)+1, 4))
        self.text.delete(1.0, tk.END)

    def thread_stop(self):
        if self.threaded:
            self.threaded = False
        else:
            self.btn_pause['text'] = 'WATCHING'
            self.btn_pause['style'] = 'active.TButton'
            self.play = {x['name']: '' for x in self.streams}
            self.threaded = True
            self.thread = threading.Thread(target=self.monitor)
            self.thread._stop_event = threading.Event()
            self.thread.start()
            self.thread_wait()

    def thread_test(self, *args, **kwargs):
        if not self.threaded:
            self.btn_pause['text'] = 'PAUSED'
            self.btn_pause['style'] = 'paused.TButton'
            self.thread._stop_event.set()
        elif self.thread.is_alive() and not self.thread._stop_event.is_set():
            self.thread_wait()
        else:
            self.btn_pause['text'] = 'PAUSED'
            self.btn_pause['style'] = 'paused.TButton'

    def thread_wait(self):
        self.parent.after(200, self.thread_test, self.thread)

if __name__ == '__main__':
    root = tk.Tk()
    bar = tk.Menu(root)
    menu = tk.Menu(bar, tearoff=0)
    menu.add_command(label='Using StreamHawk', command=lambda: webbrowser.open_new('http://scottyvercoe.com/streamhawk/'))
    bar.add_cascade(label='Guide', menu=menu)
    root.configure(bg='black', menu=bar)
    root.geometry(f'585x112+0+0')
    root.resizable(False, False)
    root.title('StreamHawk')
    root.createcommand('tkAboutDialog', lambda: root.tk.call('tk::mac::standardAboutPanel'))
    hawk = Hawk(root)
    style = ttk.Style()
    style.theme_use('clam')
    BOLD = ('Calibri', 12, 'bold')
    GRAY = dict(background='black', foreground='lightgray')
    GREEN = [('active', 'darkgreen'), ('!disabled', 'black')]
    WHITE = [('active', 'white'), ('!disabled', 'lightgray')]
    style.configure('TButton', font=('Calibri', 12, 'bold'), **GRAY)
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
    hawk.resize()
    root.mainloop()
