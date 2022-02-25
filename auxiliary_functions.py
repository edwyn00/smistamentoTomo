import sys
import json
from functools import partial
from datetime import date
import pandas as pd
import os
import json
import math

def write_risultati(smistamento):
    per_abbonato = {}
    indecisi     = {}
    rimanenti    = {}
    prezzi       = {}
    for step in smistamento.keys():
        if 'esito' not in smistamento[step].keys():
            continue
        if smistamento[step]['esito'] == "smistato":
            prezzi[smistamento[step]['nome_fornitore']] = smistamento[step]['prezzo']
            for articolo in smistamento[step]['testate'].keys():
                for abbonato in smistamento[step]['testate'][articolo].keys():
                    if abbonato not in per_abbonato.keys():
                        per_abbonato[abbonato] = {}
                    per_abbonato[abbonato][smistamento[step]['nome_fornitore']] = smistamento[step]['testate'][articolo][abbonato]

        elif smistamento[step]['esito'] == "indecisi":
            testata = smistamento[step]['testate']
            indecisi[testata] = smistamento[step]['numero']


        if 'rimanenti' in smistamento[step].keys():
            testata = smistamento[step]['nome_fornitore']
            rimanenti[testata] = smistamento[step]['rimanenti']



    sconto_arretrato = 1.0 - (float(open("scontoArretrato.txt", 'r').read())/100)
    sconto_abbonamento = 1.0 - (float(open("scontoAbbonamento.txt", 'r').read())/100)
    to_write_text = ''
    abbonati_ordinati = []
    for abbonato in per_abbonato.keys():
        abbonati_ordinati.append(abbonato)
    abbonati_ordinati.sort()
    for abbonato in abbonati_ordinati:
        to_write_text += str(abbonato) + '\n'
        for articolo in per_abbonato[abbonato].keys():
            to_write_text += ' - '+ articolo
            if per_abbonato[abbonato][articolo]['num'] >1:
                to_write_text += " ("+str(per_abbonato[abbonato][articolo]['num']) + ' copie)'
            to_write_text += '\n'
        to_write_text += '\n'

    to_write_text_alessia = ''
    for abbonato in abbonati_ordinati:
        to_write_text_alessia += "PER: " + str(abbonato) + "\n\n"
        to_write_text_alessia += open("fineMessaggio.txt", 'r').read()
        #to_write_text_alessia +=  'Ciao,\nTi scriviamo per informarti che ti sono arrivati questi al Tomo Club:\n'
        tot_prezzo = 0.0
        tot_prezzo_scontato = 0.0
        for articolo in per_abbonato[abbonato].keys():
            to_write_text_alessia += ' - '+ articolo
            to_write_text_alessia += ' [' + str(round(prezzi[articolo]*per_abbonato[abbonato][articolo]['num'],1))+ '€]'
            if per_abbonato[abbonato][articolo]['num'] >1:
                to_write_text_alessia += " ("+str(per_abbonato[abbonato][articolo]['num']) + ' copie)'
            to_write_text_alessia += '\n'
            tot_prezzo += prezzi[articolo]
            if per_abbonato[abbonato][articolo]['sconto'] == 'arretrato':
                tot_prezzo_scontato += round(((prezzi[articolo] *per_abbonato[abbonato][articolo]['num']) * sconto_arretrato),1)
            if per_abbonato[abbonato][articolo]['sconto'] == 'abbonamento':
                tot_prezzo_scontato += round(((prezzi[articolo]*per_abbonato[abbonato][articolo]['num']) * sconto_abbonamento),1)
        to_write_text_alessia += '\n\nIl tuo totale prima dello sconto è di ' + str(tot_prezzo) + '€\n'
        to_write_text_alessia += '\n\nIl tuo totale scontato è di ' + str(tot_prezzo_scontato) + '€\n'
        to_write_text_alessia += open("fineMessaggio.txt", 'r').read()
        #to_write_text_alessia += '\nTi aspettiamo ;)\n\nLo staff del Tomo\n'
        to_write_text_alessia += '___________________________________\n'

    to_write_indecisi = ''
    for testata in indecisi.keys():
        to_write_indecisi += testata + ' || ' + str(indecisi[testata]) + '\n'

    to_write_rimanenti = ''
    for testata in rimanenti.keys():
        to_write_rimanenti += testata + ' || ' + str(rimanenti[testata]) + '\n'

    file_risultato = open('./risultati/smistamento.txt', 'w')
    file_risultato.write(to_write_text)
    file_risultato.close()

    file_alessia = open('./risultati/Alessia.txt', 'w')
    file_alessia.write(to_write_text_alessia)
    file_alessia.close()

    file_indecisi = open('./risultati/indecisi.txt', 'w')
    file_indecisi.write(to_write_indecisi)
    file_indecisi.close()

    file_rimanenti = open("./risultati/rimanenti.txt", 'w')
    file_rimanenti.write(to_write_rimanenti)
    file_rimanenti.close()
    today = date.today()
    json.dump(smistamento, open("./nonToccare/json_data/"+ "json_" +str(today)+ ".json", 'w'))


def filtra_nome_testata(testata):
    if ' - ' in testata:
        testata = testata.split(' - ')[0]
    aux_testata = ''
    skip_lettera = False
    for lettera in testata:
        if not skip_lettera and '(' != lettera:
            aux_testata += lettera
        elif '(' == lettera:
            skip_lettera = True
        elif skip_lettera and ')' == lettera:
            skip_lettera = False
    testata = aux_testata
    testata = testata.strip()
    aux = testata.split(' ')
    testata = []
    for elem in aux:
        if elem != '':
            testata.append(elem)
    for c in testata[-1]:
        if c in '0123456789':
            testata = testata[:-1]
            break

    testata = ' '.join(testata)
    testata = testata.rstrip()
    return testata

def cerca_per_testata(target, data, threshold=10):
    risultati = {}
    target = filtra_nome_testata(target)
    print(target)
    for testata in data.keys():
        if target.lower() in testata.lower():
            risultati[testata] = data[testata]
            totale_copie = 0
            for abbonato in risultati[testata]['abbonati'].keys():
                totale_copie += int(risultati[testata]['abbonati'][abbonato])
            risultati[testata]['numero_copie'] = totale_copie

    if len(risultati.keys()) > threshold:
        articoli_filtrati = []
        articoli_trovati = list(risultati.keys())
        parole_articoli =   [len(x.split(' || ')[0].split(' ')) for x in articoli_trovati]
        len_testata =       len(target.split(' '))
        abs_diff =          [abs(len_testata - x) for x in parole_articoli]
        

        aux_val = 0
        while(len(articoli_filtrati)<threshold):
            for index in range(len(abs_diff)):
                if abs_diff[index] == aux_val:
                    articoli_filtrati.append(articoli_trovati[index])
        
            aux_val += 1
                

        if len(articoli_filtrati) > threshold:
            articoli_filtrati = articoli_filtrati[:threshold]
        risultati_filtrati = {}
        for articolo in risultati.keys():
            if articolo in articoli_filtrati:
                risultati_filtrati[articolo] = risultati[articolo]

        risultati = risultati_filtrati

    return risultati


def cerca_per_abbonato(target, data, threshold=5):
    risultato = []
    for chiave in data.keys():
        lista_abbonati = list(data[chiave]['abbonati'].keys())
        for abbonato in lista_abbonati:
            if target.lower() in abbonato.lower() and abbonato not in risultato:
                risultato.append(abbonato)
    if len(risultato) > threshold:
        return None
    return risultato


def trova_ultimo_numero(target, data):
    aux_name = target.split(' || ')[0].upper().strip()
    if aux_name in data.keys():
        return ' (ULTIMO ' + str(data[aux_name]) + ')'
    else:
        return ''


def prepara_excel(file_excel):
    codice = file_excel['Codice articolo'].to_list()
    editore = file_excel['Editore'].to_list()
    descrizione = file_excel['Descrizione'].to_list()
    quantità = file_excel['QuantitA\''].to_list()
    prezzi = file_excel['PrezzoListino'].to_list()
    prezziCent = file_excel['Sconto1'].to_list()
    bolla = {}
    doppioni_check = []
    iter = 0
    per_ordinare = {}
    for i in range(len(codice)):
        if editore[i] != editore[i]:
            break
        if codice[i] not in doppioni_check:
            bolla[int(iter)] = {}
            bolla[int(iter)]['editore'] = editore[i].upper()
            bolla[int(iter)]['descrizione'] = descrizione[i].upper().strip()
            bolla[int(iter)]['quantità'] = quantità[i]
            bolla[int(iter)]['codice'] = codice[i]
            bolla[int(iter)]['prezzo'] = float( str(int(prezzi[i])) + '.' + str(int(prezziCent[i])) ) 
            per_ordinare[descrizione[i].upper()] = iter
            iter += 1
            doppioni_check.append(codice[i])
        else:
            for idx in bolla.keys():
                if bolla[int(idx)]['descrizione'].strip() == descrizione[i].strip():
                    bolla[int(idx)]['quantità'] += quantità[i]

    bolla_ordinata = {}
    tt = []
    for kk in per_ordinare.keys():
        tt.append(kk)
    tt.sort()
    for elem, n in zip(tt, list(range(len(per_ordinare.keys())))):
        bolla_ordinata[int(n)] = bolla[per_ordinare[elem]]

    return bolla_ordinata

def num_results(target, where, what):
    return
