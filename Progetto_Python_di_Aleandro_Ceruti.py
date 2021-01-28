import requests
import time
from datetime import datetime
import schedule

class Report:
    def __init__(self):
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.params = {
            'start': '1',
            'limit': '100',
            'convert': 'USD'
        }
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'd6c261ac-1898-4ff3-b231-fd500b4a46ff'
        }

        self.list = []

    def fetch_currencies_data(self):
        r = requests.get(url=self.url, params=self.params, headers=self.headers).json()
        return r['data']

def job():
    now = datetime.now()
    base_report = Report()
    all_data = base_report.fetch_currencies_data()


# 1- La criptovaluta con il volume maggiore (in $) delle ultime 24 ore

    best_volume = None # la criptovaluta con il volume maggiore nelle ultime 24h

    for x in all_data:
        if not best_volume or x['quote']['USD']['volume_24h'] > best_volume['quote']['USD']['volume_24h']:
            best_volume = x

            symbol = x['symbol']
            volume = x['quote']['USD']['volume_24h']

            diz_max_vol_24 = {
                'La criptovaluta con il volume maggiore (in $) delle ultime 24 ore': {
                f'{symbol}': volume
                }
            }
    base_report.list.append(diz_max_vol_24)


# 2- Le migliori e peggiori 10 criptovalute (per incremento in percentuale delle ultime 24 ore).

    # creo dizionario con tutti incrementi percentuali
    all_incremento = {}
    for x in all_data:
        s = x['symbol']
        p = x['quote']['USD']['percent_change_24h']
        all_incremento[f'{s}'] = p

    # ordino i valori di all_incremento (creando lista di tuple)
    ordered_incremento = sorted((value, key) for (key,value) in all_incremento.items())

    # qua peggiori 10 (lista ordinata)
    min_incremento = ordered_incremento[0:10]

    # dizionario peggiori 10
    diz_min_inc = {}
    for x in min_incremento:
        diz_min_inc[f'{x[1]}'] = x[0]

    # qua migliori 10 (lista ordinata)
    max_incremento = ordered_incremento[-10:]

    # dizionario migliori 10
    diz_max_inc = {}
    for x in max_incremento:
        diz_max_inc[f'{x[1]}'] = x[0]

    # li unisco in un dizionario unico
    diz_incremento = {
        'Le 10 migliori': diz_max_inc,
        'Le 10 peggiori': diz_min_inc
    }

    # aggiungo a baseReport.list
    diz_inc = {'Le migliori e peggiori 10 criptovalute (per incremento in percentuale delle ultime 24 ore)': diz_incremento}
    base_report.list.append(diz_inc)


# 3- La quantità di denaro necessaria per acquistare una unità di ciascuna delle prime 20 criptovalute.

    # lista capitalizzazione
    all_capitalizzazione = {}
    for x in all_data:
        s = x['symbol']
        i = x['quote']['USD']['market_cap']
        all_capitalizzazione[f'{s}'] = i

    # ordino i valori di all_capitalizzazione (creando lista di tuple)
    ordered_capitalizzazione = sorted((value, key) for (key,value) in all_capitalizzazione.items())

    # prime 20 per capitalizzazione da questa lista
    top_20_market_cap_list = ordered_capitalizzazione[-20:]

    # recupera le chiavi da questa lista
    chiavi = []
    for x in top_20_market_cap_list:
        p = x[1]
        chiavi.append(p)

    # creo dizionario con chiave, se presente in lista chiavi, e valore presi da allData
    diz_price = {}
    for x in all_data:
        if x['symbol'] in chiavi:
            a = x['symbol']
            b = x['quote']['USD']['price']
            diz_price[f'{a}'] = b

    # ora faccio la somma
    price_somma = sum(diz_price.values())

    price_somma_diz = {'Quantita per acquistare una unita di ciascuna delle prime 20 criptovalute per capitalizzazione, in $': price_somma}
    base_report.list.append(price_somma_diz)


# 4- La quantità di denaro necessaria per acquistare una unità di tutte le criptovalute il cui volume
# delle ultime 24 ore sia superiore a 76.000.000$.

    diz_unita = {}

    for x in all_data:
        if x['quote']['USD']['volume_24h'] > 76000000:
            simbolo = x['symbol']
            prezzo_unita = x['quote']['USD']['price']
            diz_unita[f'{simbolo}'] = prezzo_unita

    # Somma dei valori
    somma = sum(diz_unita.values())

    prezzo_somma = {'Quantita per acquistare una unita di ogni criptovaluta con capitalizzazione superiore a 76.000.000, in $': somma}
    base_report.list.append(prezzo_somma)


# 5- La percentuale di guadagno o perdita che avreste realizzato se aveste comprato una unità di ciascuna
# delle prime 20 criptovalute* il giorno prima (ipotizzando che la classifca non sia cambiata)

    # data di oggi
    data_oggi = now.strftime('%m%d%y')

    # dizionario prezzi ieri
    diz_somma_ieri = {}
    for x in all_data:
        if x['symbol'] in chiavi:
            xs = x['symbol']
            prezzo_adesso = x['quote']['USD']['price']
            incremento_percentuale_24h = x['quote']['USD']['percent_change_24h']

            # ora comincio i calcoli
            z = 100 + incremento_percentuale_24h
            prezzo_ieri_singola = 100*prezzo_adesso/z

            # aggiungo a dizionario
            diz_somma_ieri[f'{xs}'] = prezzo_ieri_singola

    # somma dei valori di diz_somma_ieri
    somma_prezzo_ieri = sum(diz_somma_ieri.values())


    # prezzo attuale = baseReport.list[2] = price_somma
    # prezzo attuale - vecchio (=somma_prezzo_ieri) = x; x * 100 / vecchio = percentuale che voglio
    differenza_prezzi = price_somma - somma_prezzo_ieri
    incremento_percentuale = differenza_prezzi * 100 / somma_prezzo_ieri

    # aggiungiamo anche questo a baseReport.list
    incremento_percentuale_diz = {'La percentuale di guadagno o perdita che avreste realizzato se aveste comprato una unita di ciascuna delle prime 20 criptovalute (per capitalizzazione) il giorno prima (ipotizzando classifica invariata)': incremento_percentuale}
    base_report.list.append(incremento_percentuale_diz)


    #---------------

    #file JSON
    import json
    with open(f"{data_oggi}.json", "w") as outfile:
        json.dump(base_report.list, outfile, indent=4)

    # -------------------------------

# ------ TEMPO CICLO
schedule.every().day.at("10:00").do(job)
while True:
    schedule.run_pending()
    time.sleep(1)