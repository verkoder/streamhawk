import re
import json
import requests
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
from os import system
from time import sleep
from urllib.parse import quote_plus


SITES = {'soma': 'Soma.fm',
         'sirius': 'SiriusXM'}

def hawk_error(msg):
    messagebox.showerror('StreamHawk Error', msg)

def hawk_warning(msg):
    messagebox.showwarning('StreamHawk Warning', msg)

# JSON METHODS
def jload(name, fullpath=False):
    name = name if fullpath else f'{name}.json'
    try:
        with open(name) as f:
            return json.load(f)
    except FileNotFoundError:
        data = [] if 'artists' in name or 'streams' in name else {}
        json.dump(data, open(name, 'w'), indent=4)
        return data
    except json.JSONDecodeError as err:
        hawk_error(f'Error in "{name}" file:\n{err}')

def jdump(data, name):
    try:
        with open(f'{name}.json', 'w') as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        hawk_error(f'Missing file: "{name}"')

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
        self.arts = jload(self.parent.artists)

        self.title('Add Artist')
        self.geometry(f'485x400+50+{self.parent.height + 44}')
        self.minsize(350, 150)
        self.configure(background='black')

        nav = tk.LabelFrame(self, background='black', pady=5, border=0)
        nav.pack()
        self.btn_add = ttk.Button(nav, text='Add', command=self.add)
        self.btn_cancel = ttk.Button(nav, text='Cancel', command=self.destroy)
        self.btn_add.grid(row=0, column=0, padx=5)
        self.btn_cancel.grid(row=0, column=1, padx=5)

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
            if art in self.arts:
                box.config(state=tk.DISABLED)
            box.grid(row=i+1, column=0, padx=5, sticky=tk.W)
            getattr(self, f'url_{i}').grid(row=i+1, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky=tk.E)

    def add(self):
        artists = jload(self.parent.artists)
        artists += [x for i,(x,_) in enumerate(self.tunes) if getattr(self, f'var_{i}').get()]
        jdump(sorted(artists), self.parent.artists)
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
        btn_load = ttk.Button(nav, text='Load', command=self.load)
        btn_cancel = ttk.Button(nav, text='Cancel', command=self.destroy)
        btn_save.grid(row=0, column=0, padx=5)
        btn_load.grid(row=0, column=1, padx=5)
        btn_cancel.grid(row=0, column=2, padx=5)

        txt_frame = tk.LabelFrame(self, padx=5, background='black', border=0)
        txt_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.txt = scrolledtext.ScrolledText(txt_frame, height=35, width=50)
        self.txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.txt.insert(tk.END, '\n'.join(jload(self.parent.artists)))

    def save(self):
        artists = [x.strip() for x in self.txt.get(1.0, tk.END).split('\n')]
        jdump(sorted([x for x in set(artists) if x]), self.parent.artists)
        self.destroy()

    def load(self):
        fil = filedialog.askopenfilename()
        if fil:
            arts = jload(fil, fullpath=True)
            if isinstance(arts, list):
                self.txt.delete(1.0, tk.END)
                self.txt.insert(tk.END, '\n'.join(arts))
                self.parent.artists = fil.split('/')[-1].replace('.json', '')
            else:
                hawk_error(arts)

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
        btn_talk = ttk.Checkbutton(nav, text='Talk', variable=self.parent.talk)
        btn_save = ttk.Button(nav, text='Save', command=self.save)
        btn_close = ttk.Button(nav, text='Close', command=self.destroy)
        lab_manage = ttk.Label(nav, text='Manage', background='black', foreground='white')
        lab_manage.bind('<Button-1>', lambda x: self.parent.popup('Manage'))
        lab_reorder = ttk.Label(nav, text='Arrange', background='black', foreground='white')
        lab_reorder.bind('<Button-1>', lambda x: self.parent.popup('Arrange'))
        btn_talk.grid(row=0, column=0, padx=5)
        btn_save.grid(row=0, column=1, padx=5)
        btn_close.grid(row=0, column=2, padx=5)
        lab_manage.grid(row=0, column=3, padx=5)
        lab_reorder.grid(row=0, column=4, padx=5)

        shows_frame = tk.LabelFrame(self, text='Voices / Active Streams', background='white', padx=5, pady=5, border=1)
        shows_frame.pack(anchor=tk.CENTER)
        col = 0
        vox = jload('voices')
        for i,show in enumerate(self.parent.streams):
            if i >= half:
                i -= half
                col = 2
            name = show['name']
            setattr(self, name, tk.BooleanVar())
            setattr(self, f'box_{name}', tk.Checkbutton(shows_frame, text=name, width=25, justify=tk.LEFT,
                                                        variable=getattr(self, name)))
            box = getattr(self, f'box_{name}')
            if show['active']:
                box.select()
            else:
                box.deselect()
            box.grid(row=i, column=col+1, sticky=tk.W)
            setattr(self, f'vox_{name}', tk.StringVar())
            setattr(self, f'opt_{name}', ttk.OptionMenu(shows_frame, getattr(self, f'vox_{name}'), vox[0], *vox))
            getattr(self, f'vox_{name}').set(show['voice'])
            getattr(self, f'box_{name}').bind('<Button-1>', self.audition)
            getattr(self, f'opt_{name}').grid(row=i, column=col)
            getattr(self, f'opt_{name}').config(width=15)

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
        self.parent.refit_window()

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
        sirius_frame = tk.LabelFrame(meta, text='SiriusXM Streams'.rjust(44), padx=5, pady=5, background='white', border=0,
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
                hawk_warning('Limit of 24 streams - not all were added')
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
        self.parent.refit_window()

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
        self.btn_save = ttk.Button(nav, text='Save', command=self.save)
        self.btn_close = ttk.Button(nav, text='Close', command=self.parent.popup)
        self.btn_save.grid(row=0, column=0, padx=5)
        self.btn_close.grid(row=0, column=2, padx=5)

        self.order_frame = tk.LabelFrame(self, padx=5, pady=5, background='white', border=0)
        self.order_frame.pack(anchor=tk.CENTER)
        self.size = len(self.parent.streams) - 1
        self.buttons()

    def buttons(self, evt=None):
        if evt:
            show = self.parent.streams.pop(evt.widget.indx)
            shift = -1 if evt.widget.cget('text') == 'Up' else 1
            self.parent.streams.insert(evt.widget.indx + shift, show)
        for i,show in enumerate(self.parent.streams):
            name = show['name']
            lbl = tk.Label(self.order_frame, text=name.ljust(45))
            lbl.grid(row=i, column=0, sticky=tk.W, padx=5)
            if i != 0:
                setattr(self, 'u_{name}', ttk.Button(self.order_frame, text='Up'))
                btn = getattr(self, 'u_{name}')
                btn.bind('<Button-1>', self.buttons)
                btn.indx = i
                btn.grid(row=i, column=1, padx=10)
            if i != self.size:
                setattr(self, 'd_{name}', ttk.Button(self.order_frame, text='Down'))
                btn = getattr(self, 'd_{name}')
                btn.bind('<Button-1>', self.buttons)
                btn.indx = i
                btn.grid(row=i, column=2, padx=10)
        self.order_frame.update()

    def save(self):
        jdump(self.parent.streams, 'streams')
        self.parent.popup()

# MAIN WINDOW
class Hawk(tk.LabelFrame):
    height = 112
    artists = 'artists'
    play = {}
    tags = {x: re.compile(y) for x,y in jload('tags').items()}
    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, padx=2, pady=2, border=0)
        self.parent = parent
        self.win = False
        self.thread = threading.Thread(target=lambda: None)
        self.thread._stop_event = threading.Event()
        self.threaded = False
        self.changed = False
        self.second = tk.StringVar()

        self.talk = tk.BooleanVar()
        self.talk.set(True)
        self.streams = jload('streams')

        self.btn_pause = ttk.Button(self, text='PAUSED', style='paused.TButton', command=self.thread_stop)
        btn_artists = ttk.Button(self, text='for Artists', command=lambda: self.popup('Artists'))
        btn_shows = ttk.Button(self, text='in Streams', command=self.popup)
        opt_seconds = ttk.OptionMenu(self, self.second, 'every 15 sec',
                                                          *[f'every {x} sec' for x in (15, 30, 45)])
        opt_seconds.config(width=9)
        btn_quit = ttk.Button(self, text='QUIT', command=self.quit)
        self.playlist = tk.Text(self, height=4, font='Calibri 11')
        self.playlist.tag_configure('bold', font='Calibri 11 bold')
        self.playlist.configure(state='disabled')
        self.playlist.bind("<Double-Button-1>", lambda x: self.popup('AddArtist'))

        self.btn_pause.grid(row=0, column=0, sticky=tk.EW, ipadx=12)
        btn_artists.grid(row=0, column=1, sticky=tk.EW)
        btn_shows.grid(row=0, column=2, sticky=tk.EW)
        opt_seconds.grid(row=0, column=3, sticky=tk.EW)
        btn_quit.grid(row=0, column=4, sticky=tk.EW, ipadx=12)
        self.playlist.grid(row=1, column=0, columnspan=5, sticky=tk.EW)

    def monitor(self):
        if [x['active'] for x in self.streams]:
            artists = jload(self.artists)
            while not self.thread._stop_event.is_set():
                self.changed = False
                for show in [x for x in self.streams if x['active']]:
                    tune = self.now_on(show)
                    if not tune:
                        continue
                    name = show['name']
                    found = False
                    for artist in artists:
                        if artist not in tune:
                            continue
                        if self.talk.get() and self.play.get(name) != f'{tune}**':
                            system(f'say -v {show["voice"]} "{artist} on {name}"')
                        found = True
                        break
                    self.play[name] = tune + ('**' if found else '')
                    self.print_tracks()
                    for _ in range(int(self.second.get()[6:8]) * 5):
                        if self.thread._stop_event.is_set() or self.changed:
                            break
                        sleep(0.2)
                    if self.thread._stop_event.is_set() or self.changed:
                        break
        else:
            hawk_error('No active streams!')

    def now_on(self, show):
        if show['site'] == 'SiriusXM':
            response = requests.get(f'https://xmplaylist.com/api/station/{show["id"]}')
            if response.status_code == 200:
                tune = response.json()[0].get('track', {})
                if 'name' in tune and 'artists' in tune:
                    return f'{", ".join(tune["artists"])} - {tune["name"]}'
        elif show['site'] in self.tags: # Soma.fm or custom regex
            response = requests.get(show['id'])
            if response.status_code == 200:
                tune = self.tags[show['site']].search(response.content.decode('utf-8'))
                if tune:
                    return tune.group(1)
        return None

    def popup(self, win='Streams'):
        if win == 'Arrange' and len(self.streams) <= 1:
            hawk_error('Nothing to arrange!')
        else:
            if self.win:
                self.win.destroy()
            if win == 'AddArtist':
                tunes = [x.replace('**', '').split(' - ') for x in self.play.values() if ' - ' in x]
                if tunes:
                    self.win = AddArtist(self, tunes)
            else:
                self.win = globals()[win](self)

    def print_tracks(self):
        self.playlist.configure(state='normal')
        self.playlist.delete(1.0, tk.END)
        for show,tune in self.play.items():
            if tune.endswith('**'):
                self.playlist.insert('end', f'{show}\t\t{tune[:-2][:85]}\n', 'bold')
            elif tune:
                self.playlist.insert('end', f'{show}\t\t{tune[:85]}\n')
        self.playlist.configure(state='disabled')

    def quit(self):
        self.thread._stop_event.set()
        sleep(0.2)
        self.parent.quit()

    def refit_window(self):
        self.play = {x['name']: '' for x in self.streams if x['active']}
        self.changed = True
        self.height = 56 + 14 * max((len(self.play), 1))
        self.parent.geometry(f'585x{self.height}')
        self.playlist.configure(height=max(len(self.play)+1, 4))

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

    def verify(self):
        err = [x for x in ['artists', 'sirius', 'soma', 'streams', 'tags', 'voices'] if isinstance(jload(x), str)]
        if err:
            return '\n '.join(err)
        err = [x for x in {x['site'] for x in self.streams} if x != 'SiriusXM' and not x in self.tags.keys()]
        if err:
            return 'No matching "tags.json" regex for:\n ' + '\n '.join(err)
        return True
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
    msg = hawk.verify()
    if msg is True:
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Calibri', 12, 'bold'), background='black', foreground='lightgray')
        style.map('TButton', background=[('active', 'darkgreen'), ('!disabled', 'black')],
                             foreground=[('active', 'white'), ('!disabled', 'lightgray')])
        style.configure('paused.TButton', font=('Calibri', 12, 'bold'), background='black', foreground='lightgray')
        style.map('paused.TButton', background=[('active', 'darkgreen'), ('!disabled', 'darkred')],
                                    foreground=[('active', 'white'), ('!disabled', 'lightgray')])
        style.configure('active.TButton', font=('Calibri', 12, 'bold'), background='black', foreground='lightgray')
        style.map('active.TButton', background=[('active', 'darkgreen'), ('!disabled', 'darkgreen')],
                                    foreground=[('active', 'white'), ('!disabled', 'lightgray')])
        style.configure('TMenubutton', font=('Calibri', 12, 'bold'), background='black', foreground='lightgray')
        style.map('TMenubutton', background=[('active', 'darkgreen'), ('!disabled', 'black')],
                                 foreground=[('active', 'white'), ('!disabled', 'lightgray')])
        style.configure('TCheckbutton', font=('Calibri', 12, 'bold'), background='black', foreground='lightgray')
        style.map('TCheckbutton', background=[('active', 'darkgreen'), ('!disabled', 'black')],
                                 foreground=[('active', 'white'), ('!disabled', 'lightgray')])
        style.configure('TLabelFrame', font=('Calibri', 12, 'bold'), background='black', foreground='lightgray')
        style.map('TLabelFrame', background=[('active', 'darkgreen'), ('!disabled', 'black')],
                                 foreground=[('active', 'white'), ('!disabled', 'lightgray')])
        hawk.pack(padx=5, pady=5)
        hawk.refit_window()
        root.mainloop()
    else:
        hawk_error(msg)
