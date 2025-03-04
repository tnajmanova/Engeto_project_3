"""
main.py: třetí projekt do Engeto Online Python Akademie

author: Tereza Najmanova
email: najmanova.tereza@gmail.com
"""
import csv
import os
import sys
import requests
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup

def zadani() -> tuple:
    '''
    Funkce vytvoří zadání pomocí dvou argumentů v příkazovém řádků.
    '''
    if len(sys.argv) != 3:
        print('Zadejte prosím příkaz ve formátu: python main.py "URL" "nazev_souboru.csv"')
        sys.exit()
    elif not sys.argv[2].endswith('.csv'):
        print('Zadejte prosím název souboru s příponou .csv')
        sys.exit()
    else:
        return sys.argv[1], sys.argv[2]

def ziskani_html(url: str) -> BeautifulSoup:
    ''' 
    Funkce získá HTML kód ze zadané URL adresy.
    '''
    odpoved_serveru = requests.get(url)
    soup = BeautifulSoup(odpoved_serveru.text, 'html.parser')
    return soup

def ziskani_kodu_lokace(soup: BeautifulSoup, index: int) -> str:
    '''
    Funkce vyhledá buňky s kódy jednotlivých lokací (obcí) a pomocí indexu získaného z funkce scrapovani_obce() vrací postupně jejich hodnoty. 
    
    Aby program neskončil chybou IndexError, výjimka je ošetřena pomocí try / except.
    '''
    td_kod = soup.find_all('td', {'class':'cislo'})
    try:
        kod = td_kod[index].get_text() 
    except IndexError:
        kod = None
    return kod

def vytvoreni_url_lokace(url: str, kod_lokace: str) -> str:
    '''
    Funkce vrací URL adresu konkrétní lokace (obce). Ze zadané URL adresy pomocí knihovny urllib.parse získá kód kraje a okresu.
    '''
    parsovane_url = urlparse(url)
    parametry_url = parse_qs(parsovane_url.query)
    kod_kraje = parametry_url.get('xkraj', [None])[0]
    kod_okresu = parametry_url.get('xnumnuts', [None])[0]
    url_lokace = 'https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj='+ kod_kraje +'&xobec=' + kod_lokace + '&xvyber=' + kod_okresu
    return url_lokace

def ziskani_nazvu_stran(soup: BeautifulSoup) -> list:
    '''
    Funkce vyhledá buňky s názvy politických stran a vytvoří jejich seznam.
    '''
    vsechny_td = soup.find_all('td', {'class':'overflow_name'})
    nazvy = [td.get_text() for td in vsechny_td]
    return nazvy

def vytvoreni_hlavicky(nazvy: list) -> list:
    '''
    Funkce vytvoří hlavičku sloučením dvou seznamů.
    '''
    zadane_zahlavi = ['code', 'location', 'registered', 'envelopes', 'valid']
    hlavicka = [*zadane_zahlavi, *nazvy]
    return hlavicka

def ziskani_lokace(soup: BeautifulSoup, index: int) -> str:
    '''
    Funkce vyhledá řádky všech tabulek, vyselektuje ty s dvěma sloupci a vrací hodnotu z druhého sloupce. Řeší problém, kdy jednotky 
    názvů lokací (obcí) jsou na některých stránkách pod rozdílnou HTML strukturou (elementem <a>).

    Pomocí indexu získaného z funkce scrapovani_obce() vrací postupně hodnoty ze seznamu. Aby program neskončil chybou 
    IndexError, výjimka je ošetřena pomocí try / except.
    '''
    seznam_lokaci = []

    tr_lokace = soup.find_all('tr')
    for radek in tr_lokace:
        if radek.find("a", href=True):
            bunky = radek.find_all('td')
            if len(bunky) > 1:
                nazev_lokace = bunky[1].get_text()
                seznam_lokaci.append(nazev_lokace)
    try:
        lokace = seznam_lokaci[index]
    except IndexError:
        lokace = None
    return lokace

def ziskani_cisel(soup: BeautifulSoup) -> list:
    '''
    Funkce vyhledá buňky s obecnými daty a vytřídí do seznamu počty voličů, vydaných obálek a platných hlasů jedné lokace (obce).
    '''
    vsechna_cisla = soup.find_all('td', {'class':'cislo'})
    cisla = [cislo.get_text() for cislo in vsechna_cisla]
    registrovano_obalky_platne = [cisla[3], cisla[4], cisla[7]]
    return registrovano_obalky_platne

def ziskani_hlasu(soup: BeautifulSoup) -> list:
    '''
    Funkce vyhledá buňky s počty hlasů jednotlivých politických stran a vytvoří jejich seznam.
    '''
    vsechny_hlasy = soup.find_all('td', {'class':'cislo', 'headers': ['t1sb3', 't2sb3']})
    hlasy = [hlas.get_text() for hlas in vsechny_hlasy]
    return hlasy

def vyber_dat(kod_lokace: str, lokace: str, cisla: list, hlasy: list) -> list:
    '''
    Funkce vytvoří sloučením seznam dat, které bude později přidávat do existujícího CSV souboru.
    '''
    spojeny_seznam = [kod_lokace, lokace, *cisla, *hlasy]
    return spojeny_seznam

def vytvoreni_nebo_zapis_do_csv(nazev_csv: str, soup: BeautifulSoup, data: list) -> None:
    '''
    Funkce nejprve vytvoří CSV soubor (pokud už neexistuje) a zapíše do něj vytvořenou hlavičku.
    Pokud soubor již existuje zapíše do něj příslušná data.
    '''
    if not os.path.exists(nazev_csv):
        nazvy_stran = ziskani_nazvu_stran(soup)
        hlavicka = vytvoreni_hlavicky(nazvy_stran)
        with open(nazev_csv, mode='w', newline='', encoding='UTF-8') as nove_csv:
            zapisovac = csv.writer(nove_csv)
            zapisovac.writerow(hlavicka)

    with open(nazev_csv, mode='a', newline='', encoding='UTF-8') as existujici_csv:
        zapisovac = csv.writer(existujici_csv)
        zapisovac.writerow(data)

def scrapovani_obce(soup_okres: BeautifulSoup, url: str, nazev_csv: str) -> None:
    '''
    Funkce postupně spouští scrapování všech obcí (lokací), získá příslušná data a zapíše je do CSV souboru.
    '''
    index = 0
    while True:
        data_kod_lokace = ziskani_kodu_lokace(soup_okres, index)
        data_lokace = ziskani_lokace(soup_okres, index)
        if data_kod_lokace == None:
            break
        else:
            index += 1 
        url_obec = vytvoreni_url_lokace(url, data_kod_lokace)
        soup_obec = ziskani_html(url_obec)
        data_cisla = ziskani_cisel(soup_obec)
        data_hlasy = ziskani_hlasu(soup_obec)
        data_do_csv = vyber_dat(data_kod_lokace, data_lokace, data_cisla, data_hlasy)
        vytvoreni_nebo_zapis_do_csv(nazev_csv, soup_obec, data_do_csv)
        
def hlavni_funkce() -> None:
    '''
    Hlavní funkce programu. Uživatel zadá vstupní data, které program zpracuje a dále díky nim projde veškeré 
    obce (lokace) a připraví CSV soubor.
    '''
    url, nazev_csv = zadani()
    soup_okres = ziskani_html(url)
    print('Vytvářím Váš soubor ...')
    scrapovani_obce(soup_okres, url, nazev_csv)
    print('Váš soubor je připraven!')
  
hlavni_funkce()