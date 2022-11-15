import numpy
import mysql.connector
from datetime import datetime
import pandas as pd
import sqlalchemy
import json
import pyodbc

def appendDataToDict(strMonth, numMonth):
    for i in range(len(dates)): 
        if dates[i].month == numMonth:
            monthly_data[strMonth]["data"].append(array_data[i])


def populateAvgP(month):
    entries = 0
    total = 0    
    for data in monthly_data[month]["data"]:
        high = data[9]
        low = data[10]
        average = (high + low)/2
        total += average
        entries += 1
    if entries == 0:
        monthly_data[month]["avgP"] = 0
    else:
        monthly_data[month]["avgP"] = round(total/entries,2)

con = mysql.connector.connect(host="localhost", user="root", passwd="pass", database= "data1")
cursor = con.cursor()

read_data = pd.read_sql_query("SELECT * FROM table1", con, index_col = "count")

dates = [x for x in read_data["datetime"].dt.date]
monthly_data = {
    "January": {"data": [], "avgP": 0},
    "Febuary": {"data": [], "avgP": 0},
    "March": {"data": [], "avgP": 0},
    "April": {"data": [], "avgP": 0},
    "May": {"data": [], "avgP": 0},
    "June": {"data": [], "avgP": 0},
    "July": {"data": [], "avgP": 0},
    "August": {"data": [], "avgP": 0},
    "September": {"data": [], "avgP": 0},
    "October": {"data": [], "avgP": 0},
    "November": {"data": [], "avgP": 0},
    "December": {"data": [], "avgP": 0},
}
dailyAvgCol = []
monthlyAvgCol = []
months = ["January", "Febuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
array_data = read_data.to_numpy()

i = 1
for month in months:
    appendDataToDict(month, i)
    i = i+1

for month in months:
    populateAvgP(month)

for month in months:
    for i in range(len(monthly_data[month]["data"])):
        monthlyAvgCol.append(monthly_data[month]["avgP"])

for data in array_data:
    high = data[9]
    low = data[10]
    average = (high + low)/2
    dailyAvgCol.append(round(average,2))

read_data["monthly avg price"] = monthlyAvgCol
read_data["daily avg price"] = dailyAvgCol

x = zip(monthlyAvgCol, dailyAvgCol, range(0, len(dailyAvgCol)))
list = [a for a in x]

query = "ALTER TABLE table1 ADD COLUMN monthlyAvgPrice double;"
query2 = "ALTER TABLE table1 ADD COLUMN dailyAvgPrice double;"
cursor.execute(query)
cursor.execute(query2)

row = 0
for i in range(0, len(monthlyAvgCol)):
    sql = "UPDATE table1 set monthlyAvgPrice = %s, dailyAvgPrice = %s where count = %s;"
    cursor.execute(sql, (list[i]))
    row+=1

entry = cursor.execute("Select * from tatmot_nse_historical_data")
table = cursor.fetchall()
for entry in table:
    print(entry)

con.commit()