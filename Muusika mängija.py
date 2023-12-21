import tkinter as tk
import tkinter.ttk as ttk
import pygame
import os
import random
import time
import mutagen
from tkinter import filedialog
from tkinter import *
import copy
import sys


#Kasutatud materjalid: https://www.youtube.com/watch?v=jO6qQDNa2UY
#https://www.pygame.org/docs/ref/mixer.html
#https://www.youtube.com/playlist?list=PLCC34OHNcOtoC6GglhF3ncJ5rLwQrLGnV

# Käivitub pygame mixer ja pygame, mida kasutatakse helifailide taasesitamiseks
pygame.mixer.init()
pygame.init()

Muusika_Lõpp = pygame.event.custom_type()
class UI:
    # Meetod, mis uuendab lauluinfo, kui fail muutub
    def Failimuutus(self):
        try:
            # Proovib laadida faili praegusest laulude järjekorrast, kasutades hetkel mängiva laulu indeksit
            self.fail = mutagen.File(self.lauludejärjend[self.hetkelmängivalauluindeks])
        except:
            print("Faili pole veel laetud")
            
        # Proovib leida ja uuendada laulu väljaandmise aastat
        try:
            # Võtab 'date' välja esimese väärtuse, kuna see tagastatakse listina. Siin kohal toimib .flac falilidele (ja võibolla ka muudele, aga mul on olemas ainult .flac ja .mp3 laulud testimiseks)
            self.väljaandmis_aasta = self.fail['date'][0] #Millegipärast hoitakse sõnastikus elemente listis, ehk [0] võtab listi esimese elemendi.
            # Uuendab väljaandmise aasta väärtust graafilisel liidesel
            self.väljaandmis_aasta_tekst.config(text=self.väljaandmis_aasta)#Muudab graafilisel liidesel väärtust
        except:
            try:
                # Alternatiivne viis väljaandmise aasta saamiseks ehk .mp3 failide jaoks, kui enne ei saadud kätte nime.
                self.väljaandmis_aasta = self.fail['TDRC'].text[0]
                self.väljaandmis_aasta_tekst.config(text=self.väljaandmis_aasta)
            except:
                # Kui väljaandmise aastat ei leita, kuvatakse teade
                self.väljaandmis_aasta_tekst.config(text='Antud failil ei leitud väljaandmisaastat')
        
        # Järgnevad plokid püüavad leida ja uuendada laulu nime, artisti nime, albumi nime ja lüürika, järgides sarnast loogikat nagu väljaandmise aasta puhul.
        # Püüab leida ja uuendada laulu nime
        try:
            self.laulu_nimi = self.fail['title'][0]
            self.laulu_nimi_tekst.config(text=self.laulu_nimi)
        except:
            try:
                self.laulu_nimi = self.fail['TIT2'].text[0] 
                self.laulu_nimi_tekst.config(text=self.laulu_nimi)
            except:
                # Laulunimel on natuke teistmoodi exception, kui laulunime ei leita metadatast, siis väljastatakse laulunimeks helifaili nimi.
                Asendusnimele_kui_ei_leitud_metadatast = (self.lauludejärjend[self.hetkelmängivalauluindeks]).strip().split('/')[-1]
                self.laulu_nimi_tekst.config(text=Asendusnimele_kui_ei_leitud_metadatast)
        
        # Püüab leida ja uuendada artisti nime
        try:
            self.artisti_nimi = self.fail['artist'][0]
            self.artisti_nimi_tekst.config(text=self.artisti_nimi)
        except:
            try:
                self.artisti_nimi = self.fail['TPE1'].text[0] 
                self.artisti_nimi_tekst.config(text=self.artisti_nimi)
            except:
                self.artisti_nimi_tekst.config(text='Antud failil ei leitud artisti nime')
        
        # Püüab leida ja uuendada albumi nime
        try:
            self.albumi_nimi = self.fail['album'][0] 
            self.albumi_nimi_tekst.config(text=self.albumi_nimi)
        except:
            try:
                self.albumi_nimi = self.fail['TALB'].text[0]
                self.albumi_nimi_tekst.config(text=self.albumi_nimi)
            except:
                self.albumi_nimi_tekst.config(text='Antud failil ei leitud albumi nime')

        # Püüab leida ja uuendada laulu lüürikat
        try:
            self.lüürika = self.fail['lyrics'][0] 
            
        except:
            try:
                self.lüürika = self.fail['USLT::'].text[0] 
            except KeyError:
                # Kui 'USLT' silti ei leita, siis võib olla ka 'SYLT' silt
                try:
                    self.lüürika = self.fail['SYLT::'].text[0]
                except:
                    self.lüürika = 'Antud failil ei leitud laulusõnu'
        
        # Uuendab laulude järjekorra kuvamist
        self.laulude_järjekord()
        
        # Püüab leida ja uuendada laulu pikkust
        try:
            self.laulupikkus = self.fail.info.length
            self.laulupikkus_kena_visuaalselt = time.strftime('%M:%S', time.gmtime(self.laulupikkus)) # Teisendab laulu pikkuse formaadiks MM:SS
            self.laulupikkus_tekst.config(text=str(self.laulupikkus_kena_visuaalselt)) # Uuendab laulu pikkust graafilisel liidesel
        except:
            print("Ei leidnud laulupikkust")
    
    # Proovib luua uue sõne, mis kujutab laulude järjekorda
    def laulude_järjekord(self):
        try:
            uussõne = ''
            try:
                # Kontrollib, kas järjekorras on piisavalt laule, et näidata järgmisi 10 laulu
                self.lauludejärjend[self.hetkelmängivalauluindeks + 11] #Tekitab errori, kui listis on vähem, kui 10 eset, et minna edasi exceptioni juurde
                for i in self.lauludejärjend[self.hetkelmängivalauluindeks + 1:self.hetkelmängivalauluindeks + 11]:
                    nimi = 'Laulu nime ei leitud' # Kui helifailil ei leita nime või artisti laulu metadatast, siis tagastab need väärtused.
                    artist = 'Artisti nime ei leitud'
                    
                    # Püüab leida laulu pealkirja ja artisti nime iga järgneva laulu jaoks
                    try:
                        nimi = mutagen.File(i)['title'][0] 
                    except:
                        try:
                            nimi = mutagen.File(i)['TIT2'].text[0] # Laulu pealkiri
                        except:
                            print('Antud failil ei leitud laulunime (järjendiloomisel)')
                    try:
                        artist = mutagen.File(i)['artist'][0] 
                    except:
                        try:
                            artist = mutagen.File(i)['TPE1'].text[0] # Laulu pealkiri
                        except:
                            print('Antud failil ei leitud laulunime (järjendiloomisel)')
                    # Kui laulunime ei leitud, siis saab väärtuseks helifaili nimi, kui leiti, siis tulevad andmed metadatast
                    if nimi == 'Laulu nime ei leitud':
                        uussõne += i.strip().split('/')[-1] + '\n'
                    else:
                        # Lisab iga laulu info (artisti nimi ja laulu nimi) uude sõnesse
                        uussõne += artist + ' - ' + nimi + '\n'
                # Uuendab järjekorda graafilisel liidesel
                self.järjekord_tekst.config(text=uussõne)
            except:
                # Kui playlistrepeat on aktiivne ja järjekorras on vähem kui 10 laulu, siis teeb sarnaselt eelmisele reale
                if self.playlistrepeat:
                    try:
                        loetavjärjend = self.lauludejärjend[self.hetkelmängivalauluindeks:]
                        for i in range(11):
                            for j in self.lauludejärjend:
                                loetavjärjend.append(j)#Korda üksteist, sest kui järjendis ainult üks laul siis programm ei pane errorit järgmisel sammul
                        for i in loetavjärjend[1:11]:
                            nimi = 'Laulu nime ei leitud'
                            artist = 'Artisti nime ei leitud'
                            try:
                                nimi = mutagen.File(i)['title'][0] 
                            except:
                                try:
                                    nimi = mutagen.File(i)['TIT2'].text[0] # Laulu pealkiri
                                except:
                                    print('Antud failil ei leitud laulunime (järjendiloomisel)')
                            try:
                                artist = mutagen.File(i)['artist'][0] 
                            except:
                                try:
                                    artist = mutagen.File(i)['TPE1'].text[0] # Laulu pealkiri
                                except:
                                    print('Antud failil ei leitud artisti nime (järjendiloomisel)')
                            if nimi == 'Laulu nime ei leitud':
                                uussõne += i.strip().split('/')[-1] + '\n'
                            else:
                                uussõne += artist + ' - ' + nimi + '\n'
                        self.järjekord_tekst.config(text=uussõne)
                    except:
                        print("Tuli error järjekorra välja printimisel, olukorras, kus self.playlistrepeat on True")
                else:
                    # Kui playlistrepeat ei ole aktiivne, kuvatakse kõik järelejäänud laulud järjekorras
                    for i in self.lauludejärjend[self.hetkelmängivalauluindeks + 1:]:
                        nimi = 'Laulu nime ei leitud'
                        artist = 'Artisti nime ei leitud'
                        try:
                            nimi = mutagen.File(i)['title'][0] 
                        except:
                            try:
                                nimi = mutagen.File(i)['TIT2'].text[0] # Laulu pealkiri
                            except:
                                print('Antud failil ei leitud laulunime (järjendiloomisel)')
                        try:
                            artist = mutagen.File(i)['artist'][0] 
                        except:
                            try:
                                artist = mutagen.File(i)['TPE1'].text[0] # Laulu pealkiri
                            except:
                                print('Antud failil ei leitud laulunime (järjendiloomisel)')
                        if nimi == 'Laulu nime ei leitud':
                            uussõne += i.strip().split('/')[-1] + '\n'
                        else:
                            uussõne += artist + ' - ' + nimi + '\n'
                    self.järjekord_tekst.config(text=uussõne)
        except:
            print("Error laulude järjekorra väljastamisel, tõenäoliselt pole ühtegi faili laetud, või järjekorras pole lihtsalt rohkem laule")
    
    
    # Kontrollib pygame sündmusi, muudab Hetkeaega laulus (elapsed time) ja liigutab scroll bari vastavalt
    def Event_Kontroll(self):
            
        # Kontrollib, kas muusika on lõppenud
        for event in pygame.event.get():
            if event.type == Muusika_Lõpp:
                # Kui muusika lõppeb, käivitatakse järgmise laulu mängimine
                self.järgminelaul()
        
        
        
        # Uuendab hetkeaega laulus, mis näitab, mitu sekundit laulust on mängitud
        self.Hetkeaeg_laulus = int(pygame.mixer.music.get_pos() / 1000 + self.enne_scrollimist)
        # Teisendab hetkeaja laulus formaadiks MM:SS
        self.Hetkeaeg_laulus_kena_visuaalselt = time.strftime('%M:%S', time.gmtime(self.Hetkeaeg_laulus))
        # Uuendab hetkeaja teksti graafilisel liidesel
        self.hetke_aeg.config(text=str(self.Hetkeaeg_laulus_kena_visuaalselt) + ' / ' + str(self.laulupikkus_kena_visuaalselt))
        #Muudab graafilisel liidesel väärtust
        
        # Kontrollib, kas funktsioon valifail on korra tehtud, sest muidu prindib iga 100ms tagant errori "Error laulupositsiooni scrollbar'il näitamisel"
        if not(self.valifailkorratehtud):
            pass
        else:
            try:
                # Uuendab laulu positsiooni scroll bar'i väärtust vastavalt hetkeajale laulus
                self.lauluscrollslider.config(value=(self.Hetkeaeg_laulus * 100) / self.laulupikkus)
            except:
                print("Error laulupositsiooni scrollbar'il näitamisel")
                
        # Kutsub ennast uuesti välja pärast 100ms, et jätkata sündmuste kontrollimist      
        self.root.after(100, self.Event_Kontroll)
        
    # Kuvab uues aknas laulusõnad
    def Lüürika_aken(self):
        # Loob uue akna lüürika (laulusõnade) kuvamiseks
        uus_aken = tk.Toplevel(self.root)
        uus_aken.title("Laulusõnad")


        # Loob kerimisriba (scrollbar) ja tekstivälja (text widget) lüürika jaoks
        scrollbar = tk.Scrollbar(uus_aken)
        self.tekstwidget = tk.Text(uus_aken, wrap='none', yscrollcommand=scrollbar.set)

        # Seadistab kerimisriba töötama koos tekstiväljaga
        scrollbar.config(command=self.tekstwidget.yview)
        scrollbar.pack(side='right', fill='y')

        # Paigutab tekstivälja aknasse
        self.tekstwidget.pack(side='left', fill='both', expand=True)
        
        # Sisestab lüürika tekstiväljale
        self.tekstwidget.insert('1.0', self.lüürika)
    
    # Mängib või peatab laulu
    def playpause(self):
        # Kontrollib, kas muusika on hetkel peatatud või ei mängi
        if pygame.mixer.music.get_busy() == False:
             # Kui muusika on pausil, jätkatakse mängimist
            if self.musicOnPaused:
                pygame.mixer.music.unpause()
                self.musicOnPaused = False
            # Kui muusika on peatatud, alustatakse uue laulu mängimist
            else:
                self.hetkelmängivalauluindeks = -1
                self.hetkelmängivalauluindeks += 1
                pygame.mixer.music.load(self.lauludejärjend[self.hetkelmängivalauluindeks])
                pygame.mixer.music.play()
                self.musictööolek = True
                # Uuendatakse failiinfot uue laulu jaoks
                self.Failimuutus()
        # Kui muusika mängib, pannakse see pausile
        else:
            self.musictööolek = False
            self.musicOnPaused = True
            pygame.mixer.music.pause()

    # Valib faili laadimiseks              
    def valifail(self):
        self.lauludejärjend = self.originaaljärjend # Taastab laulude järjendi algsele kujule, seda on vaja teise funktsiooni playlistirepeat jaoks ja funktsiooni shuffle jaoks.
        # Avab failivaliku dialoogi, võimaldades kasutajal valida helifaile. Aknas kuvab ainult neid helifaile: '*.flac *.mp3 *.wav *.aac *.ogg *.wma *opus *.alac *.mid'
        self.failinimi = filedialog.askopenfilenames(title="Vailge helifail mida mängida", initialdir=os.path.expanduser('~/music'), filetypes=[('Audio Files', '*.flac *.mp3 *.wav *.aac *.ogg *.wma *opus *.alac *.mid')])
        #Kui kasutaja ei valinud midagi, siis ei tehta midagi
        if self.failinimi == None:
            pass
        # Kui kasutaja valib faile, lisatakse need laulude järjekorda
        else:
            for i in self.failinimi: #Viide: https://www.geeksforgeeks.org/how-to-add-music-playlist-in-pygame/
                self.lauludejärjend.append(i)
        # Tehakse koopia originaaljärjendist tuleviku tarbeks, samuti seotud funktsiooniga playlistirepeat
        self.originaaljärjend = copy.deepcopy(self.lauludejärjend)
        # Märgib, et faili valik on korra tehtud, seda on vaja et funktsioonis Event_kontroll ei tekiks erroreid.
        self.valifailkorratehtud = True
        # Uuendab failiinfot uute valitud failide põhjal
        self.Failimuutus()
    
    # Mängib järgmist laulu
    def järgminelaul(self):
        # Kontrollib, kas järjekorda on tühjendatud, seda on vaja, et saaks valitud õige hetkel mängiva laulu indeks
        if self.TühjendatiJärjekorda:
            self.hetkelmängivalauluindeks = 0
            self.TühjendatiJärjekorda = False
        # Kontrollib, kas on aktiveeritud kordusfunktsioon ühele laulule
        if self.ükslaulrepeat:
            # Laeb sama laulu uuesti ja mängib seda
            pygame.mixer.music.load(self.lauludejärjend[self.hetkelmängivalauluindeks])
            pygame.mixer.music.play()
            self.enne_scrollimist = 0.0
            self.musictööolek = True
            # Uuendab failiinfot
            self.Failimuutus()
        # Kontrollib, kas järjekord on lõpus ja kas järjekorra kordamine on aktiveeritud, kui mõlemad on tööl, siis alustab laulude järjendi algusest
        elif len(self.lauludejärjend) <= self.hetkelmängivalauluindeks + 1 and self.playlistrepeat:
            self.hetkelmängivalauluindeks = 0
            pygame.mixer.music.load(self.lauludejärjend[self.hetkelmängivalauluindeks])
            pygame.mixer.music.play()
            self.musictööolek = True
            self.enne_scrollimist = 0.0
            # Uuendab failiinfot
            self.Failimuutus()
        elif len(self.lauludejärjend) <= self.hetkelmängivalauluindeks + 1:
             # Kui järjekord on lõpus ja kordamine pole aktiveeritud, ei tehta midagi
            pass
        else:
            # Mängib järgmist laulu, kui kõik eelnev ei kehti
            self.hetkelmängivalauluindeks += 1
            pygame.mixer.music.load(self.lauludejärjend[self.hetkelmängivalauluindeks])
            pygame.mixer.music.play()
            self.musictööolek = True
            self.enne_scrollimist = 0.0
            self.Failimuutus()
    # Mängib eelmist laulu
    def eelminelaul(self):
        self.ükslaulrepeat = False #Kui keritakse tagasi, siis ei hakka tagasikeritud laulu korduvalt mängima, vaid ükslaulrepeat läheb False
        # Kontrollib, kas hetkeajast laulus on möödunud rohkem kui 2 sekundit, kui on siis laeb sama laulu algusest
        if self.Hetkeaeg_laulus > 2:
            pygame.mixer.music.load(self.lauludejärjend[self.hetkelmängivalauluindeks])
            pygame.mixer.music.play()
            self.enne_scrollimist = 0.0
        # Kontrollib, kas järjekorda on hiljuti tühjendatud
        if self.TühjendatiJärjekorda:
            # Kui järjekord on tühjendatud, alustatakse esimesest laulust
            self.hetkelmängivalauluindeks = 0
            self.TühjendatiJärjekorda = False
        # Kontrollib, kas praegu mängitav laul on esimene järjekorras ja kas playlistrepeat on aktiveeritud
        if self.hetkelmängivalauluindeks == 0 and self.playlistrepeat:
             # Liigub järjekorras viimase laulu juurde
            self.hetkelmängivalauluindeks = len(self.lauludejärjend) - 1
            pygame.mixer.music.load(self.lauludejärjend[self.hetkelmängivalauluindeks])
            pygame.mixer.music.play()
            self.enne_scrollimist = 0.0
            # Uuendab failiinfot
            self.Failimuutus()
        elif self.hetkelmängivalauluindeks == 0:#Kui on järjekorra esimene lugu, siis ei tohiks lubada tagasi minna (muidu läheks järjekorra viimase loo juurde), kuid sinna tohib minna ainult siis kui playlistrepeat on lubatud
            pass
        else:
            # Kui kõik muu ei kehti, siis liigub eelmisele laulule järjekorras
            self.hetkelmängivalauluindeks -= 1
            pygame.mixer.music.load(self.lauludejärjend[self.hetkelmängivalauluindeks])
            pygame.mixer.music.play()
            self.enne_scrollimist = 0.0
            # Uuendab failiinfot
            self.Failimuutus()
            
    def keriedasi(self):
         # Laeb praegu mängiva laulu uuesti
        pygame.mixer.music.load(self.lauludejärjend[self.hetkelmängivalauluindeks])
        self.enne_scrollimist = self.Hetkeaeg_laulus + 30 # Määrab uue alguspunkti laulus, lisades praegusele ajale 30 sekundit
        pygame.mixer.music.play(loops=0, start=self.enne_scrollimist) # Mängib laulu uuest kohast
        
    def keritagasi(self):
         # Laeb praegu mängiva laulu uuesti
        pygame.mixer.music.load(self.lauludejärjend[self.hetkelmängivalauluindeks])
        # Kontrollib, kas praegusest ajast 10 sekundit tagasi on suurem kui 0
        if self.Hetkeaeg_laulus - 10 < 0:
            self.enne_scrollimist = 0 # kui tagasi keeramisel 10 sec peaks tulema negatiivne arv, siis alustatkse laulu algusest
        else:
            # Määrab uue alguspunkti laulus, lahutades praegusest ajast 10 sekundit
            self.enne_scrollimist = self.Hetkeaeg_laulus - 10
        pygame.mixer.music.play(loops=0, start=self.enne_scrollimist) # Mängib laulu uuest kohast
    
    def shuffle(self):
        # Kontrollib, kas juhusliku esituse (shuffle) režiim on juba aktiveeritud
        if self.shuffletöömääraja: # Kui režiim on aktiveeritud, taastatakse laulude järjekord algseks
            self.lauludejärjend = self.originaaljärjend
            self.shuffletöömääraja = False
            # Uuendab laulude järjekorda kasutajaliideses
            self.laulude_järjekord()
        else:
            # Kui režiim pole aktiveeritud, tehakse algsest järjendist koopia
            self.originaaljärjend = copy.deepcopy(self.lauludejärjend)
            random.shuffle(self.lauludejärjend) # Segatakse laulude järjekord juhuslikult
            self.shuffletöömääraja = True
            # Uuendab laulude järjekorda kasutajaliideses
            self.laulude_järjekord()
            
    def playlistirepeat(self):
        # Kontrollib, kas järjekorra kordamine (playlist repeat) on aktiveeritud
        if self.playlistrepeat:
            self.playlistrepeat = False # Kui järjekorra kordamine on aktiveeritud, deaktiveeritakse see
            self.laulude_järjekord() # Uuendab laulude järjekorda kasutajaliideses
        else: # Kui järjekorra kordamine pole aktiveeritud, aktiveeritakse see
            self.playlistrepeat = True
            self.laulude_järjekord() # Uuendab laulude järjekorda kasutajaliideses
            
    def ühelaulurepeat(self):
        if self.ükslaulrepeat: # Kontrollib, kas üksiku laulu kordamine on aktiveeritud
            self.ükslaulrepeat = False
        else: # Kui üksiku laulu kordamine pole aktiveeritud, aktiveeritakse see
            self.ükslaulrepeat = True
        #Seda väärtust kasutatakse teiste funktsioonide sees.
    
    #volüümi slider
    def slider_väärtused(self, väärtus):
        # Seadistab muusika helitugevuse vastavalt slideri positsioonile
        # 'väärtus' on sliderilt saadud helitugevuse väärtus (0 kuni 100)
        pygame.mixer.music.set_volume(float(väärtus) / 100.0)
        
    def scrollilaulus(self, väärtus):
        # Seadistab laulu esituspositsiooni vastavalt slideri positsioonile
        # 'väärtus' on sliderilt saadud positsiooni väärtus (0 kuni 100)
        self.enne_scrollimist = float((float(väärtus)*self.laulupikkus)/100.0)
        #Laeb laulu uuesti ja mängib vastavalt väärtusele valitud laulu kohast.
        pygame.mixer.music.load(self.lauludejärjend[self.hetkelmängivalauluindeks])
        pygame.mixer.music.play(loops=0, start=self.enne_scrollimist)
        
    def tühjendajärjekord_fuktsioon(self):
        # Proovib tühjendada kogu laulude järjekorra, va hetkelmängitav laul, mis saab järjekorra esimeseks lauluks
        try:
            # Säilitab praegu esitatava laulu
            praegune_esitatav_laul = self.lauludejärjend[self.hetkelmängivalauluindeks]
            # Tühjendab laulude järjekorra
            self.lauludejärjend = []
            self.originaaljärjend = []
            # Lisab praegu esitatava laulu tühjendatud järjekorda
            self.lauludejärjend.append(praegune_esitatav_laul)
            self.originaaljärjend.append(praegune_esitatav_laul)
            # Märgib, et järjekord on tühjendatud
            self.TühjendatiJärjekorda = True
            # Uuendab failiinfot uue järjekorraga
            self.Failimuutus()
        except:
            # Kui tühjendamisel tekib viga, ignoreeritakse seda (näiteks kui järjekord on juba tühi)
            pass
    
    def sulgemine(self):
        pygame.mixer.quit() # Peatab pygame mixer #https://www.pygame.org/docs/ref/mixer.html
        self.root.destroy() # Sulgeb Tkinteri akna
        sys.exit() # Lõpetab kogu programmi
    
    # Klassi konstruktor, määratleb algseadistused ja loob kasutajaliidese
    def __init__(self):
        pygame.mixer.music.set_endevent(Muusika_Lõpp) # Määrab pygame mixerile, millist sündmust kasutada muusika lõppemise tuvastamiseks.
        # 'Muusika_Lõpp' on konstant, mis tähistab seda sündmust.
        
        # Kutsub välja meetodi 'valmista_põhi', mis loob ja seadistab kasutajaliidese.
        # See hõlmab akna loomist, nuppude ja teiste graafiliste elementide lisamist.
        self.valmista_põhi()
    
     # Loob ja kuvab peamise kasutajaliidese akna
    def valmista_põhi(self):
        
        self.root = tk.Tk() # Loo peamine Tkinteri aken

        self.root.geometry("1000x600") # Seadista akna suurus ja pealkiri
        self.root.title("Muusikamängija") # Akna pealkiri
        
        # Taustavärv   
        self.root.configure(bg='white')
       
      #  Loob ja paigutab eelmise laulu/tagasikerimise
        self.eelminelaul_nupp = tk.Button(self.root, text="⏮", font=("Arial", 10), command=self.eelminelaul, fg='indigo', bg='white')
        self.eelminelaul_nupp.place(x=335, y=500)
        
        self.keritagasi_nupp = tk.Button(self.root, text="⏪", font=("Arial", 10), command=self.keritagasi,fg='indigo', bg='white')
        self.keritagasi_nupp.place(x=435, y=500)
       
       # Loob ja paigutab play/pause nupu
        self.playPause_nupp = tk.Button(self.root, text="⏯", font=("Impact", 10), command=self.playpause, fg='indigo', bg='white')
        self.playPause_nupp.place(x= 485, y=499)
        # Seadistab muutujad muusika mängimise oleku jälgimiseks
        self.laululõpukontrollija = False
        self.musicOnPaused = False
        
        self.lauluscrollslider = ttk.Scale(self.root, from_=0, to = 100, orient=HORIZONTAL, value=0, length= 400, command=self.scrollilaulus, ) #https://www.youtube.com/watch?v=s_YUe0z09XU&t=3s&ab_channel=Codemy.com
        self.lauluscrollslider.place(x=300, y=450)
        style = ttk.Style()
        style.configure("TScale", background= "white")
        self.enne_scrollimist = 0.0
        
        
        # Loob ja paigutab faili valimise nupu
        self.Fail_nupp = tk.Button(self.root, text="Fail", font=("Arial", 11), command=self.valifail, fg='indigo', bg='white')
        self.Fail_nupp.place(x=480, y=400)
        # Seadistab muutujad laulude järjekorra ja hetkel mängiva laulu indeksi jälgimiseks
        self.originaaljärjend = []
        self.lauludejärjend = []
        self.valifailkorratehtud = False
        self.hetkelmängivalauluindeks = 0
        
        self.keriedasi_nupp = tk.Button(self.root, text="⏩", font=("Arial", 10), command=self.keriedasi, bg= 'indigo', fg= 'white', highlightbackground="white", highlightcolor="white")
        self.keriedasi_nupp.place(x=535, y=500)
        
        # Loob ja paigutab nupud järgmise ja eelmise laulu jaoks ning kerimiseks edasi-tagasi nupud
        self.järgminelaul_nupp = tk.Button(self.root, text="⏭", font=("Arial", 10), command=self.järgminelaul, bg= 'indigo', fg= 'white')
        self.järgminelaul_nupp.place(x=635, y=500)
        
       
        
        
        
        # Loob ja paigutab juhusliku esituse ja kordusfunktsioonide nupud
        self.shuffle_nupp = tk.Button(self.root, text="🔀", font=("Arial", 11), command=self.shuffle, bg= 'indigo', fg= 'white')
        self.shuffle_nupp.place(x=735, y=499)
        self.shuffletöömääraja = False
        
        self.playlistrepeat_nupp = tk.Button(self.root, text="⟳ Playlist", font=("Arial", 11), command=self.playlistirepeat, fg='indigo', bg='white')
        self.playlistrepeat_nupp.place(x=50, y=500)
        self.playlistrepeat = False
        
        self.ükslaulrepeat_nupp = tk.Button(self.root, text="⟳ Laul", font=("Arial", 11), command=self.ühelaulurepeat, fg='indigo', bg='white')
        self.ükslaulrepeat_nupp.place(x=150, y=500)
        self.ükslaulrepeat = False
        
        # Loob ja paigutab helitugevuse ja laulu positsiooni reguleerimise sliderid
        self.volüümslider = ttk.Scale(self.root, from_=0, to=100, length=100, command=self.slider_väärtused, orient=HORIZONTAL,)
        self.volüümslider.set(100)
        self.volüümslider.place(x=825, y=480)
        stiil = ttk.Style()
        stiil.configure("TLabel", background="white")
        volüümi_ikoon_tekst = tk.StringVar()
        volüümi_ikoon_tekst.set("🔊")
        volüümi_ikoon_silt = ttk.Label(self.root, textvariable= volüümi_ikoon_tekst, font=("Arial", 14))
        volüümi_ikoon_silt.place(x=800, y=476)
        
        # Loob ja paigutab lüürika ja järjekorra tühjendamise nupud
        self.Lüürika_leht_nupp = tk.Button(self.root, text="Lüürika", font=("Arial", 11), command=self.Lüürika_aken, fg='indigo', bg='white')
        self.Lüürika_leht_nupp.place(x=471, y=550)
        
        self.tühjendajärjekord_nupp = tk.Button(self.root, text="Tühjenda järjekord", font=("Arial", 10), command=self.tühjendajärjekord_fuktsioon, fg='white', bg='indigo')
        self.tühjendajärjekord_nupp.place(x=800, y=550)
        self.TühjendatiJärjekorda = False
        
        # Loob ja paigutab erinevad teabe kuvamiseks mõeldud tekstisildid
        tekstiraam = tk.Frame(self.root)
        tekstiraam.pack()
        
        self.hetke_aeg = Label(self.root, text = '', bd=1, anchor=E, bg='white', fg= 'indigo')
        self.hetke_aeg.place(x=460, y=472)
        self.laulupikkus_kena_visuaalselt = '00:00'
        
        self.artisti_nimi_tekst = Label(self.root, text = 'Lae laul, et näidata artisti nime', bd=1, anchor=E, bg='white', fg= 'indigo')
        self.artisti_nimi_tekst.place(x=20, y=20)
        
        self.laulu_nimi_tekst = Label(self.root, text = 'Lae laul, et näidata laulunime', bd=1, anchor=E, bg='white', fg= 'indigo')
        self.laulu_nimi_tekst.place(x=20, y=40)
        
        self.albumi_nimi_tekst = Label(self.root, text = 'Lae laul, et näidata albuminime', bd=1, anchor=E, bg='white', fg= 'indigo')
        self.albumi_nimi_tekst.place(x=20, y=60)
        
        self.väljaandmis_aasta_tekst = Label(self.root, text = 'Lae laul, et näidata väljaandmisaastat', bd=1, anchor=E, bg='white', fg= 'indigo')
        self.väljaandmis_aasta_tekst.place(x=20, y=80)
        
        self.laulupikkus_tekst = Label(self.root, text = '00:00', bd=1, anchor=E, bg='white', fg= 'indigo')
        self.laulupikkus_tekst.place(x=500, y=472)
        
        self.järjekordjärgmine_tekst = Label(self.root, text = 'Järjekorras järgmised laulud on:', bd=1, anchor=E, bg='white', fg= 'indigo')
        self.järjekordjärgmine_tekst.place(x=650, y=20)
        
        self.järjekord_tekst = Label(self.root, text = '', bd=1, anchor=E, bg='white', fg= 'indigo')
        self.järjekord_tekst.place(x=650, y=50)
        
        
        
        
        # Seadistab akna sulgemise käitumist, seostades akna sulgemissündmuse sulgemisfunktsiooniga
        self.root.protocol("WM_DELETE_WINDOW", self.sulgemine)
        
        # Käivitab sündmuste kontrolli funktsiooni
        self.Event_Kontroll()
        
        # Käivitab Tkinteri sündmustsükli
        self.root.mainloop()
    
UI()

