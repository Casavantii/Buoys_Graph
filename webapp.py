#coding=utf-8
from flask import Flask, request, abort
from flask import render_template
import json
import mysql.connector
import sys
from datetime import datetime

import logging
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)


DB_HOST = 'localhost'  # IP or hostname of database
DB_NAME = 'rsconcep_uberg_data'  # Name of the database to use
DB_USER = 'rsconcep_xavier_uberg'  # Username for accessing database
DB_PASS = '5H8uvuM8f9HBkSv'  # Password for database user

dict_bouees = ''

def insert_into_db(buoyIMEI, timestamp, tempUP, tempDOWN, doUP, doDOWN, depth):
    try:
      cnx = mysql.connector.connect(host=DB_HOST,
                                    user=DB_USER,
                                    password=DB_PASS,
                                    database=DB_NAME)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return "Something is wrong with your user name or password"
        else:
            return str(err)
    
    try:
        cursor = cnx.cursor()
        sql = 'insert into vertical_profiles (buoyIMEI, timestamp, tempUP, tempDOWN, doUP, doDOWN, depth) values ( %s, %s, %s, %s, %s, %s, %s)'
        values = (buoyIMEI, timestamp, tempUP, tempDOWN, doUP, doDOWN, depth)
        cursor.execute(sql, values)
    except Exception as err:
        cnx.close()
        return str(err)
    
    cnx.close()
    return 'success'
    
def get_all_data():
    try:
      cnx = mysql.connector.connect(host=DB_HOST,
                                    user=DB_USER,
                                    password=DB_PASS,
                                    database=DB_NAME)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return "Something is wrong with your user name or password"
        else:
            return str(err)
    
    try:
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM vertical_profiles GROUP BY timestamp, depth")

        dict_bouees = cursor.fetchall()


    except Exception as err:
        cnx.close()
        return str(err)
    
    cnx.close()
    return dict_bouees

@app.route("/allo")
def hello():
    return 'Hello Bruno Courtemanche'
 
@app.route("/simple_chart")
def chart():
    buoyImei = []
    timestamps = []
    tempUP = []
    tempDN = []
    doUP = []
    doDOWN = []
    depth = []
    values = [[],[]]
    labels = [[],[]]
    dbo = get_all_data()
    for x in dbo:
        datestring = x[1].strftime("%A, %d. %B %Y %I:%M%p")
        y = list(x)
        buoyImei.append(x[0])
        timestamps.append(datestring)
        tempUP.append(x[2])
        tempDN.append(x[3])
        doUP.append(x[4])
        doDOWN.append(x[5])
        depth.append(x[6])
    legend = ['Temperature UP', 'Temperature DOWN']
    for i in range(19):
        values[0].append(tempUP[i])
        values[1].append(depth[i])
        labels.append(depth[i])
    
    return render_template('chart.html', values=values, labels=labels, legend=legend)

@app.route("/")
def helloa():
    timestamps = []
    html = "<h3>Température et oxygène dissoute ordonés par l'heure de profilage et la profondeur</h3>"
    dbo = get_all_data()
    for x in dbo:
        datestring = x[1].strftime("%A, %d. %B %Y %I:%M%p")
        y = list(x)
        y[1] = datestring
        timestamps.append(datestring)
        html += '<p>' + str(y) + '</p>'
    
    html += '<br><br>'
    html += '''<label for="pet-select">Choose a pet:</label>
    <select name="pets" id="pet-select">
    <option value="">--Please choose an option--</option>'''
    for y in timestamps:
        html += '<option value="' + y + '">' + y + '</option>'
    html += '</select>'
    
    
    return html


@app.route('/upload')
def upload():
    buoyIMEI = request.args.get('buoyIMEI')
    timestamp = request.args.get('timestamp')
    tempUP = request.args.get('tempUP')
    tempDOWN = request.args.get('tempDOWN')
    doUP = request.args.get('doUP')
    doDOWN = request.args.get('doDOWN')
    depth = request.args.get('depth')
    
    if buoyIMEI and timestamp and tempUP and tempDOWN and doUP and doDOWN and depth:
        return insert_into_db(buoyIMEI, timestamp, tempUP, tempDOWN, doUP, doDOWN, depth)

if __name__ == '__main__':
    app.run(debug=True)
