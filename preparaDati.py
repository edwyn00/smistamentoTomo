import sys
import PyQt5
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QPushButton, QCheckBox, QScrollArea
from PyQt5.QtCore import Qt, QSize
import json
from functools import partial
from datetime import date
import pandas as pd
import os
import json
import math
import threading
import time

def prepare_data():
    path_dati_input = "./ProgrammaSimone"
    path_dati_output = "./nonToccare"

    if not os.path.exists(path_dati_output):
        os.mkdir(path_dati_output)

    path_lista   = path_dati_input + '/lista.xlsx'
    path_testate = path_dati_input + '/testate.xlsx'
    path_ultimi  = path_dati_input + '/ultimi.xlsx'


    aux_data = pd.read_excel (r''+path_lista)
    lista_nomi = aux_data['Cognome e Nome'].to_list()
    lista_stato = aux_data['Abbonamento'].to_list()
    lista_bloccati = []
    num_bloccati = 0
    for i in range(len(lista_nomi)):
        if lista_stato[i] == "BLOCCATO":
            lista_bloccati.append(lista_nomi[i].lower())
            num_bloccati += 1

    #print("LEN LISTA BLOCCATI:", num_bloccati)
    #print("LISTA BLOCCATI:\n", lista_bloccati, '\n\n')

    data = pd.read_excel (r''+path_testate)

    #stato_abbonato_old  = data['TESSERE E ABBONAMENTI::Stato Tessera'].to_list()
    abbonati_old        = data['Abbonato'].to_list()
    testata_old         = data['Testata'].to_list()
    editore_old         = data['Editore'].to_list()
    num_copie_old       = data['N° Copie'].to_list()

    abbonati        = []
    testate         = []
    editori         = []
    num_copie       = []

    seg = 0
    for i, t in enumerate(testata_old):
        if "dune" in t.lower():
            print(t, abbonati_old[i])
            print(i)
            seg = i

    print(seg, len(num_copie_old))
    for i in range(len(num_copie_old)):
        if i == seg:
            print("ecco")
            #print(stato_abbonato_old[i], abbonati_old[i])
        #if stato_abbonato_old[i] == 0 and abbonati_old[i] != '':
        if abbonati_old[i] != '':
            problem=False
            if editore_old[i] != editore_old[i]:
                continue
            for elem in lista_bloccati:
                str1 = list(elem.lower())
                str1.sort()
                str2 = list(abbonati_old[i].lower())
                str2.sort()
                str1 = ''.join(str1)
                str2 = ''.join(str2)
                if str1==str2:#cmp_strings(abbonati_old[i].lower(), elem.lower()):
                    problem = True
            if problem:
                continue
            abbonati.append(abbonati_old[i].upper().strip())
            testate.append(testata_old[i].upper().strip())
            editori.append(editore_old[i].upper().strip())
            num_copie.append(num_copie_old[i])

    # for i in range(len(abbonati)):
    #     print(abbonati[i], testate[i], num_copie[i])

    for elem in testate:
        if "DUNE" in elem:
            print(elem, "DUNE")
    tot = {}
    for i in range(len(abbonati)):
        titolo = testate[i] + " || " + editori[i]

        if titolo not in tot.keys():
            if "dune" in titolo.lower():
                print(titolo, "DUNE DUNE")
            tot[titolo] = {}
            tot[titolo]['testata']  = testate[i]
            tot[titolo]['editore']  = editori[i]
            tot[titolo]['abbonati'] = {}
        tot[titolo]['abbonati'][abbonati[i]] = num_copie[i]

    ultimo = pd.read_excel(path_ultimi)
    dd = ultimo['Articolo'].to_list()
    ultimi = {}
    for elem in dd:
        if '#' not in elem:
            continue
        nome_aux = elem.split('#')[0].upper().strip()
        numero_aux = elem.split('#')[1].upper().strip().split(' ')[0]
        ultimi[nome_aux] = numero_aux

    json.dump(ultimi, open(os.path.join(path_dati_output,"ultimi.json"), 'w'))
    json.dump(tot, open(os.path.join(path_dati_output,"abbonamenti.json"), 'w'))



class mainPage(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)


        self.fontSize = 45

        self.layout = QtWidgets.QGridLayout()

        self.h = 1200
        self.w = 1000
        self.setGeometry(0, 100, self.w, self.h)
        self.setWindowTitle('Nuvole 104')
        self.setWindowIcon(QtGui.QIcon('./nonToccare/logo.png'))

        self.oImage = QtGui.QImage("./nonToccare/background.png")
        #self.oImage = QtGui.QImage("bg.jpg")
        sImage = self.oImage.scaled(QSize(self.w, self.h))                   # resize Image to widgets size

        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(sImage))
        self.setPalette(palette)


        self.label_testata = QtWidgets.QLabel("STO PREPARANDO I DATI")

        self.label_testata.setFont(QtGui.QFont('Times', self.fontSize))
        self.label_testata.setStyleSheet("color: white; background-color: purple")

        self.layout.addWidget(self.label_testata, 80, 0)
        self.setLayout(self.layout)


    def prepara_dati(self):

        start = time.time()
        t = threading.Thread(name='non-daemon', target=prepare_data)
        t.start()
        t.join()
        self.label_testata.setParent(None)
        if (time.time() - start) < 20:
            self.label_testata = QtWidgets.QLabel("Forse qualcosa è andato storto : (\nCompara i file excel con quelli del mese precedente.\n In alternativa contatta Edoardo")
        else:
            self.label_testata = QtWidgets.QLabel("HO FINITO!\nGRAZIE PER L'ATTESA :)")


        self.label_testata.setFont(QtGui.QFont('Times', self.fontSize))
        self.label_testata.setStyleSheet("color: white; background-color: purple")

        self.layout.addWidget(self.label_testata, 80, 0)
        self.setLayout(self.layout)

def main():


    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('QtCurve')

    main_page = mainPage()

    main_page.show()
    main_page.prepara_dati()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
