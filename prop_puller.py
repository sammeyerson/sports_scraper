import requests
from datetime import date, datetime
import pandas as pd
import numpy as np
from scraper import get_game_logs
from datetime import timedelta, date, datetime
import dateutil.parser
import ast
import time
import os

def cleanDataValues(data):

    labels = data.get('Labels')
    df = data.get('Data Values')
    dataValues = []
    for x in df:
        replacer = ast.literal_eval(x)
        dataValues.append(replacer)

    print(type(dataValues))
    print(dataValues)
    data = {
        'Labels': labels,
        'Data Values': dataValues
    }


    return data


def pullFullSeasonProps():
    pathName = 'fullSeasonPropData.csv'
    if os.path.exists(pathName):

        fullSeasonData = pd.read_csv('fullSeasonPropData.csv')
        labels = fullSeasonData['Label'].tolist()
        dataValues = fullSeasonData['Data'].tolist()

        data = {
            'Labels': labels,
            'Data Values': dataValues
        }
        data = cleanDataValues(data)
    else:
        data = {
            'Labels': 'n/a',
            'Data Values': []
        }

    return data

def pull_last2MonthsProps():
    pathName = 'last2months_SeasonPropData.csv'
    if os.path.exists(pathName):
        fullSeasonData = pd.read_csv('last2months_SeasonPropData.csv')
        labels = fullSeasonData['Label'].tolist()
        dataValues = fullSeasonData['Data'].tolist()
        data = {
            'Labels': labels,
            'Data Values': dataValues
        }
        data = cleanDataValues(data)
    else:
        data = {
            'Labels': 'n/a',
            'Data Values': []
        }

    return data

def pull_lastMonthSeasonProps():

    pathName = 'lastmonth_PropData.csv'
    if os.path.exists(pathName):

        fullSeasonData = pd.read_csv('lastmonth_PropData.csv')
        labels = fullSeasonData['Label'].tolist()
        dataValues = fullSeasonData['Data'].tolist()
        data = {
            'Labels': labels,
            'Data Values': dataValues
        }
        data = cleanDataValues(data)
    else:
        data = {
            'Labels': 'n/a',
            'Data Values': []
        }


    return data



def gameLogsInfo(name, category, start, end, number):
    #print('-',name,'-')
    gameData = get_game_logs(name, start, end, False)
    gameDataP = get_game_logs(name, start, end, True)
    frames = [gameData, gameDataP]
    gameData = pd.concat(frames)



    overCount = 0
    underCount = 0
    pushCount = 0

    number = float(number)
    outTags = ["Inactive","Did Not Play","Not With Team","Did Not Dress"]
    #print(gameData)
    #print(type(gameData))
    if gameData is None:
        return [['Over', 'Under', 'Push'], [overCount, underCount, pushCount]]
    gameData = gameData.loc[~gameData['MP'].isin(outTags)]


    if category == "RA":

        for index, row in gameData.iterrows():

            assist = float(row['AST'])
            rebound = float(row['TRB'])
            dataPoint = assist+rebound

            if dataPoint > number:
                overCount += 1
            elif dataPoint < number:
                underCount +=1
            else:
                pushCount +=1


        returnVal = [['Over', 'Under', 'Push'], [overCount, underCount, pushCount]]
        return returnVal

    elif "PRA" in category:

        for index, row in gameData.iterrows():

            point = float(row['PTS'])
            assist = float(row['AST'])
            rebound = float(row['TRB'])
            dataPoint = point+assist+rebound

            if dataPoint > number:
                overCount += 1
            elif dataPoint < number:
                underCount +=1
            else:
                pushCount +=1


        returnVal = [['Over', 'Under', 'Push'], [overCount, underCount, pushCount]]
        return returnVal
    elif "PTS+TRB" in category:

        for index, row in gameData.iterrows():

            point = float(row['PTS'])

            rebound = float(row['TRB'])
            dataPoint = point+rebound

            if dataPoint > number:
                overCount += 1
            elif dataPoint < number:
                underCount +=1
            else:
                pushCount +=1


        returnVal = [['Over', 'Under', 'Push'], [overCount, underCount, pushCount]]
        return returnVal
    elif "PTS+AST" in category:

        for index, row in gameData.iterrows():

            point = float(row['PTS'])

            rebound = float(row['AST'])
            dataPoint = point+rebound

            if dataPoint > number:
                overCount += 1
            elif dataPoint < number:
                underCount +=1
            else:
                pushCount +=1


        returnVal = [['Over', 'Under', 'Push'], [overCount, underCount, pushCount]]
        return returnVal



    for index, row in gameData.iterrows():


        dataPoint = float(row[category])
        if dataPoint > number:
            overCount += 1
        elif dataPoint < number:
            underCount +=1
        else:
            pushCount +=1

    returnVal = [['Over', 'Under', 'Push'], [overCount, underCount, pushCount]]
    return returnVal




def getNBAProps(game, itter):

    r = requests.get(game)
    print('\n',r)

    x = r.json()[0]
    #print(x)
    events = x['events'][0]
    description = events['description']
    print(description)
    displayGroups = events['displayGroups']

    propDescriptionHits = []
    propDescriptions = []
    handicaps =[]
    americanPrices = []
    games = []
    print(game)
    for x in displayGroups:
        if 'Player Props' in x['description']:
            markets = x['markets']
            for a in markets:
                propDescription = a['descriptionKey']
                note = a['notes']
                outcomes = a['outcomes']
                #propDescriptions.append(propDescription)
                #propDescriptions.append(propDescription)
                #print(propDescription)
                #print(outcomes,'\n')
                itt = 0
                overFound = False
                underFound = False
                overOdd = 0
                underOdd = 0
                for i in outcomes:

                    propDescriptionHit = i['description']
                    price = i['price']
                    americanPrice = price['american']
                    if 'Over' in propDescriptionHit:
                        overFound = True
                        overOdd = americanPrice

                    if 'Under' in propDescriptionHit:
                        underFound = True
                        underOdd = americanPrice

                    if 'handicap' in price:
                        handicap = price['handicap']

                        #propDescriptionHits.append(propDescriptionHit)
                        #americanPrices.append(americanPrice)
                        #handicaps.append(handicap)
                    #else:
                        #handicap = price['handicap']
                        #propDescriptionHits.append(propDescriptionHit)
                        #americanPrices.append(americanPrice)
                        #handicaps.append(0)
                    itt+=1
                    if itt == 2:

                        if overFound and underFound:
                            games.append(description)
                            propDescriptionHits.append('Over/Under')
                            toAdd = str(overOdd+'/'+underOdd)
                            americanPrices.append(toAdd)
                            propDescriptions.append(propDescription)
                            handicaps.append(handicap)
                        elif overFound:
                            games.append(description)
                            propDescriptionHits.append('Over')
                            toAdd = str(overOdd)
                            americanPrices.append(toAdd)
                            propDescriptions.append(propDescription)
                            handicaps.append(handicap)
                        elif underFound:
                            games.append(description)
                            propDescriptionHits.append('Under')
                            toAdd = str(underOdd)
                            americanPrices.append(toAdd)
                            propDescriptions.append(propDescription)
                            handicaps.append(handicap)




    data = {
        'Prop Descriptions': propDescriptions,
        'Prop Description Hits': propDescriptionHits,
        'Handicaps' : handicaps,
        'Prices': americanPrices,
        'Game': games
    }
    df = pd.DataFrame.from_dict(data)
    #print(df)
    #print(df)
    #today = str(date.today())
    #csvFile = 'props'+today+'_'+str(itter)+'.csv'
    #df.to_csv(csvFile)

    return df


def getNBAGames(currentTime):

    r = requests.get('https://www.bovada.lv/services/sports/event/v2/events/A/description/basketball/nba')
    x = r.json()[0]

    events = x['events']
    returnList = []
    for x in events:
        #print('\n\n\n\n',x)
        time_date = str(x['link'].split('-')[-1])[-4:]
        print(time_date)
        difference = int(time_date)-int(currentTime)
        print(difference)
        #if difference > 0 and difference < 300:
        description = x['description']
        if '@' in description:
            link = x['link']
            links = link.split('/')
            link = links[-1]
            link = 'https://www.bovada.lv/services/sports/event/v2/events/A/description/basketball/nba/'+link+'?lang=en'
            returnList.append(link)

    return returnList

def analyzeProps(df, startDate, endDate):


    dataList = []
    labels = []
    overPercents = []
    games = []
    for index, row in df.iterrows():
        #print(row)
        description = row['Prop Descriptions']
        handicap = row['Handicaps']
        over_under = row['Prop Description Hits']
        price = row['Prices']

        #print(description)
        splitDescription = description.split('-')
        name = splitDescription[1].split('(')[0][:-1]
        name = name[1:]
        today = str(datetime.now()).split()[0]
        propType = splitDescription[0]

        if 'Points' in propType and 'Rebounds' in propType and 'Assists' in propType:

            propType = 'PRA'
            data = gameLogsInfo(name, propType, startDate, endDate, handicap)
            nums = data[1]
            overNum = int(nums[0])
            under_push_nums = int(nums[1])+int(nums[2])
            if under_push_nums == 0:
                continue
            percOver = float(overNum/(under_push_nums+overNum))
            overPercents.append(percOver)
            dataList.append(data)
            temp = name +' '+ over_under+' '+str(handicap)+' '+propType+' @ '+str(price)
            labels.append(temp)
            games.append(row['Game'])
            #print(name, over_under,propType, handicap, '@', price)
            #print(data)
        elif 'Rebounds' in propType and 'Assists' in propType:

            propType = 'RA'
            data = gameLogsInfo(name, propType, startDate, endDate, handicap)
            nums = data[1]
            overNum = int(nums[0])
            under_push_nums = int(nums[1])+int(nums[2])
            if under_push_nums == 0:
                continue
            percOver = float(overNum/(under_push_nums+overNum))
            overPercents.append(percOver)
            dataList.append(data)
            temp = name +' '+ over_under+' '+str(handicap)+' '+propType+' @ '+str(price)
            labels.append(temp)
            games.append(row['Game'])
            #print(name, over_under,propType, handicap, '@', price)
            #print(data)
        elif 'Points' in propType and 'Rebounds' in propType:

            propType = 'PTS+TRB'
            data = gameLogsInfo(name, propType, startDate, endDate, handicap)
            nums = data[1]
            overNum = int(nums[0])
            under_push_nums = int(nums[1])+int(nums[2])
            if under_push_nums == 0:
                continue
            percOver = float(overNum/(under_push_nums+overNum))
            overPercents.append(percOver)
            dataList.append(data)
            temp = name +' '+ over_under+' '+str(handicap)+' '+propType+' @ '+str(price)
            labels.append(temp)
            games.append(row['Game'])
            #print(name, over_under,propType, handicap, '@', price)
            #print(data)
        elif 'Points' in propType and 'Assists' in propType:

            propType = 'PTS+AST'
            data = gameLogsInfo(name, propType, startDate, endDate, handicap)
            nums = data[1]
            overNum = int(nums[0])
            under_push_nums = int(nums[1])+int(nums[2])
            if under_push_nums == 0:
                continue
            percOver = float(overNum/(under_push_nums+overNum))
            overPercents.append(percOver)
            dataList.append(data)
            temp = name +' '+ over_under+' '+str(handicap)+' '+propType+' @ '+str(price)
            labels.append(temp)
            games.append(row['Game'])
        elif 'Points' in propType:

            propType = 'PTS'
            data = gameLogsInfo(name, propType, startDate, endDate, handicap)
            nums = data[1]
            overNum = int(nums[0])
            under_push_nums = int(nums[1])+int(nums[2])
            if under_push_nums == 0:
                continue
            percOver = float(overNum/(under_push_nums+overNum))
            overPercents.append(percOver)
            dataList.append(data)
            temp = name +' '+ over_under+' '+str(handicap)+' '+propType+' @ '+str(price)
            labels.append(temp)
            games.append(row['Game'])
            #print(name, over_under,propType, handicap, '@', price)
            #print(data)
        elif 'Rebounds' in propType:

            propType = 'TRB'
            data = gameLogsInfo(name, propType, startDate, endDate, handicap)
            nums = data[1]
            overNum = int(nums[0])
            under_push_nums = int(nums[1])+int(nums[2])
            if under_push_nums == 0:
                continue
            percOver = float(overNum/(under_push_nums+overNum))
            overPercents.append(percOver)
            dataList.append(data)
            temp = name +' '+ over_under+' '+str(handicap)+' '+propType+' @ '+str(price)
            labels.append(temp)
            games.append(row['Game'])
            #print(name, over_under,propType, handicap, '@', price)
            #print(data)
        elif 'Assists' in propType:

            propType = 'AST'
            data = gameLogsInfo(name, propType, startDate, endDate, handicap)
            nums = data[1]
            overNum = int(nums[0])
            under_push_nums = int(nums[1])+int(nums[2])
            if under_push_nums == 0:
                continue
            percOver = float(overNum/(under_push_nums+overNum))
            overPercents.append(percOver)
            dataList.append(data)
            temp = name +' '+ over_under+' '+str(handicap)+' '+propType+' @ '+str(price)
            labels.append(temp)
            games.append(row['Game'])
            #print(name, over_under,propType, handicap, '@', price)
            #print(data)

        #gameLogsInfo(name, category, start, end, number)

    data = {
        'Label':labels,
        'Data': dataList,
        'Percentage Over': overPercents,
        'Game': games
    }
    df = pd.DataFrame(data)

    #print(df)
    #returnList = [dataList, labels]
    return df



"""
links = getNBAGames()

listNames = []
for link in links:
    linkList = link.split('/')
    link = linkList[-1]
    linksList = link.split('?')
    link = linksList[0]
    listNames.append(link)

itt = 0
for i in links:
    getNBAProps(i, listNames[itt])
    itt+=1
"""
#analyzeProps()
now = datetime.now()
lastMonth = str(now + dateutil.relativedelta.relativedelta(months=-1)).split()[0]
#print(lastMonth)

twoMonthsAgo = str(now + dateutil.relativedelta.relativedelta(months=-2)).split()[0]
#print(twoMonthsAgo)



"""
seasonStartDate = '2020-12-22'
today = str(datetime.now()).split()[0]
itt = 0
os.environ['TZ'] = 'US/Eastern'
time.tzset()
timestamp = str(time.strftime('%H:%M:%S')).split(':')
timestamp = timestamp[0]+timestamp[1]
games = getNBAGames(timestamp)
print(games)

totalDF = pd.DataFrame()
for i in games:
    df = getNBAProps(i, itt)
    val = analyzeProps(df, seasonStartDate, today)
    print('val df:\n',val)
    totalDF = totalDF.append(val, ignore_index=True)
    itt+=1
totalDF = totalDF.sort_values(by=['Percentage Over'], ascending=False)
totalDF.to_csv('/home/sammeyerson/dailyPropData/fullSeasonPropData.csv')
print('\n\nTotal df for full season:\n',totalDF)

totalDF = pd.DataFrame()
for i in games:
    df = getNBAProps(i, itt)
    val = analyzeProps(df, lastMonth, today)
    print('val df:\n',val)
    totalDF = totalDF.append(val, ignore_index=True)
    itt+=1
totalDF = totalDF.sort_values(by=['Percentage Over'], ascending=False)
totalDF.to_csv('/home/sammeyerson/dailyPropData/lastmonth_PropData.csv')
print('\n\nTotal df for last month season:\n',totalDF)

totalDF = pd.DataFrame()
for i in games:
    df = getNBAProps(i, itt)
    val = analyzeProps(df, twoMonthsAgo, today)
    print('val df:\n',val)
    totalDF = totalDF.append(val, ignore_index=True)
    itt+=1
totalDF = totalDF.sort_values(by=['Percentage Over'], ascending=False)
totalDF.to_csv('/home/sammeyerson/dailyPropData/last2months_SeasonPropData.csv')
print('\n\nTotal df for last 2 months season:\n',totalDF)
#df = getNBAProps('https://www.bovada.lv/services/sports/event/v2/events/A/description/basketball/nba/philadelphia-76ers-denver-nuggets-202103302100?lang=en',0)
#print(getNBAGames())
#today = str(datetime.now()).split()[0]
#print(today)
#print(analyzeProps(df))"""
"""
os.environ['TZ'] = 'US/Eastern'
time.tzset()
timestamp = str(time.strftime('%H:%M:%S')).split(':')
timestamp = timestamp[0]+timestamp[1]
games = getNBAGames(timestamp)
print(games)"""
