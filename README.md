# Projekt Elections Scraper

Script main.py byl vytvořen jako třetí projekt v rámci Engeto Online Python Akademie.

## Cíl programu

Cílem projektu bylo vytvoření programu, který extrahuje data z výsledků voleb do Poslanecké sněmovny Parlamentu ČR z roku 2017 dostupných [zde](https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ).

## Použité knihovny

Soubor requirements obsahuje použité knihovny, které se doporučují nainstalovat v separátním virtuálním prostředí.

### Příkazy pro instalaci knihoven třetích stran:
```
pip install requests
pip install bs4
```
## Spuštění programu

Uživatel zadá do příkazového řádku dva argumenty:

1. URL - Odkaz na konkrétní okres
2. Název souboru - s příponou .csv

a to ve formátu python main.py ‘URL’ ‘Název souboru’.

## Ukázka spuštění programu
```
python main.py 'https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=14&xnumnuts=8106' 'Ostrava.csv'
```
Program vytvoří soubor ve formátu CSV s výsledky voleb pro daný okres.

