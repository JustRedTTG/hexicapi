from hexicapi.verinfo import *
import os, datetime, atexit, zipfile
from colorama import Fore
from hexicapi.save import save, load
buses = {}
loc = "logs"
silent = False
logFile = None
latest = None
firstL = True
files = None
zipfiles = None
def close_log():
    global logFile, latest, files, zipfiles
    if logFile:
        logFile.close()
    if latest:
        latest.close()
    if files and zipfiles:
        save(os.path.join(loc, 'info'), files, zipfiles)
atexit.register(close_log)


def datemaker():
    date = datetime.datetime.now()
    return f'{date.day}-{date.month}-{date.year} {int(date.hour)}.{int(date.minute)}.{int(date.second)}'


colors = {
    'OK': Fore.LIGHTBLUE_EX,
    'OK_SOFT': Fore.LIGHTBLACK_EX,
    'INFO': Fore.GREEN,
    'WARNING': Fore.YELLOW,
    'ERROR': Fore.LIGHTRED_EX,
    'FATAL': Fore.RED,
    'LOG': Fore.CYAN,
    'EXIT': Fore.RESET
}


def funk(name):
    return ' '.join([item.capitalize() for item in name.split('_')])


def log(name:str, info:str, sign:str="LOG"):
    global firstL
    if not firstL:
        logFile.write('\n')
        latest.write('\n')
    else:
        firstL = False
    l = f'[{datemaker()}][{funk(name)}/{" ".join(sign.split("_"))}] - {info}'
    logFile.write(l)
    latest.write(l)
    if not silent:
        print(colors[sign]+l+colors['EXIT'])


def init(location = "logs"):
    global loc, logFile, firstL, latest, files, zipfiles
    firstL = True
    close_log()
    logFile = None
    latest = None
    loc = location
    if not os.path.exists(loc):
        os.makedirs(loc)
    if not os.path.exists(os.path.join(loc, 'old')):
        os.makedirs(os.path.join(loc, 'old'))
    if os.path.exists(os.path.join(loc, 'info')):
        files, zipfiles = load(os.path.join(loc, 'info'))
        am = 0
        am1 = 0
        y = False
        y1 = False
        if len(files) >= 10:
            zipname = f'{files[0].replace(".txt","")} - {files[len(files)-1].replace(".txt","")}.zip'
            zipfiles.append(zipname)
            zip = zipfile.ZipFile(os.path.join(loc, 'old', zipname), 'w')
            for file in files:
                filename = os.path.join(loc, file)
                try:
                    zip.write(filename, os.path.basename(filename))
                    os.remove(filename)
                except:
                    pass
                am += 1
            zip.close()
            files = []
            y = True
        if len(zipfiles) >= 5:
            for file in zipfiles:
                filename = os.path.join(loc, 'old', file)
                try:
                    os.remove(filename)
                except:
                    pass
                am += 1
            zipfiles = []
            y1 = True
        while os.path.exists(os.path.join(loc, f'{datemaker()}.txt')):
            pass
        filename = f'{datemaker()}.txt'
        logFile = open(os.path.join(loc, filename), 'w')
        if os.path.exists(os.path.join(loc, 'latest.txt')):
            os.remove(os.path.join(loc, 'latest.txt'))
        latest = open(os.path.join(loc, 'latest.txt'), 'w')
        if y:
            log('logger', f'Packed {am} files to "{zipname}".')
        if y1:
            log('logger', f'Deleted {am1} zips from old folder')
        files.append(filename)
        save(os.path.join(loc, 'info'), files, zipfiles)
    else:
        save(os.path.join(loc, 'info'), [], [])
        init(location)

# SIGNS
ERROR = "ERROR"
FATAL = "FATAL"
WARNING = "WARNING"
INFO = "INFO"
OK = "OK"
OK_SOFT = "OK_SOFT"


# Loggers
server = lambda i, s=INFO: log('server', i, s)
client_handle = lambda i, s=OK: log('client_handle', i, s)
client_handle_soft = lambda i, s=OK_SOFT: log('client_handle', i, s)
shadow = lambda i, s=OK: log('shadow', i, s)
connection_acceptor = lambda i, s=INFO: log('connection', i, s)
reader = lambda i, s=WARNING: log('reader', i, s)
debug = lambda i, s=INFO: log('debug', i, s)