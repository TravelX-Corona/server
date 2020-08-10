import requests
import json
import math
import datetime
import populartimes
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os.path
import _thread
from os import path
from flask import Flask, send_file
app = Flask(__name__)

def convertTemp(kelvin):
    temp = math.floor((kelvin-273.15) * ( 9 / 5 ) + 32)
    return temp
def generateUrl(ident):
    url = "http://openweathermap.org/img/wn/" + ident + "@2x.png"
    return url
@app.route('/info/<inlat>/<inlon>')
def getapiresquest(inlat, inlon):
    lat = float(inlat)
    lon = float(inlon)
    apikey = "48cf356c4a913e3d6d803b9ca9ebf1d5"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=" + str(lat) + "&lon=" + str(lon) + "&exclude=minutely&appid=" + apikey
    response= requests.request("POST", url)
    response = response.json()
    ##Current values
    sunrise = response["current"]["sunrise"]
    sunset = response["current"]["sunset"]
    sunrise = datetime.datetime.fromtimestamp(sunrise).strftime("%I:%M %p")
    sunset = datetime.datetime.fromtimestamp(sunset).strftime("%I:%M %p")
    currentTemp = convertTemp(response["current"]["temp"])
    weatherdescr = response["current"]["weather"][0]["description"]
    currentimgurl = generateUrl(response["current"]["weather"][0]["icon"])
    currentvals = [currentTemp, weatherdescr, currentimgurl, sunrise, sunset]
    print(currentimgurl)
    ##Future values
    futureTemps = [convertTemp(response["hourly"][0]["temp"]), convertTemp(response["hourly"][1]["temp"]), convertTemp(response["hourly"][2]["temp"]), convertTemp(response["hourly"][3]["temp"]), convertTemp(response["hourly"][4]["temp"]), convertTemp(response["hourly"][5]["temp"])]
    futureIcons = [generateUrl(response["hourly"][0]["weather"][0]["icon"]), generateUrl(response["hourly"][1]["weather"][0]["icon"]),generateUrl(response["hourly"][2]["weather"][0]["icon"]),generateUrl(response["hourly"][3]["weather"][0]["icon"]),generateUrl(response["hourly"][4]["weather"][0]["icon"]),generateUrl(response["hourly"][5]["weather"][0]["icon"])]
    futurePrecipitation = [response["hourly"][0]["pop"], response["hourly"][1]["pop"],response["hourly"][2]["pop"], response["hourly"][3]["pop"], response["hourly"][4]["pop"], response["hourly"][5]["pop"]]
    vals = {
        "currentVals": currentvals,
        "sixhrstemps": futureTemps,
        "sixhrsicons": futureIcons,
        "sixhrsprecip": futurePrecipitation
        }
    val_son = json.dumps(vals)
    return val_son

@app.route('/histodata/<place_ide>/<iday>')
def histogram(place_ide, iday):
    api_key = "AIzaSyBvOur9iaRBPKa7aJWgHZObOIwr1b1O7PM"
    place_id = str(place_ide)
    day = int(iday)-1
    try:
        data = populartimes.get_id(api_key, place_id)
        daily = data["populartimes"]
        histovals = daily[day]["data"]
        returner = { "histovals": histovals}
        returner = json.dumps(returner)
        print(returner)
    except:
        returner = { "histovals": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
    return returner

@app.route('/openhours/<place_ide>/<weekda>')
def openhours(place_ide, weekda):
    place_id = str(place_ide)
    weekday = int(weekda)
    weekday-=1
    api_key = "AIzaSyBvOur9iaRBPKa7aJWgHZObOIwr1b1O7PM"
    url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + place_id + "&fields=name,opening_hours&key=" + api_key
    response = requests.request("POST", url)
    response = response.json()
    opennow = response["result"]["opening_hours"]["open_now"]
    texttodisplay = response["result"]["opening_hours"]["weekday_text"][weekday]
    print(texttodisplay)
    vals = { "opennow": opennow, "text": texttodisplay}
    vals_son = json.dumps(vals)
    return vals_son

@app.route('/scoredisplay/<inlat>/<inlon>')
def scoredisplay(inlat, inlon):
    lat = float(inlat)
    lon = float(inlon)
    filename = str(lat) + "," + str(lon) + ".txt"
    if (path.exists(filename)):
        with open(filename, 'r') as reader:
            score = float(reader.readline())
            scorefreq = int(reader.readline())
            returner = ""
            valo = { "score" : score}
            if score <= 1.45:
                valo["status"] = "VERY LOW"
            elif 1.45 < score <= 1.60:
                valo["status"] = "LOW"
            elif 1.60 < score <= 1.7:
                valo["status"] = "MEDIUM"
            elif 1.70 < score <= 1.80:
                valo["status"] = "HIGH"
            else:
                valo["status"] = "VERY HIGH"
    else:
        valo = { "score": 0}
        valo["status"] = "NO ENTRIES DETECTED"
    valo_son = json.dumps(valo)
    return valo_son

@app.route('/logo.png')
def logo():
    return send_file("logo.png")

@app.route('/calcdata/<inlat>/<inlon>')
def calcdata(inlat, inlon):
    lat = str(inlat)
    lon = str(inlon)
    comment = []
    avgscore = 0.00
    scorefreq = 0
    filenametwo = str(lat) + "," + str(lon) + "_comments.txt"
    with open(filenametwo, 'r') as reader:
        comment.append(reader.readline())
    filenameone = str(lat) + "," + str(lon) + ".txt"
    with open(filenameone, 'r') as readero:
        avgscore = float(readero.readline())
        scorefreq = int(readero.readline())
    valo = {"comments" : comment, "avgscore" : avgscore, "scorefreq" : scorefreq}
    valo_son = json.dumps(valo)
    return valo_son

@app.route('/riskscore/<capacity>/<crowd>/<masks>/<soc_distance>/<inlat>/<inlon>/<comme>')
def calcrisk(capacity, crowd, masks, soc_distance, inlat, inlon, comme):
    masks = int(masks)
    soc_distance = bool(soc_distance)
    crowd = int(crowd)
    capacity = int(capacity)
    lat = float(inlat)
    lon = float(inlon)
    comment = str(comme)
    score = 1
    if masks == 2:
        score*=1.031
    elif masks == 1:
        score*=1.1025
    else:
        score*=1.174
    if soc_distance:
        score*=1.026
    else:
        score*=1.128
    score*=1+(0.442744*math.log((float(crowd)/float(capacity) + 1), 2))
    score = round(score, 3)
    filename = str(lat) + "," + str(lon) + ".txt"
    currentavg = 0
    scorefreq = 0
    if (path.exists(filename)):
        with open(filename, 'r') as reader:
            currentavg = float(reader.readline())
            scorefreq = int(reader.readline())
        currentavg = (currentavg*scorefreq + score)/(scorefreq+1)
        scorefreq+=1
        with open(filename, 'w') as writer:
            writer.write(str(round(currentavg,3)) + "\n")
            writer.write(str(scorefreq) + "\n")
        filenametwo = str(lat) + "," + str(lon) + "_comments.txt"
        with open(filenametwo, 'a') as writer:
            writer.write(comment + "\n")
    else:
        with open(filename, 'w') as writer:
            writer.write(str(score) + "\n")
            writer.write("1\n")
        filenametwo = str(lat) + "," + str(lon) + "_comments.txt"
        with open(filenametwo, 'a') as writer:
            writer.write(comment + "\n")
    if score <= 1.45:
        return str(score) + " - VERY LOW"
    elif 1.45 < score <= 1.60:
        return str(score) + " - LOW"
    elif 1.60 < score <= 1.7:
        return str(score) + " - MEDIUM"
    elif 1.70 < score <= 1.80:
        return str(score) + " - HIGH"
    else:
        return str(score) + " - VERY HIGH"
    return "This wasn't supposed to happen"
app.run(host="0.0.0.0", port=7000)    


