import pandas as pd
import folium as f 
import numpy as np
from folium.plugins import TimestampedGeoJson
from datetime import datetime
import requests
import io

#uses api to retrieve data for all states
response = requests.get("https://api.covidtracking.com/v1/states/daily.csv")
r = response.content
df=pd.read_csv(io.StringIO(r.decode('utf-8'))) #converts data into df

#uses df stored in github to retrieve lat/long for each state
url= "https://raw.githubusercontent.com/erub24/COVIDMap/master/stateLatLong.csv"
s=requests.get(url).content
df2=pd.read_csv(io.StringIO(s.decode('utf-8')))

#makemap2 creates one timeslider, makemap creates two that are not synchronized

#if you want a dynamic title, try merging the newDF with df3?
#didnt' quite work but coudl be worth looking into more


newDF=df.merge(df2, left_on="state", right_on="State")


def convertDates(df):
    dateList=[]
    for index in range(len(df["date"])):
        s= df["date"][index]
        s=str(s)
        date = datetime(year=int(s[0:4]), month=int(s[4:6]), day=int(s[6:8]))
        dateList.append(date)
    return dateList
#adds formatted date column to dataframe
newDates = convertDates(newDF)
newDates = pd.Series(newDates)
newDF["newDates"] =newDates

def perCapCases(df):
    popList=[]
    for index in range(len(df["Population"])):
        perPerson = float(df["positiveIncrease"][index])/float(df["Population"][index])
        perCap = perPerson*1000000 #finds cases per 1,000,000
        popList.append(perCap)
    return popList

def perCapDeath(df):
    popList=[]
    for index in range(len(df["Population"])):
        perPerson = float(df["deathIncrease"][index])/float(df["Population"][index])
        perCap = perPerson*1000000 #finds deaths per 1,000,000
        popList.append(perCap)
    return popList

casesPerCap = perCapCases(newDF)
casesPerCap = pd.Series(casesPerCap)
newDF["casesPerCap"] =casesPerCap

deathsPerCap = perCapDeath(newDF)
deathsPerCap = pd.Series(deathsPerCap)
newDF["deathsPerCap"] =deathsPerCap

def create_geojson_features3(df):
    print('> Creating GeoJSON features...')
    features = []
    for index, row in df.iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type':'Point', 
                'coordinates':[row['Longitude'],row['Latitude']]
            },
            'properties': {
                'time': row['newDates'].date().__str__(),
                'popup':'<h1> <p style = "font-family:helvetica;font-size:20px;">'+\
                    row['FullName']+'</p> <p style = "font-family:helvetica;font-size:16px;">'\
                    +str(row['newDates'].strftime('%b %d'))+": "+\
                    str((df["positiveIncrease"][index]))+" new cases</p><h1>",
                'icon': 'circle',
                'iconstyle':{
                    'color': '#7082c2',
                    'fillColor': '#7082c2',
                    'fillOpacity': .5,
                    'stroke': 'true',
                    'radius': df['casesPerCap'][index]/50
                }
                
                }
                }
        feature2 = {
        'type': 'Feature',
        'geometry': {
            'type':'Point', 
            'coordinates':[row['Longitude'],row['Latitude']]
        },
        'properties': {
            'time': row['newDates'].date().__str__(),
            'popup':'<h1> <p style = "font-family:helvetica;font-size:20px;">'+\
                row['FullName']+'</p> <p style = "font-family:helvetica;font-size:16px;">'\
                +str(row['newDates'].strftime('%b %d'))+": "+\
                str((df["deathIncrease"][index]))+" new deaths</p><h1>",
            'icon': 'circle',
            'iconstyle':{
                'color': '#636363',
                'fillColor': '#636363',
                'fillOpacity': 1,
                'stroke': 'true',
                'radius': df['deathsPerCap'][index]/50
                }
            }
            }
        features.append(feature)
        features.append(feature2)
    return features


def make_map2(features):
    print('> Making map...')
    coords=[37.0902,-95.7129]
    m = f.Map(location=coords, tiles='cartodbpositron', control_scale=True, zoom_start=3)
    TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features': features}
        , period='P1D'
        , add_last_point=True
        , auto_play=False
        , loop=False
        , max_speed=2
        , loop_button=True
        , date_options='MM/DD'
        , time_slider_drag_update=True
        , duration='P0D' #prevents new data from layering on top of old
    ).add_to(m)
    print("Done!")
    return m

def plotMap(df):
    features = create_geojson_features3(df)
    return make_map2(features)

covidMap= plotMap(newDF)

covidMap
