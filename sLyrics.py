import psutil
import requests
from bs4 import BeautifulSoup
import win32gui, win32process
import threading, tkinter

import tkinter
from tkinter.ttk import *
from tkinter.constants import *

tk = tkinter.Tk()
tk.title("sLyrics")

s=Style()
s.configure("BW.TLabel",foreground='black',background='white')

s.theme_use('alt')

frame = tkinter.Frame(tk, relief=RIDGE, borderwidth=2) 

frame.pack(fill=BOTH,expand=1)

label = tkinter.Label(frame, text="", bg='black', fg='white')

label.pack(fill=X, expand=1)

# Vertical (y) Scroll Bar
scroll = tkinter.Scrollbar(tk)
scroll.pack(side=RIGHT, fill=Y)

# Text Widget
eula = tkinter.Text(tk, wrap=NONE, yscrollcommand=scroll.set, bg='black', fg='white')
eula.insert("1.0", '')
eula.pack(side="left")

# Configure the scrollbars
scroll.config(command=eula.yview)

genius_key = None
query_url = 'https://api.genius.com/search?q=%s'
genius_headers = {'Authorization': 'Bearer %s'%genius_key}

# null
last_lyrics = ''

def get_genius_url(query):
    url = query_url%(query)
    r = requests.get(url, headers=genius_headers)
    if r.status_code == 200:
        r_data = r.json()
        r_data = r_data['response']
        hits = r_data['hits']
        if hits:
            return hits[0]['result']['url']
        else:
            return query_url%'error_error_error'
    else:
        return r.text

def get_genius_lyrics(url):
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        lyrics = []
        for div in soup.findAll('div', attrs={'class': 'lyrics'}):
            lyrics.append(div.text)
        if lyrics:
            return ''.join(lyrics)
        else:
            return '`[Lyrics not found]`'
    else:
        if page.status_code == 401:
            return '[Lyrics not found]'

#

def get_hwnds_for_pid(pid):
    def callback(hwnd, hwnds):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid == pid:

            hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds 

def isSpotifyActive():
    widTitle = None
    p = psutil.pids()
    try:
        for p in p:
            p = psutil.Process(p)
            if 'spotify.exe' in str(p.name).lower():
                pr = p.parent()
                pr = pr.pid
                hwnd = get_hwnds_for_pid(pr)
                for x in hwnd:
                    if len(win32gui.GetWindowText(x)) > 2:
                        widTitle = win32gui.GetWindowText(x)
                        break
                break
        return widTitle
    except:
        pass       

def get_current_Song():

    global last_lyrics

    name = isSpotifyActive()    
    if name:
        name = name.lower()

        if not last_lyrics == name:
            if not name == None and not 'spotify' in name:

                last_lyrics = name
                global label 
                global eula
                label.config(text=name)
                eula.delete(0.0, tkinter.END)
                eula.insert(tkinter.INSERT, get_genius_lyrics(get_genius_url(name)))
closed = 0

def main():
    global closed
    if closed == 0:
        get_current_Song()  
        threading.Timer(1.1, main).start()    

def on_closing():
    global closed
    tk.destroy()
    closed = 1

if __name__ == "__main__":
    main()
    tk.protocol("WM_DELETE_WINDOW", on_closing)
    tk.mainloop()