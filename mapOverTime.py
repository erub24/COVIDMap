import pandas as pd
import folium as f 
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import webbrowser
from folium.plugins import TimestampedGeoJson
from datetime import datetime

df = pd.read_csv("allstates.csv")
df2=pd.read_csv("stateLatLong.csv")

#makemap2 creates one timeslider, makemap creates two that are not synchronized

#if you want a dynamic title, try merging the newDF with df3?
#didnt' quite work but coudl be worth looking into more


def findPerPositive(df):
    list =[]
    for index in range(len(df["totalTestResultsIncrease"])):
        if df["totalTestResultsIncrease"][index] != 0:
            div = df["positiveIncrease"][index]/df["totalTestResultsIncrease"][index]
            list.append(div)
        else:
            list.append(0)
    return list


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
        perCap = perPerson*1000000
        popList.append(perCap)
    return popList

def perCapTests(df):
    popList=[]
    for index in range(len(df["Population"])):
        perPerson = float(df["totalTestResultsIncrease"][index])/float(df["Population"][index])
        perCap = perPerson*1000000
        popList.append(perCap)
    return popList

casesPerCap = perCapCases(newDF)
casesPerCap = pd.Series(casesPerCap)
newDF["casesPerCap"] =casesPerCap

testsPerCap = perCapTests(newDF)
testsPerCap = pd.Series(testsPerCap)
newDF["testsPerCap"] =testsPerCap

    

def create_geojson_features(df):
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
                    str((df["totalTestResultsIncrease"][index]))+" New Tests </p><h1>",
                'icon': 'circle',
                'iconstyle':{
                    'fillColor': '#B7B6DD',
                    'fillOpacity': 0.5,
                    'stroke': 'true',
                    'radius': df['testsPerCap'][index]/100
   
                
                }
            }
        }
        
        features.append(feature)
    return features
def create_geojson_features2(df):
    print('> Creating More GeoJSON features...')
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
                    str((df["positiveIncrease"][index]))+" New Cases </p><h1>",
                'icon': 'circle',
                'iconstyle':{
                    'color': '#DA4737',
                    'fillColor': '#DA4737',
                    'fillOpacity': 0.5,
                    'stroke': 'true',
                    'radius': df['casesPerCap'][index]/100
                }
                
                }
     
                }
        features.append(feature)
    return features


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
                    str((df["positiveIncrease"][index]))+" New Cases </p><h1>",
                'icon': 'circle',
                'iconstyle':{
                    'color': '#DA4737',
                    'fillColor': '#DA4737',
                    'fillOpacity': 1,
                    'stroke': 'true',
                    'radius': df['casesPerCap'][index]/100
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
                str((df["totalTestResultsIncrease"][index]))+" New Tests </p><h1>",
            'icon': 'circle',
            'iconstyle':{
                'color': '#B7B6DD',
                'fillColor': '#B7B6DD',
                'fillOpacity': 0.5,
                'stroke': 'true',
                'radius': df['testsPerCap'][index]/100
                }
            }
            }
        features.append(feature2)
        features.append(feature)
    return features


def make_map(features,features2):
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
    
    TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features': features2}
        , period='P1D'
        , add_last_point=True
        , auto_play=False
        , loop=False
        , max_speed=2
        , loop_button=True
        , date_options='MM/DD'
        , time_slider_drag_update=True
        , duration='P0D'
    ).add_to(m)
    
    print('> Done.')
    return m

def make_map2(features):
    title = "test"
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
    #features2 = create_geojson_features2(df)
    return make_map2(features)

#tried adding title, and it didn't work well with timeslider, not visible until
    #you zoom in and then title disappears 

covidMap= plotMap(newDF)
covidMap.save('mapTest.html')
webbrowser.open("mapTest.html")


          