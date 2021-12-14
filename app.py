from os import name
import flask
from flask import Flask, render_template, request
import requests
import pandas as pd
import plotly
import plotly.express as px
import json
import pickle
import numpy as np
from flask_ngrok import run_with_ngrok

import matplotlib.pylab as plt
from matplotlib import pyplot
import plotly.graph_objects as go

from sklearn.preprocessing import MinMaxScaler
import joblib
from sklearn.preprocessing import MinMaxScaler, StandardScaler



# Create Flask's `app` object
app = Flask(
    __name__,
    template_folder="templates"
)
run_with_ngrok(app) 
scaler=MinMaxScaler()

district = {'Delhi' : 'datatraining.txt', 'Mumbai' : "datatraining.txt",'Goa' : "datatraining.txt"}
def tocelcius(temp):
    return str(round(float(temp) - 273.16,2))

def plotgraph(city,sdate,edate) :
    str1 = 'static/csv/'
    str2 = str(district[city])
    path = str1 + str2
    print(path)
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    mask = (df['date'] >= sdate) & (df['date'] <= edate)
    df = df.loc[mask]
    temperature = px.line(df, x="date", y="Temperature", labels={ "date": "Time", "max": "Temperature(C)",},width=1200, height=280 )
    maxspeed = px.line(df, x = 'date', y = "Humidity", labels={ "date": "Time", "min": "Humidity",},width=1200, height=280)
    precip = px.line(df, x='date', y='CO2', labels={ "date": "Time", "mxspd": "Co2 Level",},width=1200, height=280)
    tempJSON = json.dumps(temperature, cls=plotly.utils.PlotlyJSONEncoder)
    mxspdJSON = json.dumps(maxspeed, cls=plotly.utils.PlotlyJSONEncoder)
    prcpJSON = json.dumps(precip, cls=plotly.utils.PlotlyJSONEncoder)
    return tempJSON,mxspdJSON,prcpJSON

def weatherapi(city,sdate,edate):
    try:
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=48a90ac42caa09f90dcaeee4096b9e53'
        source = requests.get(url.format(city)).json()
    except:
        return None
    # converting json data to dictionary

    # data for variable list_of_data
    data = {
        "temp_cel" : tocelcius(source['main']['temp']) + ' C',
        "humidity" : str(source['main']['humidity']) + " %",
        "cityname" : city.upper(),
        "speed" : str(source['wind']['speed']) + ' km/h',
        "pressure" : str(source['main']['pressure']),
        "startdate" : sdate,
        "enddate" : edate

    }
    return data

city = 'Delhi'


@app.route("/" , methods = ['POST', 'GET'])
def index():
    global city
    if request.method == 'POST' :
        city =  request.form['city']
    else :
        city = 'Delhi'

    data = weatherapi(city,sdate = "2015-02-04",edate="2015-02-15")
    # Ploting graphs
    tempJSON,mxspdJSON,prcpJSON = plotgraph(city,sdate = "2015-02-04",edate="2015-02-15")
    return render_template('index.html',data=data, temp = tempJSON, spd = mxspdJSON, prcp = prcpJSON)

@app.route("/dataselect" , methods = ['POST', 'GET'])
def dataselect() :
    global city
    if request.method == 'POST' :
        sdate = request.form['startdate']
        edate = request.form['enddate']
    data = weatherapi(city,sdate,edate)
    tempJSON,mxspdJSON,prcpJSON = plotgraph(city,sdate,edate)
    return render_template('index.html', data=data,temp = tempJSON, spd = mxspdJSON, prcp = prcpJSON)

@app.route('/charts')
def charts():
	return render_template('charts.html')

@app.route('/tables')
def tables():
	return render_template('tables.html')

app.run()
