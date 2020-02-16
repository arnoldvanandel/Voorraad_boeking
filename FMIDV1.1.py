from flask import Flask, render_template, url_for, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import pyodbc
import mysql.connector
from mysql.connector import Error
import pandas as pd
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FMID.db'
db = SQLAlchemy(app)

SESSION_TYPE = 'redis'
app.secret_key = "abc"

#cnxn = pyodbc.connect('DRIVER={FreeTDS};SERVER=192.168.5.1;PORT=1433;DATABASE=AXDB30SP4;UID=Andelcontrol;PWD=########')
#cursor = cnxn.cursor()

connection = mysql.connector.connect(host='192.168.178.221',
                                         database='FMID',
                                         user='arnold',
                                         password='1407')

now = datetime.datetime.now()

class Voorraad_boeking(db.Model):
    Index = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.String(80), nullable=False)
    artikelnummer = db.Column(db.String(80), nullable=False)
    locatie = db.Column(db.String(80), nullable=False)
    Aantal_Volle_Dozen = db.Column(db.Integer(), nullable=True)
    Rest_Doos_Aantal = db.Column(db.Integer(), nullable=True)
    Alles = db.Column(db.Integer(), nullable=True)
    Totaal_Aantal = db.Column(db.Integer(), nullable=True)
    Check_Aantal_Volle_Dozen = db.Column(db.Integer(), nullable=True)
    Check_Rest_Doos_Aantal = db.Column(db.Integer(), nullable=True)
    Check_Totaal_Aantal = db.Column(db.Integer(), nullable=True)
    In_Axapta_Geboekt = db.Column(db.String(80), nullable=True)

    def __init__(self, Index=None, datum=None, artikelnummer=None, locatie=None, Aantal_Volle_Dozen=None, Rest_Doos_Aantal=None, Alles=None, Totaal_Aantal=None, Check_Aantal_Volle_Dozen=None, Check_Rest_Doos_Aantal=None, Check_Totaal_Aantal=None, In_Axapta_Geboekt=None):
        self.Index = Index
        self.datum = datum
        self.artikelnummer = artikelnummer
        self.locatie = locatie
        self.Aantal_Volle_Dozen = Aantal_Volle_Dozen
        self.Rest_Doos_Aantal = Rest_Doos_Aantal
        self.Alles = Alles
        self.Totaal_Aantal = Totaal_Aantal
        self.Check_Aantal_Volle_Dozen = Check_Aantal_Volle_Dozen
        self.Check_Rest_Doos_Aantal = Check_Rest_Doos_Aantal
        self.Check_Totaal_Aantal = Check_Totaal_Aantal
        self.In_Axapta_Geboekt = In_Axapta_Geboekt

    def __repr__(self):
        return '<artikelnummer %r>' % (self.artikelnummer)

def FMID():
    data_form = list(dict(request.form).items())
    barcode = data_form[0][1]
    selectline_barcode_artikel = "SELECT itemId FROM InventItemBarcode WHERE (itemBarCode =" + barcode + ")" 
    cursor.execute(selectline_barcode_artikel)
    rows = cursor.fetchall()
    artikel = str(rows[0][0])
    selectline_axapta = "SELECT SUM(dbo.INVENTSUM.PHYSICALINVENT) AS Expr1, dbo.INVENTDIM.WMSLOCATIONID AS Expr2 FROM dbo.INVENTSUM INNER JOIN dbo.INVENTDIM ON dbo.INVENTSUM.INVENTDIMID = dbo.INVENTDIM.INVENTDIMID WHERE (dbo.INVENTSUM.ITEMID ='" + artikel + "') AND (dbo.INVENTSUM.PHYSICALINVENT <> 0) GROUP BY dbo.INVENTDIM.WMSLOCATIONID"
    cursor.execute(selectline_axapta)
    rows = cursor.fetchall()
    voorraad = []
    voorraad1 = []
    for row in rows:
        voorraad1 = []
        if row[0]!=0:
            voorraad1.append(str(int(row[0])) + " stuks")
            voorraad1.append(row[1])
            voorraad.append(voorraad1) 
    return voorraad, artikel, barcode

def thuis():
    voorraad = []
    voorraad1 = []
    voorraad1.append("900 stuks")
    voorraad1.append('1225-1')
    voorraad.append(voorraad1)
    voorraad1 = []
    voorraad1.append("50 stuks")
    voorraad1.append('2321-4')
    voorraad.append(voorraad1)
    artikel = "A105 22-22"
    result = list(dict(request.form).items())
    barcode = result[0][1]
    return voorraad, artikel, barcode

@app.route('/')
@app.route("/home")
def home():
    artikel = ""
    barcode = ""
    rows=[]
    session['response']='session#1'
    return render_template('home.html', locaties=rows, artikel=artikel, barcode=barcode)

@app.route('/locaties', methods=['GET', 'POST'])
def locaties():  
    if request.method == "GET":
        return render_template('home.html')

    gegevens = thuis()
    #gegevens = FMID()
    session['artikel'] = gegevens[1]
    session['barcode'] = gegevens[2]
    session['locatie'] = ""
    session['in_uit'] = ""
    return render_template('locaties.html', locaties=gegevens[0], artikel=session['artikel'], barcode=session['barcode'])

@app.route("/test")
def test():
    
    df = pd.read_sql('SELECT * FROM Voorraad_boeking', con=connection)
    print(df.to_html())
    gegevens = list(dict(request.form).items())
    print(gegevens)
    artikel = df.to_html()
    barcode = ""
    rows=[]
    session['response']='session#1'
    return render_template('test.html', locaties=rows, artikel=artikel, barcode=barcode)
    
@app.route('/locatieuit', methods=['GET', 'POST'])
def locatieuit():  
    if request.method == "GET":
        return render_template('home.html')

    if request.form['submit_button'] == "Voorraad in":
        session['in_uit'] = "Inboeken Voorraad"
    elif request.form['submit_button'] == "Uit voorraad":
        session['in_uit'] = "Uit voorraad boeken"
    return render_template('locatieuit.html', artikel=session['artikel'], barcode=session['barcode'], in_uit=session['in_uit'])

@app.route('/locatieuitboeken', methods=['GET', 'POST'])
def locatieuitboeken():  
    if request.method == "GET":
        return render_template('home.html')

    gegevens = list(dict(request.form).items())
    session['locatie'] = gegevens[0][1]
    if session['in_uit'] == "Inboeken Voorraad":
        checkbox = 'hidden'
        alles = ''
        checkbox_value = '0'
    elif session['in_uit'] == "Uit voorraad boeken":
        checkbox = 'checkbox'
        alles = 'Alles'
        checkbox_value = '1'
    return render_template('locatieuitboeken.html', artikel=session['artikel'], barcode=session['barcode'], locatie=session['locatie'], in_uit=session['in_uit'],
        checkbox=checkbox, alles=alles, checkbox_value=checkbox_value)

@app.route('/locatieuitgeboekt', methods=['GET', 'POST'])
def locatieuitgeboekt():  
    if request.method == "GET":
        return render_template('home.html')

    gegevens = list(dict(request.form).items())
    datum = now.strftime("%d-%m-%Y")
    if session['in_uit'] == "Inboeken Voorraad":
        if gegevens[1][1] == '':
            aantal_volle_dozen = '0'
        else:
            aantal_volle_dozen = gegevens[1][1]

        if gegevens[2][1] == '':
            rest_doos_aantal = '0'
        else:
            rest_doos_aantal = gegevens[2][1]
    elif session['in_uit'] == "Uit voorraad boeken":
        if gegevens[1][1] == '':
            aantal_volle_dozen = '0'
        else:
            aantal_volle_dozen = str(int(gegevens[1][1]) * -1)

        if gegevens[2][1] == '':
            rest_doos_aantal = '0'
        else:
            rest_doos_aantal = str(int(gegevens[2][1]) * -1)
    mySql_insert_query = "INSERT INTO Voorraad_boeking (Datum, Artikelnummer, Locatie, Aantal_Volle_Dozen, Rest_Doos_Aantal, Alles) VALUES ('" + datum + "', '" + session['artikel'] + "', '" + session['locatie'] + "', " + aantal_volle_dozen + ", " + rest_doos_aantal + ", " + gegevens[0][1] + ")"
    cursor = connection.cursor()
    cursor.execute(mySql_insert_query)
    connection.commit()
    print(cursor.rowcount, "Record inserted successfully into Laptop table")
    cursor.close()
    #new_user = Voorraad_boeking(datum='10-5-2020', artikelnummer=session['artikel'], locatie=session['locatie'], Aantal_Volle_Dozen=gegevens[0][1], Rest_Doos_Aantal=gegevens[1][1], Alles=gegevens )  # Create an instance of the User class
    #db.session.add(new_user)  # Adds new User record to database
    #db.session.commit()  # Commits all changes
    return render_template('locatieuitgeboekt.html', artikel=session['artikel'], barcode=session['barcode'], locatie=session['locatie'], Aantal_Volle_Dozen=aantal_volle_dozen, Rest_Doos_Aantal=rest_doos_aantal, Alles=gegevens[0][1], in_uit=session['in_uit'])

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')