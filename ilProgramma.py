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
from auxiliary_functions import *

'''
Prezzi ('Prezzo netto')
preview prossimi
preview smistamento
Rimanenti                   DONE
'''


class mainPage(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.layout = QtWidgets.QGridLayout()

        self.fontSize = 15
        self.h = 1200
        self.w = 1000

        self.setGeometry(0, 100, self.w, self.h)
        self.setWindowTitle('Nuvole 104')
        self.setWindowIcon(QtGui.QIcon('logo.png'))

        self.oImage = QtGui.QImage("nonToccare/background.png")
        sImage = self.oImage.scaled(QSize(self.w, self.h))
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(sImage))
        self.setPalette(palette)

        self.idx = 0

        self.database      = json.load(open("nonToccare/abbonamenti.json"))
        self.ultimi_numeri = json.load(open("nonToccare/ultimi.json"))
        self.trash = []
        self.selected = []
        self.smistamento = {}

        self.bolla = pd.read_excel("./bolla/bolla.xlsx")
        self.bolla = prepara_excel(self.bolla)

        if not os.path.exists("./risultati"):
            os.mkdir("./risultati")
        if not os.path.exists("./nonToccare"):
            os.mkdir("./nonToccare")
        if not os.path.exists("./nonToccare/json_data"):
            os.mkdir("./nonToccare/json_data")

        #prepare bolla

        self.tot_bolla = len(self.bolla.keys())
        self.num_arretrati = 0



        self.label_testata = QtWidgets.QLabel("TESTATA:")
        self.line_testata = QtWidgets.QLineEdit()
        self.label_testata.setFont(QtGui.QFont('Times', self.fontSize))
        self.line_testata.setFont(QtGui.QFont('Times', self.fontSize))
        self.layout.addWidget(self.label_testata, 30, 0)
        self.layout.addWidget(self.line_testata, 30, 1)

        self.label_abbonato = QtWidgets.QLabel("# COPIE ORDINATE:")
        self.line_abbonato = QtWidgets.QLineEdit()
        self.label_abbonato.setFont(QtGui.QFont('Times', self.fontSize))
        self.line_abbonato.setFont(QtGui.QFont('Times', self.fontSize))
        self.layout.addWidget(self.label_abbonato, 50, 0)
        self.layout.addWidget(self.line_abbonato, 50, 1)

        self.label_editore = QtWidgets.QLabel("EDITORE:")
        self.line_editore = QtWidgets.QLineEdit()
        self.label_editore.setFont(QtGui.QFont('Times', self.fontSize))
        self.line_editore.setFont(QtGui.QFont('Times', self.fontSize))
        self.layout.addWidget(self.label_editore, 40, 0)
        self.layout.addWidget(self.line_editore, 40, 1)

        self.label_progress = QtWidgets.QLabel("PROGRESSO ATTUALE:")
        self.label_percentage = QtWidgets.QLabel(str(self.idx) + "/" + str(self.tot_bolla) )
        self.label_progress.setFont(QtGui.QFont('Times', self.fontSize))
        self.label_percentage.setFont(QtGui.QFont('Times', self.fontSize))
        self.layout.addWidget(self.label_progress, 60, 0)
        self.layout.addWidget(self.label_percentage, 61, 0)


        self.search0_button = QtWidgets.QPushButton('INIZIA DA ZERO')
        self.search0_button.setFont(QtGui.QFont('Times', self.fontSize))
        self.search0_button.clicked.connect(lambda x: self.search(scratch=True))
        self.search0_button.setStyleSheet("background-color: red")
        self.layout.addWidget(self.search0_button, 60, 0, 10, 2)

        self.search_button = QtWidgets.QPushButton('RIPRENDI')
        self.search_button.setFont(QtGui.QFont('Times', self.fontSize))
        self.search_button.clicked.connect(lambda x: self.search(scratch=False))
        self.search_button.setStyleSheet("background-color: green")
        self.layout.addWidget(self.search_button, 61, 0, 10, 2)

        self.label_testata.setStyleSheet("color: white")
        self.label_testata.setStyleSheet("color: white")
        self.label_abbonato.setStyleSheet("color: white")
        self.label_editore.setStyleSheet("color: white")
        self.label_progress.setStyleSheet("color: white; background-color: purple")
        self.label_percentage.setStyleSheet("color: white; background-color: purple")

        self.line_testata.returnPressed.connect(lambda: self.next_search("change", self.bolla[int(self.idx)]['descrizione'], name_mod=self.line_testata.text()))

        self.setLayout(self.layout)


    def new_page(self):
        for elem in self.trash:
            elem.setParent(None)
        self.trash = []
        self.setLayout(self.layout)

    def next_search(self, mode, nome, name_mod=None, copie=1):
        self.new_page()

        self.num_arretrati = 0

        if mode == "previous":
            if self.idx == 0:
                self.smistamento = {}
            else:
                self.smistamento.pop(int(self.idx), None)
                self.idx -= 1
                self.smistamento[int(self.idx)] = {}
                f = open("./nonToccare/dove_eravamo.txt", 'w')
                f.write(str(self.idx))
                f.close()

            write_risultati(self.smistamento)
            self.search(skip=True)

            return

        elif mode == "boh":
            if int(self.idx) not in self.smistamento.keys():
                self.smistamento[self.idx] = {}
            self.smistamento[int(self.idx)]['esito']   = "indecisi"
            self.smistamento[int(self.idx)]['testate'] = nome
            self.smistamento[int(self.idx)]['numero']  = copie

        elif mode == "next":
            if int(self.idx) not in self.smistamento.keys():
                self.smistamento[self.idx] = {}
            if len(self.selected) == 0:
                if 'testate' not in self.smistamento[int(self.idx)].keys():
                    #if len(self.smistamento[int(self.idx)]['testate']) == 0:
                    self.smistamento[int(self.idx)] = {}
                    self.search(skip=True, name_mod=name_mod)
                    return
            self.smistamento[int(self.idx)]['esito'] = "smistato"
            self.smistamento[int(self.idx)]['rimanenti'] = self.rimanenti
            self.smistamento[int(self.idx)]['prezzo'] = float(self.bolla[int(self.idx)]['prezzo'])


        self.selected = []
        if mode != "change":
            write_risultati(self.smistamento)

            self.idx += 1
            f = open("./nonToccare/dove_eravamo.txt", 'w')
            f.write(str(self.idx))
            f.close()
            self.label_percentage.setText(str(self.idx) + "/" + str(self.tot_bolla))

        if self.idx == self.tot_bolla:
            self.fine_bolla()
            return

        self.smistamento[int(self.idx)] = {}
        self.search(skip=True, name_mod=name_mod)


    def fine_bolla(self):
        self.new_page()

        label_nuovo_nome = QtWidgets.QLabel("FINE!")
        label_nuovo_nome.setFont(QtGui.QFont('Times', 50))
        self.layout.addWidget(label_nuovo_nome, 100, 1, 10, 2)


    def arretrato_match(self, nome):

        self.new_page()

        label_nuovo_nome = QtWidgets.QLabel("DI CHI E'?")
        line_nuovo_nome = QtWidgets.QLineEdit()
        label_nuovo_nome.setFont(QtGui.QFont('Times', self.fontSize))
        line_nuovo_nome.setFont(QtGui.QFont('Times', self.fontSize))
        self.layout.addWidget(label_nuovo_nome, 80, 0)
        self.layout.addWidget(line_nuovo_nome, 80, 1)

        add_button_1 = QtWidgets.QPushButton('CERCA')
        add_button_1.setFont(QtGui.QFont('Times', self.fontSize))
        add_button_1.setStyleSheet("background-color: blue")
        add_button_1.clicked.connect(lambda x: self.user_search(line_nuovo_nome.text().upper(), nome))

        add_button_2 = QtWidgets.QPushButton('STOP ARRETRATI')
        add_button_2.setFont(QtGui.QFont('Times', self.fontSize))
        add_button_2.setStyleSheet("background-color: red")
        add_button_2.clicked.connect(lambda x: self.search(skip=True))

        line_nuovo_nome.returnPressed.connect(lambda: self.user_search(line_nuovo_nome.text().upper(), nome))
        self.layout.addWidget(add_button_1, 82, 0, 10, 2)
        self.layout.addWidget(add_button_2, 84, 0, 10, 2)

        self.trash.append(line_nuovo_nome)
        self.trash.append(label_nuovo_nome)
        self.trash.append(add_button_1)
        self.trash.append(add_button_2)


    def user_search(self, nome, nome_original):
        self.new_page()

        self.arretrato_match(nome_original)

        lista_casellanti = cerca_per_abbonato(nome, self.database)

        if lista_casellanti == None:
            return

        else:
            pos = 0
            for casellante in lista_casellanti:
                aux = QtWidgets.QPushButton(casellante)
                aux.setFont(QtGui.QFont('Times', self.fontSize))
                aux.clicked.connect(lambda checked, text=[casellante,nome_original] : self.add_arretrato(text))
                self.layout.addWidget(aux, 90+pos, 0, 10, 2)
                self.trash.append(aux)
                pos += 5
            arretrato = QtWidgets.QPushButton("NUOVO: "+ nome)
            arretrato.setStyleSheet("background-color: orange")
            arretrato.setFont(QtGui.QFont('Times', self.fontSize))
            arretrato.clicked.connect(lambda x: self.add_arretrato([nome, nome_original]))
            self.layout.addWidget(arretrato, 95+pos, 0, 10, 2)
            self.trash.append(arretrato)
            self.setLayout(self.layout)



    def add_arretrato(self, input):
        abbonato, nome_original = input
        if 'testate' not in self.smistamento[int(self.idx)].keys():
            self.smistamento[int(self.idx)]['testate'] = {}
        if 'nome_fornitore' not in self.smistamento[int(self.idx)].keys():
            self.smistamento[int(self.idx)]['nome_fornitore'] = nome_original
        if nome_original not in self.smistamento[int(self.idx)]['testate'].keys():
            self.smistamento[int(self.idx)]['testate'][nome_original] = {}
        self.smistamento[int(self.idx)]['testate'][nome_original][abbonato] = {}
        self.smistamento[int(self.idx)]['testate'][nome_original][abbonato]['num'] = 1
        self.smistamento[int(self.idx)]['testate'][nome_original][abbonato]['sconto'] = 'arretrato'
        self.num_arretrati += 1
        self.rimanenti -= 1
        self.arretrato_match(nome_original)

    def selection_clicked(self, input):
        nome_fornitore, articolo, lista_abbonati, bottone = input
        if articolo not in self.selected:
            if self.idx not in self.smistamento.keys():
                self.smistamento[int(self.idx)] = {}
            if 'testate' not in self.smistamento[int(self.idx)].keys():
                self.smistamento[int(self.idx)]['testate'] = {}
            if 'nome_fornitore' not in self.smistamento[int(self.idx)].keys():
                self.smistamento[int(self.idx)]['nome_fornitore'] = nome_fornitore
            if nome_fornitore not in self.smistamento[int(self.idx)]['testate'].keys():
                self.smistamento[int(self.idx)]['testate'][articolo] = {}
            for abbonato in lista_abbonati.keys():
                self.smistamento[int(self.idx)]['testate'][articolo][abbonato] = {}
                self.smistamento[int(self.idx)]['testate'][articolo][abbonato]['num'] = lista_abbonati[abbonato]
                self.smistamento[int(self.idx)]['testate'][articolo][abbonato]['sconto'] = 'abbonamento'
                self.rimanenti -= 1
            self.selected.append(articolo)
            bottone.setStyleSheet("background-color: green")
        else:
            self.selected.remove(articolo)
            for abbonato in lista_abbonati.keys():
                if articolo in self.smistamento[int(self.idx)]['testate'].keys():
                    self.smistamento[int(self.idx)]['testate'][articolo].pop(abbonato, None)
                    self.rimanenti += 1
            if articolo in self.smistamento[int(self.idx)]['testate'].keys():
                if len(self.smistamento[int(self.idx)]['testate'][articolo].keys()) == 0:
                    self.smistamento[int(self.idx)]['testate'].pop(articolo, None)
            bottone.setStyleSheet("background-color: white")


    def search(self, skip=False, scratch=True, add_pair=None, name_mod=None):
        self.new_page()

        if not skip:
            if not scratch:
                f = open("./nonToccare/dove_eravamo.txt", 'r')
                self.idx = int(f.readlines()[0])
                self.label_percentage.setText(str(self.idx) + "/" + str(self.tot_bolla))

                where = './nonToccare/json_data'
                json_data = os.listdir(where)
                json_data = [os.path.join(where, x) for x in json_data]
                json_data.sort(key=os.path.getctime)
                self.json_path = json_data[-1]
                self.smistamento = json.load(open(self.json_path))
                write_risultati(self.smistamento)

            else:
                where = './nonToccare/json_data'
                today = date.today()
                json.dump({}, open(os.path.join(where, "json_" +str(today)+ ".json" ), 'w'))
                self.smistamento = {}
                write_risultati(self.smistamento)
                self.smistamento[int(self.idx)] = {}


            self.search_button.setParent(None)
            self.search0_button.setParent(None)
            self.setLayout(self.layout)




        nome_fornitore = self.bolla[int(self.idx)]['descrizione']
        self.rimanenti = self.bolla[int(self.idx)]['quantità']
        testata = filtra_nome_testata(nome_fornitore)
        self.line_testata.setText(nome_fornitore)
        if name_mod != None:
            testata = name_mod


        editore = self.bolla[int(self.idx)]['editore']
        self.line_editore.setText(editore)

        copie = int(self.bolla[int(self.idx)]['quantità'])
        self.line_abbonato.setText(str(copie))

        risultati = cerca_per_testata(testata, self.database)

        #Getta il testo del bottone cliccato che chiama la funzione
        next_button = QtWidgets.QPushButton("PREVIOUS :(")
        next_button.setFont(QtGui.QFont('Times', self.fontSize))
        next_button.clicked.connect(lambda x: self.next_search("previous", nome_fornitore, copie=copie))
        next_button.setStyleSheet("background-color: gray")
        self.layout.addWidget(next_button, 50, 0, 10, 2)
        self.trash.append(next_button)

        next_button = QtWidgets.QPushButton("NEXT!")
        next_button.setFont(QtGui.QFont('Times', self.fontSize))
        next_button.clicked.connect(lambda x: self.next_search("next", nome_fornitore))
        next_button.setStyleSheet("background-color: blue")
        self.layout.addWidget(next_button, 60, 0, 10, 2)
        self.trash.append(next_button)

        unknown = QtWidgets.QPushButton("Ah Boh..")
        unknown.setFont(QtGui.QFont('Times', self.fontSize))
        unknown.clicked.connect(lambda x: self.next_search("boh", nome_fornitore, copie=copie))
        unknown.setStyleSheet("background-color: red")
        self.layout.addWidget(unknown, 80, 0, 10, 2)
        self.trash.append(unknown)

        arretrato = QtWidgets.QPushButton("Arretrati (Attualmente: " + str(self.num_arretrati) + ')')
        arretrato.setFont(QtGui.QFont('Times', self.fontSize))
        #arretrato.setAlignment(Qt.AlignCenter)
        arretrato.clicked.connect(lambda x: self.arretrato_match(nome_fornitore))
        arretrato.setStyleSheet("background-color: yellow")
        self.layout.addWidget(arretrato, 82, 0, 10, 2)
        self.trash.append(arretrato)

        pos = 0

        for risultato in risultati.keys():
            final_text = '(' + str(risultati[risultato]['numero_copie']) + ')  -->' + risultato
            final_text += trova_ultimo_numero(risultato, self.ultimi_numeri)
            aux = QtWidgets.QPushButton(final_text)
            aux.setFont(QtGui.QFont('Times', self.fontSize))

            aux.clicked.connect(lambda checked, text=[nome_fornitore, risultato, risultati[risultato]['abbonati'], aux] : self.selection_clicked(text))
            aux.setStyleSheet("background-color: white")
            if risultato in self.selected:
                aux.setStyleSheet("background-color: green")
            ll = list(risultati[risultato]['abbonati'].keys())
            suggestion_text = ""
            for elem in ll:
                suggestion_text += elem
                suggestion_text += '\n'
            aux.setToolTip(suggestion_text)
            self.layout.addWidget(aux, 84+pos, 0, 10, 2)
            self.trash.append(aux)
            pos += 2

        self.setLayout(self.layout)



def main():


    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('QtCurve')

    main_page = mainPage()
    main_page.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
