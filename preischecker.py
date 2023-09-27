import requests, os
from bs4 import BeautifulSoup
from datetime import datetime

# Copyright 2023 by Sprecher und Twitch-Chat
# Data Division:
directory = 'conf'
directory2 = 'data'
decimalinhistory = ","
MySet = set()
altpreis = 0
ntfyServer = '192.168.111.154'
ntfyTopic = 'Preisbot'
header = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0'}
# END Data Division

def doyourmagic(soup,Kennung,htmltag1,htmltag2,htmltag3,aschalter,maxpreis,history):
    preis = soup.find(htmltag1, {htmltag2: htmltag3}).text.strip()
    datei = 'data/' + Kennung + '-preis.csv'

    # alte Datei wird eingelesen, wenn sie existiert.
    if os.path.exists(datei):
        with open(datei, 'r', encoding='UTF-8') as file:
            altdata = file.readline().split(" ")
            altpreis = float(altdata[2].replace(decimalinhistory, '.'))
    else:
        altpreis = 0

    # alte Datei im Data Verzeichnis wird überschrieben
    with open(datei, 'w') as fp:
        datum = datetime.now()
        dt_string = datum.strftime("%d.%m.%Y %H:%M:%S")
        neupreis = float(preis.replace(',','.').replace('€','').replace('-','0').replace('EUR','').strip())
        neupreisstr = "{:.2f}".format(neupreis).replace('.', decimalinhistory)
        zeile = dt_string + " " + neupreisstr
        fp.write(zeile)
        befehl = 'curl -d \"' + Kennung + ' für ' + neupreisstr + '\" ' + ntfyServer + '/' + ntfyTopic
        match aschalter:
            case 1:
                # Preis unter selbstgewählter Preisgrenze
                if neupreis < maxpreis:
                    print(Kennung + ' für ' + neupreisstr)
                    #os.system(befehl)
            case 2:
                # Preisverfall in %
                if neupreis <= altpreis * (maxpreis/100):
                    print(Kennung + ' für ' + neupreisstr)
                    #os.system(befehl)
            case 3:
                # Neupreis unter Altpreis
                if neupreis < altpreis:   
                    print(Kennung + ' für ' + neupreisstr)
                    #os.system(befehl)
    # Daten werden auch in die History-Dateien geschrieben
    if history == "1":
        with open('history/' + Kennung + '.csv', 'a') as fp:
            fp.write(zeile + "\n")

# Alle Conf-Dateien einlesen
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f) and f.endswith('.conf'):
        with open(f, 'r', encoding='UTF-8') as file:
            MySet.add(file.readline().strip())

# Aufsplitten der Daten
for item in MySet:
    configdata = item.split('|')
    Kennung = configdata[0]
    url = configdata[1]
    htmltag1 = configdata[2]
    htmltag2 = configdata[3]
    htmltag3 = configdata[4]
    aschalter = int(configdata[5])
    maxpreis = float(configdata[6])
    history = configdata[7]
    seite = requests.get(url, headers=header)
    soup = BeautifulSoup(seite.content, 'html.parser')
    doyourmagic(soup,Kennung,htmltag1,htmltag2,htmltag3,aschalter, maxpreis,history)
